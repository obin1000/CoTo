
CUPTI_ACTIVITY_KIND_MEMCPY="CUPTI_ACTIVITY_KIND_MEMCPY"
CUPTI_ACTIVITY_KIND_MEMSET="CUPTI_ACTIVITY_KIND_MEMSET"
CUPTI_ACTIVITY_KIND_KERNEL="CUPTI_ACTIVITY_KIND_KERNEL"
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
CUPTI_ACTIVITY_KIND_SYNCHRONIZATION="CUPTI_ACTIVITY_KIND_SYNCHRONIZATION"
CUPTI_ACTIVITY_KIND_CUDA_EVENT="CUPTI_ACTIVITY_KIND_CUDA_EVENT"
CUPTI_ACTIVITY_KIND_GRAPH_TRACE="CUPTI_ACTIVITY_KIND_GRAPH_TRACE"
CUPTI_ACTIVITY_KIND_RUNTIME="CUPTI_ACTIVITY_KIND_RUNTIME"
TARGET_INFO_GPU_METRICS="TARGET_INFO_GPU_METRICS"
GPU_METRICS="GPU_METRICS"
# GPU_METRICS (
#      -- GPU Metrics, events and values.
#      timestamp                   INTEGER,                               -- Event timestamp (ns).
#      typeId                      INTEGER   NOT NULL,                    -- REFERENCES TARGET_INFO_GPU_METRICS(typeId) and GENERIC_EVENT_TYPES(typeId)
#      metricId                    INTEGER   NOT NULL,                    -- REFERENCES TARGET_INFO_GPU_METRICS(metricId)
#      value                       INTEGER   NOT NULL                     -- Counter data value
#  );

STRING_IDS="StringIds"
# StringIds (
#      -- Consolidation of repetitive string values.
#      id                          INTEGER   NOT NULL   PRIMARY KEY,      -- ID reference value.
#      value                       TEXT      NOT NULL                     -- String value.
#  );


METRIC_ID_PCIE_TX=0
METRIC_ID_PCIE_RX=1
METRIC_GPC_CLOCK_FREQUENCY=9
METRIC_SYS_CLOCK_FREQUENCY=10
METRIC_GR_ACTIVE=11
METRIC_SM_ACTIVE=12
METRIC_SM_ISSUE=13
METRIC_COMPUTE_WARPS=17
METRIC_UNALLOCATED_WARPS=18
METRIC_DRAM_READ=19
METRIC_DRAM_WRITE=20


