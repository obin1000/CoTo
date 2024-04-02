import pandas as pd

from .nsys_reader import NsysReader
from . import nsys_constants as nsys_const

TIME_SPLITTER_NS = 50_000

COMPRESSION_KERNELS = ['snap_kernel', 'lz_compression_kernel', 'lz4CompressBatchKernel', 'compress_kernel', 'batch_encoder_kernel', 'cascaded_compression_kernel', 'lz_compress_longest_matches', 'lz_compress_greedy_hash', 'huffman_encode', 'gdeflate_encode']
DECOMPRESSION_KERNELS = ['unsnap_kernel', 'decompression_kernel', 'lz4DecompressBatchKernel', 'decompress_kernel', 'batch_decoder_kernel', 'cascaded_decompression_kernel_type_check', 'inflate_kernel', 'gdeflateDecompress']

CATEGORY_COMPRESSION='compress'
CATEGORY_DECOMPRESSION='decompress'
CATEGORY_OTHER='other'


class NsysParserGPUMetrics:
    def __init__(self, nsys_reader: NsysReader, file_size) -> None:
        self.file_size = file_size
        self.reader = nsys_reader
        self.kernel_event_df = nsys_reader.get_kernel_events()
        self.target_info_gpu_metrics_df = nsys_reader.get_target_info_gpu_metrics()
        self.gpu_metric_df = nsys_reader.get_gpu_metrics()
        self.strings_df = nsys_reader.get_string_ids()
        self.add_extra_info()
    
    def add_extra_info(self) -> None:
        """ Calculates the average utilization of each kernel """
        self.kernel_event_df['utilization'] = self.kernel_event_df.apply(lambda row: self.get_avg_utilization_of_span(row['start'], row['end']), axis=1)
        self.kernel_event_df['name'] = self.kernel_event_df['shortName'].apply(self.get_string)

        self.kernel_event_df['chunk_size'] = (self.file_size / self.kernel_event_df['gridX']).astype(int)
        self.kernel_event_df['duration'] = self.kernel_event_df['end'] - self.kernel_event_df['start']
        
    def get_string(self, id) -> str:
        """ Translate a string id to a string """
        return str(self.strings_df.loc[self.strings_df['id'] == id, 'value'].values[0], encoding='utf-8')
    
    def decode_bytes(byte_str):
        return byte_str.decode('utf-8')
    
    def get_gpu_metric_id(self, name) -> int:
        metric_ids = self.target_info_gpu_metrics_df[self.target_info_gpu_metrics_df['metricName'].apply(NsysParserGPUMetrics.decode_bytes).str.contains(name, case=False)]
        if len(metric_ids) > 0:
            return int(metric_ids['metricId'].values[0])
        # print('Did not find metric id for ' + str(name))
        return 17
    
    def get_utilization_metrics_in_span(self, begin, end) -> pd.DataFrame:
        """ Gives a dataframe with GPU utilisation metrics between give timestamps (ns) """
        utilisation_metric_id = self.get_gpu_metric_id(nsys_const.METRIC_COMPUTE_WARPS)
        compute_metrics = self.gpu_metric_df.loc[self.gpu_metric_df['metricId'] == utilisation_metric_id]
        return compute_metrics[compute_metrics['timestamp'].between(begin, end, inclusive="both")]
    
    def get_unallocated_metrics_in_span(self, begin, end) -> pd.DataFrame:
        """ Gives a dataframe with unallocated warps metrics between give timestamps (ns) """
        compute_metrics = self.gpu_metric_df.loc[self.gpu_metric_df['metricId'] == nsys_const.METRIC_UNALLOCATED_WARPS]
        return compute_metrics[compute_metrics['timestamp'].between(begin, end, inclusive="both")]


    def get_avg_utilization_of_span(self, begin, end) -> float:
        """ Gives the average GPU utilisation between give timestamps (ns) """
        utilizations = self.get_utilization_metrics_in_span(begin, end)
        if len(utilizations) < 1:
            # print('Waning: No utilization data found in provided range')
            return -1
        if len(utilizations) == 1:
            return utilizations['value'].iloc[0]
        # Get the time difference between all metric timestamps
        utilizations['metric_diff'] = utilizations['timestamp'].diff()
        # Remove broken data
        utilizations = utilizations.dropna(subset=['metric_diff', 'value'])
        # Total time difference between all metric points in the span
        time_diff_sum = utilizations['metric_diff'].sum()
        if time_diff_sum == 0:
            # print("No time difference between metrics")
            return -1
        # Weighted average of each metric and their duration
        utilization = (utilizations['metric_diff'] * utilizations['value']).sum() / time_diff_sum
        
        return utilization
    

    def weighted_mean(df):
        return (df['utilization'] * df['duration']).sum() / df['duration'].sum()


    def categorize_group(group):
        """ Determines the category for a group of kernels """
        if any(string in COMPRESSION_KERNELS for string in group['name'].values):
            return CATEGORY_COMPRESSION
        elif any(string in DECOMPRESSION_KERNELS for string in group['name'].values):
            return CATEGORY_DECOMPRESSION
        else:
            return CATEGORY_OTHER
        
    def get_group_data(self) -> pd.DataFrame:
        """ Gives a dataframe with the data grouped in compression, decompression, and other """
        self.kernel_event_df['time_since_previous'] = self.kernel_event_df['start'] - self.kernel_event_df['end'].shift(1)
        self.kernel_event_df['group'] = self.kernel_event_df['time_since_previous'].gt(TIME_SPLITTER_NS).cumsum()

        # Apply the function to each group
        groups_durations = self.kernel_event_df.groupby('group')['duration'].sum().rename('duration').reset_index()
        groups_categories = self.kernel_event_df.groupby('group').apply(NsysParserGPUMetrics.categorize_group).rename('category')
        groups_utilizations = self.kernel_event_df.groupby('group').apply(NsysParserGPUMetrics.weighted_mean).rename('utilization')
        groups_num_kernels = self.kernel_event_df.groupby('group').size().rename('num_kernels')
        
        return pd.concat([groups_categories, groups_durations, groups_utilizations, groups_num_kernels], axis=1)
    
    def get_compressions_average_utilizations(self) -> tuple[float, float]:
        group_data = self.get_group_data()
        group_data_compress = group_data[group_data['category'] != CATEGORY_OTHER]

        group_data_compress = group_data_compress.groupby('category').agg({'duration': 'mean',
                                                                   'utilization': 'mean',})
        
        compression = group_data_compress['utilization'].loc[CATEGORY_COMPRESSION]
        decompression = group_data_compress['utilization'].loc[CATEGORY_DECOMPRESSION]
                
        return [compression, decompression]
    
    def get_compressions_average_durations(self) -> tuple[float, float]:
        group_data = self.get_group_data()
        group_data_compress = group_data[group_data['category'] != CATEGORY_OTHER]

        group_data_compress = group_data_compress.groupby('category').agg({'duration': 'mean',
                                                                   'utilization': 'mean',})
        
        compression = group_data_compress['duration'].loc[CATEGORY_COMPRESSION]
        decompression = group_data_compress['duration'].loc[CATEGORY_DECOMPRESSION]
                
        return [compression, decompression]
    
    
    
    
