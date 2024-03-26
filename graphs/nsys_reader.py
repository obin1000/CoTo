
import pandas as pd
import numpy as np
import h5py
import nsys_constants as nsys
from tqdm import tqdm
tqdm.pandas()

TIME_SPLITTER_NS = 100_000
FILE_SIZE = 8589934592

COMPRESSION_KERNELS = ['snap_kernel', 'lz_compression_kernel', 'lz4CompressBatchKernel', 'compress_kernel', 'batch_encoder_kernel', 'cascaded_compression_kernel', 'lz_compress_longest_matches', 'lz_compress_greedy_hash', 'huffman_encode', 'gdeflate_encode']
DECOMPRESSION_KERNELS = ['unsnap_kernel', 'decompression_kernel', 'lz4DecompressBatchKernel', 'decompress_kernel', 'batch_decoder_kernel', 'cascaded_decompression_kernel_type_check', 'inflate_kernel', 'gdeflateDecompress']

CATEGORY_COMPRESSION='compress'
CATEGORY_DECOMPRESSION='decompress'
CATEGORY_OTHER='other'

class NsysReader:
    def __init__(self, input_file_hdf) -> None:
        """ Read an nsys report (export) and convert it pandas dataframes """
        h5_file = h5py.File(input_file_hdf)
        self.gpu_metric_df = pd.DataFrame(np.array(h5_file[nsys.GPU_METRICS])).sort_values(by=['timestamp'])
        self.kernel_event_df = pd.DataFrame(np.array(h5_file[nsys.CUPTI_ACTIVITY_KIND_KERNEL])).sort_values(by=['start'])
        self.strings_df = pd.DataFrame(np.array(h5_file[nsys.STRING_IDS]))
        self.add_extra_info()
        
    def add_extra_info(self) -> None:
        """ Calculates the average utilization of each kernel """
        self.kernel_event_df['utilization'] = self.kernel_event_df.apply(lambda row: self.get_avg_utilization_of_span(row['start'], row['end']), axis=1)
        self.kernel_event_df['name'] = self.kernel_event_df['shortName'].apply(self.get_string)

        self.kernel_event_df['chunk_size'] = (FILE_SIZE / self.kernel_event_df['gridX']).astype(int)
        self.kernel_event_df['duration'] = self.kernel_event_df['end'] - self.kernel_event_df['start']
        
    def get_string(self, id) -> str:
        """ Translate a string id to a string """
        return str(self.strings_df.loc[self.strings_df['id'] == id, 'value'].values[0], encoding='utf-8')

    def get_utilization_metrics_in_span(self, begin, end) -> pd.DataFrame:
        """ Gives a dataframe with GPU utilisation metrics between give timestamps (ns) """
        compute_metrics = self.gpu_metric_df.loc[self.gpu_metric_df['metricId'] == nsys.METRIC_COMPUTE_WARPS]
        return compute_metrics[compute_metrics['timestamp'].between(begin, end, inclusive="both")]
    
    def get_unallocated_metrics_in_span(self, begin, end) -> pd.DataFrame:
        """ Gives a dataframe with unallocated warps metrics between give timestamps (ns) """
        compute_metrics = self.gpu_metric_df.loc[self.gpu_metric_df['metricId'] == nsys.METRIC_UNALLOCATED_WARPS]
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
        groups_categories = self.kernel_event_df.groupby('group').apply(NsysReader.categorize_group).rename('category')
        groups_utilizations = self.kernel_event_df.groupby('group').apply(NsysReader.weighted_mean).rename('utilization')
        groups_num_kernels = self.kernel_event_df.groupby('group').size().rename('num_kernels')
        
        return pd.concat([groups_categories, groups_durations, groups_utilizations, groups_num_kernels], axis=1)
    
    def get_compressions_utilizations(self) -> tuple[float, float]:
        group_data = self.get_group_data()
        group_data_compress = group_data[group_data['category'] != CATEGORY_OTHER]

        group_data_compress = group_data_compress.groupby('category').agg({'duration': 'mean',
                                                                   'utilization': 'mean',})
        
        compression = group_data_compress['utilization'].loc[CATEGORY_COMPRESSION]
        decompression = group_data_compress['utilization'].loc[CATEGORY_DECOMPRESSION]
                
        return [compression, decompression]
        
        
class NsysScanner:
    
    def __init__(self, dir) -> None:
        self.dir = dir
        
    def get_utilisation_df(self, compression_files, compressors, approx_number_of_threads) -> pd.DataFrame:
        result_df = pd.DataFrame(columns=['standard', 'chunk_size', 'file', 'compression_utilization', 'decompression_utilization'])

        for compression_file in compression_files:
            for compressor in compressors:
                for threads_num in approx_number_of_threads:
                    input_file = self.dir + 'output_' + str(compressor) + '_' + str(compression_file) + '_' + str(threads_num) + 'threads.h5'
                    chunk_size = FILE_SIZE/threads_num
                    print(input_file)
                    try:
                        reader = NsysReader(input_file)
                        compression_utilisation, decompression_utilisation = reader.get_compressions_utilizations()
                    except Exception as e:
                        print('Failed getting utilization of ' + str(compressor) + ' ' + str(compression_file) + ' ' + str(threads_num) + ' threads: ' +str(e))
                        continue
                    result_df.loc[len(result_df)] = {'standard': str(compressor), 
                                                'chunk_size': int(chunk_size),
                                                'file': str(compression_file),
                                                'compression_utilization': float(decompression_utilisation), 
                                                'decompression_utilization': float(compression_utilisation)}
                
        return result_df