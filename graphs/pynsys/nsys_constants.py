
TABLE_CUPTI_ACTIVITY_KIND_MEMCPY="CUPTI_ACTIVITY_KIND_MEMCPY"
TABLE_CUPTI_ACTIVITY_KIND_KERNEL="CUPTI_ACTIVITY_KIND_KERNEL"
# CUPTI_ACTIVITY_KIND_KERNEL (
#      start                       INTEGER   NOT NULL,                    -- Event start timestamp (ns).
#      end                         INTEGER   NOT NULL,                    -- Event end timestamp (ns).
#      deviceId                    INTEGER   NOT NULL,                    -- Device ID.
#      contextId                   INTEGER   NOT NULL,                    -- Context ID.
#      streamId                    INTEGER   NOT NULL,                    -- Stream ID.
#      correlationId               INTEGER,                               -- REFERENCES CUPTI_ACTIVITY_KIND_RUNTIME(correlationId)
#      globalPid                   INTEGER,                               -- Serialized GlobalId.
#      demangledName               INTEGER   NOT NULL,                    -- REFERENCES StringIds(id) -- Kernel function name w/ templates
#      shortName                   INTEGER   NOT NULL,                    -- REFERENCES StringIds(id) -- Base kernel function name
#      mangledName                 INTEGER,                               -- REFERENCES StringIds(id) -- Raw C++ mangled kernel function name
#      launchType                  INTEGER,                               -- REFERENCES ENUM_CUDA_KERNEL_LAUNCH_TYPE(id)
#      cacheConfig                 INTEGER,                               -- REFERENCES ENUM_CUDA_FUNC_CACHE_CONFIG(id)
#      registersPerThread          INTEGER   NOT NULL,                    -- Number of registers required for each thread executing the kernel.
#      gridX                       INTEGER   NOT NULL,                    -- X-dimension grid size.
#      gridY                       INTEGER   NOT NULL,                    -- Y-dimension grid size.
#      gridZ                       INTEGER   NOT NULL,                    -- Z-dimension grid size.
#      blockX                      INTEGER   NOT NULL,                    -- X-dimension block size.
#      blockY                      INTEGER   NOT NULL,                    -- Y-dimension block size.
#      blockZ                      INTEGER   NOT NULL,                    -- Z-dimension block size.
#      staticSharedMemory          INTEGER   NOT NULL,                    -- Static shared memory allocated for the kernel (B).
#      dynamicSharedMemory         INTEGER   NOT NULL,                    -- Dynamic shared memory reserved for the kernel (B).
#      localMemoryPerThread        INTEGER   NOT NULL,                    -- Amount of local memory reserved for each thread (B).
#      localMemoryTotal            INTEGER   NOT NULL,                    -- Total amount of local memory reserved for the kernel (B).
#      gridId                      INTEGER   NOT NULL,                    -- Unique grid ID of the kernel assigned at runtime.
#      sharedMemoryExecuted        INTEGER,                               -- Shared memory size set by the driver.
#      graphNodeId                 INTEGER,                               -- REFERENCES CUDA_GRAPH_NODE_EVENTS(graphNodeId)
#      sharedMemoryLimitConfig     INTEGER                                -- REFERENCES ENUM_CUDA_SHARED_MEM_LIMIT_CONFIG(id)
#  );
TABLE_TARGET_INFO_GPU_METRICS="TARGET_INFO_GPU_METRICS"


TABLE_CUDA_GPU_MEMORY_USAGE_EVENTS="CUDA_GPU_MEMORY_USAGE_EVENTS"
#  CREATE TABLE CUDA_GPU_MEMORY_USAGE_EVENTS (
#      start                       INTEGER   NOT NULL,                    -- Event start timestamp (ns).
#      globalPid                   INTEGER   NOT NULL,                    -- Serialized GlobalId.
#      deviceId                    INTEGER   NOT NULL,                    -- Device ID.
#      contextId                   INTEGER   NOT NULL,                    -- Context ID.
#      address                     INTEGER   NOT NULL,                    -- Virtual address of the allocation/deallocation.
#      pc                          INTEGER   NOT NULL,                    -- Program counter of the allocation/deallocation.
#      bytes                       INTEGER   NOT NULL,                    -- Number of bytes allocated/deallocated (B).
#      memKind                     INTEGER   NOT NULL,                    -- REFERENCES ENUM_CUDA_MEM_KIND(id)
#      memoryOperationType         INTEGER   NOT NULL,                    -- REFERENCES ENUM_CUDA_DEV_MEM_EVENT_OPER(id)
#      name                        TEXT,                                  -- Variable name, if available.
#      correlationId               INTEGER,                               -- REFERENCES CUPTI_ACTIVITY_KIND_RUNTIME(correlationId)
#      localMemoryPoolAddress      INTEGER,                               -- Base address of the local memory pool used
#      localMemoryPoolReleaseThreshold   INTEGER,                         -- Release threshold of the local memory pool used
#      localMemoryPoolSize         INTEGER,                               -- Size of the local memory pool used
#      localMemoryPoolUtilizedSize   INTEGER,                             -- Utilized size of the local memory pool used
#      importedMemoryPoolAddress   INTEGER,                               -- Base address of the imported memory pool used
#      importedMemoryPoolProcessId   INTEGER                              -- Process ID of the imported memory pool used
#  );

TABLE_GPU_METRICS="GPU_METRICS"
# GPU_METRICS (
#      -- GPU Metrics, events and values.
#      timestamp                   INTEGER,                               -- Event timestamp (ns).
#      typeId                      INTEGER   NOT NULL,                    -- REFERENCES TARGET_INFO_GPU_METRICS(typeId) and GENERIC_EVENT_TYPES(typeId)
#      metricId                    INTEGER   NOT NULL,                    -- REFERENCES TARGET_INFO_GPU_METRICS(metricId)
#      value                       INTEGER   NOT NULL                     -- Counter data value
#  );

TABLE_STRING_IDS="StringIds"
# StringIds (
#      -- Consolidation of repetitive string values.
#      id                          INTEGER   NOT NULL   PRIMARY KEY,      -- ID reference value.
#      value                       TEXT      NOT NULL                     -- String value.
#  );



METRIC_COMPUTE_WARPS="Compute Warps In Flight"
METRIC_UNALLOCATED_WARPS="Unallocated Warps in Active SMs"

# A100
TARGET_INFO_GPU_METRICS_VALUES = {
    "PCIe TX Throughput": 0,
	"PCIe RX Throughput": 1,
 	"NVLink TX Responses User Data": 2,
	"NVLink TX Responses Protocol Data": 3,
	"NVLink TX Requests User Data": 4,
	"NVLink TX Requests Protocol Data": 5,
	"NVLink RX Responses User Data": 6,
	"NVLink RX Responses Protocol Data": 7,
 	"NVLink RX Requests User Data": 8,
	"GPC Clock Frequency": 9,
	"SYS Clock Frequency": 10,
	"GR Active": 11,
	"SM Active": 12,
	"SM Issue": 13,
	"Tensor Active": 14,
	"Vertex/Tess/Geometry Warps in Flight": 15,
	"Pixel Warps in Flight": 16,
	"Compute Warps in Flight": 17,
	"Unallocated Warps in Active SMs": 18,
	"DRAM Read Bandwidth": 19,
	"DRAM Write Bandwidth": 20,
	"NVLink RX Requests Protocol Data": 21, 
}

# RTX2080TI
TARGET_INFO_GPU_METRICS_VALUES = {
    "PCIe Write Requests to BAR1": 0,
    "PCIe Read Requests to BAR1": 1,
    "PCIe TX Throughput": 2,
    "PCIe RX Throughput": 3,
    "DRAM Write Throughput": 4,
    "DRAM Read Throughput": 5,
    "Unallocated Warps in Active SMs": 6,
    "Compute Warps In Flight": 7,
    "Pixel Warps In Flight": 8,
    "GR Active": 9,
    "Dispatch Started": 10,
    "Draw Started": 11,
    "GPC Clock Frequency": 12,
    "SYS Clock Frequency": 13,
    "Sync Compute In Flight": 14,
    "Async Compute In Flight": 15,
    "SM Active": 16,
    "SM Issue": 17,
    "Tensor Active / FP16 Active": 18,
    "Vertex/Tess/Geometry Warps In Flight": 19,
}

# RTX3050TI
TARGET_INFO_GPU_METRICS_VALUES = {
    "GPC Clock Frequency [MHz]": 0,
    "SYS Clock Frequency [MHz]": 1,
    "GR Active [Throughput %]": 2,
    "Sync Compute in Flight [Throughput %]": 3,
    "Async Compute in Flight [Throughput %]": 4,
    "SM Active [Throughput %]": 5,
    "SM Issue [Throughput %]": 6,
    "Tensor Active [Throughput %]": 7,
    "Vertex/Tess/Geometry Warps in Flight [Throughput %]": 8,
    "Vertex/Tess/Geometry Warps in Flight [Avg]": 9,
    "Vertex/Tess/Geometry Warps in Flight [Avg Warps per Cycle]": 10,
    "Pixel Warps in Flight [Throughput %]": 11,
    "Pixel Warps in Flight [Avg]": 12,
    "Pixel Warps in Flight [Avg Warps per Cycle]": 13,
    "Compute Warps in Flight [Throughput %]": 14,
    "Compute Warps in Flight [Avg]": 15,
    "Compute Warps in Flight [Avg Warps per Cycle]": 16,
    "Unallocated Warps in Active SMs [Throughput %]": 17,
    "Unallocated Warps in Active SMs [Avg]": 18,
    "Unallocated Warps in Active SMs [Avg Warps per Cycle]": 19,
    "DRAM Read Bandwidth [Throughput %]": 20,
    "DRAM Write Bandwidth [Throughput %]": 21,
    "PCIe RX Throughput [Throughput %]": 22,
    "PCIe TX Throughput [Throughput %]": 23,
    "PCIe Read Requests to BAR1 [Requests]": 24,
    "PCIe Write Requests to BAR1 [Requests]": 25,
}
