



if __name__=="__main__":
    #weight = weight % 3
    IN_CHANNELS  = 4
    OUT_CHANNELS = 4
    KX = 2
    KY = 2
    INPUT_X = 4
    INPUT_Y = 4
    INPUT_BATCH = 1
    STRIDE = 1
    PADDING = 0


    WEI_PREC = "INT8"
    ACT_PREC = "INT8"
    
    wei_prec, act_prec, psum_prec, floating = get_prec({        "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC,})
    act = np.arange(0, IN_CHANNELS*INPUT_X*INPUT_Y*INPUT_BATCH).reshape([INPUT_BATCH, IN_CHANNELS, INPUT_X, INPUT_Y])
    weight = np.arange(0, IN_CHANNELS*KX*KY*OUT_CHANNELS).reshape([OUT_CHANNELS, IN_CHANNELS, KX, KY])

    act += 15
    weight += 7


    act = act % (2<<(act_prec-1) -1)
    weight = weight % (2<<(wei_prec-1) - 1)
    #act = act % 2

    weight = weight.reshape(-1)
    for i in range(len(weight)//2):
        
        weight[(i+1)*49 % len(weight)] = 0

    weight = weight.reshape([OUT_CHANNELS, IN_CHANNELS, KX, KY])
  
    ####################################
    from real_data import get_data
    #BASE = "real_weights/ResNet50_vd_QAT"
    #NETWORK = "resnet50_conv2"
    #IN_CHANNELS, OUT_CHANNELS, KX, KY, INPUT_X, INPUT_Y, INPUT_BATCH, STRIDE, PADDING, weight, act = get_data(BASE, NETWORK)



    #print(weight, act)
    #exit(0)
    runtime_config = {
        "DDR_CLK": 40, #in ns
        "CORE_CLK": 10, #in ns

        "Operation": "CONV2D", #CONV2D, CONV2D_ACT, CONV2D_ACT_POOL2D, POOL2D
        "Operation_Params": {
            "KX": KX,
            "KY": KY,
            "X": INPUT_X,
            "Y": INPUT_Y,
            "I": IN_CHANNELS,
            "N": OUT_CHANNELS,
            "B": INPUT_BATCH,

            "STRIDE": STRIDE,
            "PADDING": PADDING,
        },
        #If given will be the actual weights, otherwise is random
        #Can be sparsely random or densely random
        "WEIGHTS": weight,#
        "INPUTS": act,#CHW
        "WEI_PREC": WEI_PREC,
        "ACT_PREC": ACT_PREC,

        "BURST": 4,
        "DRAM_DELAY": 4,

        "FIRST_LAYER": True,

        "SPARSITY_EN": True,#如果没有，就用已有得dataflow.如果有，用Sparsity版本的dataflow
       # "I2XY_OPTIMIZATION": True, #for the compiler to do, NVDLA does this. TI (i.e. 32) >> 3, so TI --> TX, TI --> TY,   不用改架构, 虽然是TI=32, 实际是TX = 4, TY = 8 
    }



#if True:
    hardware_config = {
        "SUPPORTED_WEI_DTYPES": [WEI_PREC],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_ACT_DTYPES": [ACT_PREC],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants

        #############SPARSITY###############
        "ACT_ZERO_GATING": 0,
        "WEI_ZERO_GATING": 0,

        ##############PE AND MULTIPLIER TYPE########################
        "MULT_TYPE_INT": "UNIVERSAL_SERIAL_MULT",#"UNIVERSAL_SERIAL_MULT", #SHIFT_ACCUMULATE#BASIC#ADAPTIVE_INNER#"ADAPTIVE_OUTER",#ADAPTIVE_TI",#"ADAPTIVE_TXTY_TN",#ADAPTIVE_TXTY_TN is like outer product, ADAPTIVE_TI is like inner product
        ##ADAPTIVE_TXTY_TN#BASIC is verilog *, ADAPTIVE/BitFusion, BitSerial is from Stripes work, BitPragmatic is from Pragmatic Work, Bit
        "MULT_TYPE_FP": "BASIC", #BASIC is verilog *, ADAPTIVE (meaning if max precision is 16, want 8 bit, will have double throughput)
        "MULT_TYPE_INT_META": {
                               #BIT SERIAL PARAMETERS
                               "RADIX": 1,#ONly apply for shifting multipliers, 2 means shift by 2 bits
                               #(TODOS) exceptional case, RADIX = BIT PRECISION, and OUTPUT STATIONARY
                               #Do we do something like a fifo ? ....       
                               #Two FIFOs, and then interchange to sum up.  
                               
                               "MULTICANT": "WEI",#WEI/ACT, The one that is moving in the multiplier if any
                               "PIPELINE": False, #can then achieve 1 output per cycle
                               "BIT_STRIPE_ZEROS": "NONE", #NONE,SINGLE, DOUBLE#"WEI", #WEI, ACT, WEI_ACT, WEI_PRAGMATIC, ACT_PRAGMATIC, WEI_ACT_PRAGMATIC, PRAGMATIC skips even more

                                "SIGN_MODE": "SERIAL", #Do at the last cycle (shift add + final negative), or parallel (convert number to positive then sign)
                                "DOUBLE_BUFFER_OUTPUT": False, #We should do this
                               
                                              
                                #BIT FUSION PARAMETERS
                               "MIN_MULT_TYPE": "BASIC", #BASIC, LUT, SHIFT_ACC, only applies to BITFUSION/ADAPTIVE MULT_TYPES
                               "ADAPTIVE_MIXED_AAW_EN": True,
                               "ADAPTIVE_MIXED_WWA_EN": True,
                               "ADAPTIVE_MIXED_AAW": "TX",#TX, TY, TB
                               "ADAPTIVE_MIXED_WWA":  "TN" ,#TKX,TKY,TN
                               "ADAPTIVE_UNIFORM_WA": "TN" ,#TKX,TKY,TN, TX,TY,TB,  TI
        },

        #(TODOS) new framework
        # "MULT_TYPE_INT": {"type": "ADAPTIVE", "DIMENSIONS": "TXTY_TN"}
        # "MULT_TYPE_FLOAT": {"type": "BitSerial", "VARIANT": "BITPRAGMATIC"}
        # "MULT_TYPE_INT": {"type": "BASIC"}
        "REMOVE_DUPLICATE_ROWS": False,#(TODOS)

        "UNIFIED_ACC_COUNTER": False,#(TODOS), ACC and WEI/ACT COUNTER CAN BE RE-USED




        "COUNTER": {
            "WEI_L1_GATE_SAME_READ": False,
            "ACT_L1_GATE_SAME_READ": False,
        },
        
        ##############TILING and ALGORITHMIC DATAFLOW###############
        "TILINGS": {
            #Convolution of 2D type
            "CONV2D": {
                "DEFAULT": {
                    "ID": "0",
                    "DATAFLOW": "SPARSE_DIRECT_LARGE_TILING",#SPARSE_DIRECT_LARGE_TILING"SPARSE_DIRECT", #SPARSE_DIRECT_LARGE_TILING # SPARSE_DIRECT/SPARSE_DIRECT_WINDOW #SPARSE_DIRECT#WINOGRAD"DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.

                    #SPARSE_DIRECT_LARGE_TILINGS is structured sparsity, don't need to save address ( to ideal)
                    #SPARSE_DIRECT_WINDOW        is un-structured sparsity, need to save the address of each element potentially to do accumulation (is much faster, closer to ideal)
                    # pour le methode "SPARSE LARGE TILINGS", la capicite de la memoire est dependent sur c'est nombres et parametres ici
                    
                    "TX": 1, "TY": 1,  "TKX": 2, "TKY": 2, "TI": 1, "TN": 4, "TB":1,
                    "TXX": -1, "TYY": -1, "TII": -1, "TNN": -1,
                    #"LOOP": ["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                    "LOOP": ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                    #"LOOP": ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                    #"LOOP": ["B","X", "Y", "I","KY", "KX","N"], #IS1
                    #"LOOP": ["B","X", "Y", "I","KY", "KX","N"], #IS2
                    
                    #TX and TY should be multiple of WINO_TX and WINO_TY respectively
                    #Winograd specific
                    "WINO_TX":2, "WINO_TY": 2,
                    "WINO_PRE_WEIGHT": False, #(TODOS)

                    #-1是没有，>=1 就是有
                    "SYSTOLIC": {

                        #TWO TYPES OF SYSTOLIC
                        #ONE IS FROM L1_BUF -> PE_ARRAY
                        #DUO      PE_ARRAY --> PE_ARRAY
                        
                        "WEIGHT_LOAD": {"TKX":-1, "TKY":-1, "TN": -1, "TI":-1 },
                        "ACT_LOAD":    {"TKX": -1, "TKY": -1, "TX": -1 , "TY": -1 , "TI": -1, "TB": -1,}, #Can also be smaller than TX, etc. 1, will take
                        #TX cycles in that case
                        "PSUM_OFFLOAD": {"TX":-1, "TY":-1, "TN":-1},
                        
                        #"INTER_PE_X": False,
                        #"INTER_PE_Y": False,
                        #"INTER_PE": "NONE",#"X", "Y", "XY", "DIAG_XY","NONE",

                        #(CASTING) INTER_PE 
                        "WEIGHT_CAST": {"TX": -1, "TY": -1, "TB": -1,},
                        "ACT_CAST": {"TN": -1, "TKX": -1, "TKY": -1 },
                        "PSUM_CAST": {"TB": -1, "TKX": -1, "TKY": -1},

                        #RE_USE
                        "ACT_X_INTER": False, #Further reduce
                        "ACT_Y_INTER": False, #Further reduce memory
                    },



                    ########################################
                    #WORK IN PROGRESS
                    #les limites
                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                    "REMOVE_DUPLICATE_ROWS": True,

                    #Sparsity specific
                    "SPARSITY": {
                        "WEI_ENCODING":"SPARSE_MAP", #NONE, SPARSE_MAP, CSR, etc.
                        "ACT_ENCODING":"NONE",

                        #1. SPARSE WINDOW (unstructured sparsity)
                        "WEI_WINDOW"  :4, #How many to look ahead,
                        "ACT_WINDOW"  :4, #Will affect the buffer
                        "WINDOW_MULTICAST":True,  #If remove, each window (i.e. if input image overlap) will only contain necessary data

                        "LOAD_BALANCE": None, #Weight Re-order, Shuffler, greedy-approaches etc.
                        "WINDOW_GROUP" : ["TX"], #Can do by tile, TX, TI, TN, 数组也可以 ["TX", "TY"],


                        #2. SPARSE TILING (structured sparsity)
                        #The real tiling, PE tiling
                        "SPARSE_TILING": { #应该比Tiling要小一倍
                            # les numeros ici nous donnent la taille et grandeur de la grille de la multiplication
                                #会影响accum
                                  "TX": 1, "TY": 1,  "TN": 4, "TB":1,

                                #不会大影响accum
                                  "TKX": 1, "TKY": 1, "TI": 1, 
                        },



                        "VALUE_SPARSITY": "WEI",#WEI, ACT, WEI_ACT, PSUM, etc.

                        #"WEI_VALUE_SPARSITY": True,
                        #"ACT_VALUE_SPARSITY": False,
                        #"PSUM_VALUE_SPARSITY": False,
                        "WEI_COMPRESSION": False, #With compression, the window size can be a lot smaller (i.e. 4)                        
                        "ACT_COMPRESSION": False, #Only transfer non-zero values into buffers
                        "PSUM_COMPRESSION": False, #Only transfer non-zero values into output buffers
                        "ADDRESS_GEN": "ADDERS", #PREFIX_ADDER, ADDERS?
                     }

                    
                }
            }
         
        },

        "ACCUMULATOR": { 
            "AFTER_MAC_ADDER_TRUE": True, #If false, will be a cycle based accumulator based on terms
            "AFTER_MAC_CYCLE_ADDER_TERMS": 4, #If is more than the TI*TKX*TKY, then will be simply an adder tree (saturated at TI*TKX*TKY)

            
            "DOUBLE_CLOCK": False, #
            "PIPELINED_ADD": False, #
            "MERGED_REG_ADD": False, #OK - 0929 (huge issues when the values are negative
        },

        ##############################################
        # DIRECT DATAFLOW RELATED PARAMETERS
        ##############################################
        "multicast": True,
        ###############################################
        ###############################################
        # L1 RELATED PARAMETERS
        ###############################################

        
            #BUFFER (Here, buffer is the total buffer size. Rows are calculated dynamically, depending on the PE format which depends on the tiling)
            "WEI_BUFFER": 128*1024*8,#16KBytes
            "WEI_BANKS": 8, #For saving power and energy (TODOS), "WEI_BANKING": 16,
            ##I.e. , if each cycle transfers 16 weights, we put each weight in a seperate bank. BANKING = multiple*WEIGHT ELEMENTS PER CYCLE
            "WEI_L1_READ_DELAY": 1,

            
            "WEI_BUFFER_ON_MAX_LAYER": 0, #True,False
        
            "ACT_BUFFER": 128*1024*8,#16KBytes
            "ACT_BANKS": 1, #For saving power and energy
        

            "PSUM_BUFFER":16*1024*8,#16KBytes
            "PSUM_BANKS": 1,

            "PSUM_BUFFER_ON_MAX_LAYER": 0, #True,False

        
            "WEI_L2_READ_DELAY": 1, #no. of cycles of delay (TODOS)
            "ACT_L2_READ_DELAY": 1, #no of cycles of delay (TODOS)
        

            #L2 issues

            "WEI_L2_READ_DELAY": 1, #no. of cycles of delay (TODOS)
            "ACT_L2_READ_DELAY": 1, #no of cycles of delay (TODOS)
            
            "WEI_PREFETCH":True,
            "ACT_PREFETCH":True,
            "WEI_L2_L1_BW_RATIO": 1, #We presume L2 is a ratio of L1 (TODOS), i.e. 2 means L2 carries two 'tiles' at a time
            "ACT_L2_L1_BW_RATIO": 1, #We presume L2 is a ratio of L1 (TODOS), i.e. 2 means L2 carries two 'tiles' at a time
            #If is higher than 1 means we can put multiple data into the L1 at the same time

        
            "L2_WEI_BUFFER_SIZE": 256*8*1024, #256KBytes
            "L2_ACT_BUFFER_SIZE": 256*8*1024, #256KBytes
            ###(TODOS) we can actually dynamically allocate this buffer size ...

        
            ## EITHER:
            ## 1. Give WEI_BUFFER_SIZE, will get rows dynamically
            ## 2. Give WEI_ROWS       , will get buffer size dynamically
            ## 3. Give Largest dimensions of the convolution, will get buffer rows and rows dynamically

            "ALIGNED_L1_DATA": False,
    
            #general constraints
            #CONSTRAINTS FOR MAX SIZE, if is -1, will default to 16
            #和缓存可能有约束性质的冲突(todos)
            "GEN_CONSTRAINTS":{
                "MAX_STRIDE": 2,
                "MAX_KX": 3,
                "MAX_KY": 3,
                "MAX_X": 128,
                "MAX_Y": 128,
                "MAX_N": 64,
                "MAX_I": 64,
                "MAX_B": 1,
                "MAX_PADDING_X": 1,
                "MAX_PADDING_Y": 1,
                #GROUPS? DILATION?
            },
        
            #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
            "DDR_WIDTH": 128,
            "DDR_MAX_BURST": 4,



            #Some constraints for SRAM COMPILER, which will affect the buffer
            #Will change the buffer so as to meet these constraints
            #
            #(USE INTEGER PROGRAMMING?)
            "SRAM_CONSTRAINTS": {
                "LOW_POWER": {
                    "MAX_WIDTH": 72,
                    "MAX_DEPTH": 1024,
                    "MIN_MUX"  : 2,
                    "MIN_WORD_TO_MUX_RATIO": 16,
                    "MIN_WORD_TO_MUX_MULTIPLE": 4,
                    "MAX_WORD_TO_MUX_RATIO": 256,
                    "NB>36": "CM=2",
                    "NB>18": "CM<=4",
                    "READ_DELAY": "10ns",
                    "NB/CM>256": "NO",
                },
                "FAST":  {
                    "MAX_WIDTH": 144,
                    "MAX_DEPTH": 2048,
                    "MIN_MUX": 4,
                    "MAX_MUX": 4,
                    
                }
                
            },
            "SRAM_COMPILER_CONFIG": "LOW_POWER",


    }




    meta_config = {
        "dossier": "MyAccelerator",
        "tc": "tc1",
    }


    ########################################################################################

    print("GEN_HARDWARE")
    MACRO_CFG = gen_macro_file(hardware_config, meta_config)


    
                               
