import numpy as np


#KEY FEATURES
# 1. Reconfigurability in the PE precision level
# 2. Reconfigurability in the dataflow level (i.e. IS, OS, WS , Winograd, Strassen)
# 3. Reconfigurability in the sparsity level (i.e. sparsity Input, sparsity weight, gating sparsity)
# 4. Reconfigurability in the buffers level (delays, buffer sizes, buffer widths)
# 5. Support common operations, such as CONV2D, FC, RELU/ACTIVATIONS, POOLING2D and their fusion operations
# 6. Support an AI-based PPA explorer tool

#7. Future, operation-level parallelism. What about Transformer, other operations ? Multi-cores, multi-dies, chiplet, emerging technologies such as CIM? DSE and design. 

from generators.gen_multiplier import  gen_multiplier
from generators.gen_pe_array import gen_pe_array, gen_pe_input_mapping, gen_pe_output_mapping

from generators.gen_accum import gen_accum

#from generators.gen_addr_cnt import gen_addr_cnt

from generators.gen_core import gen_core_v1,gen_core_v2

from generators.gen_buffer import gen_buffers

from generators.gen_elt_unit import gen_elt_unit

def gen_testbench(hardware_config, meta_config):
    pass

def gen_dma(hardware_config, meta_config):
    pass


#the top module
def gen_dla(hardware_config, meta_config, macro_cfg):
    pass



def gen_adder_tree(hardware_config, meta_config, macro_config):
    #number of adders is the max
    pass

def gen_sdp_unit(hardware_config, meta_config, macro_config):
    pass





def gen_dma(hardware_config, meta_config, macro_config):

    #including units to interact with the DDR, and for conversion of the data into suitable formats (if is IMG2COL or sparsity something like that)
    pass





    
def gen_macro_file(hardware_config, meta_config):

    print("\n// GEN_MACR_FILE\n")
    f = open(meta_config["dossier"] + "/macro.vh", "w")


    PES = []
    LINEAR_PES = [0] #optional
    POOL_PES = [0] #optional
    
    WEI_BUF_DATA = []
    ACT_BUF_DATA = []
    PSUM_BUF_DATA = []
    
    WEI_SPARSE_MAP_BUF_DATA = [0]
    ACT_SPARSE_MAP_BUF_DATA = [0]
    PSUM_SPARSE_MAP_BUF_DATA = [0]


    LINEAR_WEI_BUF_DATA = [0]
    LINEAR_ACT_BUF_DATA = [0]
    LINEAR_PSUM_BUF_DATA = [0]


    POOL_WEI_BUF_DATA = [0]
    POOL_ACT_BUF_DATA = [0]
    POOL_PSUM_BUF_DATA = [0]


    #1. analyze convoution dataflows
    #MAX_WEI_PRECISION = max(hardware_config["SUPPORTED_WEI_PRECISIONS"])
    #MAX_ACT_PRECISION = max(hardware_config["SUPPORTED_ACT_PRECISIONS"])
    SUPPORTED_WEI_DTYPES_INT = []
    SUPPORTED_WEI_DTYPES_FP = []
    for wei in hardware_config["SUPPORTED_WEI_DTYPES"]:
        if("INT" in wei):
            SUPPORTED_WEI_DTYPES_INT.append(wei)
        else:
            SUPPORTED_WEI_DTYPES_FP.append(wei)
    SUPPORTED_ACT_DTYPES_INT = []
    SUPPORTED_ACT_DTYPES_FP = []
    for act in hardware_config["SUPPORTED_ACT_DTYPES"]:
        if("INT" in act):
            SUPPORTED_ACT_DTYPES_INT.append(act)
        else:
            SUPPORTED_ACT_DTYPES_FP.append(act)

    SUPPORTED_OUT_DTYPES_INT = []
    SUPPORTED_OUT_DTYPES_FP = []
    for act in hardware_config["SUPPORTED_OUT_DTYPES"]:
        if("INT" in act):
            SUPPORTED_OUT_DTYPES_INT.append(act)
        else:
            SUPPORTED_OUT_DTYPES_FP.append(act)



            
    SUPPORTED_WEI_PRECISIONS_FP = []
    for wei in SUPPORTED_WEI_DTYPES_FP:
        if(wei[-2:] == "32"):
            SUPPORTED_WEI_PRECISIONS_FP.append(32)
        elif(wei[-2:] == "16"):
            SUPPORTED_WEI_PRECISIONS_FP.append(16)            
        elif(wei[-1:] == "8"):
            SUPPORTED_WEI_PRECISIONS_FP.append(8)
        elif(wei[-1:] == "4"):
            SUPPORTED_WEI_PRECISIONS_FP.append(4)
        elif(wei[-1:] == "2"):
            SUPPORTED_WEI_PRECISIONS_FP.append(2)
        elif(wei[-1:] == "1"):
            SUPPORTED_WEI_PRECISIONS_FP.append(1)

    SUPPORTED_WEI_PRECISIONS_INT = []
    for wei in SUPPORTED_WEI_DTYPES_INT:
        if(wei[-2:] == "32"):
            SUPPORTED_WEI_PRECISIONS_INT.append(32)
        elif(wei[-2:] == "16"):
            SUPPORTED_WEI_PRECISIONS_INT.append(16)            
        elif(wei[-1:] == "8"):
            SUPPORTED_WEI_PRECISIONS_INT.append(8)
        elif(wei[-1:] == "4"):
            SUPPORTED_WEI_PRECISIONS_INT.append(4)
        elif(wei[-1:] == "2"):
            SUPPORTED_WEI_PRECISIONS_INT.append(2)
        elif(wei[-1:] == "1"):
            SUPPORTED_WEI_PRECISIONS_INT.append(1)

    SUPPORTED_ACT_PRECISIONS_FP = []
    for act in SUPPORTED_ACT_DTYPES_FP:
        if(act[-2:] == "32"):
            SUPPORTED_ACT_PRECISIONS_FP.append(32)
        elif(act[-2:] == "16"):
            SUPPORTED_ACT_PRECISIONS_FP.append(16)            
        elif(act[-1:] == "8"):
            SUPPORTED_ACT_PRECISIONS_FP.append(8)
        elif(act[-1:] == "4"):
            SUPPORTED_ACT_PRECISIONS_FP.append(4)
        elif(act[-1:] == "2"):
            SUPPORTED_ACT_PRECISIONS_FP.append(2)
        elif(act[-1:] == "1"):
            SUPPORTED_ACT_PRECISIONS_FP.append(1)

    SUPPORTED_ACT_PRECISIONS_INT = []
    for act in SUPPORTED_ACT_DTYPES_INT:
        if(act[-2:] == "32"):
            SUPPORTED_ACT_PRECISIONS_INT.append(32)
        elif(act[-2:] == "16"):
            SUPPORTED_ACT_PRECISIONS_INT.append(16)            
        elif(act[-1:] == "8"):
            SUPPORTED_ACT_PRECISIONS_INT.append(8)
        elif(act[-1:] == "4"):
            SUPPORTED_ACT_PRECISIONS_INT.append(4)
        elif(act[-1:] == "2"):
            SUPPORTED_ACT_PRECISIONS_INT.append(2)
        elif(act[-1:] == "1"):
            SUPPORTED_ACT_PRECISIONS_INT.append(1)

    SUPPORTED_OUT_PRECISIONS_FP = []
    for act in SUPPORTED_OUT_DTYPES_FP:
        if(act[-2:] == "32"):
            SUPPORTED_OUT_PRECISIONS_FP.append(32)
        elif(act[-2:] == "16"):
            SUPPORTED_OUT_PRECISIONS_FP.append(16)            
        elif(act[-1:] == "8"):
            SUPPORTED_OUT_PRECISIONS_FP.append(8)
        elif(act[-1:] == "4"):
            SUPPORTED_OUT_PRECISIONS_FP.append(4)
        elif(act[-1:] == "2"):
            SUPPORTED_OUT_PRECISIONS_FP.append(2)
        elif(act[-1:] == "1"):
            SUPPORTED_OUT_PRECISIONS_FP.append(1)

    SUPPORTED_OUT_PRECISIONS_INT = []
    for act in SUPPORTED_OUT_DTYPES_INT:
        if(act[-2:] == "32"):
            SUPPORTED_OUT_PRECISIONS_INT.append(32)
        elif(act[-2:] == "16"):
            SUPPORTED_OUT_PRECISIONS_INT.append(16)            
        elif(act[-1:] == "8"):
            SUPPORTED_OUT_PRECISIONS_INT.append(8)
        elif(act[-1:] == "4"):
            SUPPORTED_OUT_PRECISIONS_INT.append(4)
        elif(act[-1:] == "2"):
            SUPPORTED_OUT_PRECISIONS_INT.append(2)
        elif(act[-1:] == "1"):
            SUPPORTED_OUT_PRECISIONS_INT.append(1)

            
    #print(max(SUPPORTED_WEI_PRECISIONS_FP+ SUPPORTED_WEI_PRECISIONS_INT))
    if(len(SUPPORTED_WEI_PRECISIONS_INT) == 0):
        SUPPORTED_WEI_PRECISIONS_INT = [0]

    if(len(SUPPORTED_ACT_PRECISIONS_INT) == 0):
        SUPPORTED_ACT_PRECISIONS_INT = [0]

    if(len(SUPPORTED_WEI_PRECISIONS_FP) == 0):
        SUPPORTED_WEI_PRECISIONS_FP = [0]

    if(len(SUPPORTED_ACT_PRECISIONS_FP) == 0):
        SUPPORTED_ACT_PRECISIONS_FP = [0]

    if(len(SUPPORTED_OUT_PRECISIONS_FP) == 0):
        SUPPORTED_OUT_PRECISIONS_FP = [0]

    if(len(SUPPORTED_OUT_PRECISIONS_INT) == 0):
        SUPPORTED_OUT_PRECISIONS_INT = [0]
        
            
    MAX_WEI_PRECISION = max(SUPPORTED_WEI_PRECISIONS_FP+ SUPPORTED_WEI_PRECISIONS_INT)
    MIN_WEI_PRECISION = min(SUPPORTED_WEI_PRECISIONS_FP+ SUPPORTED_WEI_PRECISIONS_INT)
    MAX_ACT_PRECISION = max(SUPPORTED_ACT_PRECISIONS_FP+ SUPPORTED_ACT_PRECISIONS_INT)
    MIN_ACT_PRECISION = min(SUPPORTED_ACT_PRECISIONS_FP+ SUPPORTED_ACT_PRECISIONS_INT)

    MAX_OUT_PRECISION = max(SUPPORTED_OUT_PRECISIONS_FP+ SUPPORTED_OUT_PRECISIONS_INT)
    MIN_OUT_PRECISION = min(SUPPORTED_OUT_PRECISIONS_FP+ SUPPORTED_OUT_PRECISIONS_INT)


    
    MAX_WEI_PRECISION_INT = max(SUPPORTED_WEI_PRECISIONS_INT)
    MIN_WEI_PRECISION_INT = min(SUPPORTED_WEI_PRECISIONS_INT)
    MAX_ACT_PRECISION_INT = max(SUPPORTED_ACT_PRECISIONS_INT)
    MIN_ACT_PRECISION_INT = min(SUPPORTED_ACT_PRECISIONS_INT)

    MAX_OUT_PRECISION_INT = max(SUPPORTED_OUT_PRECISIONS_INT)
    MIN_OUT_PRECISION_INT = min(SUPPORTED_OUT_PRECISIONS_INT)



    WINOGRAD_EN = False
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):

        WINOGRAD_EN = True
        
        #print("WINOGRAD")
        #exit()
       
    MAX_WEI_PRECISION_FP = max(SUPPORTED_WEI_PRECISIONS_FP)
    MIN_WEI_PRECISION_FP = min(SUPPORTED_WEI_PRECISIONS_FP)
    MAX_ACT_PRECISION_FP = max(SUPPORTED_ACT_PRECISIONS_FP)
    MIN_ACT_PRECISION_FP = min(SUPPORTED_ACT_PRECISIONS_FP)

    MAX_OUT_PRECISION_FP = max(SUPPORTED_OUT_PRECISIONS_FP)
    MIN_OUT_PRECISION_FP = min(SUPPORTED_OUT_PRECISIONS_FP)
    
    MAX_PRECISION_FP = max(SUPPORTED_WEI_PRECISIONS_FP + SUPPORTED_ACT_PRECISIONS_FP)



    MAX_STRIDE = hardware_config["GEN_CONSTRAINTS"].get("MAX_STRIDE", 2)#:     (MAX_STRIDE <= 0)*16   + (MAX_STRIDE > 0)*MAX_STRIDE ,
    MAX_KX = hardware_config["GEN_CONSTRAINTS"].get("MAX_KX",5)##:         (MAX_KX <= 0)*16   + (MAX_KX > 0)*MAX_KX ,
    MAX_KY = hardware_config["GEN_CONSTRAINTS"].get("MAX_KY",5)#:         (MAX_KY <= 0)*16   + (MAX_KY > 0)*MAX_KY ,
    MAX_X = hardware_config["GEN_CONSTRAINTS"].get("MAX_X",128)#:        (MAX_X <= 0)*16   + (MAX_X > 0)*MAX_X ,
    MAX_Y = hardware_config["GEN_CONSTRAINTS"].get("MAX_Y",128)#:   (MAX_Y <= 0)*16   + (MAX_Y > 0)*MAX_Y ,
    MAX_N = hardware_config["GEN_CONSTRAINTS"].get("MAX_N",64)#:  (MAX_N <= 0)*16   + (MAX_N > 0)*MAX_N ,
    MAX_I = hardware_config["GEN_CONSTRAINTS"].get("MAX_I",64)#:   (MAX_I <= 0)*16   + (MAX_I > 0)*MAX_I ,
    MAX_B = hardware_config["GEN_CONSTRAINTS"].get("MAX_B",1)#:   (MAX_B <= 0)*16   + (MAX_B > 0)*MAX_B ,
    MAX_PADDING_X = hardware_config["GEN_CONSTRAINTS"].get("MAX_PADDING_X",1)#:   (MAX_PADDING_X <= 0)*16   + (MAX_PADDING_X > 0)*MAX_PADDING_X ,
    MAX_PADDING_Y = hardware_config["GEN_CONSTRAINTS"].get("MAX_PADDING_Y",1)#:   (MAX_PADDING_Y <= 0)*16   + (MAX_PADDING_Y > 0)*MAX_PADDING_Y ,
    

    #TAKE INTO ACCOUNT ADDITION WILL NEED MORE BITS
    #FROM MAX_X    
    MAX_PSUM_PRECISION = max([MAX_WEI_PRECISION_INT + MAX_ACT_PRECISION_INT ,  MAX_ACT_PRECISION_FP  ])
    MAX_PSUM_PRECISION_INT = max([MAX_WEI_PRECISION_INT + MAX_ACT_PRECISION_INT ])
    MAX_PSUM_PRECISION_FP = MAX_ACT_PRECISION_FP

    MAX_ACC_PRECISION = max([MAX_WEI_PRECISION_INT + MAX_ACT_PRECISION_INT + int(np.log2(MAX_KX*MAX_KY*MAX_I)),  MAX_ACT_PRECISION_FP  ])
    MAX_ACC_PRECISION_INT = max([MAX_WEI_PRECISION_INT + MAX_ACT_PRECISION_INT + int(np.log2(MAX_KX*MAX_KY*MAX_I))])
    MAX_ACC_PRECISION_FP = MAX_ACT_PRECISION_FP


    SPARSE_ENABLE = False

 
    #Les limites (une unite c'est une calcul pour une cycle)
    WEI_L1_MIN = [] #
    WEI_FIFO_MIN = [] #DMA 
    ACT_L1_MIN = [] #
    ACT_FIFO_MIN = [] #DMA
    PSUM_L1_MIN = [] #
    PSUM_FIFO_MIN = [] #DMA


    WEI_WINDOWS_DICT = {}
    ACT_WINDOWS_DICT = {}
    
    #analyze based on the convolution flow
    for flows in hardware_config["TILINGS"]["CONV2D"]:


         
        flow_details = hardware_config["TILINGS"]["CONV2D"][flows]
        fd = flow_details

        '''
        if("MAX_KY" in fd):
            MAX_KY = fd["MAX_KY"]
        else:
            MAX_KY = hardware_config["MAX_KY"]

        if("MAX_KX" in fd):
            MAX_KX = fd["MAX_KX"]
        else:
            MAX_KX = hardware_config["MAX_KX"]

        if("MAX_X" in fd):
            MAX_X = fd["MAX_X"]
        else:
            MAX_X = hardware_config["MAX_X"]
        
        if("MAX_Y" in fd):
            MAX_Y = fd["MAX_Y"]
        else:
            MAX_Y = hardware_config["MAX_Y"]

        if("MAX_N" in fd):
            MAX_N = fd["MAX_N"]
        else:
            MAX_N = hardware_config["MAX_N"]


        if("MAX_I" in fd):
            MAX_I = fd["MAX_I"]
        else:
            MAX_I = hardware_config["MAX_I"]

        if("MAX_B" in fd):
            MAX_B = fd["MAX_B"]
        else:
            MAX_B = hardware_config["MAX_B"]

        if(MAX_B <= 0):
            MAX_B = 1
        if(MAX_I <= 0):
            MAX_I = 1
        if(MAX_N <= 0):
            MAX_N = 1
        if(MAX_Y <= 0):
            MAX_Y = 1
        if(MAX_X <= 0):
            MAX_X = 1
        if(MAX_KX <= 0):
            MAX_KX = 1
        if(MAX_KY <= 0):
            MAX_KY = 1
        '''
        #check the fd for tiling
        if(fd["TX"] <= 0):
            print("WARNING TX < 0, 改 to 1")
        if(fd["TY"] <= 0):
            print("WARNING TY < 0, 改 to 1")
            #todos

            
        #(todos) TXX TYY TNN TII

        ##################
        #DENSE DATAFLOWS
        ##################
        #analyze all the flows and extract the maximum we need      
        if(flow_details["DATAFLOW"] == "DIRECT"): #is direct just IMG2COL ?
            #Essentially Maestro, Timeloop
            PE = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]


            PE = flow_details["TX"]*fd["TKX"]*flow_details["TY"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]


            from utils import SYSTOLIC_WEIGHT_LOAD_CYCLES, SYSTOLIC_ACT_LOAD_CYCLES, SYSTOLIC_WEI_LOOP_ORDER
    
            WEI_SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(hardware_config, flow_details)

            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = PE*MAX_WEI_PRECISION // WEI_SYS_CYCLES
                ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
            else:
                WEI_BUF_DATUM = (fd["TKX"])*(fd["TKY"])*flow_details["TI"]*flow_details["TN"]*MAX_WEI_PRECISION // WEI_SYS_CYCLES
                ACT_BUF_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]*MAX_ACT_PRECISION

            PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION #c'est beaucoup plus moins parce qu'on le reduit apres l'arbre d'addition

            #反
            #"LOOP": ["B", "N", "I", "X", "Y", "KX", "KY"],
            #for B -> for N -> for I -> for X -> for Y -> for KX -> for KY

            '''
            x_lv = 1
            y_lv = 1
            lv = 1
            cun = []
            fang = []
            cent = []
            for ll in fd["LOOP"][::-1]:
                fang.append(ll)
                if(ll == "TXX"):
                    if("KX" in fang):
                     

            
            lv = 1
            cun = []
            fang = []
            lv = 1
            ceng = {}
            cun_ss = []
            ss = "1"
            for ll in fd["LOOP"][::-1]:
                fang.append(ll)
                if(ll == "KY"):
                    if("Y" in fang):
                        #lv = lv // MAX_KY * MAX_Y
                        cun.append(lv - ceng["Y"])
                        cun_ss.append(ss+"-Y")
                    else:
                        lv *= MAX_KY//fd["TKY"]
                        ss += '*MAX_KY'
                elif(ll == "KX"):
                    if("X" in fang):
                        cun.append(lv - ceng["X"])
                        cun_ss.append(ss+"-X")
                    elif("TXX" in fang):
                        cun.append(lv - ceng["TXX"])
                        cun_ss.append(ss+"-TXX")
                        #lv = lv * MAX_X
                    else:
                        lv *=  max(1, MAX_KX//fd["TKX"])
                        ss += '*MAX_KX'
                elif(ll == "X"):
                    if("TXX" in fang):
                        if("KX" in fang):
                            cun.append(lv - ceng["KX"])
                            cun_ss.append(ss+"-KX")
                            lv = lv // max(1, MAX_KX//fd["TKX"]) * max(1, MAX_X//fd["TXX"])
                            ss = ss.replace("*MAX_KX","")
                        else:
                            lv = lv * MAX_X    //fd["TXX "]

                    else:
                        if("KX" in fang):
                            cun.append(lv - ceng["KX"])
                            cun_ss.append(ss+"-KX")
                            lv = lv // max(1, MAX_KX//fd["TKX"]) * max(1, MAX_X//fd["TX"])
                            ss = ss.replace("*MAX_KX","")
                        else:
                            lv = lv * max(1, MAX_X    //fd["TX "])
                    
                    ss += ' * MAX_X '
                elif(ll == "Y"):
                    if("KY" in fang):
                        cun.append(lv - ceng["KY"])
                        cun_ss.append(ss+"-KY")

                        ss = ss.replace("*MAX_KY","")
                        lv = lv // (MAX_KY//fd["TKY"]) * MAX_Y//fd["TY"]
                    else:
                        lv = lv * MAX_Y//fd["TY"]        
                    ss += ' * MAX_Y '

                elif(ll == "TNN"):
                    cun.append(lv)
                    cun_ss.append(ss)
                elif(ll == "I"):
                    if("TII" in fang):
                        lv *= max(1, MAX_I//fd["TII"])
                    else:
                        lv *= max(1, MAX_I//fd["TI"])
                    ss += '* MAX_I'
                elif(ll == "N"):
                    if(fd["TN"] < MAX_N):
                        if("TNN" in fang):
                            if(fd["TNN"] < MAX_N):
                                cun.append(lv)
                                cun_ss.append(ss)
                        else:
                            cun.append(lv)
                            cun_ss.append(ss)
                            
                elif(ll == "B"):
                    if("TBB" in fang):
                        lv *= max(1, MAX_B//fd["TBB"])
                    else:
                        lv *= max(1, MAX_B//fd["TB"])
                    ss += '* MAX_B'

                elif(ll == "TXX"):
                    if("KX" in fang):
                        cun.append(        lv//(max(1, (MAX_KX//fd["TKX"])))*(MAX_KX <= fd["TX"])     +     (lv - ceng["KX"])*(MAX_KX > fd["TX"])  )
                        #cun_ss.append(ss+"-KX")
                        lv = lv //  max(1, (MAX_KX//fd["TKX"])) *  max(1, fd["TXX"]//fd["TX"])
                        #ss = ss.replace("*MAX_KX","")
                    else:
                        lv = lv *  max(1, fd["TXX"]    //fd["TX "])
                    
                    ss += ' * TXX '
                    
                else:
                    print("todos")

                print(ll, lv,cun, fang)
                #print(ll, ss, cun_ss, cun, np.log2(cun))
                ceng[ll] = lv
                     
                #calculate min rows based on max network size
            '''
        elif(flow_details["DATAFLOW"] == "WINOGRAD_STRIDE_1" or flow_details["DATAFLOW"] == "WINOGRAD"):


            
            from utils import SYSTOLIC_WEIGHT_LOAD_CYCLES, SYSTOLIC_ACT_LOAD_CYCLES, SYSTOLIC_WEI_LOOP_ORDER
    
            WEI_SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(hardware_config, flow_details)

            
            if("DEFAULT" in flows):
                pass
            else:
                flow_details["TKX"] = int(flows.split("kx")[1].split()[1])
                flow_details["TKY"] = int(flows.split("ky")[1].split()[1])
            
            PE = (fd["TX"]+fd["TKX"]-1)*(fd["TY"]+fd["TKY"]-1)*fd["TN"]*fd["TI"]*fd["TB"]
            #(TODOS) fd["TX"]//fd["WINO_X"]*fd["TY"]//fd["WINO_Y"]
            PE = (fd["TX"]//fd["WINO_TX"]) * (fd["TY"]//fd["WINO_TY"]) * fd["TN"] * fd["TI"] * fd["TB"] * (fd["WINO_TX"]+fd["TKX"]-1)*(fd["WINO_TY"]+fd["TKY"]-1)
            
            print("PE",PE,fd["TX"],fd)
            #if(flow_details["WINO_PRE_WEIGHT"] == True):
            #    PE = (fd["TX"]+fd["TKX"]-1)*(fd["TY"]+fd["TKY"]-1)*fd["TN"]*fd["TI"]
            #else:
            #    PE = fd["TKX"]*fd["TKY"]*fd["TI"]*fd["TN"]
             
            #PE = fd["TX"]*fd["TY"]*fd["TN"]*fd["TI"]*fd["TB"] #we essentially reduce the filter dimensions
            #need to increase the bit size
            #because winograd transform increases the precision requirements, look at Micro 23 paper from Huawei regarding this issue
            import wincnn
            wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6],
                    int(fd["WINO_TX"]), int(fd["TKX"]))
            MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])
            WINO_MAX_WEI_PRECISION_INT = MAX_WEI_PRECISION_INT + int(np.log2(MU))
            WINO_MAX_ACT_PRECISION_INT = MAX_ACT_PRECISION_INT + int(np.log2(MU))
            WINO_MAX_PSUM_PRECISION_INT = WINO_MAX_WEI_PRECISION_INT + WINO_MAX_ACT_PRECISION_INT
            WINO_MAX_ACC_PRECISION_INT = WINO_MAX_PSUM_PRECISION_INT + int(np.log2(MAX_I))




            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = PE*MAX_WEI_PRECISION // WEI_SYS_CYCLES
                ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
            else:
                if("WINO_PRE_WEIGHT" in fd and flow_details["WINO_PRE_WEIGHT"]):
                    WEI_BUF_DATUM = (fd["TX"]+fd["TKX"]-1)*(fd["TY"]+fd["TKY"]-1)*fd["TI"]*fd["TN"]*MAX_WEI_PRECISION // WEI_SYS_CYCLES#il y a une autre solution, ou on mets l'addition apres le buffer, mais ca vaut mieux de le placer avant
                    ACT_BUF_DATUM = (fd["TX"]+fd["TKX"]-1)*(fd["TY"]+fd["TKY"]-1)*fd["TI"]*fd["TB"]*MAX_ACT_PRECISION
                else:
                    WEI_BUF_DATUM = (fd["TKX"])*(fd["TKY"])*fd["TI"]*fd["TN"]*MAX_WEI_PRECISION //WEI_SYS_CYCLES #il y a une autre solution, ou on mets l'addition apres le buffer, mais ca vaut mieux de le placer avant
                    ACT_BUF_DATUM = (fd["TX"]+fd["TKX"]-1)*(fd["TY"]+fd["TKY"]-1)*fd["TI"]*fd["TB"]*MAX_ACT_PRECISION
                    
            PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION_INT #Look at NVDLA



            
        elif(flow_details["DATAFLOW"] == "DIAGONAL_FLOW_SYSTOLIC" or fd["DATAFLOW"] == "EYERISS"):
            #PE = fd[]*fd[]
            pass #Look at Eyeriss
        elif(flow_details["DATAFLOW"] == "IMG2COL_DIRECT"):
            PE = fd["TXY"]*fd["TN"]*fd["TKXKYI"]
            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
            else:
                WEI_BUF_DATUM = fd["TKXKYI"]*fd["TN"]*MAX_WEI_PRECISION
                ACT_BUF_DATUM = fd["TI"]*fd["TKXKYI"]*MAX_ACT_PRECISION
            PSUM_BUF_DATUM = fd["TXY"]*fd["TN"]*MAX_ACC_PRECISION
            #Look at Huawei's DaVinci Architecture


        ################## 
        #SPARSE DATAFLOWS
        #################
        elif(flow_details["DATAFLOW"] == "SPARSE_DIRECT"):
            SPARSE_ENABLE = True
            PE = flow_details["TX"]*fd["TKX"]*flow_details["TY"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]
            #(flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]
            #ignore multicast issues for now

            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                ACT_BUF_DATUM = PE*MAX_ACT_PRECISION                
            else:
                WEI_BUF_DATUM = fd["TKX"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]*MAX_WEI_PRECISION
                ACT_BUF_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]*MAX_ACT_PRECISION


            if(True):
                #Consider window size (i.e. compression ratio)
                #If would be naive to do the window size by
                # compress the window like multicasting, only move in the necessary for the number of windows we have
                window = 0
                loop_idx = [0]*len(fd["LOOP"])

                WINDOW_MAPPING = {
                        "B": MAX_B // fd["TB"] ,
                        "KX": MAX_KX // fd["TKX"] ,
                        "KY": MAX_KY // fd["TKY"],

                        "X": ((MAX_X + MAX_PADDING_X*2 - 1 + 1) // 1  ) // fd["TXX"],
                        "Y": ((MAX_Y + MAX_PADDING_Y*2 - 1 + 1) // 1  ) // fd["TYY"],
                        "N": MAX_N // fd["TNN"],
                        "I": MAX_I // fd["TII"],
                        "TNN": fd["TNN"] // fd["TN"],
                        "TII": fd["TII"] // fd["TI"],
                        "TXX": fd["TXX"] // fd["TX"],
                        "TYY": fd["TYY"] // fd["TY"],
                    }

                WINDOW_MAPPING_NO_SECONDARY_TILING = {
                        "X": ((MAX_X + MAX_PADDING_X*2 - 1 + 1) // 1  ) // fd["TX"],
                        "Y": ((MAX_Y + MAX_PADDING_Y*2 - 1 + 1) // 1  ) // fd["TY"],
                        "N": MAX_N // fd["TN"],
                        "I": MAX_I // fd["TI"],
                    }
                if(fd["TXX"] == -1):
                    WINDOW_MAPPING["X"] = WINDOW_MAPPING_NO_SECONDARY_TILING["X"]
                    WINDOW_MAP_Y = True
                else:
                    WINDOW_MAP_X = False
        
                if(fd["TYY"] == -1):
                    WINDOW_MAPPING["Y"] = WINDOW_MAPPING_NO_SECONDARY_TILING["Y"]
                    WINDOW_MAP_Y = True
                else:
                    WINDOW_MAP_Y = False

                if(fd["TNN"] == -1):
                    WINDOW_MAPPING["N"] = WINDOW_MAPPING_NO_SECONDARY_TILING["N"]
                    WINDOW_MAP_N = True
                else:
                    WINDOW_MAP_N = False
                        
                if(fd["TII"] == -1):
                    WINDOW_MAPPING["I"] = WINDOW_MAPPING_NO_SECONDARY_TILING["I"]
                    WINDOW_MAP_I = True
                else:
                    WINDOW_MAP_I = False
                        
                #print(MAX_N, MAX_I, MAX_X, MAX_Y)

                '''
                #we can only assume the worst case, the maximum layer for the loop
                #["TX","TY","KX","KY"]
                WEI_WINDOW = set()
                ACT_WINDOW = set()
                    
                while(window < flow_details["SPARSITY"]["WINDOW"]   ):
                    touched = fd["LOOP"][-1]   
                    loop_idx[-1] += 1
                    s = -1
                    for idx,li in enumerate(fd["LOOP"][::-1]):
                        if(loop_idx[s] >= WINDOW_MAPPING[li]):
                            loop_idx[s] = 0
                            s -= 1
                            loop_idx[s] += 1
                            touched = fd["LOOP"][s]
                            continue
                        else:
                            break

                    #print(loop_idx)
                    loop_idx_map = {}
                    for idx, li in enumerate(loop_idx):
                        loop_idx_map[fd["LOOP"][idx]] = li
                    #print(loop_idx)
                    #print(loop_idx_map)
                    #(TODOS) optimize the kernel with act interaction ...
                    ACT_WINDOW.add(str(    loop_idx_map["B"])+"_"+\
                                           str(    loop_idx_map["I"]*abs(fd["TII"])+loop_idx_map.get("TII",0))+"_"+\
                                           str(    loop_idx_map["KY"] + loop_idx_map["Y"]*abs(fd["TYY"])+loop_idx_map.get("TYY",0))+"_"+\
                                           str(    loop_idx_map["KX"] + loop_idx_map["X"]*abs(fd["TXX"])+loop_idx_map.get("TXX",0)))
                    WEI_WINDOW.add( str(    loop_idx_map["N"]*abs(fd["TNN"])+loop_idx_map.get("TNN",0))+"_"+\
                                           str(    loop_idx_map["I"]*abs(fd["TII"])+loop_idx_map.get("TII",0))+"_"+\
                                           str(    loop_idx_map["KY"])+"_"+\
                                           str(    loop_idx_map["KX"]))
                    window += 1
                '''


                #HACK IT, the WINDOW should not be fixed and should be by the user
                #WEI_WINDOW = 

                ACT_SPARSITY_MAP_DATUM = 0
                WEI_SPARSITY_MAP_DATUM = 0

                if(flow_details["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        WEI_SPARSITY_MAP_DATUM = PE        
                    else:
                        WEI_SPARSITY_MAP_DATUM = fd["TKX"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]

                if(flow_details["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        ACT_SPARSITY_MAP_DATUM = PE              
                    else:
                        ACT_SPARSITY_MAP_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]
                    
                print("ORIGINAL_ROW_LEN", WEI_BUF_DATUM, ACT_BUF_DATUM)
                if(fd["SPARSITY"]["WEI_COMPRESSION"] ):
                    WEI_BUF_DATUM *= flow_details["SPARSITY"]["WEI_WINDOW"] #// flow_details["SPARSITY"].get(" (TODOS) systolic WEI_WINDOW_LOAD
                    WEI_WINDOW = flow_details["SPARSITY"]["WEI_WINDOW"]
                else:
                    if(not flow_details["SPARSITY"]["WINDOW_MULTICAST"]):
                        WEI_BUF_DATUM *= flow_details["SPARSITY"]["WEI_WINDOW"]

                        WEI_WINDOW = flow_details["SPARSITY"]["WEI_WINDOW"]
                    else:
                        WEI_BUF_DATUM *= flow_details["SPARSITY"]["WEI_WINDOW"]#len(WEI_WINDOW)

                        WEI_WINDOW = flow_details["SPARSITY"]["WEI_WINDOW"]#len(WEI_WINDOW)
                    
                if(fd["SPARSITY"]["ACT_COMPRESSION"] ):
                    ACT_BUF_DATUM *= flow_details["SPARSITY"]["ACT_WINDOW"]
                    ACT_BUF_DATUM = flow_details["SPARSITY"]["ACT_WINDOW"]
                else:
                    if(not flow_details["SPARSITY"]["WINDOW_MULTICAST"]):
                        ACT_BUF_DATUM *= flow_details["SPARSITY"]["ACT_WINDOW"]
                        ACT_WINDOW = flow_details["SPARSITY"]["ACT_WINDOW"]
                    else:
                        ACT_BUF_DATUM *= flow_details["SPARSITY"]["ACT_WINDOW"]#len(ACT_WINDOW)
                        ACT_WINDOW = flow_details["SPARSITY"]["ACT_WINDOW"]#len(ACT_WINDOW)

                WEI_SPARSITY_MAP_DATUM = WEI_BUF_DATUM // MAX_WEI_PRECISION
                ACT_SPARSITY_MAP_DATUM = ACT_BUF_DATUM // MAX_ACT_PRECISION

                #print(ACT_BUF_DATUM)

                #how many unique tiles there are

                print(WEI_WINDOW, ACT_WINDOW)
                #print(WEI_WINDOW*WEI_BUF_DATUM, ACT_WINDOW*ACT_BUF_DATUM)
                #print(len(WEI_WINDOW), len(ACT_WINDOW))
                print("BUF_ROW_LEN", WEI_BUF_DATUM, ACT_BUF_DATUM)
                print("BUF_SPARSE_MAP", WEI_SPARSITY_MAP_DATUM, ACT_SPARSITY_MAP_DATUM)
                #print(WEI_BUF_DATUM*len(WEI_WINDOW), ACT_BUF_DATUM*len(ACT_WINDOW))
                #print("SPARSITY LEVEL", 1/flow_details["SPARSITY"]["WINDOW"])

                WEI_WINDOWS_DICT["WEI_WINDOW_"+str(fd["ID"])] = WEI_WINDOW
                ACT_WINDOWS_DICT["ACT_WINDOW_"+str(fd["ID"])] = ACT_WINDOW
                
                #exit()        
                    #sparsity va chercher dans l'ordre d'operation
                    #if(fd["LOOP"][-1] in ["I", "TII", "KX", "KY"]):
                    #NAIVE is WINDOW * fd["..."]...
                
            #(TODOS)
            PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION#(MAX_WEI_PRECISION+MAX_ACT_PRECISION)
            #else:
            #   PSUM_BUF_DATUM = fd["RAW_BLOCKS"]*fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION

        elif(flow_details["DATAFLOW"] == "SPARSE_DIRECT_LARGE_TILING"): 
            SPARSE_ENABLE = True

            WEI_WINDOW = 1
            ACT_WINDOW = 1

            tiling = flow_details["SPARSITY"]["SPARSE_TILING"]
            PE = tiling["TX"]*tiling["TKX"]*tiling["TY"]*tiling["TKY"]*tiling["TI"]*tiling["TN"]*tiling["TB"]
            #(flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]

            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = fd["TX"]*fd["TKX"]*fd["TY"]*fd["TKY"]*fd["TI"]*fd["TN"]*fd["TB"]*MAX_WEI_PRECISION
                ACT_BUF_DATUM = fd["TX"]*fd["TKX"]*fd["TY"]*fd["TKY"]*fd["TI"]*fd["TN"]*fd["TB"]*MAX_ACT_PRECISION                
            else:
                WEI_BUF_DATUM = fd["TKX"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]*MAX_WEI_PRECISION
                ACT_BUF_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]*MAX_ACT_PRECISION


            if(True):
                #Consider window size (i.e. compression ratio)
                #If would be naive to do the window size by
                # compress the window like multicasting, only move in the necessary for the number of windows we have
                window = 0
                loop_idx = [0]*len(fd["LOOP"])

                WINDOW_MAPPING = {
                        "B": MAX_B // fd["TB"] ,
                        "KX": MAX_KX // fd["TKX"] ,
                        "KY": MAX_KY // fd["TKY"],

                        "X": ((MAX_X + MAX_PADDING_X*2 - 1 + 1) // 1  ) // fd["TXX"],
                        "Y": ((MAX_Y + MAX_PADDING_Y*2 - 1 + 1) // 1  ) // fd["TYY"],
                        "N": MAX_N // fd["TNN"],
                        "I": MAX_I // fd["TII"],
                        "TNN": fd["TNN"] // fd["TN"],
                        "TII": fd["TII"] // fd["TI"],
                        "TXX": fd["TXX"] // fd["TX"],
                        "TYY": fd["TYY"] // fd["TY"],
                    }

                WINDOW_MAPPING_NO_SECONDARY_TILING = {
                        "X": ((MAX_X + MAX_PADDING_X*2 - 1 + 1) // 1  ) // fd["TX"],
                        "Y": ((MAX_Y + MAX_PADDING_Y*2 - 1 + 1) // 1  ) // fd["TY"],
                        "N": MAX_N // fd["TN"],
                        "I": MAX_I // fd["TI"],
                    }
                if(fd["TXX"] == -1):
                    WINDOW_MAPPING["X"] = WINDOW_MAPPING_NO_SECONDARY_TILING["X"]
                    WINDOW_MAP_Y = True
                else:
                    WINDOW_MAP_X = False
        
                if(fd["TYY"] == -1):
                    WINDOW_MAPPING["Y"] = WINDOW_MAPPING_NO_SECONDARY_TILING["Y"]
                    WINDOW_MAP_Y = True
                else:
                    WINDOW_MAP_Y = False

                if(fd["TNN"] == -1):
                    WINDOW_MAPPING["N"] = WINDOW_MAPPING_NO_SECONDARY_TILING["N"]
                    WINDOW_MAP_N = True
                else:
                    WINDOW_MAP_N = False
                        
                if(fd["TII"] == -1):
                    WINDOW_MAPPING["I"] = WINDOW_MAPPING_NO_SECONDARY_TILING["I"]
                    WINDOW_MAP_I = True
                else:
                    WINDOW_MAP_I = False
                        
                ACT_SPARSITY_MAP_DATUM = 0
                WEI_SPARSITY_MAP_DATUM = 0
                ACT_SPARSITY_MAP_DATUM = 0
                WEI_SPARSITY_MAP_DATUM = 0

                if(flow_details["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        WEI_SPARSITY_MAP_DATUM = PE        
                    else:
                        WEI_SPARSITY_MAP_DATUM = fd["TKX"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]

                if(flow_details["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        ACT_SPARSITY_MAP_DATUM = PE              
                    else:
                        ACT_SPARSITY_MAP_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]



                    
                if(flow_details["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        WEI_SPARSITY_MAP_DATUM = PE        
                    else:
                        WEI_SPARSITY_MAP_DATUM = fd["TKX"]*fd["TKY"]*flow_details["TI"]*flow_details["TN"]

                if(flow_details["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
                    if(not hardware_config["multicast"]):
                        ACT_SPARSITY_MAP_DATUM = PE              
                    else:
                        ACT_SPARSITY_MAP_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TB"]
                

                #WEI_SPARSITY_MAP_DATUM = WEI_BUF_DATUM // MAX_WEI_PRECISION
                #ACT_SPARSITY_MAP_DATUM = ACT_BUF_DATUM // MAX_ACT_PRECISION

                print(WEI_SPARSITY_MAP_DATUM)
                print(ACT_SPARSITY_MAP_DATUM)
                #exit(0)
                
            PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION#(MAX_WEI_PRECISION+MAX_ACT_PRECISION)
            #PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION
        elif(fd["DATAFLOW"] == "SPARSE_IMG2COL"):
            PE = fd["TXY"]*fd["TN"]*fd["TKXKYI"]
            if(not hardware_config["multicast"]):
                WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
            else:
                WEI_BUF_DATUM = fd["TKXKYI"]*fd["TN"]*MAX_WEI_PRECISION
                ACT_BUF_DATUM = fd["TI"]*fd["TKXKYI"]*MAX_ACT_PRECISION

            #sparsity will search in the timelooped order
            if(fd["LOOP"][-1] in ["KXKYI, TILE_KXKYI"]): 
                PSUM_BUF_DATUM = fd["TXY"]*fd["TN"]*MAX_ACC_PRECISION#(MAX_WEI_PRECISION+MAX_ACT_PRECISION)
            else:
                PSUM_BUF_DATUM = fd["RAW_BLOCKS"]*fd["TXY"]*fd["TN"]*MAX_ACC_PRECISION#MAX_PSUM_PRECISION              
            pass #Cambricon-X
        
        
        ################## 
        #SYSTOLIC DATAFLOWS (todos)
        ################## 
        elif(flow_details["DATAFLOW"] == "IMG2COL_1D_SYSTOLIC"):
            pass
        elif(fd["DATAFLOW"] == "IMG2COL_2D_SYSTOLIC"):
            pass
        #Look at Characterizing and Demystifying the Implicit Convolution Algorithm on Commercial Matrix-Multiplication Accelerators
        elif(flow_details["DATAFLOW"] == "DIRECT_1D_SYSTOLIC"): #only push the data in one at a time
            #systolic on input or weight
            PE = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*flow_details["TN"]*flow_details["TB"]
            
            if(fd["SYSTOLIC_VAR"] in ["TX", "TY", "TI", "TB", "TKX", "TKY"] and fd["SYSTOLIC"] == "ACT"):
                if(not hardware_config["multicast"]):
                    WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                    ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
                else:
                    WEI_BUF_DATUM = (fd["TKX"])*(fd["TKY"])*flow_details["TI"]*flow_details["TN"]*MAX_WEI_PRECISION 
                    ACT_BUF_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]*\
                                    flow_details["TB"]*MAX_ACT_PRECISION // fd[fd["SYSTOLIC_VAR"]]


                #does psum also change with systolic configurations ? (todos)
                PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION#(MAX_WEI_PRECISION+MAX_ACT_PRECISION) #c'est beaucoup plus moins parce qu'on le reduit apres l'arbre d'addition

            elif(fd["SYSTOLIC_VAR"] in ["TI", "TN", "TKX", "TKY"] and fd["SYSTOLIC"] == "WEI"):
                if(not hardware_config["multicast"]):
                    WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                    ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
                else:
                    WEI_BUF_DATUM = (fd["TKX"])*(fd["TKY"])*flow_details["TI"]*flow_details["TN"]*MAX_WEI_PRECISION // fd[fd["SYSTOLIC_VAR"]]
                    ACT_BUF_DATUM = (flow_details["TX"]+fd["TKX"]-1)*(flow_details["TY"]+fd["TKY"]-1)*flow_details["TI"]* \
                                    flow_details["TB"]*MAX_ACT_PRECISION

                PSUM_BUF_DATUM = fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]*MAX_ACC_PRECISION#MAX_PSUM_PRECISION #c'est beaucoup plus moins parce qu'on le reduit apres l'arbre d'addition

            else:
                print("INVALID SYSTOLIC CONFIGURATION !!")
            pass #Look at Google TPU


        
        elif(flow_details["DATAFLOW"] == "DIRECT_2D_SYSTOLIC"): #push the data in one at a time
            pass #Look at Google TPU or Thinker
        elif(flow_details["DATAFLOW"] == "DA_DIAN_NAO"): #some combination of inter-pe, with multicasting
            pass #DaDianNao

        ################## 
        #OTHER DATAFLOWS (todos)
        ##################
        elif(flow_details["DATAFLOW"] == "WINOGRAD_STRIDE2"):
            pass #look at the UManitoba Paper for winograd stride = 2
        elif(flow_details["DATAFLOW"] == "UNIVERSAL_RECONFIGURABLE_PE"):
            pass #this is something like a CRGA, we can change the dataflow but overhead is expected to be extremely high
        elif(flow_details["DATAFLOW"] == "some other flow ?"):
            pass
        else:
            print("other flow, there is strassen, img2col then matrix multiply, winograd, strassen what else ? ... todos")

        WEI_BUF_DATA.append(WEI_BUF_DATUM)
        ACT_BUF_DATA.append(ACT_BUF_DATUM)
        PSUM_BUF_DATA.append(PSUM_BUF_DATUM)

        if("SPARSE" in flow_details["DATAFLOW"]):
            WEI_SPARSE_MAP_BUF_DATA.append(WEI_SPARSITY_MAP_DATUM)
            ACT_SPARSE_MAP_BUF_DATA.append(ACT_SPARSITY_MAP_DATUM)
        
        PES.append(PE)

    
    #2. analyze fully connected dataflows
    if("LINEAR" in hardware_config["TILINGS"]):
        for flows in hardware_config["TILINGS"]["LINEAR"]:
            
            flow_details = hardware_config["TILINGS"]["LINEAR"][flows]
            fd = flow_details
            if(flow_details["DATAFLOW"] == "DIRECT"):
                PE = fd["TI"]*fd["TN"]*fd["TB"]

                if(not hardware_config["multicast"]):
                    WEI_BUF_DATUM = PE*MAX_WEI_PRECISION
                    ACT_BUF_DATUM = PE*MAX_ACT_PRECISION
                else:
                    WEI_BUF_DATUM = fd["TI"]*fd["TN"]*MAX_WEI_PRECISION
                    ACT_BUF_DATUM = fd["TI"]*fd["TB"]*MAX_ACT_PRECISION

                PSUM_BUF_DATUM = fd["TN"]*fd["TB"]*MAX_PSUM_PRECISION
                
            elif(fd["DATAFLOW"] == "STRASSEN"):
                pass
            elif(fd["DATAFLOW"] == "SPARSE"):
                pass
            else:
                print("other flow, there is ... ? what can we do with a linear?")

            
            if("SEPERATE_MODULE" in fd and fd["SEPERATE_MODULE"] == True):
                PES.append(PE)
                WEI_BUF_DATA.append(WEI_BUF_DATUM)
                ACT_BUF_DATA.append(ACT_BUF_DATUM)
                PSUM_BUF_DATA.append(PSUM_BUF_DATUM)
                
            else:
                LINEAR_PES.append(PE) #= [] #optional
                LINEAR_WEI_BUF_DATA.append(WEI_BUF_DATUM)
                LINEAR_ACT_BUF_DATA.append(ACT_BUF_DATUM)
                LINEAR_PSUM_BUF_DATA.append(PSUM_BUF_DATUM)            

    #3. analyze pooling dataflows
    if("POOL2D" in hardware_config["TILINGS"]):
        for flows in hardware_config["TILINGS"]["POOL2D"]:
            pass #todos

    #4. analyze other dataflows (i.e. something like transformer ? attention layer ?) [todos]

    #对齐 WITH BIT_PRECISION (bug)
    REQUIRED_PES = max(PES)
    REQUIRED_WEI_BUF_DATA = ((max(WEI_BUF_DATA) + MAX_WEI_PRECISION - 1)//MAX_WEI_PRECISION)*MAX_WEI_PRECISION
    REQUIRED_ACT_BUF_DATA = ((max(ACT_BUF_DATA) + MAX_ACT_PRECISION - 1)//MAX_ACT_PRECISION)*MAX_ACT_PRECISION
    REQUIRED_PSUM_BUF_DATA = ((max(PSUM_BUF_DATA) + MAX_PSUM_PRECISION - 1)//MAX_PSUM_PRECISION)*MAX_PSUM_PRECISION

    REQUIRED_WEI_SPARSE_MAP_BUF_DATA = max(WEI_SPARSE_MAP_BUF_DATA)
    REQUIRED_ACT_SPARSE_MAP_BUF_DATA = max(ACT_SPARSE_MAP_BUF_DATA)

    REQUIRED_LINEAR_PES = max(LINEAR_PES)
    REQUIRED_LINEAR_WEI_BUF_DATA = ((max(LINEAR_WEI_BUF_DATA)+ MAX_WEI_PRECISION - 1)//MAX_WEI_PRECISION)*MAX_WEI_PRECISION
    REQUIRED_LINEAR_ACT_BUF_DATA = ((max(LINEAR_ACT_BUF_DATA) + MAX_ACT_PRECISION - 1)//MAX_ACT_PRECISION)*MAX_ACT_PRECISION
    REQUIRED_LINEAR_PSUM_BUF_DATA = ((max(LINEAR_PSUM_BUF_DATA)    + MAX_PSUM_PRECISION - 1)//MAX_PSUM_PRECISION)*MAX_PSUM_PRECISION

    REQUIRED_POOL_PES = max(POOL_PES)
    REQUIRED_POOL_WEI_BUF_DATA = max(POOL_WEI_BUF_DATA)
    REQUIRED_POOL_ACT_BUF_DATA = max(POOL_ACT_BUF_DATA)
    REQUIRED_POOL_PSUM_BUF_DATA = max(POOL_PSUM_BUF_DATA)


    DEFAULT_ELEMENT_UNITS = REQUIRED_PSUM_BUF_DATA//MAX_PSUM_PRECISION


    #####ELEMENT UNIT

    MAX_ACT_PRECISION = max(SUPPORTED_ACT_PRECISIONS_FP+ SUPPORTED_ACT_PRECISIONS_INT)
    MIN_ACT_PRECISION = min(SUPPORTED_ACT_PRECISIONS_FP+ SUPPORTED_ACT_PRECISIONS_INT)

    ELEMENT = hardware_config.get("ELEMENT_UNIT", {})
    BN_UNIT = ELEMENT.get("BATCH_NORM_UNIT", 0)
    ACTIVATION_UNIT = ELEMENT.get("ACTIVATION_UNIT", 0)
    RELU_UNIT = ELEMENT.get("RELU_UNIT", 0)
    ADD_UNIT = ELEMENT.get("ADD_UNIT", 0)
    MULT_SCALE_UNIT = ELEMENT.get("MULT_SCALE_UNIT", 0)



    MAX_ELEMENT_UNITS = max(BN_UNIT, ACTIVATION_UNIT, RELU_UNIT, ADD_UNIT, MULT_SCALE_UNIT)


    #####VECTOR UNIT (TODOS)

    



    '''
        #Les limites (une unite c'est une calcul pour une cycle)
        "WEI_L1_MIN":   max(WEI_L1_MIN),
        "WEI_FIFO_MIN": max(WEI_FIFO_MIN),#pour dma
        "ACT_L1_MIN":   max(ACT_L1_MIN),
        "ACT_FIFO_MIN": max(ACT_FIFO_MIN),#pour dma
        "PSUM_L1_MIN":  max(PSUM_L1_MIN),
        "PSUM_FIFO_MIN": max(PSUM_FIFO_MIN),#pour dma
    '''

    MACRO_CFG = {
        "REQUIRED_PES": REQUIRED_PES,
        "MAX_WEI_PRECISION": MAX_WEI_PRECISION,
        "MAX_ACT_PRECISION": MAX_ACT_PRECISION,
        "MIN_WEI_PRECISION": MAX_WEI_PRECISION,
        "MIN_ACT_PRECISION": MAX_ACT_PRECISION,

        "MAX_OUT_PRECISION": MAX_OUT_PRECISION,
        "MIN_OUT_PRECISION": MIN_OUT_PRECISION,

        "MAX_ELEMENT_UNITS":MAX_ELEMENT_UNITS,
        
        "MAX_WEI_PRECISION_INT": MAX_WEI_PRECISION_INT,
        "MIN_WEI_PRECISION_INT": MIN_WEI_PRECISION_INT,
        "MAX_ACT_PRECISION_INT": MAX_ACT_PRECISION_INT,
        "MIN_ACT_PRECISION_INT": MIN_ACT_PRECISION_INT,
        "MAX_OUT_PRECISION_INT": MAX_ACT_PRECISION_INT,
        "MIN_OUT_PRECISION_INT": MIN_ACT_PRECISION_INT,

        
        "MAX_WEI_PRECISION_FP": MAX_WEI_PRECISION_FP,
        "MIN_WEI_PRECISION_FP": MIN_WEI_PRECISION_FP,
        "MAX_ACT_PRECISION_FP": MAX_ACT_PRECISION_FP,
        "MIN_ACT_PRECISION_FP": MIN_ACT_PRECISION_FP,

        "MAX_PRECISION_FP": MAX_PRECISION_FP,

        "MAX_PSUM_PRECISION": MAX_PSUM_PRECISION,

        "MAX_PSUM_PRECISION_INT": MAX_PSUM_PRECISION_INT,
        "MAX_PSUM_PRECISION_FP": MAX_PSUM_PRECISION_FP,

        "MAX_ACC_PRECISION":MAX_ACC_PRECISION,
        "MAX_ACC_PRECISION_INT":MAX_ACC_PRECISION_INT,
        "MAX_ACC_PRECISION_FP":MAX_ACC_PRECISION_FP,


        #MACROS
        "CONV2D_OP": 0,
        "LINEAR_OP": 1,
        "TRANSFORMER_OP":   2,
        #OTHER OPS? POOL DOESN"T NEED THIS? pool only make sense in the context of a PDP (i.e. 没有乘法器呀。。。)

        
        
        #todos (les limites)
        #"MAX_STRIDE":     (MAX_STRIDE <= 0)*16   + (MAX_STRIDE > 0)*MAX_STRIDE ,
        #"MAX_KX":         (MAX_KX <= 0)*16   + (MAX_KX > 0)*MAX_KX ,
        #"MAX_KY":         (MAX_KY <= 0)*16   + (MAX_KY > 0)*MAX_KY ,
        #"MAX_X":        (MAX_X <= 0)*16   + (MAX_X > 0)*MAX_X ,
        #"MAX_Y":   (MAX_Y <= 0)*16   + (MAX_Y > 0)*MAX_Y ,
        #"MAX_N":  (MAX_N <= 0)*16   + (MAX_N > 0)*MAX_N ,
        #"MAX_I":   (MAX_I <= 0)*16   + (MAX_I > 0)*MAX_I ,
        #"MAX_B":   (MAX_B <= 0)*16   + (MAX_B > 0)*MAX_B ,
        #"MAX_PADDING_X":   (MAX_PADDING_X <= 0)*16   + (MAX_PADDING_X > 0)*MAX_PADDING_X ,
        #"MAX_PADDING_Y":   (MAX_PADDING_Y <= 0)*16   + (MAX_PADDING_Y > 0)*MAX_PADDING_Y ,
        "MAX_STRIDE": MAX_STRIDE,
        "MAX_KX": MAX_KX,
        "MAX_KY": MAX_KY,
        "MAX_X": MAX_X,
        "MAX_Y": MAX_Y,
        "MAX_N": MAX_N,
        "MAX_I":MAX_I,
        "MAX_B":MAX_B,
        "MAX_PADDING_X": MAX_PADDING_X,
        "MAX_PADDING_Y": MAX_PADDING_Y,



        "MAX_STRIDE_LOG": int(np.ceil(np.log2(MAX_STRIDE))+1),
        "MAX_KX_LOG": int(np.ceil(np.log2(MAX_KX))+1),
        "MAX_KY_LOG": int(np.ceil(np.log2(MAX_KY))+1),
        "MAX_X_LOG": int(np.ceil(np.log2(MAX_X))+1),
        "MAX_Y_LOG": int(np.ceil(np.log2(MAX_Y))+1),
        "MAX_N_LOG": int(np.ceil(np.log2(MAX_N))+1),
        "MAX_I_LOG": int(np.ceil(np.log2(MAX_I))+1),
        "MAX_B_LOG": int(np.ceil(np.log2(MAX_B))+1),
        "MAX_PADDING_X_LOG": int(np.ceil(np.log2(MAX_PADDING_X))+1),
        "MAX_PADDING_Y_LOG": int(np.ceil(np.log2(MAX_PADDING_Y))+1),


        "WEI_BUF_DATA": REQUIRED_WEI_BUF_DATA,
        "ACT_BUF_DATA": REQUIRED_ACT_BUF_DATA,
        "PSUM_BUF_DATA": REQUIRED_PSUM_BUF_DATA,

    }

    if SPARSE_ENABLE:
        MACRO_CFG.update({
            "WEI_SPARSITY_MAP_BUF_DATA":  REQUIRED_WEI_SPARSE_MAP_BUF_DATA,
            "ACT_SPARSITY_MAP_BUF_DATA":  REQUIRED_ACT_SPARSE_MAP_BUF_DATA,
            "WEI_WINDOW": WEI_WINDOW,
            "ACT_WINDOW": ACT_WINDOW,
            #..?
        })

        MACRO_CFG.update(ACT_WINDOWS_DICT)
        MACRO_CFG.update(WEI_WINDOWS_DICT)

    #################################################################################
    #   DYNAMIC ALLOCATION OF WEIGHT AND ACT BUFFERS (L1)
    ## EITHER:
    ## 1. Give WEI_BUFFER_SIZE, will get rows dynamically
    ## 2. Give WEI_ROWS       , will get buffer size dynamically
    ## 3. Give Largest dimensions of the convolution, will get buffer rows and rows dynamically
    ## 如果有多个选最大的
    #WEI
    if("WEI_BUFFER" in hardware_config):
        MACRO_CFG["WEI_BUF_ROWS"] = hardware_config["WEI_BUFFER"] // REQUIRED_WEI_BUF_DATA
        
    if("WEI_BUFFER_ROWS" in hardware_config):
        if("WEI_BUF_ROWS" in MACRO_CFG):
            if(MACRO_CFG["WEI_BUF_ROWS"] < hardware_config["WEI_BUFFER_ROWS"]):
                MACRO_CFG["WEI_BUF_ROWS"] = hardware_config["WEI_BUFFER_ROWS"]
                                 
    if("WEI_BUFFER_ON_MAX_LAYER" in hardware_config
       and hardware_config["WEI_BUFFER_ON_MAX_LAYER"]):
        from utils import calculate_wei_reuse
        MIN_WEI_BUF_ROWS = calculate_wei_reuse(hardware_config)
        if(MACRO_CFG["WEI_BUF_ROWS"] < MIN_WEI_BUF_ROWS):
                MACRO_CFG["WEI_BUF_ROWS"] = MIN_WEI_BUF_ROWS
    #MAKE TAIJI
    MACRO_CFG["WEI_BUF_ROWS_LOG2"] = int(np.log2(MACRO_CFG["WEI_BUF_ROWS"])) + 1
    MACRO_CFG["WEI_BUF_ROWS"] = int(2**MACRO_CFG["WEI_BUF_ROWS_LOG2"])


    #PSUM
    if("PSUM_BUFFER" in hardware_config):
        MACRO_CFG["PSUM_BUF_ROWS"] = hardware_config["PSUM_BUFFER"] // REQUIRED_PSUM_BUF_DATA
        
    if("PSUM_BUFFER_ROWS" in hardware_config):
        if("PSUM_BUF_ROWS" in MACRO_CFG):
            if(MACRO_CFG["PSUM_BUF_ROWS"] < hardware_config["PSUM_BUFFER_ROWS"]):
                MACRO_CFG["PSUM_BUF_ROWS"] = hardware_config["PSUM_BUFFER_ROWS"]
                                 
    if("PSUM_BUFFER_ON_MAX_LAYER" in hardware_config
       and hardware_config["PSUM_BUFFER_ON_MAX_LAYER"]):
        from utils import calculate_psum_reuse
        MIN_BUF_ROWS = calculate_psum_reuse(hardware_config)
        if(MACRO_CFG["PSUM_BUF_ROWS"] < MIN_BUF_ROWS):
                MACRO_CFG["PSUM_BUF_ROWS"] = MIN_BUF_ROWS
    #MAKE TAIJI
    MACRO_CFG["PSUM_BUF_ROWS_LOG2"] = int(np.log2(MACRO_CFG["PSUM_BUF_ROWS"])) + 1
    MACRO_CFG["PSUM_BUF_ROWS"] = int(2**MACRO_CFG["PSUM_BUF_ROWS_LOG2"])


    #calculate_psum_reuse

    MACRO_CFG.update({  
        "ACT_BUF_ROWS": hardware_config["ACT_BUFFER"] // REQUIRED_ACT_BUF_DATA ,

        "ACT_BUF_ROWS_LOG2": int(np.log2(hardware_config["ACT_BUFFER"] // REQUIRED_ACT_BUF_DATA )),
        #"PSUM_BUF_ROWS": hardware_config["PSUM_BUFFER"] // REQUIRED_PSUM_BUF_DATA,

       # "PSUM_BUF_ROWS_LOG2": int(np.log2(hardware_config["PSUM_BUFFER"] // REQUIRED_PSUM_BUF_DATA)),
    })


    #"L2_WEI_BUF_DATA": hardware_config["WEI_BUF_DATA"],
    #L2 configs, what if L2 buf data size != L1 buf data size ? systolic shift possibilities
    MACRO_CFG.update({
        
        "L2_WEI_BUF_ROWS": hardware_config["L2_WEI_BUFFER_SIZE"] // REQUIRED_WEI_BUF_DATA ,
        "L2_WEI_BUF_ROWS_LOG2": int(np.log2(hardware_config["L2_WEI_BUFFER_SIZE"] // REQUIRED_WEI_BUF_DATA )),

        "L2_ACT_BUF_ROWS": hardware_config["L2_ACT_BUFFER_SIZE"] // REQUIRED_ACT_BUF_DATA ,
        "L2_ACT_BUF_ROWS_LOG2": int(np.log2(hardware_config["L2_ACT_BUFFER_SIZE"] // REQUIRED_ACT_BUF_DATA )),
    })

    if(WINOGRAD_EN):
        MACRO_CFG.update({
            "MU":0,
            "WINO_MAX_WEI_PRECISION_INT":MAX_WEI_PRECISION_INT,
            "WINO_MAX_ACT_PRECISION_INT":MAX_ACT_PRECISION_INT,
            "WINO_MAX_PSUM_PRECISION_INT":MAX_PSUM_PRECISION_INT,
            "WINO_MAX_ACC_PRECISION_INT":MAX_ACC_PRECISION_INT,

            "WINO_MAX_WEI_PRECISION":MAX_WEI_PRECISION_INT,
            "WINO_MAX_ACT_PRECISION":MAX_ACT_PRECISION_INT,
            "WINO_MAX_PSUM_PRECISION":MAX_PSUM_PRECISION_INT,
            "WINO_MAX_ACC_PRECISION":MAX_ACC_PRECISION_INT,
        })


    print(MACRO_CFG)

    for k in MACRO_CFG:
        #we skip writing some of the features
        #if(k not in ["SUPPORTED_WEI_PRECISIONS", "SUPPORTED_ACT_PRECISIONS"]):
        f.write("`define\t" + k + "\t" + str(MACRO_CFG[k])+"\n")

    print("\n// GEN_MACR_FILE - DONE\n")
    f.close()

    return MACRO_CFG

def gen_hardware(hardware_config, meta_config):
    print("\n")
    print("\t\t\t\t\t\t//////////////////////////////////////////////////////////////")
    print("\t\t\t\t\t\t// DNN Inference Machine Summa Unum Minus Unum (DIMSUMU)        //")
    print("\t\t\t\t\t\t// ACCESS / HKUST Software                                  //")
    print("\t\t\t\t\t\t// 2024 07 11 - Version 1                                   //")
    print("\t\t\t\t\t\t// Open-License GPL V3.0                                    //")
    print("\t\t\t\t\t\t// Feel free to use this software for research and          //")
    print("\t\t\t\t\t\t// open-source purposes, please reference this work if you  //")
    print("\t\t\t\t\t\t// use it in your research                                  //")
    print("\t\t\t\t\t\t// The code is not for commercial purposes, please contact  //")
    print("\t\t\t\t\t\t// the authors of the code for commercial reasons           //")
    print("\t\t\t\t\t\t// 多谢!                                                     //")
    print("\t\t\t\t\t\t//////////////////////////////////////////////////////////////\n")
    
    print(hardware_config)
    MACRO_CFG = gen_macro_file(hardware_config, meta_config)
    gen_buffers(hardware_config, meta_config, MACRO_CFG)
    gen_multiplier(hardware_config, meta_config, MACRO_CFG) #ok (7-18-2024)
    gen_pe_array(hardware_config, meta_config, MACRO_CFG)
    gen_pe_input_mapping(hardware_config, meta_config, MACRO_CFG)
    gen_pe_output_mapping(hardware_config, meta_config, MACRO_CFG)

    gen_accum(hardware_config, meta_config, MACRO_CFG)

    #fix for now (TODOS)
    #if(hardware_config["MULT_TYPE_INT"] =="BASIC"):
    #from generators.gen_addr_cnt import gen_addr_cnt
    #from generators.gen_addr_cnt_v2 import gen_addr_cnt
    

    from generators.gen_addr_cnt_v3 import gen_addr_cnt
    gen_addr_cnt(hardware_config, meta_config, MACRO_CFG)

    gen_elt_unit(hardware_config, meta_config, MACRO_CFG)
    
    #else:
    #    from generators.gen_addr_cnt import gen_addr_cnt
    #    gen_addr_cnt(hardware_config, meta_config, MACRO_CFG)
    #gen_core_v1(hardware_config, meta_config, MACRO_CFG)
    gen_core_v2(hardware_config, meta_config, MACRO_CFG)
        
if __name__ == "__main__":

    ###############################################################################################################################################
    #####################################################改改改改改改改改#############################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################


    hardware_config = {

        #Constraint: require the min to be factor of all the other precisions, i.e. 4 --> 8, 16, 32. 8, 16, 24, 32 and so forth. We don't allow like 9 bits, 11 bit precisions.
        #"SUPPORTED_WEI_PRECISIONS": [8, 16],#weight precisions supported
        #"SUPPORTED_ACT_PRECISIONS": [8, 16],#activation precisions supported, applies to conv, activations, pooling, transformer inputs
        "SUPPORTED_WEI_DTYPES": ["INT4", "INT8","INT16", "FP16", "FP32"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_ACT_DTYPES": ["INT4", "INT8", "INT16", "FP16", "FP32"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants
        #https://blog.csdn.net/tMb8Z9Vdm66wH68VX1/article/details/133834344

        
        #"PE_NO": #This number is the max of the tilings produced below

        #############SPARSITY############### 
        "ACT_ZERO_GATING": False,
        "WEI_ZERO_GATING": False,

        ##############PE AND MULTIPLIER TYPE########################
        "MULT_TYPE_INT": "ADAPTIVE_TXTY_TN",#ADAPTIVE_TXTY_TN is like outer product, ADAPTIVE_TI is like inner product
        ##ADAPTIVE_TXTY_TN#BASIC is verilog *, ADAPTIVE/BitFusion, BitSerial is from Stripes work, BitPragmatic is from Pragmatic Work, Bit
        "MULT_TYPE_FP": "BASIC", #BASIC is verilog *, ADAPTIVE (meaning if max precision is 16, want 8 bit, will have double throughput)

        #(TODOS) new framework
        # "MULT_TYPE_INT": {"type": "ADAPTIVE", "DIMENSIONS": "TXTY_TN"}
        # "MULT_TYPE_FLOAT": {"type": "BitSerial", "VARIANT": "BITPRAGMATIC"}
        # "MULT_TYPE_INT": {"type": "BASIC"}

        
        ##############TILING and ALGORITHMIC DATAFLOW###############
        "TILINGS": {
            #Convolution of 2D type
            "CONV2D": {
                "DEFAULT": {

                    "DATAFLOW": "DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.
                    "SYSTOLIC_VAR": "TX", #TILING hardware level
                    "SYSTOLIC": "ACT", #ACT, WEI

                    "TX": 1, "TY": 1, "TKX": 1, "TKY": 1, "TI": 8, "TN": 8, "TB":1,
                    "TXX": 4, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],

                    #les limites
                    "PE_BUF": "NONE" #NONE, BUFFER, PING_PONG

                },

                '''
                "DEFAULT": {
                    "DATAFLOW": "SYSTOLIC_1D",
                    "SYSTOLIC_VAR": ["TX", "TY", "TI"], ...

                    #Systolic必须是有BUFFER的或者传不过去
                    "PE_BUF": "BUFFER" #BUFFER, PING_PONG
                }
                '''
                "ic == 3": {
                    "DATAFLOW": "DIRECT",
                    "TX": 1, "TY": 1, "TKX":1, "TKY":1, "TI":3, "TN":16, "TB":1,
                    "TXX":-1, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "X", "Y", "KX", "KY","I", ],

                    #additional constraints
                    "MAX_STRIDE": 2,
                    "MAX_KX": 3, 
                    "MAX_KY": 3,
                    "MAX_X": 16,
                    "MAX_Y": 16,
                    "MAX_N": 16,
                    "MAX_I": 3,
                    "MAX_B": 1,
                    "MAX_PADDING_X": 2,
                    "MAX_PADDING_Y": 2,

                    "PE_BUF": "NONE" #NONE, BUFFER, PING_PONG

                },

                #constraint is that TX==TY > kx size
                "kx == 3 && ky == 3": {
                    "DATAFLOW": "WINOGRAD_STRIDE_1",#Pour Winograd, nous nous supposeons que les poids sont deja calcules par l'ordi, les activations sont calcule en ligne
                    "TX": 4, "TY": 4, "TI": 2, "TN": 2, "TB": 1,
                    "TXX":-1, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "I", "X", "Y"],

                    
                    "PE_BUF": "NONE" #NONE, BUFFER, PING_PONG
                    
                }

                
            },
            #
            "LINEAR": {
                "DEFAULT": {
                    "DATAFLOW": "DIRECT",
                    "TI": 8, "TN": 8, "TB": 1,
                    "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "I"],
                    "SEPERATE_MODULE": False, #True is a Vector Unit
                },#or strassen .. ?
            },

            "POOL2D": {
                "DEFAULT": {
                    "TX": 1, "TY": 1, "TKX": 3, "TKY": 3, "TN": 4,
                    "SEPERATE_MODULE": False, #True or False, True is a PDP
                }
            },

        },




        ##############################################
        # DATAFLOW RELATED PARAMETERS
        ##############################################
        "multicast": True,
        ##############################################################
        ###############################################
        # L1 RELATED PARAMETERS
        ###############################################

            #BUFFER (Here, buffer is the total buffer size. Rows are calculated dynamically, depending on the PE format which depends on the tiling)
            "WEI_BUFFER": 16*1024*8,#4KBytes
            "WEI_BANKS": 8, #For saving power and energy
            "ACT_BUFFER": 16*1024*8,#4KBytes
            "ACT_BANKS": 8, #For saving power and energy
            "PSUM_BUFFER":16* 1024*8, #4KBytes
            "PSUM_BANKS": 8,


            #general constraints
            #CONSTRAINTS FOR MAX SIZE, if is -1, will default to 16
            #和缓存可能有约束性质的冲突(todos)
            "MAX_STRIDE": 5,
            "MAX_KX": 7,
            "MAX_KY": 7,
            "MAX_X": 1024,
            "MAX_Y": 1024,
            "MAX_N": 256,
            "MAX_I": 256,
            "MAX_B": 8,
            "MAX_PADDING_X": 4,
            "MAX_PADDING_Y": 4,

            "GEN_CONSTRAINTS": {
                "MAX_STRIDE": 5,
                "MAX_KX": 7,
                "MAX_KY": 7,
                "MAX_X": 1024,
                "MAX_Y": 1024,
                "MAX_N": 256,
                "MAX_I": 256,
                "MAX_B": 8,
                "MAX_PADDING_X": 4,
                "MAX_PADDING_Y": 4,
            },

            #GROUPS? DILATION?
            
            #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
            "DDR_WIDTH": 128,
    }

    


    '''
    runtime_config = {
        "DDR_CLK": 40, #in ns
        "CORE_CLK": 40, #in ns

        "Operation": "CONV2D", #CONV2D, CONV2D_ACT, CONV2D_ACT_POOL2D, POOL2D
        "Operation_Params": {
            "KX": 3,
            "KY": 3,
            "X": 128,
            "Y": 128,
            "I": 3,
            "N": 64,
            "B": 1
        },
        "WEIGHTS": [],
        "INPUTS": [],
        "WEI_PREC": "INT4",
        "ACT_PREC": "INT8",
        

        "BURST": 4,
        "DRAM_DELAY": 4,



       # "I2XY_OPTIMIZATION": True, #for the compiler to do, NVDLA does this. TI (i.e. 32) >> 3, so TI --> TX, TI --> TY,   不用改架构, 虽然是TI=32, 实际是TX = 4, TY = 8 
    }
    '''


    hardware_config = {
        "SUPPORTED_WEI_DTYPES": ["INT4", "INT8","INT16", "FP16", "FP32"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_ACT_DTYPES": ["INT4", "INT8", "INT16", "FP16", "FP32"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants

        #############SPARSITY###############
        "ACT_ZERO_GATING": False,
        "WEI_ZERO_GATING": False,

        ##############PE AND MULTIPLIER TYPE########################
        "MULT_TYPE_INT": "ADAPTIVE_TXTY_TN",#ADAPTIVE_TXTY_TN is like outer product, ADAPTIVE_TI is like inner product
        ##ADAPTIVE_TXTY_TN#BASIC is verilog *, ADAPTIVE/BitFusion, BitSerial is from Stripes work, BitPragmatic is from Pragmatic Work, Bit
        "MULT_TYPE_FP": "BASIC", #BASIC is verilog *, ADAPTIVE (meaning if max precision is 16, want 8 bit, will have double throughput)

        #(TODOS) new framework
        # "MULT_TYPE_INT": {"type": "ADAPTIVE", "DIMENSIONS": "TXTY_TN"}
        # "MULT_TYPE_FLOAT": {"type": "BitSerial", "VARIANT": "BITPRAGMATIC"}
        # "MULT_TYPE_INT": {"type": "BASIC"}
        "REMOVE_DUPLICATE_ROWS": False,
        
        ##############TILING and ALGORITHMIC DATAFLOW###############
        "TILINGS": {
            #Convolution of 2D type
            "CONV2D": {
                "DEFAULT": {

                    "DATAFLOW": "DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.
                    "TX": 2, "TY": 1, "TKX": 1, "TKY": 1, "TI": 8, "TN": 8, "TB":1,
                    "TXX": 4, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],

                    #les limites
                    "PE_BUF": "NONE" #NONE, BUFFER, PING_PONG

                },
               "X == 5 && Y == 5": {
                    "MING": "SYSTOLIC_FLOW_1",
                    "DATAFLOW": "SYSTOLIC_1D_A", #Systolic 1D for the activations
                    #SYSTOLIC_2D_AW for act + wei
                    #SYSTOLIC_3D  for act + wei + psum

                    #For now, efficiency reasons, only support move in one direction (X, Y)
                    "SYSTOLIC_VAR": "X", #or I no advantage tho for I? #Only X and Y directions can be systolic moving, (todos) X2,Y2 for skipping connections (i.e. useful for stride = 2?)
                    #"SHIFT_COLS": 8, #SHIFT_COLS, SHIFT_ROWS for 2D
                    
                    #not worth searching in the I direction ? (no large save in bandwidth)

                    #"SCRATCHPAD_ROWS_ACT": 24, #if the re-use of a systolic move (KX<->X or KY<->Y) is below this, we can use the values from the scratchpad, otherwise will have to read from the L1. -1 means no scratchpad only shifting from L1.
                    #"SCRATCHPAD_ROWS_WEI": 24, #WEI valid only for SYSTOLIC_*W or SYSTOLIC3D, ACT valid only for SYSTOLIC_*A or SYSTOLIC3D
                    #SCRATCHPAD rows will be determined dynamically by MAX dimensions of the NN
                    
                    "TX": 2, "TKX":1, "TY": 1,"TKY":1, "TI":3, "TN":16, "TB":1,
                    "TXX":-1, "TYY":-1, "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "X", "Y", "KX", "KY", "I",],
                    #Systolic必须是有BUFFER的或者传不过去
                    "PE_BUF": "BUFFER", #BUFFER, PING_PONG,

                    "REMOVE_DUPLICATE_ROWS": True, #when shifting, x+kx may repeat (i.e. x = 1, kx = 2, x = 2, kx = 1, x = 3, kx = 0), these are equivalent rows remove from buffer
                },
                
                "i == 3": {
                    "DATAFLOW": "DIRECT",
                    "TX": 2, "TY": 2, "TKX":1, "TKY":1, "TI":3, "TN":16, "TB":1,
                    "TXX":-1, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "X", "Y", "KX", "KY","I", ],

                    #additional constraints
                    "MAX_STRIDE": 2,
                    "MAX_KX": 3, 
                    "MAX_KY": 3,
                    "MAX_X": 16,
                    "MAX_Y": 16,
                    "MAX_N": 32,
                    "MAX_I": 3,
                    "MAX_B": 1,
                    "MAX_PADDING_X": 2,
                    "MAX_PADDING_Y": 2,



                    "PE_BUF": "NONE" #NONE, BUFFER, PING_PONG

                },

                #constraint is that TX==TY > kx size
                "kx == 4 && ky == 4": {
                    "DATAFLOW": "WINOGRAD_STRIDE_1",#Pour Winograd, nous nous supposeons que les poids sont deja calcules par l'ordi, les activations sont calcule en ligne
                    "TX": 2, "TY": 2, "TI": 1, "TN": 1, "TB": 1, #"TKX": 4, "TKY": 4, #WINOGRAD no KXKY, les dimensions pour les filtres
                    "TXX":-1, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "I", "X", "Y"],

                    "WINO_PRE_WEIGHT": True, #Moins d'additions pour G trans mais plus de transfers (trade-off)
                    
                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG

                    "SUPPORTED_WEI_DTYPES": ["INT8"],#the pre-weights will be INT8, post-weights will be longer (can be up to INT16!)
                    #(todos)
                    
                }

                
            },
            #
            "LINEAR": {
                "DEFAULT": {
                    "DATAFLOW": "DIRECT",
                    "TI": 8, "TN": 8, "TB": 1,
                    "TII": -1, "TNN": -1,
                    "LOOP": ["B", "N", "I"],
                    "SEPERATE_MODULE": False, #True is a Vector Unit
                },#or strassen .. ?
            },

            "POOL2D": {
                "DEFAULT": {
                    "TX": 1, "TY": 1, "TKX": 3, "TKY": 3, "TN": 4,
                    "SEPERATE_MODULE": False, #True or False, True is a PDP
                }
            },

        },


        ##############################################
        # DIRECT DATAFLOW RELATED PARAMETERS
        ##############################################
        "multicast": True,
        ##############################################################
        ###############################################
        # L1 RELATED PARAMETERS
        ###############################################

            #BUFFER (Here, buffer is the total buffer size. Rows are calculated dynamically, depending on the PE format which depends on the tiling)
            "WEI_BUFFER": 16*1024*8,#4KBytes
            "WEI_BANKS": 8, #For saving power and energy
            "ACT_BUFFER": 16*1024*8,#4KBytes
            "ACT_BANKS": 8, #For saving power and energy
            "PSUM_BUFFER":16* 1024*8, #4KBytes
            "PSUM_BANKS": 8,

            "ALIGNED_L1_DATA": False,
    
            #general constraints
            #CONSTRAINTS FOR MAX SIZE, if is -1, will default to 16
            #和缓存可能有约束性质的冲突(todos)
            "MAX_STRIDE": 5,
            "MAX_KX": 7,
            "MAX_KY": 7,
            "MAX_X": 1024,
            "MAX_Y": 1024,
            "MAX_N": 256,
            "MAX_I": 256,
            "MAX_B": 8,
            "MAX_PADDING_X": 4,
            "MAX_PADDING_Y": 4,
            #GROUPS? DILATION?
            
            #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
            "DDR_WIDTH": 128,
            "DDR_MAX_BURST": 4,
    }

    meta_config = {
        "dossier": "MyAccelerator"
    }
    ###############################################################################################################################################
    #####################################################改改改改改改改改#############################################################################
    ###############################################################################################################################################
    ###############################################################################################################################################




    gen_hardware(hardware_config, meta_config)
