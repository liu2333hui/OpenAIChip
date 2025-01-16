hardware_config = {

        ###############################################
        # Control and Scheduling RELATED PARAMETERS
        ###############################################
    
        #"AUTOMATIC_ADDRESS_GENERATION": False, #We generate the address internally in hardware or no
        "PE_FINE_GRAIN_CONTROL": True, #We from a user can control the way the PE functions, or it is largely automatic\
        "ADDRESS_FINE_GRAIN_CONTROL": True, #We as a user control the way the Addresses generation is done
        "SPARSITY_SORTING": False, #We can re-arrange rows of sparsity
        "COMPRESSED_FORMAT": False, #We send in the sparse data via the entire data with a bitmap
        "SPARSE_BITMAP": False, #We send a bitmap of the sparsity, if this is not sent, we would have to infer the sparsity
        #Automatic means
        #Fine grain control means more work done in the software, such as address generation and PE control
        #Coarse grain control means more work done in the hardware, such as address generation and PE control

        ###############################################
        # PE RELATED PARAMETERS
        ###############################################

        "SUPPORTED_PRECISIONS": [8],
        #MAX_PRECISIONS = max(SUPPORTED_PRECISIONS)

        "SPARSITY_CLOCK_GATING": True, #Will clock gate if the activation or weight is 0
        "MULTIPLIER_TYPE": "BASIC", #"BASIC", "PARALLEL", "STRIPES", "PRAGMATIC", "BITFUSION", "BOOTH_MULT", "WALLACE_MULT", etc.

        #Number of size in BYTES (THE SCRATCHPAD, L1, L2 bit widths are inferred by the tiling)
        "WEIGHT_SCRATCHPAD": 8, #This is the closest proximity, increase this will decrease weight_buffer reads
        "ACT_SCRATCHPAD": 8,

        
        ###############################################
        # PE ARRAY AND DATAFLOW RELATED PARAMETERS
        ###############################################
        #This is essentially systolic
        #Meaning if we only define one dataflow (say for convolution, fixed)
        #Then the Inter_PE  [-1, 1] means we can move up and down
        #Then the compiler through the dataflow (if it is fixed)
        # 1. We find the systolic flow that makes most sense, i.e. either on the weight or the activation or both
        # 2. This is internal PE flow
        # 3. For the external PE flow, we can allow systolic in, systolic output, systolic weights to be turned-on
        # each will save time and energy and space
        # (TODOS)

        
        "SYSTOLIC_INPUT": False,
        "SYSTOLIC_OUTPUT": False,
        "SYSTOLIC_WEIGHT": False,
        
        
        #BY MANHATTAN DISTANCE (or extended manhattan with diagonal move)
        "INTER_PE": [1], #(If we have enabled INTER_PE to be larger than the row size, we have p2p over the entire network
        #This means we have any re-use
        
        #If allow diagonal passing
        "ALLOW_DIAGONAL": False, #(THIS IS FOR A VERY SPECIAL FLOW, EYERISSV1)

        # Any crazy NoC systems ?
        #(TODOS) allow knight/horse move
        # ->->
        #     |
        #     V

        ###############################################
        # ACCUMULATION RELATED PARAMETERS
        ###############################################
        # ADDERS ARE INFERRED BY THE DATAFLOW

    
        ###############################################
        # L1/L2 RELATED PARAMETERS
        ###############################################

        #L1
        "WEIGHT_BUFFER": 1024,#1KBytes
        "WEIGHT_BANKS": 8, #For saving power and energy
        "ACT_BUFFER": 1024,#1KBytes
        "ACT_BANKS": 8, #For saving power and energy
        "L1_DELAY": 1,

        #L2
        "GLOBAL_SRAM": 128000, #128KBytes
        "SRAM_WIDTH": 64,
        "SRAM_DELAY": 2,
        
        #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
        "DDR_WIDTH": 128,
        "BURST": 4,
        "DRAM_DELAY": 4,

        ##############################################
        # DATAFLOW RELATED PARAMETERS
        ##############################################
        
        #Reconfigurable Tiling
        "CONV_TILINGS": {
            "DEFAULT":  {
                   "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
                    "TX": 1,
                    "TY": 1,
                    "TB": 1,
                    "TN": 8,
                    "TI": 8,
                    "TKX": 1,
                    "TKY": 1,
                    #NUM_ROWS(ACTIVATIONS) = TX*TY*TB*TI
                    #NUM_PES = TX*TY*TB*TN*TI*TKX*TKY
                    
                    #Time based tiling
                    "TNN": TNN,
                    "TII": TII,
                    "TXX": TXX,
                    "TYY": TYY,
                },
        }
    }

other_configs = {
        "CONV_TILINGS": {
            "batch": {
                "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
                #...(todos)
            },
            #Input image
            "ic_3": {
                "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
                #...(todos)
            },
            "kx_3_ky_3": {
                "DATAFLOW_TYPE": "TENSOR_UNIT_WINOGRAD",
                #Tiling is inferred
                #...(todos)
                #Is an element-wise multiplication against element-wise multiplication, so we basically need a unicast to unicast dataflow
            },
            "kx_5_ky_5": {
               "DATAFLOW_TYPE": "TENSOR_UNIT_FFT",
               #...(todos)
            },
            "kx_1_ky_1": {
                "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
                "TX": 1,
                "TY": 1,
                "TB": 1,
                "TN": 8,
                "TI": 8,
                "TKX": 1,
                "TKY": 1,
            },

        },
        "POOL_TILINGS": {
            "DEFAULT": {
                #TODOS
                "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER", #"PDP_UNIT"
                
                 "SUPER_PES": 8, #This will reflect in the tiling, number of PE units will become SUPER_PEs
                #meaning a comparator and adder is added into the PE array

                
                
            }
        },
        "SDP_TILINGS": {
            "DEFAULT": {
                #TODOS
                "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER", #"SDP_UNIT"
                "SUPER_PES": 8, #This will reflect in the tiling, number of units that become changed to SUPER_PES
                #This number should be less than the total PEs, will embed the sdp units into the PE units

            }
        },
        "TRANSFORMER_TILINGS": {
            "DEFAULT": {
                #TODOS
                "DATAFLOW_TYPE": "TRANSFORMER_UNIT_LOOP_ORDER", #"SDP_UNIT"
            }
        }

}
