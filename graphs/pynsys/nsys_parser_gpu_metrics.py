import pandas as pd

from .nsys_reader import NsysReader
from . import nsys_constants as nsys_const



class NsysParserGPUMetrics:
    def __init__(self, nsys_reader: NsysReader, file_size: int) -> None:
        self.file_size = file_size
        self.reader = nsys_reader
        self.kernel_event_df = nsys_reader.get_kernel_events()
        self.target_info_gpu_metrics_df = nsys_reader.get_target_info_gpu_metrics()
        self.gpu_metric_df = nsys_reader.get_gpu_metrics()
        self.strings_df = nsys_reader.get_string_ids()
        self.add_extra_info()
        
    def get_metrics_df(self) -> pd.DataFrame:
        """ Gives a df with executed kernels and metric data combined """
        return self.kernel_event_df
    
    def add_extra_info(self) -> None:
        """ Calculates the average utilization of each kernel """
        self.kernel_event_df['utilization'] = self.kernel_event_df.apply(lambda row: self.get_avg_utilization_of_span(row['start'], row['end']), axis=1)
        self.kernel_event_df['name'] = self.kernel_event_df['shortName'].apply(self.get_string)

        self.kernel_event_df['chunk_size'] = (self.file_size / self.kernel_event_df['gridX']).astype(int)
        self.kernel_event_df['duration'] = self.kernel_event_df['end'] - self.kernel_event_df['start']
        
        # self.kernel_event_df['memory_usage_avg']
        # self.kernel_event_df['memory_usage_max']
        
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
    
    def get_metrics_in_span(self, begin: int, end: int, type: int) -> pd.DataFrame:
        """ Gives a dataframe with GPU metrics of given type between give timestamps (ns) """
        compute_metrics = self.gpu_metric_df.loc[self.gpu_metric_df['metricId'] == type]
        return compute_metrics[compute_metrics['timestamp'].between(begin, end, inclusive="both")]
    
    def get_avg_memory_of_span(self, begin, end) -> float:
        """ Gives the average memory usage between given timestamps (ns) """
        pass

    def get_avg_utilization_of_span(self, begin, end) -> float:
        """ Gives the average GPU utilisation between give timestamps (ns) """
        utilisation_metric_id = self.get_gpu_metric_id(nsys_const.METRIC_COMPUTE_WARPS)
        utilizations = self.get_metrics_in_span(begin, end, utilisation_metric_id)
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
    


    
    
    
    
