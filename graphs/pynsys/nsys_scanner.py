import pandas as pd
from .nsys_reader import NsysReader
from .nsys_parser_gpu_metrics import NsysParserGPUMetrics

def human_format(num):
    magnitude = 0
    while abs(num) >= 1024:
        magnitude += 1
        num /= 1024
    return '{}{}B'.format('{}'.format(num).rstrip('0').rstrip('.'), ['', 'k', 'M', 'G', 'T'][magnitude])

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

class NsysScanner:
    def __init__(self, dir, file_size) -> None:
        self.dir = dir
        self.file_size = file_size
        
    def get_utilisation_df(self, compression_files, compressors, approx_number_of_threads) -> pd.DataFrame:
        result_df = pd.DataFrame(columns=['standard', 'chunk_size', 'file', 'compression_utilization', 'decompression_utilization'])

        for compression_file in compression_files:
            for compressor in compressors:
                for threads_num in approx_number_of_threads:
                    input_file = self.dir + 'output_' + str(compressor) + '_' + str(compression_file) + '_' + str(threads_num) + 'threads.h5'
                    chunk_size = self.file_size/threads_num
                    try:
                        reader = NsysReader(input_file)
                        parser = NsysParserGPUMetrics(reader, self.file_size)
                        compression_utilisation, decompression_utilisation = parser.get_compressions_average_utilizations()
                    except Exception as e:
                        print('Failed getting utilization of ' + str(compressor) + ' ' + str(compression_file) + ' ' + str(threads_num) + ' threads: ' +str(e))
                        continue
                    print(str(compression_file) + '  ' + str(compressor) + '  ' + str(threads_num) + '  ' + str(compression_utilisation) + '  ' + str(decompression_utilisation))
                    result_df.loc[len(result_df)] = {'standard': str(compressor), 
                                                'chunk_size': int(chunk_size),
                                                'file': str(compression_file),
                                                'compression_utilization': float(compression_utilisation), 
                                                'decompression_utilization': float(decompression_utilisation)}
                
        return result_df