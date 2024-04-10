import pandas as pd
from pynsys.nsys_reader import NsysReader
from pynsys.nsys_parser_gpu_metrics import NsysParserGPUMetrics


TIME_SPLITTER_NS = 50_000

COMPRESSION_KERNELS = ['snap_kernel', 'lz_compression_kernel', 'lz4CompressBatchKernel', 'compress_kernel', 'batch_encoder_kernel', 'cascaded_compression_kernel', 'lz_compress_longest_matches', 'lz_compress_greedy_hash', 'huffman_encode', 'gdeflate_encode']
DECOMPRESSION_KERNELS = ['unsnap_kernel', 'decompression_kernel', 'lz4DecompressBatchKernel', 'decompress_kernel', 'batch_decoder_kernel', 'cascaded_decompression_kernel_type_check', 'inflate_kernel', 'gdeflateDecompress']

CATEGORY_COMPRESSION='compress'
CATEGORY_DECOMPRESSION='decompress'
CATEGORY_OTHER='other'


def human_format(num):
    magnitude = 0
    while abs(num) >= 1024:
        magnitude += 1
        num /= 1024
    return '{}{}'.format('{}'.format(num).rstrip('0').rstrip('.'), ['', 'k', 'M', 'G', 'T'][magnitude])

def fix_chunks(df, file_size):
    """ 
    chunk: number of chunks (approx number of threads), 
    chunksize_Byte: number of bytes in chunk
    """
    df['chunksize_Bytes'] = file_size / df['chunks']
    df['chunksize_Bytes_formatted'] = df['chunksize_Bytes'].apply(human_format)
    df['chunks_formatted'] = df['chunks'].apply(human_format)
    df['chunks_combined_formatted'] = df['chunks'].apply(lambda x : f"{human_format(x)} chunks of {human_format(file_size / x)}B")
    return df
        
def weighted_mean(df):
    return (df['utilization'] * df['duration']).sum() / df['duration'].sum()


def categorize_group(group):
    """ Determines the category for a group of kernels """
    if any(string in DECOMPRESSION_KERNELS for string in group['name'].values):
        return CATEGORY_DECOMPRESSION
    elif any(string in COMPRESSION_KERNELS for string in group['name'].values):
        return CATEGORY_COMPRESSION
    else:
        return CATEGORY_OTHER
    
def get_group_data(kernel_event_df: pd.DataFrame) -> pd.DataFrame:
    """ Gives a dataframe with the kernel data grouped in compression, decompression, and other """
    kernel_event_df['time_since_previous'] = kernel_event_df['start'] - kernel_event_df['end'].shift(1)
    kernel_event_df['group'] = kernel_event_df['time_since_previous'].gt(TIME_SPLITTER_NS).cumsum()
    
    groups_durations = kernel_event_df.groupby('group')['duration'].sum().rename('duration').reset_index()
    groups_categories = kernel_event_df.groupby('group').apply(categorize_group).rename('category')
    groups_utilizations = kernel_event_df.groupby('group').apply(weighted_mean).rename('utilization')
    groups_num_kernels = kernel_event_df.groupby('group').size().rename('num_kernels')
    
    return pd.concat([groups_categories, groups_durations, groups_utilizations, groups_num_kernels], axis=1)

def get_compressions_average_utilizations(kernel_event_df: pd.DataFrame) -> tuple[float, float]:
    """ Gives the average compression and decompression utilization of given kernel events """
    group_data = get_group_data(kernel_event_df)
    group_data_compress = group_data[group_data['category'] != CATEGORY_OTHER]

    group_data_compress = group_data_compress.groupby('category').agg({'duration': 'mean',
                                                                'utilization': 'mean',})
    
    compression = group_data_compress['utilization'].loc[CATEGORY_COMPRESSION]
    decompression = group_data_compress['utilization'].loc[CATEGORY_DECOMPRESSION]
            
    return [compression, decompression]

def get_compressions_average_durations(kernel_event_df: pd.DataFrame) -> tuple[float, float]:
    group_data = get_group_data(kernel_event_df)
    group_data_compress = group_data[group_data['category'] != CATEGORY_OTHER]

    group_data_compress = group_data_compress.groupby('category').agg({'duration': 'mean',
                                                                'utilization': 'mean',})
    
    compression = group_data_compress['duration'].loc[CATEGORY_COMPRESSION]
    decompression = group_data_compress['duration'].loc[CATEGORY_DECOMPRESSION]
            
    return [compression, decompression]



def get_utilisation_df(dir, file_size, compression_files, compressors, approx_number_of_threads) -> pd.DataFrame:
    result_df = pd.DataFrame(columns=['standard', 'chunk_size', 'chunks', 'file', 'compression_utilization', 'decompression_utilization'])

    for compression_file in compression_files:
        for compressor in compressors:
            for threads_num in approx_number_of_threads:
                input_file = dir + 'output_' + str(compressor) + '_' + str(compression_file) + '_' + str(threads_num) + 'threads.h5'
                chunk_size = file_size/threads_num
                try:
                    reader = NsysReader(input_file)
                    metrics_parser = NsysParserGPUMetrics(reader, file_size)
                    
                    compression_utilisation, decompression_utilisation = get_compressions_average_utilizations(metrics_parser.get_metrics_df())
                except Exception as e:
                    print('Failed getting utilization of ' + str(compressor) + ' ' + str(compression_file) + ' ' + str(threads_num) + ' threads: ' +str(e))
                    continue
                print(str(compression_file) + '  ' + str(compressor) + '  ' + str(threads_num) + '  ' + str(compression_utilisation) + '  ' + str(decompression_utilisation))
                result_df.loc[len(result_df)] = {'standard': str(compressor), 
                                            'chunk_size': int(chunk_size),
                                            'file': str(compression_file),
                                            'chunks': int(threads_num),
                                            'compression_utilization': float(compression_utilisation), 
                                            'decompression_utilization': float(decompression_utilisation)}
            
    return result_df


