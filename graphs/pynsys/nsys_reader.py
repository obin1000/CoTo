
import pandas as pd
import numpy as np
import h5py
from . import nsys_constants as nsys


class NsysReader:
    def __init__(self, input_file_hdf) -> None:
        """ Read an nsys report (export) and convert it pandas dataframes """
        self.h5_file = h5py.File(input_file_hdf)
        
    def get_kernel_events(self) -> pd.DataFrame:
        return pd.DataFrame(np.array(self.h5_file[nsys.TABLE_CUPTI_ACTIVITY_KIND_KERNEL])).sort_values(by=['start'])
    
    def get_gpu_metrics(self) -> pd.DataFrame:
        return pd.DataFrame(np.array(self.h5_file[nsys.TABLE_GPU_METRICS])).sort_values(by=['timestamp'])
    
    def get_string_ids(self) -> pd.DataFrame:
        return pd.DataFrame(np.array(self.h5_file[nsys.TABLE_STRING_IDS]))
    
    def get_target_info_gpu_metrics(self) -> pd.DataFrame:
        return pd.DataFrame(np.array(self.h5_file[nsys.TABLE_TARGET_INFO_GPU_METRICS]))


        
        
