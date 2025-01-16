import paddle
import paddle.inference as paddle_infer
import numpy as np
import wincnn


#################################################################
#Generate a DDR file for the verilog to read and process

hardware_config = {

    #Instruction filter
    "IFU": 0, #0, 1
    "EXU": {
        "TU": { #Tensor Unit for convolutions
            "precision": "int8", #or ["int4","fp8"] meaning support
            #both int4 and fp8
            "tiling": [2,2,4,8],
            "type": "basic", #"Basic" ==> all Basic
            #"type": {"basic": 0.75, "superpe": 0.25} ==> mixed PEs
            "dataflow": "direct", #"broadcast", #"direct",
                #"broadcast", "systolic", "different systolic styles?"
            "loop_order": "ws", #"ws", "os", "is", "rs" or "custom" need to provide
            "sparsity_power_gate": 0, #0 or 1, 1 means when == 0, does not evaluate
            "winograd": 0, #enable winograd convolution feature or not

            "systolic_scratchpad":{
                "buffer_size": "128"    
            }
        },

        "RT": {
            "type": "tree", #"tree", "cycle"
            
        },
        "VU": {  #Element-Wise Unit for pooling operation
            "throughput": 8     
        },
        "VReg": {
            "type": "ping-pong", #ping pong registers, or none
            "input_quantization": 0, #enable input quantization
        },
        "CDB": {
              #todos
            }
    },

    "LSU":{
        "ACT_MEM": {
            "banks": 8,
            "buffer_size": "16K",
            "compressed": 0
        },
        "WEIGHT_MEM": {
            "banks": 8,
            "buffer_size": "16K",
            "compressed": 0 
        },
        "OUT_MEM": {
            "banks": 8,
            "buffer_size": "8K",
        }    
    },

    "SU":{
        "throughput": 8,    
    },


#IS there something we should do with the padding ? like a padding unit ? (TODOS)

    "Accelerator": {
         "Cores": 4,
         "NoC": "bus" #"bus" means transfer point to point, or systolic
         #or broadcast if possible
    },
    

    "DDR": {
        "data_width": 32,
        "cycle_delay": 4,
        "number": 1 #number of DDR units, can have multiple, will be placed
        # in the most optimal position based on the Accelerator.NoC
    },

    "Circuit": {
        "Clock": "1MHz",
        "DDR_Clock": "200Mhz",
        "PowerSupply": "1V",
        "FeatureSize": "45nm",
        "DeviceType": "TP",
    }



}



####################################################################
# Software  (CHANGEME)
####################################################################
#WEIGHT
IN_CHANNELS = 1
OUT_CHANNELS = 1
KERNEL_SIZE = [3,3]
STRIDE = [1,1]
PADDING = [0,0]
DILATION = 1 #todos
GROUPS = 1 #todos
BIAS = True

POOL_SIZE = [2,2]
POOL_STRIDE = 1
POOL_PAD = [0,0]

#optional
CONV = True
ACTIVATION = False#"relu" #"relu"
POOLING = False #"avg", "max"
BATCH_NORM = False #False True

#INPUT
INPUT_BATCH = 1
INPUT_CHANNELS = IN_CHANNELS
INPUT_X = 6
INPUT_Y = 6

#Sparsity and Pruning and Quantization
#precision = 8
weight_precision = 8
activation_precision = 8
sparsity = 0.5
strategy = 'UnstructurePrune'#"ChannelPrune"

##Save name
benchmark = "./benchmarks/paddle/ConvFuseOp"
################################################################


################################################################
if(CONV):
    benchmark += "."+ "_".join([str(s) for s in [OUT_CHANNELS, IN_CHANNELS, KERNEL_SIZE[0],
                                                     KERNEL_SIZE[1], STRIDE[0], STRIDE[1], PADDING[0], PADDING[1],
                         DILATION, GROUPS, BIAS]])
if(BATCH_NORM):
    benchmark += ".BN"
        
if(ACTIVATION):
    benchmark += "."+ ACTIVATION

if(POOLING):
    benchmark += "." + "_".join([str(s) for s in [POOL_SIZE[0], POOL_SIZE[1], POOL_STRIDE[0], POOL_STRIDE[1], POOL_PAD[0],POOL_PAD[1]]])

benchmark += "/%s%s_INT%d_%d" % (strategy, str(sparsity), activation_precision, weight_precision)

state_dict = paddle.load(benchmark+"/inference")
print(state_dict.keys())


# 创建 config
config = paddle_infer.Config(benchmark+"/inference.pdmodel", benchmark+"/inference.pdiparams")

# 根据 config 创建 predictor
predictor = paddle_infer.create_predictor(config)

# 获取输入的名称
input_names = predictor.get_input_names()
input_handle = predictor.get_input_handle(input_names[0])

# 设置输入
LEN = 2

#b
fake_input =[b*state_dict['inputs@scale']/(2**(activation_precision-1)-1)*np.ones((INPUT_CHANNELS, INPUT_X,INPUT_Y)).astype("float32") for b in range(LEN)]

cnt = 0
for i in range(INPUT_CHANNELS):
    for x in range(INPUT_X):
        for y in range(INPUT_Y):
            fake_input[0][i][x][y] = state_dict['inputs@scale']/(2**(activation_precision-1)-1)*cnt
            cnt += 1
print(fake_input)

fake_input = np.array(fake_input)
input_handle.reshape([LEN, INPUT_CHANNELS, INPUT_X,INPUT_Y])
input_handle.copy_from_cpu(fake_input)

# 运行predictor
predictor.run()

#print(config.summary())
# 获取输出
output_names = predictor.get_output_names()
output_handle = predictor.get_output_handle(output_names[0])
output_data = output_handle.copy_to_cpu() # numpy.ndarray类型
print("Output data size is {}".format(output_data.size))
print("Output data shape is {}".format(output_data.shape))
#s = state_dict['inputs@scale']*state_dict['conv2d_0.w_0@scale']/state_dict['conv2d_1.tmp_0@scale']/(2**(precision-1)-1)
#o = np.round(np.array(output_data/state_dict['conv2d_1.tmp_0@scale']*(2**(precision-1)-1)).astype("int"))
#print(o)

###COMPLETION OF GROUND TRUTH RUN FROM THE SOFTWARE LEVEL###



####################################################################
# Hardware Config  (CHANGEME）
####################################################################

#################################CUSTOM RUN OF THE DATA#######################
#With loop reordering for spatial architectures
#How to use algorithm to represent 1D systolic (Thinker/TPU) ?
#How to use algorithm to represent 2D systolic (Eyeriss, ShiDianNao)?
#(TODOS) This script generates ground turth (output_data from predictor), another ground truth via tiling (systolic or spatial),
#Then based on these patterns and memory analysis, we can generate the DDR and instructions


#QUANTIZE THE INPUT
fake_input = fake_input/state_dict['inputs@scale']*(2**(activation_precision-1)-1)
#print(np.round(fake_input))
fake_input = np.round(fake_input).astype(dtype="int")
#print(fake_input)

TB = 1
TN = 2
TI = 1
TX = 2
TY = 2
TKX = 1
TKY = 1

#Time based tiling
TNN = 4 #Multiplied by the TN
TII = 4
TXX = 4
TYY = 4

TNN = int(TNN*TN)
TII = int(TNN*TN)
TXX = int(TXX*TX)
TYY = int(TYY*TY)


#方的
WINOGRAD_CHINESE = {
    "FILTER3": 4,
    "TILING3": ["B", "X", "Y", "N", "I", "nn", "yy", "xx", "I" , "ii"], #TODOS, there are some loop orders as well

    "FILTER5": -1,
    "TILING5": []
    
    #"FILTER5": 7
    #"Filter": [3,5]#Support one filter or different input sizes
    #"Input": [4],#,5,6,7,8,9,10]
}
FFT = {
   #todos
}





DATAFLOW = "Default"
#Capitals represent the outermost loop
#lower case repatead means tiling
FIXED_LOOP_ORDER = ["B", "KX", "KY", "X", "Y", "N", "I", "nn", "yy", "xx", "ii"]
FIXED_LOOP_ORDER = ["B", "N",  "nn","X", "Y", "I", "ii", "KX", "KY" , "yy", "xx"]#WS
FIXED_LOOP_ORDER = ["B","X", "Y", "yy", "xx", "I", "ii", "KX", "KY" , "N", "nn"]#IS 
FIXED_LOOP_ORDER = ["B","X",  "KY" ,"Y", "yy", "xx","I", "ii", "KX",  "N", "nn"]#IS_KX

#THIS IS FOR THE FIXED MAPPING ONLY
MAPPING = {
        "B": "for bb in range(0, INPUT_BATCH , TB):",
        "KX": "for kkx in range(0, KERNEL_SIZE[0], TKX):",
        "KY": "for kky in range(0, KERNEL_SIZE[1], TKY):",
        "X": "for xxx in range(0, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ), TXX):",
        "Y": "for yyy in range(0, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ), TYY):",
        "N": "for nnn in range(0, OUT_CHANNELS, TNN):",
        "I": "for iii in range(0, INPUT_CHANNELS , TII):",

        "nn": "for nn in range(nnn, min(nnn+TNN, OUT_CHANNELS), TN):",
        "ii": "for ii in range(iii, min(iii+TII, INPUT_CHANNELS), TI):",
        "xx": "for xx in range(xxx, min(xxx+TXX, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )), TX):",
        "yy": "for yy in range(yyy, min(yyy+TYY, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  )), TY):",
    }

SUPPORTED_PRECISIONS = [8, 16] #See how we can support multiple precisions, [From 1 to 32 bit subsets, for example] [4, 5, 6, 7, 8] or [8, 10, 12, 14, 16]


#This config is for fixed dataflows
op_config = {
        "IN_CHANNELS": IN_CHANNELS,
        "OUT_CHANNELS": OUT_CHANNELS,
        "KERNEL_SIZE": KERNEL_SIZE,
        "STRIDE": STRIDE,
        
        "PADDING": PADDING,
        "DILATION":DILATION,
        "GROUPS":GROUPS,

        "POOL_SIZE":POOL_SIZE,
        "POOL_STRIDE": POOL_STRIDE,
        "POOL_PAD": POOL_PAD,

        "CONV": CONV,
        "ACTIVATION": ACTIVATION,
        "POOLING": POOLING,
        "BATCH_NORM": BATCH_NORM,

        "INPUT_BATCH": INPUT_BATCH,
        "INPUT_CHANNELS": INPUT_CHANNELS,
        "INPUT_X": INPUT_X,
        "INPUT_Y": INPUT_Y,

        "activation_precision": activation_precision,
        "weight_precision": weight_precision,
        
        
        "sparsity": sparsity,
        "strategy": strategy,

        "benchmark": benchmark,

        #SOFTWARE PARAMTERS (UP)
}

hardware_config = {
        #HARDWARE PARAMETERS (DOWN)
        #TILING
        "TX": TX,
        "TY": TY,
        "TB": TB,
        "TN": TN,
        "TI": TI,
        "TKX": TKX,
        "TKY": TKY,
        #NUM PES = TX*TY*TB*TN*TI*TKX*TKY
        
        #Time based tiling
        "TNN": TNN,
        "TII": TII,
        "TXX": TXX,
        "TYY": TYY,


        #scratchpad only use for inter-pe communication architectures
        #Number of size in BYTES (THE SCRATCHPAD, L1, L2 bit widths are inferred by the tiling)
        "WEIGHT_SCRATCHPAD": 8, #This is the closest proximity, increase this will decrease weight_buffer reads
        "ACT_SCRATCHPAD": 8,
        #BY MANHATTAN DISTANCE (or extended manhattan with diagonal move)
        "INTER_PE": 0,
        #If allow diagonal passing
        "ALLOW_DIAGONAL": False,
        

        #(TODOS) allow knight/horse move
        # ->->
        #     |
        #     V

        #L1
        "WEIGHT_BUFFER": 1024,#1KBytes
        "WEIGHT_BANKS": 8, #For saving power and energy
        "ACT_BUFFER": 1024,#1KBytes
        "ACT_BANKS": 8, #For saving power and energy

        "OUTPUT_BANKS": 8,
        "OUTPUT_BUFFER": 1024,
        

        #L2
        "GLOBAL_SRAM": 128000, #128KBytes
        "L2_DATA_FORMAT": "FEED", #FEED, DENSE or SPARSE
        "L2_WIDTH": 128,
        "L2_ROWS": 128,
        "L2_BANKS": 1,
        
        #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
        "DDR_WIDTH": 128,
        "BURST": 4,
        "DDR_DATA_FORMAT": "FEED",

        "SUPPORTED_PRECISIONS": SUPPORTED_PRECISIONS,
        "MAX_PRECISIONS": max(SUPPORTED_PRECISIONS)
}

 
#Another config for reconfigurable dataflows
reconfigurable_op_config = dict(op_config)
'''
reconfigurable_op_config += {
    "INTER_PE": [0,1,2,3,4], #ARRAY OF ALLOWABLE INTER_PE PASSING DISTANCES
    "ALLOW_DIAGONAL": False, #True or False

    #Reconfigurable Tiling
    "CONV_TILINGS": {
        "DEFAULT":  {
               "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
                "TX": TX,
                "TY": TY,
                "TB": TB,
                "TN": TN,
                "TI": TI,
                "TKX": TKX,
                "TKY": TKY,
                #NUM PES = TX*TY*TB*TN*TI*TKX*TKY
                
                #Time based tiling
                "TNN": TNN,
                "TII": TII,
                "TXX": TXX,
                "TYY": TYY,
            },
        "kx_3_ky_3": {
            "DATAFLOW_TYPE": "TENSOR_UNIT_WINOGRAD",
            #Tiling is inferred
            #Is an element-wise multiplication against element-wise multiplication, so we basically need a unicast to unicast dataflow
        },
        "kx_5_ky_5": {
           "DATAFLOW_TYPE": "TENSOR_UNIT_FFT",
        },
        "kx_1_ky_1": {
            "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER",
            "TX": 1,
            "TY": 1,
            "TB": TB,
            "TN": TN,
            "TI": TI,
            "TKX": TKX,
            "TKY": TKY,
        },
    "POOL_TILINGS": {
        "DEFAULT": {
            #TODOS
            "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER", #"PDP_UNIT"
        }
    },
    "SDP_TILINGS": {
        "DEFAULT": {
            #TODOS
            "DATAFLOW_TYPE": "TENSOR_UNIT_LOOP_ORDER", #"SDP_UNIT"
        }
    },
    "TRANSFORMER_TILINGS": {
        "DEFAULT": {
            #TODOS
            "DATAFLOW_TYPE": "TRANSFORMER_UNIT_LOOP_ORDER", #"SDP_UNIT"
        }
    }

}}
'''

#Given a network, a tiling, analyze and compute the minimum buffer needed for each level of loop
def analyze_L1_buffer(FIXED_LOOP_ORDER, MAPPING, DATAFLOW, hardware_config, config):

    print("ANALYZING ", FIXED_LOOP_ORDER[::-1])

    IN_CHANNELS = config["IN_CHANNELS"]
    OUT_CHANNELS=config["OUT_CHANNELS"] 
    KERNEL_SIZE=config["KERNEL_SIZE"]
    STRIDE=config["STRIDE"] 
    
    PADDING=config["PADDING"]
    DILATION=config["DILATION"]
    GROUPS=config["GROUPS"]

    POOL_SIZE=config["POOL_SIZE"]
    POOL_STRIDE=config["POOL_STRIDE"] 
    POOL_PAD=config["POOL_PAD"] 

    CONV=config["CONV"] 
    ACTIVATION=config["ACTIVATION"] 
    POOLING=config["POOLING"]
    BATCH_NORM=config["BATCH_NORM"]
    
    INPUT_BATCH=config["INPUT_BATCH"] 
    INPUT_CHANNELS=config["INPUT_CHANNELS"]
    INPUT_X=config["INPUT_X"] 
    INPUT_Y=config["INPUT_Y"] 

    activation_precision=config["activation_precision"]
    weight_precision = config["weight_precision"]
    
    sparsity=config["sparsity"] 
    strategy=config["strategy"] 

    benchmark=config["benchmark"]


    TX = hardware_config["TX"]
    TY = hardware_config["TY"]
    TB = hardware_config["TB"]
    TN = hardware_config["TN"]
    TI = hardware_config["TI"]
    TKX = hardware_config["TKX"]
    TKY = hardware_config["TKY"]
    TNN = hardware_config["TNN"]
    TII = hardware_config["TII"]
    TXX = hardware_config["TXX"]
    TYY = hardware_config["TYY"]
    
    L1_wei_row_width = TN*TKX*TKY*TI
    L1_act_row_width = TI*TB*TX*TY
    L1_out_row_width = TN*TX*TY


    L1_input_reuse = [1]
    L1_wei_reuse = [1]
    L1_out_reuse = [1]

    #(todos) for systolic and other architectures
    #THe key idea here is that
    #Every data send to the PE array can be re-used
    #There is some re-use cycle depending on the time loop.
    #

    X_RANGE = ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )
    Y_RANGE = ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  )
    
    for item in FIXED_LOOP_ORDER[::-1]:
        #print(item)
        if(item == "B"):
            L1_out_reuse.append(    INPUT_BATCH//min(INPUT_BATCH,TB) * L1_out_reuse[-1] )
            L1_input_reuse.append(  INPUT_BATCH//min(INPUT_BATCH,TB) * L1_input_reuse[-1] )
            L1_wei_reuse.append(    L1_wei_reuse[-1] )
        elif(item == "X"):
            L1_out_reuse.append(   ( X_RANGE //min(TXX, X_RANGE)) * L1_out_reuse[-1] )
            L1_input_reuse.append( ( X_RANGE //min(TXX, X_RANGE)) * L1_input_reuse[-1] )
            L1_wei_reuse.append( L1_wei_reuse[-1] )
        elif(item == "Y"):
            L1_out_reuse.append(   ( Y_RANGE //min(TYY, Y_RANGE)) * L1_out_reuse[-1] )
            L1_input_reuse.append( ( Y_RANGE //min(TYY, Y_RANGE))  * L1_input_reuse[-1] )
            L1_wei_reuse.append( L1_wei_reuse[-1] )
        elif(item == "yy"):
            L1_out_reuse.append( (min(TYY, Y_RANGE)//min(TY, Y_RANGE) )  * L1_out_reuse[-1] )
            L1_input_reuse.append( (min(TYY, Y_RANGE)//min(TY, Y_RANGE) ) * L1_input_reuse[-1] )
            L1_wei_reuse.append( L1_wei_reuse[-1] )
        elif(item == "xx"):
            L1_out_reuse.append((min(TXX, X_RANGE)//min(TX,X_RANGE) )  * L1_out_reuse[-1] )
            L1_input_reuse.append((min(TXX, X_RANGE)//min(TX,X_RANGE) ) * L1_input_reuse[-1] )
            L1_wei_reuse.append( L1_wei_reuse[-1] )
            
        elif(item == "I"):
            L1_out_reuse.append(1 * L1_out_reuse[-1] )
            L1_input_reuse.append( (INPUT_CHANNELS//min(TII, INPUT_CHANNELS)) * L1_input_reuse[-1] )
            L1_wei_reuse.append( (INPUT_CHANNELS//min(TII, INPUT_CHANNELS)) *  L1_wei_reuse[-1] )
        elif(item == "ii"):
            L1_out_reuse.append(1 * L1_out_reuse[-1] )
            L1_input_reuse.append(min(TII, INPUT_CHANNELS)//min(TI, INPUT_CHANNELS) * L1_input_reuse[-1] )
            L1_wei_reuse.append( min(TII, INPUT_CHANNELS)//min(TI, INPUT_CHANNELS) * L1_wei_reuse[-1] )
        elif(item == "KX"):
            L1_out_reuse.append( 1 * L1_out_reuse[-1] )
            L1_input_reuse.append( 1 * L1_input_reuse[-1] )
            L1_wei_reuse.append( (KERNEL_SIZE[0]//min(KERNEL_SIZE[0],TKX))  * L1_wei_reuse[-1] )
        elif(item == "KY"):
            L1_out_reuse.append(1 * L1_out_reuse[-1] )
            L1_input_reuse.append(1 * L1_input_reuse[-1] )
            L1_wei_reuse.append( (KERNEL_SIZE[1]//min(KERNEL_SIZE[1],TKY))  * L1_wei_reuse[-1] )
        elif(item == "N"):
            L1_out_reuse.append( (OUT_CHANNELS//min(OUT_CHANNELS,TNN)) * L1_out_reuse[-1] )
            L1_input_reuse.append(1 * L1_input_reuse[-1] )
            L1_wei_reuse.append( (OUT_CHANNELS//min(OUT_CHANNELS,TNN)) * L1_wei_reuse[-1] )
        elif(item == "nn"):
            L1_out_reuse.append( (min(OUT_CHANNELS,TNN)//min(OUT_CHANNELS,TN) ) * L1_out_reuse[-1] )
            L1_input_reuse.append( 1 * L1_input_reuse[-1] )
            L1_wei_reuse.append( (min(OUT_CHANNELS,TNN)//min(OUT_CHANNELS,TN) ) * L1_wei_reuse[-1] )
            
        
    return {

        "L1_wei_row_width":L1_wei_row_width,
        "L1_act_row_width": L1_act_row_width,
        "L1_out_row_width": L1_out_row_width,

        "L1_out_reuse": L1_out_reuse[1:],
        "L1_input_reuse":L1_input_reuse[1:],
        "L1_wei_reuse":L1_wei_reuse[1:]

    }
    

#CREATE A FIXED DATAFLOW FOR THE CONVOLUTION OPERATOR (DIRECT CONVOLUTION)
def create_dataflow(FIXED_LOOP_ORDER, MAPPING, DATAFLOW, hardware_config, config):

    IN_CHANNELS = config["IN_CHANNELS"]
    OUT_CHANNELS=config["OUT_CHANNELS"] 
    KERNEL_SIZE=config["KERNEL_SIZE"]
    STRIDE=config["STRIDE"] 
    
    PADDING=config["PADDING"]
    DILATION=config["DILATION"]
    GROUPS=config["GROUPS"]

    POOL_SIZE=config["POOL_SIZE"]
    POOL_STRIDE=config["POOL_STRIDE"] 
    POOL_PAD=config["POOL_PAD"] 

    CONV=config["CONV"] 
    ACTIVATION=config["ACTIVATION"] 
    POOLING=config["POOLING"]
    BATCH_NORM=config["BATCH_NORM"]
    
    INPUT_BATCH=config["INPUT_BATCH"] 
    INPUT_CHANNELS=config["INPUT_CHANNELS"]
    INPUT_X=config["INPUT_X"] 
    INPUT_Y=config["INPUT_Y"] 

    activation_precision=config["activation_precision"]
    weight_precision = config["weight_precision"]

    
    sparsity=config["sparsity"] 
    strategy=config["strategy"] 

    benchmark=config["benchmark"]
    

    #Analyze the L1 buffers
    L1_buffer_stats = analyze_L1_buffer(FIXED_LOOP_ORDER, MAPPING, DATAFLOW, hardware_config, config)
    print(L1_buffer_stats)
    
    f = open("dataflow_gen.py", "w")

    f.write("def dataflow_gen(hardware_config, software_config, activation, weight):\n")



    depth = 1


    for k in hardware_config:
        f.write("    "*depth + k  + '=hardware_config["'+k+'"]\n')
    for k in config:
        f.write("    "*depth + k  + '=software_config["'+k+'"]\n')


    #Output datasets for the testbenches
    f.write("    "*depth + 'weight_out = open(\'' +  benchmark+"/weights.txt'"  +  ',"w")' +  '\n')
    f.write("    "*depth + 'act_out = open(\'' +     benchmark+"/activation.txt'"  + ',"w")' +  '\n')
    
    #(any other things to out? such as Sigmoid/Tanh parameters, bias ?)
    


    f.write("    "*depth + "cycle = 0\n")
    for var in FIXED_LOOP_ORDER:
        #FIXED_LOOP_ORDER = ["B", "KX", "KY", "X", "Y", "N", "I",
        #            "nn", "yy", "xx", "ii"]

        f.write("    "*depth + MAPPING[var]+"\n")
        depth += 1


    f.write("\
    "+"    "*depth + "print('@CYCLE = ', cycle)\n\
    "+"    "*depth + "pe_no = 0\n\
    "+"    "*depth + "cycle += 1\n\
    "+"    "*depth + "#ACT_ATOMIC = set()\n\
    "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
    "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
    "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
    "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
    "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
    "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
    "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
    "+"    "*depth + "                            print('  ACT', pe_no, '\tB', b, '\tI', i, '\tIX', x+kx, '\tIY', y+ky, activation[b][i][x+kx][y+ky]) #b, i, x + kx, y + ky)\n\
    "+"    "*depth + "                            pe_no += 1\n\
    "+"    "*depth + "pe_no = 0\n\
    "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
    "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
    "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
    "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
    "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
    "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
    "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
    "+"    "*depth + "                            print('  Wei', pe_no, '\tN', n, '\tI', i, '\tKX', kx, '\tKY', ky, weight[n][i][kx][ky])\n\
    "+"    "*depth + "                            pe_no += 1\n\
    ")

    '''
    #Write out the data readmemh for the verilog (the order of the data)
    if(hardware_config["L2_DATA_FORMAT"] == "FEED"):#We assume there is broadcast in this version
        f.write("\
        "+"    "*depth + "pe_no = 0\n\
        "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
        "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
        "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
        "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
        "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
        "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
        "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
        "+"    "*depth + "                            ## (TODOS) L1_READ = act_address(b, i, x+kx, y+ky) , the act_address will index based on hte loop order ! that will the indices will be monotonous and increase in some step (todo and research this one) \n\
        "+"    "*depth + "                            ## (TODOS) L1_MISS = 
        "+"    "*depth + "                            print('  ACT', pe_no, '\tB', b, '\tI', i, '\tIX', x+kx, '\tIY', y+ky, activation[b][i][x+kx][y+ky]) #b, i, x + kx, y + ky)\n\
        "+"    "*depth + "                            pe_no += 1\n\
        "+"    "*depth + "pe_no = 0\n\
        "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
        "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
        "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
        "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
        "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
        "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
        "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
        "+"    "*depth + "##(TODOS) L1_READ = wei_address(n,i,kx,ky) , we will L1_READ % (L1_ROWS) or L1_READ % (L2_ROWS) with some shifts to find the data with this address. Because we don't want a cache, we just have a rolling buffer to immediately get the value
        "+"    "*depth + "##(TODOS) L1_MISS = (??)#if this signal is MISS, then we need to retrieve the data from L2, otherwise just read the L1_READ address, the way we retrieve it is send a read request to L2, and L2 will send the data into a shifter register (if BW not matched or foramt not matched)
                          ## HOW DO WE KNOW THERE IS A MISS ? 
        # then keep on reading L2 until enough data, then reshape the data and save it into L1, then read this value (or we can bypass it) to speed-it up
        "+"    "*depth + "                            pe_no += 1\n\
        ")
    elif(hardware_config["L2_DATA_FORMAT"] == "DENSE"):  
        pass
    elif(hardware_config["L2_DATA_FORMAT"] == "SPARSE"):
        pass
    else:#no assumptions, will feed the entire thing no broadcast
        f.write("\
        "+"    "*depth + "pe_no = 0\n\
        "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
        "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
        "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
        "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
        "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
        "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
        "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
        "+"    "*depth + "                            activation[b][i][x+kx][y+ky]\n\
        "+"    "*depth + "                            pe_no += 1\n\
        "+"    "*depth + "pe_no = 0\n\
        "+"    "*depth + "for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):\n\
        "+"    "*depth + "    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):\n\
        "+"    "*depth + "        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):\n\
        "+"    "*depth + "            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):\n\
        "+"    "*depth + "                for i in range(ii, min(ii+TI, IN_CHANNELS)):\n\
        "+"    "*depth + "                    for n in range(nn, min(nn+TN, OUT_CHANNELS)):\n\
        "+"    "*depth + "                        for b in range(bb, min(bb + INPUT_BATCH, TB)):\n\
        "+"    "*depth + "                            weight[n][i][kx][ky]\n\
        "+"    "*depth + "                            pe_no += 1\n\
        ")        
    '''
    f.close()





#CREATE THE DATAFLOW WITH THE GIVEN DATAFLOW
create_dataflow(FIXED_LOOP_ORDER, MAPPING, DATAFLOW, hardware_config, op_config)
from dataflow_gen import dataflow_gen
#Run the operation

#Need to fix the input
fix_input = np.zeros((LEN, IN_CHANNELS, INPUT_X + int(PADDING[0])*2, INPUT_Y + int(PADDING[1])*2)).astype("int")

for b in range(LEN):
    for i in range(IN_CHANNELS):
        for x in range(INPUT_X):
            for y in range(INPUT_Y):
                fix_input[b][i][x+int(PADDING[0])][y+int(PADDING[1])] = fake_input[b][i][x][y]

fake_input = np.array(fix_input)  

dataflow_gen(hardware_config, op_config, fake_input, state_dict['conv2d_0.w_0'])

nn = 0
ii = 0
yy = 0
xx = 0
kkx = 0
kky = 0
bb = 0

cycle = 0

#(How to iterate through to get the below tilings)

#(At every clock cycle, these below events happen) Inner tiling (Hardware spatial based)



#WITHOUT ANY REUSE
FETCH_WEI = []
FETCH_DATA = []



'''
if (DATAFLOW == "Default"):

    

    



    print("@CYCLE = ", cycle)
    pe_no = 0
    #ACT_ATOMIC = set()
    for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0] - KERNEL_SIZE[0] + 1) / STRIDE[0]  )):
        for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1] - KERNEL_SIZE[1] + 1))):
            for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                    for i in range(ii, min(ii+TI, IN_CHANNELS)):
                        for n in range(nn, min(nn+TN, OUT_CHANNELS)):
                            for b in range(bb, min(bb + INPUT_BATCH, TB)):
                                print("  ACT", pe_no, "\tB", b, "\tI", i, "\tIX", x+kx, "\tIY", y+ky, fake_input[b][i][x+kx][y+ky]) #b, i, x + kx, y + ky)
                                #print("Wei", pe_no, "\tN", n, "\tI", i, "\tKX", kx, "\tKY", ky)
                                pe_no += 1
                                
    pe_no = 0
    for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0] - KERNEL_SIZE[0] + 1) / STRIDE[0]  )):
        for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1] - KERNEL_SIZE[1] + 1))):
            for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                    for i in range(ii, min(ii+TI, IN_CHANNELS)):
                        for n in range(nn, min(nn+TN, OUT_CHANNELS)):
                            for b in range(bb, min(bb + INPUT_BATCH, TB)):
                                #print("ACT", pe_no, "\tB", b, "\tI", i, "\tIX", x+kx, "\tIY", y+ky) #b, i, x + kx, y + ky)
                                print("  Wei", pe_no, "\tN", n, "\tI", i, "\tKX", kx, "\tKY", ky, state_dict['conv2d_0.w_0'][n][i][kx][ky])
                                pe_no += 1

                                
    cycle += 1
                            
elif (DATAFLOW == "1DSystolic"):
    #TODOS
    pass
elif (DATAFLOW == "2DSystolic"):
    #TODOS
    pass
'''
#################################CHECKING###################################
#print(s)

if BIAS ==False:
    state_dict['conv2d_1.tmp_0@scale'] = state_dict['conv2d_0.w_0@scale']
    
#print(output_data[0:2])
#s = state_dict['inputs@scale']*state_dict['conv2d_0.w_0@scale']/state_dict['conv2d_1.tmp_0@scale']/(2**(precision-1)-1) #conv_w + bias
s = (state_dict['inputs@scale']*state_dict['conv2d_0.w_0@scale']/state_dict['conv2d_1.tmp_0@scale']/(2**(activation_precision-1)-1)).reshape((-1, 1, 1)) #conv_w

   

for b in range(LEN):
    o = np.round(np.array(output_data[b]/state_dict['conv2d_1.tmp_0@scale']*(2**(activation_precision-1)-1)))
    #print(o)

    print("###############################")
    #Direct Convolution
    shou_q = np.zeros((OUT_CHANNELS, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0] , (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1] )).astype('int')
    for kx in range(KERNEL_SIZE[0]):
        for ky in range(KERNEL_SIZE[1]):
            for x in range((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ):
                for y in range((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]):
                    for i in range(IN_CHANNELS):
                        for n in range(OUT_CHANNELS):
                            shou_q[n][x][y] += state_dict['conv2d_0.w_0'][n][i][kx][ky]*fake_input[b][i][x+kx][y+ky]
    #Winograd Convolution
    wino_q = np.zeros((OUT_CHANNELS, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0] , (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1] )).astype('int')
    if KERNEL_SIZE[0] == 3 and KERNEL_SIZE[1] == 3 and STRIDE[0] == 1 and STRIDE[1] == 1 and "FILTER3" in WINOGRAD_CHINESE:
        WINO_INPUT =  WINOGRAD_CHINESE["FILTER3"]

        mods = [0]
        for i in range(WINO_INPUT - 3+1):
            if(mods[-1] == 0):
                mods.append(1)
            elif(mods[-1] > 0):
                mods.append(-mods[-1])
            else:
                mods.append(-mods[-1]+1)
        #print(mods)
        AT,G,BT,f = wincnn.cookToomFilter(mods, WINO_INPUT - 3 + 1, 3)
        A = np.array(AT).transpose()
        GT = np.array(G).transpose()
        B = np.array(BT).transpose()

        TILE_WINO = WINO_INPUT-3+1
   
        for xx in range(0, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0] , TILE_WINO):
            for yy in range(0, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1], TILE_WINO):
                for i in range(IN_CHANNELS):
                    for n in range(OUT_CHANNELS):
                        W = state_dict['conv2d_0.w_0'][n][i]
                        I = np.zeros((WINO_INPUT, WINO_INPUT))
                        
                        for x in range(xx, min(xx+WINO_INPUT, INPUT_X + PADDING[0]*2 )):
                            for y in range(yy, min(yy+WINO_INPUT, INPUT_Y ++ PADDING[1]*2 )):
                                I[x-xx][y-yy] = fake_input[b][i][x][y]
                        
                        #I = fake_input[b][0][0:0+WINO_INPUT][0:0+WINO_INPUT]
                        wino_shou = np.matmul(np.matmul(AT,np.matmul(np.matmul(G,W),GT)*np.matmul(np.matmul(BT,I),B)),A)
                        #print(I,W,wino_shou)
                        for x in range(xx, min(xx+TILE_WINO, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0] )):
                            for y in range(yy, min(yy+TILE_WINO, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1] )):
                                wino_q[n][x][y] += wino_shou[x - xx][y - yy]
                                #print(x,y)
        print("wino_q")
        print(wino_q)
    #, #Support one filter or different input sizes
    #6,#,5,6,7,8,9,10]

    #FFT Convolution (TODOS)
                        
    #shou_q = i*(127 + -39 + 73 + 112)
    print("SHOU_q (unscaled)")
    print(shou_q)

    
    #print(shou_q)
    #Post process
    shou = shou_q*s
    #shou = shou_q
    print("SHOU (scaled)")
    print(shou)
    #shou = np.min(np.max(np.round(shou), -128),127)
    shou = np.round(shou)
    print("INPUT")
    print(fake_input[b])
    print("Output[FLOAT]")
    print(output_data[b])
    #print("shou_q (before scaling)")
    #print(shou_q)
    print("OUTPUT[INT] (REFERENCE)")
    print(o - (state_dict['conv2d_0.b_0']/s).astype("int"))
    print("手动")
    print(shou)
    print("检查")
    print((o - (state_dict['conv2d_0.b_0']/s).astype("int")) == np.clip(np.round(s*shou_q), -2**(activation_precision-1), 2**(activation_precision-1)-1 ))
    print((o - (state_dict['conv2d_0.b_0']/s).astype("int")) == np.clip(np.round(s*wino_q), -2**(activation_precision-1), 2**(activation_precision-1)-1 ))
    #print()


print("weights", state_dict['conv2d_0.w_0'])

if(BIAS):
    print("bias", state_dict['conv2d_0.b_0'])
    
