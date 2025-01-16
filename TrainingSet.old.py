
from Generate_DDR_Xin import trouve_df, get_dataflow_meta, get_prec, GET_LOOP_FILTERS

from Generate_Verilog import gen_hardware, gen_macro_file#(hardware_config, meta_config)
    
import numpy as np
    
from Generate_DDR_Xin import gen_buf

from Generate_TB import gen_tb_L2_1_level


def run_generate(hardware_config, runtime_config, meta_config):

    print("GEN_HARDWARE")
    MACRO_CFG = gen_macro_file(hardware_config, meta_config)
    
    gen_hardware(hardware_config, meta_config)

    print("GEN_SOFTWARE")
    gen_buf(hardware_config, runtime_config, meta_config)

    print("GEN TESTBENCH")
    #Generate test for L1 + PEs
    #gen_tb_L1_level(hardware_config, runtime_config, meta_config)

    #Generate test for L2
    gen_tb_L2_1_level(hardware_config, runtime_config, meta_config, macro_config = MACRO_CFG)




def benchmark(hardware_config, debug = True):

    IN_CHANNELS  = 1
    OUT_CHANNELS = 1
    KX = 3
    KY = 3
    INPUT_X = 5
    INPUT_Y = 5
    INPUT_BATCH = 1
    STRIDE = 1
    PADDING = 0

    print(hardware_config)
    WEI_PREC =  hardware_config["SUPPORTED_WEI_DTYPES"][0]
    ACT_PREC =  hardware_config["SUPPORTED_ACT_DTYPES"][0]

    print(WEI_PREC, ACT_PREC)
    
    
    wei_prec, act_prec, psum_prec, floating = get_prec({        "WEI_PREC": WEI_PREC, "ACT_PREC": ACT_PREC,})
    act = np.arange(0, IN_CHANNELS*INPUT_X*INPUT_Y*INPUT_BATCH).reshape([INPUT_BATCH, IN_CHANNELS, INPUT_X, INPUT_Y])
    weight = np.arange(0, IN_CHANNELS*KX*KY*OUT_CHANNELS).reshape([OUT_CHANNELS, IN_CHANNELS, KX, KY])

    act += 15
    weight += 7


    act = act % (2<<(act_prec-1) -1)
    weight = weight % (2<<(wei_prec-1) - 1)
    #act = act % 2
    
    runtime_config = {
        "DDR_CLK": 40, #in ns
        "CORE_CLK": 2, #in ns

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



    if(debug):
        KERNEL_SIZE = [KX, KY]
        STRIDE = [1,1]
        PADDING = [0,0]
        shou_q = np.zeros((INPUT_BATCH, OUT_CHANNELS, (INPUT_X + 0*2 - KERNEL_SIZE[0] + 1) // STRIDE[0] , (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1] )).astype('int')
        for b in range(INPUT_BATCH):
            for kx in range(KX):
                for ky in range(KY):
                    for x in range((INPUT_X + 0*2 - KX + 1) // 1  ):
                        for y in range((INPUT_Y + 0*2 - KY + 1) // 1):
                            for i in range(IN_CHANNELS):
                                for n in range(OUT_CHANNELS):
                                    if(x+kx > INPUT_Y):
                                        continue
                                    if(y + ky > INPUT_X):
                                        continue
                                    shou_q[b][n][x][y] += weight[n][i][kx][ky]*act[b][i][x+kx][y+ky] 
        print("GOLDEN", shou_q )#% (2<<(act_prec+ wei_prec-1+4)))                  
        print(act)
        print(weight)
    
    return runtime_config


def training_set_1(count_samples= True, do_inference = False):

    from Generate_TB import gen_tb_L2_1_level#(hardware_config, runtime_config, meta_config, macro_config)

    #RUNTIME AND META
    


    meta_config = {
        "dossier": "MyAccelerator",
        "tc": "tc1",
    }
    if(do_inference):
        meta_config["dossier"] += "_Test"


    #SPACE
    SUPPORTED_WEI_DTYPES = [["INT16"],["INT8"]]#, "INT16","FP8"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
    SUPPORTED_ACT_DTYPES = [["INT16"],["INT8"]]#, "INT16","FP8"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants
    ACT_ZERO_GATING = [0]#,1]
    WEI_ZERO_GATING = [0]#,1]


    RADIX = [1,2,4,8]
    MULTICANT = ["WEI", "ACT"]
    BIT_STRIPE_ZEROS = ["NONE", "SINGLE"]

    TILINGS = [
    {
    "FLOW": "CONV2D",
    "DATAFLOWS": "DIRECT",
        "LOOP": [["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                 ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                  ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS2
                 ],
        "TX": [1,2,4],
        "TY": [1,2,4],
        "TKX":[1],
        "TKY":[1],
        "TI": [1,2,4,8,16][::-1],
        "TN": [1,2,4,8,16][::-1],
        "TB": [1],
        "TXX": [-1],
        "TYY": [-1],
        "TII": [-1],
        "TNN": [-1],
    },
    {
       "DATAFLOWS": "WINOGRAD",
        "LOOP": [["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                 ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                  ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS2
                 ],
        "TX": [2,4,6],
        "TY": [2,4,6],
        "TKX":[3,5,7],
        "TKY":[3,5,7],
        "TI": [1,2,4,8,16][::-1],
        "TN": [1,2,4,8,16][::-1],
        "TB": [1],
        "TXX": [-1],
        "TYY": [-1],
        "TII": [-1],
        "TNN": [-1],

        "WINO_TX": [2],
        "WINO_TY": [2],
        "WINO_PRE_WEIGHT": [False],
    }]

    
    kongjian = 0
    for SUPPORTED_WEI_DTYPES0 in SUPPORTED_WEI_DTYPES:
        for SUPPORTED_ACT_DTYPES0 in SUPPORTED_ACT_DTYPES:
            for ACT_ZERO_GATING0 in ACT_ZERO_GATING:
                for WEI_ZERO_GATING0 in WEI_ZERO_GATING:
                    for RADIX0 in RADIX:
                        for MULTICANT0 in MULTICANT:
                            for BIT_STRIPE_ZEROS0 in BIT_STRIPE_ZEROS:
                                for TILINGS0 in TILINGS:
                                    for LOOP0 in TILINGS0["LOOP"]:
                                        for TX0 in TILINGS0["TX"]:
                                            for TY0 in TILINGS0["TY"]:
                                                for TKX0 in TILINGS0["TKX"]:
                                                    for TKY0 in TILINGS0["TKY"]:
                                                        for TI0 in TILINGS0["TI"]:
                                                            for TN0 in TILINGS0["TN"]:
                                                                if True:
                                                                    for TXX0 in TILINGS0["TXX"]:
                                                                        for TYY0 in TILINGS0["TYY"]:
                                                                            if True:
                                                                                if True:
                                                                                    #continue
                                                                                    
                                                                                    #GENERAL FLOW
                                                                                    hardware_config = {
                                                                                        "SUPPORTED_WEI_DTYPES": SUPPORTED_WEI_DTYPES0,
                                                                                        "SUPPORTED_ACT_DTYPES": SUPPORTED_ACT_DTYPES0,
                                                                                        "ACT_ZERO_GATING": ACT_ZERO_GATING0,
                                                                                        "WEI_ZERO_GATING": WEI_ZERO_GATING0,

                                                                                        "MULT_TYPE_INT": "UNIVERSAL_SERIAL_MULT",
                                                                                        "MULT_TYPE_FP": "BASIC",

                                                                                        "MULT_TYPE_INT_META": {
                                                                                            "PIPELINE": False,
                                                                                           "RADIX": RADIX0,
                                                                                           "MULTICANT": MULTICANT0,
                                                                                           "BIT_STRIPE_ZEROS": BIT_STRIPE_ZEROS0, #NONE,SINGLE, DOUBLE#"WEI", #WEI, ACT, WEI_ACT, WEI_PRAGMATIC, ACT_PRAGMATIC, WEI_ACT_PRAGMATIC, PRAGMATIC skips even more
                                                                                         },


                                                                                        "TILINGS": {
                                                                                                #Convolution of 2D type
                                                                                                "CONV2D": {
                                                                                                    "DEFAULT": {
                                                                                                        "DATAFLOW": TILINGS0["DATAFLOWS"], #WINOGRAD"DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.
                                                                                                        "TX": TX0, "TY": TY0,  "TKX": TKX0, "TKY": TKY0, "TI": TI0, "TN": TN0, "TB":1,
                                                                                                        "TXX": TXX0, "TYY": TYY0, "TII": -1, "TNN": -1,
                                                                                                        "LOOP": LOOP0,

                                                                                                        "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                                                                                                        "REMOVE_DUPLICATE_ROWS": True,
                                                                                                    }
                                                                                                }
                                                                                             
                                                                                            },

                                                                                        "multicast": True,

                                                                                        #BUFFER (Here, buffer is the total buffer size. Rows are calculated dynamically, depending on the PE format which depends on the tiling)
                                                                                        "WEI_BUFFER": 16*1024*8,#16KBytes

                                                                                        "WEI_BANKS": 8, #For saving power and energy (TODOS)
                                                                                        "WEI_BUFFER_ON_MAX_LAYER": 0, #True,False
                                                                                    
                                                                                        "ACT_BUFFER": 16*1024*8,#16KBytes
                                                                                        "ACT_BANKS": 8, #For saving power and energy

                                                                                        "PSUM_BUFFER":16*1024*8,#16KBytes
                                                                                        "PSUM_BANKS": 8,

                                                                                        "PSUM_BUFFER_ON_MAX_LAYER": 0, #True,False

                                                                                        "L2_READ_DELAY": 1, #no. of cycles of delay
                                                                                        "L2_L1_BW_RATIO": 1, #We presume L2 is a ratio of L1 (TODOS), i.e. 2 means L2 carries two 'tiles' at a time
                                                                                        "L2_WEI_BUFFER_SIZE": 256*8*1024, #256KBytes
                                                                                        "L2_ACT_BUFFER_SIZE": 256*8*1024, #256KBytes
                                                                                    
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

                                                                                                                                                         
                                                                                        "ACCUMULATOR": { 
                                                                                            "AFTER_MAC_ADDER_TRUE": True, #If false, will be a cycle based accumulator based on terms
                                                                                            "AFTER_MAC_CYCLE_ADDER_TERMS": 4, #If is more than the TI*TKX*TKY, then will be simply an adder tree (saturated at TI*TKX*TKY)

                                                                                            
                                                                                            "DOUBLE_CLOCK": False, #
                                                                                            "PIPELINED_ADD": False, #
                                                                                            "MERGED_REG_ADD": True, #OK - 0929
                                                                                        },

                                                                                    }

                                                                                    #1. Generate
                                                                                    #runtime_config = benchmark(hardware_config)
                                                                                    #run_generate(hardware_config, runtime_config, meta_config)
                                                                                    #WINOGRAD FLOW
                                                                                    
                                                                                    if(TILINGS0["DATAFLOWS"] == "WINOGRAD"):
                                                                                        for WINO_TX0 in TILINGS0["WINO_TX"]:
                                                                                            for WINO_TY0 in TILINGS0["WINO_TY"]:
                                                                                                for WINO_PRE_WEIGHT0 in TILINGS0["WINO_PRE_WEIGHT"]:

                                                                                                    hardware_config["TILINGS"]["CONV2D"]["DEFAULT"]["WINO_TX"] = WINO_TX0
                                                                                                    
                                                                                                    hardware_config["TILINGS"]["CONV2D"]["DEFAULT"]["WINO_TY"] = WINO_TY0
                                                                                                    hardware_config["TILINGS"]["CONV2D"]["DEFAULT"]["WINO_PRE_WEIGHT"] = WINO_PRE_WEIGHT0

                                                                                                    if(count_samples):
                                                                                                        kongjian += 1
                                                                                                    else:
                                                                                                        runtime_config = benchmark(hardware_config)
                                                                                                        run_generate(hardware_config, runtime_config, meta_config)
                                                                                    else:
                                                                                        if(count_samples):
                                                                                            kongjian += 1
                                                                                        else:
                                                                                            runtime_config = benchmark(hardware_config)
                                                                                            run_generate(hardware_config, runtime_config, meta_config)

                                                                                    if(count_samples):
                                                                                        kongjian += 1
                                                                                    else:


                                                                                        if(not do_inference):
                                                                                            
                                                                                            #2. Synthesis
                                                                                            from Generate_SYN import config2dse_node, syn

                                                                                            dse_node = config2dse_node(hardware_config, runtime_config)
                                                                                            syn(dse_node)

                                                                                            import os
                                                                                            os.system("dc_shell -f zonghe.tcl")
                                                                                            

                                                                                            #(TODOS) SPARSE FLOW and other flows
                                                                                            #exit()
                                                                                        else:



                                                                                            from ptpx import ptpx
                                                                                            dse_node = config2dse_node(hardware_config, runtime_config)
                                                                                            ptpx(dse_node, meta_config)

                                                                                            import os
                                                                                            os.system("source ptpx.sh")
                                                                                        

    print("探索的DLA空间是 = ", kongjian)






training_set_1(count_samples= False, do_inference = True)


'''
#HARDWARE SPACE (THEORETICAL)


SUPPORTED_WEI_DTYPES = [["INT16"],["INT8"]],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
SUPPORTED_ACT_DTYPES = [["INT16"],["INT8"]],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants
ACT_ZERO_GATING = [0,1]
WEI_ZERO_GATING = [0,1]

MULT_TYPE_INT_META = [
    {
        "MULT_TYPE_INT": "UNIVERSAL_SERIAL_MULT",
        "RADIX": [1,2,4,8],
        "MULTICANT": ["WEI", "ACT"],
        "BIT_STRIPE_ZEROS": ["NONE", "SINGLE", "DOUBLE"],
    },
    {
        "MULT_TYPE_INT": "ADAPTIVE_INNER",
        "RADIX": [1,2,4,8],
        "MULTICANT": ["WEI", "ACT"],
        "BIT_STRIPE_ZEROS": ["NONE", "SINGLE", "DOUBLE"],

        "MIN_MULT_TYPE": "BASIC", #BASIC, LUT, SHIFT_ACC, only applies to BITFUSION/ADAPTIVE MULT_TYPES
                               "ADAPTIVE_MIXED_AAW_EN": True,
                               "ADAPTIVE_MIXED_WWA_EN": True,
                               "ADAPTIVE_MIXED_AAW": "TX",#TX, TY, TB
                               "ADAPTIVE_MIXED_WWA":  "TN" ,#TKX,TKY,TN
                               "ADAPTIVE_UNIFORM_WA": "TN" ,#TKX,TKY,TN, TX,TY,TB,  TI                
    }
]

TILINGS = [
    {
    "FLOW": "CONV2D",
    "DATAFLOWS": ["DIRECT"],
        "LOOP": [["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                 ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                  ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS2
                 ],
        "TX": [1,2,4,8],
        "TY": [1,2,4,8],
        "TKX":[1,2,3],
        "TKY":[1,2,3],
        "TI": [1,2,4,8,16,32,64],
        "TN": [1,2,4,8,16,32,64],
        "TB": [1],
        "TXX": [-1],
        "TYY": [-1],
        "TII": [-1],
        "TNN": [-1],
    },
    #OTHER FLOWS, POOLING? TRANSFORMER?
       "DATAFLOWS": ["WINOGRAD"],
        "LOOP": [["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                 ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                  ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS2
                 ],
        "TX": [2,4],
        "TY": [2,4],
        "TKX":[3,5,7],
        "TKY":[3,5,7],
        "TI": [1,2,4,8,16,32,64],
        "TN": [1,2,4,8,16,32,64],
        "TB": [1],
        "TXX": [-1],
        "TYY": [-1],
        "TII": [-1],
        "TNN": [-1],

        "WINO_TX": [2,3,4]
        "WINO_TY": [2,3,4]
        "WINO_PRE_WEIGHT": False,
    },

   "DATAFLOWS": ["SPARSE"],
        "LOOP": [["B",  "N", "I","X", "Y","KY", "KX"],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],#["B",  "N", "I", "X", "Y","KY", "KX","TYY","TXX",],#["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                 ["B",  "N", "I","KY", "KX","X", "Y",], #WS1
                  ["B",  "N", "I","X", "Y","KY", "KX"], #OS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS1
                  ["B","X", "Y", "I","KY", "KX","N"], #IS2
                 ],
        "TX": [1,2,4,8],
        "TY": [1,2,4,8],
        "TKX":[1,2,3],
        "TKY":[1,2,3],
        "TI": [1,2,4,8,16,32,64],
        "TN": [1,2,4,8,16,32,64],
        "TB": [1],
        "TXX": [-1],
        "TYY": [-1],
        "TII": [-1],
        "TNN": [-1],

         #Sparsity specific
                    "SPARSITY": {
                        "WEI_ENCODING":["SPARSE_MAP"], #SPARSE_MAP, CSR, etc.
                        "ACT_ENCODING":["SPARSE_MAP"],
                        
                        "WINDOW"  :[2,4,8,16,32], #How many to look ahead,
                        "WINDOW_MULTICAST":True,  #If remove, each window (i.e. if input image overlap) will only contain necessary data

                        "LOAD_BALANCE": None, #Weight Re-order, Shuffler, greedy-approaches etc.
                        "WINDOW_GROUP" : "TX", #Can do by tile, TX, TI, TN, 数组也可以 ["TX", "TY"],
                        "WEI_VALUE_SPARSITY": [True, False],
                        "ACT_VALUE_SPARSITY": [True, False],
                        "PSUM_VALUE_SPARSITY":[True,False],
                        "WEI_COMPRESSION": [True,False], #With compression, the window size can be a lot smaller (i.e. 4)                        
                        "ACT_COMPRESSION": [True, False],#Only transfer non-zero values into buffers
                        "INNER_JOIN_TECHNIQUE": ["ADDERS", "PREFIX"], #PREFIX, ADDERS?
                     }

                    
    },

    
]



L2_WEI_BUFFER_SIZE = [256*8*1024] #256KBytes
L2_ACT_BUFFER_SIZE = [256*8*1024] #256KBytes
WEI_BUFFER = [16*1024*8,  32*1024*8, 64*1024*8, 128*1024*8, 256*1024*8]#16KBytes
ACT_BUFFER = [16*1024*8,  32*1024*8, 64*1024*8, 128*1024*8, 256*1024*8]#16KBytes
PSUM_BUFFER = [16*1024*8, 32*1024*8, 64*1024*8, 128*1024*8, 256*1024*8]#16KBytes

ACCUMULATOR ={ 
    "AFTER_MAC_ADDER_TRUE": [True,False], #If false, will be a cycle based accumulator based on terms
    "AFTER_MAC_CYCLE_ADDER_TERMS": [4], #If is more than the TI*TKX*TKY, then will be simply an adder tree (saturated at TI*TKX*TKY)            
    "DOUBLE_CLOCK": [False], #
    "PIPELINED_ADD": [False], #
    "MERGED_REG_ADD": [True], #OK - 0929
}

SYSTOLIC= {
    "WEIGHT_LOAD": [{},{"TKX":[1]},{"TKY":[1]}],
    "ACT_LOAD": [{},{"TX":[1]},{"TY":[1]}], #Can also be smaller than TX, etc. 1, will take
    #TX cycles in that case
    "PSUM_OFFLOAD": [{}], 
    "INTER_PE_X": [False,True],
    "INTER_PE_Y": [False,True],
}

'''

