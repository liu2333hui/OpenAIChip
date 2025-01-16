from utils import order_dataflows
from generators.gen_multiplier import analyze_floating, analyze_int
import wincnn





from utils import gen_index, GET_LOOP_FILTERS



def get_prec(runtime_config):
    if("FP" in runtime_config["WEI_PREC"]):
        floating = True
        wei_prec = analyze_floating([runtime_config["WEI_PREC"]])[0][-1]
    else:
        floating = False
        wei_prec = analyze_int([runtime_config["WEI_PREC"]])[0]

    if("FP" in runtime_config["ACT_PREC"]):
        floating = True
        act_prec = analyze_floating([runtime_config["ACT_PREC"]])[0][-1]
    else:
        floating = False
        act_prec = analyze_int([runtime_config["ACT_PREC"]])[0]
        
    if(floating):
        psum_prec = act_prec
    else:
        psum_prec = act_prec + wei_prec
    
    #todos
    #todos
    return wei_prec ,act_prec, psum_prec, floating

def trouve_df(hardware_config, runtime_config):
   #1. 获得全部的流程
    dataflows = order_dataflows(hardware_config)

    #print(dataflows)
        


    #2. 符合哪一个流程？
    for df in dataflows:
        satisfy = True
        for cond in df.split("&&"):
            if("==" in cond):
                t = cond.split("==")
            elif("<=" in cond):
                t = cond.split("<=")
            elif(">=" in cond):
                t = cond.split(">=")
            elif(">" in cond):
                t = cond.split(">")
            elif("<" in cond):
                t = cond.split("<")
            else:
                t = cond
                
            if(len(t) == 2):
                yi = t[0].strip().upper()
                if(yi in runtime_config["Operation_Params"]):

                    if("==" in cond):
                        if(runtime_config["Operation_Params"][yi] == int(t[1])):
                            satisfy = True
                        else:
                            satisfy = False
                            break
                    elif("<=" in cond):
                        if(runtime_config["Operation_Params"][yi] <= int(t[1])):
                            satisfy = True
                        else:
                            satisfy = False
                            break
                    elif(">=" in cond):
                        if(runtime_config["Operation_Params"][yi] >= int(t[1])):
                            satisfy = True
                        else:
                            satisfy = False
                            break
                    elif("<" in cond):
                        if(runtime_config["Operation_Params"][yi] < int(t[1])):
                            satisfy = True
                        else:
                            satisfy = False
                            break
                    elif(">" in cond):
                        if(runtime_config["Operation_Params"][yi] > int(t[1])):
                            satisfy = True
                        else:
                            satisfy = False
                            break
                        
                else:
                    satisfy = False
                    break
                    
            else:
                satisfy = False
                break



        #auxillary conditions
        if(df in hardware_config["TILINGS"]["CONV2D"]):
            if("WINOGRAD_STRIDE_1" == hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"]):
                if(runtime_config["Operation_Params"]["STRIDE"] == 1):
                    satisfy = satisfy
                else:
                    satisfy = False

            elif("WINOGRAD_STRIDE_2" == hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"]):
                if(runtime_config["Operation_Params"]["STRIDE"] == 2):
                    satisfy = satisfy
                else:
                    satisfy = False

                
        if(satisfy == True):
            #print("Satisfy " , df, "dataflow")
            break

    #print("Satisfy " , df, "dataflow")

    if(satisfy == False):
        if("DEFAULT" in dataflows):
            return "DEFAULT"
        else:
            return dataflows[-1]
        #return "DEFAULT"
    else:
        return df



def get_dataflow_meta(hardware_config, df):
    if(df in hardware_config["TILINGS"]["CONV2D"]):
        return hardware_config["TILINGS"]["CONV2D"][df]
    elif(df in hardware_config["TILINGS"]["LINEAR"]):
        return hardware_config["TILINGS"]["LINEAR"][df]

###############################


#generate ddr files
def gen_ddr(hardware_config, runtime_config, meta_config):
    pass


#(todos) floating ?
#for testing only
#generate the testcase data for the L1 buffer
def gen_buf(hardware_config, runtime_config, meta_config):
    

    

    
    import os
    if (not os.path.isdir(meta_config["dossier"])):
        os.mkdir(meta_config["dossier"])
    if( not os.path.isdir(meta_config["dossier"] + "/" + meta_config["tc"])):
        os.mkdir(meta_config["dossier"] + "/" + meta_config["tc"])

        
    ########################
    #1. identify which layer we are in whether it is first layer or not
    df = trouve_df(hardware_config, runtime_config)

    print(df)

    ####################
    #2. also 打印输入数据
    if(runtime_config["FIRST_LAYER"]):
        pass

    #######################
    #3. 准备数据再=在格式下
    df_d = get_dataflow_meta(hardware_config, df)

    print(df_d)
    print(df)
    
    if("WINOGRAD" in df_d["DATAFLOW"]):
        if(df == "DEFAULT"):
            pass
        else:
            df_d["TKX"] = int(df.split("kx")[1].split()[1])
            df_d["TKY"] = int(df.split("ky")[1].split()[1])





    
    ##########################
    #3.0.1 timeplexed loop for weight
    ################################
    '''
    for var in df_d["LOOP"]:
        #FIXED_LOOP_ORDER = ["B", "KX", "KY", "X", "Y", "N", "I",
        #            "nn", "yy", "xx", "ii"]
        if(var == "X" and df_d["TXX"] == -1):
            f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
        elif(var == "Y" and df_d["TYY"] == -1):
            f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
        elif(var == "N" and df_d["TNN"] == -1):
            f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
        elif(var == "I" and df_d["TII"] == -1):
            f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
        else:
            f.write("    "*depth + MAPPING[var]+"\n")
        depth += 1
    '''


        

    ##############################
    #3..0.2 phys loop
    ##############################
    
    #debug purpose
    ddr_line_break = '\\n' #should be \\n
    ddr_data_break = '' #should be ''





    #Special case: X-Y may have duplicate rows due to conv windows
    #"REMOVE_DUPLICATE_ROWS": False,
    if("REMOVE_DUPLICATE_ROWS" in df_d):
        REMOVE_DUPLICATE_ROWS = df_d["REMOVE_DUPLICATE_ROWS"]
    else:
        REMOVE_DUPLICATE_ROWS= hardware_config["REMOVE_DUPLICATE_ROWS"]

    SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
        WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)

    ########################
    #3.0 准备工作
    #CONV MAPPING

    WULI_MAPPING = {
        "TX": "for x in range(xx, min(xx+TX+TKX-1, (X+PADDING*2)//STRIDE)):",
        "TY": "for y in range(yy, min(yy+TY+TKY-1, (Y+PADDING*2)//STRIDE)):",
        
        "TX_FULL": "for x in range(xx, min(xx+TX+TKX-1, (X+PADDING*2)//STRIDE)):",
        "TY_FULL": "for y in range(yy, min(yy+TY+TKY-1, (Y+PADDING*2)//STRIDE):",
        "KX": "for kx in range(0, KX):",
        "KY": "for ky in range(0, KY):",
        "TKX": "for kx in range(kkx, min(kkx + TKX, KX)):",
        "TKY": "for ky in range(kky, min(kky + TKY, KY)):",
        "TI" : "for i in range(ii, min(ii+TI, I)):",
        "TN":  "for n in range(nn, min(nn+TN, N)):",
        "TB":  "for b in range(bb, min(bb +TB, B)):",

        "WINO_KX": "for kx in range(0,KX+TX-1):",
        "WINO_KY": "for ky in range(0,KY+TY-1):",
        "WINO_X": "TODOS",
        "WINO_Y": "TODOS",

        
    }


    #TEMPORAL MPAPPING below
    #LIM_X = "X+PADDING*2"
    #LIM_Y = "Y+PADDING*2"
    MAPPING = {
        "B": "for bb in range(0, B , TB):",
        "KX": "for kkx in range(0, KX, TKX):",
        "KY": "for kky in range(0, KY, TKY):",

        "X": "for xxx in range(0, "+LIM_X+", TXX):",
        "Y": "for yyy in range(0, "+LIM_Y+", TYY):",
        "N": "for nnn in range(0, N, TNN):",
        "I": "for iii in range(0, I , TII):",

        "TNN": "for nn in range(nnn, min(nnn+TNN, N), TN):",
        "TII": "for ii in range(iii, min(iii+TII, I), TI):",
        "TXX": "for xx in range(xxx, min(xxx+TXX, "+LIM_X+" ) , TX):",
        "TYY": "for yy in range(yyy, min(yyy+TYY, "+LIM_Y+" ), TY):",
    }

    MAPPING_NO_SECONDARY_TILING = {
        "X": "for xx in range(0, "+LIM_X+", TX):",
        "Y": "for yy in range(0, "+LIM_Y+", TY):",
        "N": "for nn in range(0, N, TN):",
        "I": "for ii in range(0, I , TI):",
    }


    ####################
    #3.0 权重数据生成器
    #####################
    f = open(meta_config["dossier"]+"/"+meta_config["tc"] + "/dataflow_gen_tc.py", "w")
    f.write("import numpy as np\n")
    f.write("import wincnn\n")
    f.write("def dataflow_gen_tc(hardware_config, runtime_config):\n")



    ##########################
    #3.1 macros
    ##########################
    depth = 1
    for k in hardware_config:
        if(k == "TILINGS"):
            continue
        f.write("    "*depth + k  + '=hardware_config["'+k+'"]\n')
    for k in runtime_config:
        f.write("    "*depth + k  + '=runtime_config["'+k+'"]\n')
    for k in runtime_config["Operation_Params"]:
        f.write("    "*depth + k  + '=runtime_config["Operation_Params"]["'+k+'"]\n')
    for k in df_d:
        if(k[0] == "T"):
            f.write("    "*depth + k  + '='+str(df_d[k])+'\n')
        else:
            f.write("    "*depth + k  + '="'+str(df_d[k])+'"\n')
    wei_prec, act_prec, psum_prec, floating = get_prec(runtime_config)
    f.write("    "*depth + "weight_precision = " + str(wei_prec)+"\n")
    f.write("    "*depth + "act_precision = " + str(act_prec)+"\n")
    f.write("    "*depth + "psum_precision = " + str(psum_prec)+"\n")        

    ###########################
    #3.2 wei+act
    #########################

    #Output datasets for the testbenches
    f.write("    "*depth + 'wei_data_f = open(\'' +  meta_config["dossier"]+"/"+meta_config["tc"]  +"/weights.txt'"  +  ',"w")' +  '\n')
    f.write("    "*depth + 'act_data_f = open(\'' +     meta_config["dossier"] +"/"+meta_config["tc"] +"/activation.txt'"  + ',"w")' +  '\n')
    
    #(any other things to out? such as Sigmoid/Tanh parameters, bias ?)



    f.write("    "*depth + "WEI_LINE = 1\n")
    f.write("    "*depth + "ACT_LINE = 1\n")
    


    f.write("    "*depth + "cycle = 0\n")
    f.write("    "*depth + "act_ddr_idx = 0\n")
    f.write("    "*depth + "wei_ddr_idx = 0\n")
    f.write("    "*depth + "kkx = 0\n") #kkx init
    f.write("    "*depth + "kky = 0\n")

    ##########################
    #3.2.1 for winograd only
    ##########################
    if("WINOGRAD_STRIDE_1" == df_d["DATAFLOW"]): #assume is multicast
        if(df_d["WINO_PRE_WEIGHT"]):
            f.write("    "*depth + "wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6], WINO_TX, KX)\n")
            f.write("    "*depth + "MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])\n")
            f.write("    "*depth + "wino_G = np.array(MU*wino_G).astype('int')\n")
            f.write("    "*depth + "wino_A = np.array(wino_AT).transpose()\n")
            f.write("    "*depth + "wino_GT = np.array(wino_G).transpose()\n")
            f.write("    "*depth + "wino_B = np.array(wino_BT).transpose()\n")
            f.write("    "*depth + "print(wino_G.reshape((1,1,wino_G.shape[0], wino_G.shape[1])))\n")
            f.write("    "*depth + "POST_WEIGHTS = np.matmul(np.matmul(wino_G.reshape((1,1,wino_G.shape[0], wino_G.shape[1])),WEIGHTS),\
                wino_GT.reshape((1,1,wino_GT.shape[0], wino_GT.shape[1])))\n")
            f.write("    "*depth + "POST_WEIGHTS = POST_WEIGHTS.astype('int')\n")
            f.write("    "*depth + "print(POST_WEIGHTS)\n")

            f.write("    "*depth + "weight_precision = int(weight_precision + np.log2(MU)+1)\n")

    ##########################
    #3.2.2 for sparsity only
    ##########################
    #SPARSITY CONDITIONS
    #SPARSE_MAP
    wei_encoding = "NONE"
    act_encoding = "NONE"
    if("SPARSE" in df_d["DATAFLOW"]):
        sp_meta = df_d["SPARSITY"]

        wei_encoding = sp_meta.get("WEI_ENCODING","NONE")
        act_encoding = sp_meta.get("ACT_ENCODING","NONE")

        if(wei_encoding == "SPARSE_MAP"):
            f.write("    "*depth + 'wei_sparse_map_f = open(\'' + meta_config["dossier"]+"/"+meta_config["tc"]  +"/weights_sparse_map.txt'"  +  ',"w")' +  '\n')
        else:
            pass

        if(act_encoding == "SPARSE_MAP"):
            f.write("    "*depth + 'act_sparse_map_f = open(\'' + meta_config["dossier"] +"/"+meta_config["tc"] +"/activation_sparse_map.txt'"  + ',"w")' +  '\n')
        else:
            pass
    print(wei_encoding, act_encoding)
    #exit()


    print(df_d["LOOP"])

    #####################################
    #写宽度
    ###########################################
    multicast = {
                    "TI": "TI",
                    "TX": "(TX+TKX-1)",
                    "TY": "(TY+TKY-1)",
                    "TN": "TN",
                    "TB": "TB",
                    "TKX":"TKX",
                    "TKY": "TKY",
                    "KX": "KX",
                    "KY": "KY",
                    "WINO_KX": "(TX+TKX-1)",
                    "WINO_KY": "(TY+TKY-1)",
                    "TX_FULL": "(TX+TKX-1)",
                    "TY_FULL": "(TY+TKY-1)",
                }


    multicast_line = {
                    "TI": "TI",
                    "TX": "(TX+TKX-1)",
                    "TY": "(TY+TKY-1)",
                    "TN": "TN",
                    "TB": "TB",
                    "TKX":"TKX",
                    "TKY": "TKY",
                    "KX": "KX",
                    "KY": "KY",
                    "WINO_KX": "(TX+TKX-1)",
                    "WINO_KY": "(TY+TKY-1)",
                    "TX_FULL": "(TX+TKX-1)",
                    "TY_FULL": "(TY+TKY-1)",
                }

    
    #SYSTOLIC 改变ACT_LINE, WEI_LINE
    
    wl = df_d["SYSTOLIC"]["WEIGHT_LOAD"]

    ge = []
    #SYSTOLIC 的改变
    if(wl["TKX"] != -1):
        multicast_line["TKX"] = str(wl["TKX"])
        ge.append("TKX")
    if(wl["TKY"] != -1):
        multicast_line["TKY"] = str(wl["TKY"])
        ge.append("TKY")
    if(wl["TN"] != -1):
        multicast_line["TN"] = str(wl["TN"])
        ge.append("TN")
    if(wl["TI"] != -1):
        multicast_line["TI"] = str(wl["TI"])
        ge.append("TI")

    #Reorder the WULI_LOOP_WEI to make systolic
    for wlw in WULI_LOOP_WEI:
        if(wlw not in ge):
            ge.append(wlw)

    WULI_LOOP_WEI = ge
    #print(WULI_LOOP_WEI)
    #exit(0)

    if(hardware_config["multicast"] == True):
        f.write("    "*depth + "WEI_LINE *= weight_precision*"+ "*".join([multicast_line[w] for w in WULI_LOOP_WEI])+"\n")
    else:
        f.write("    "*depth + "WEI_LINE *= weight_precision*"+ "*".join(WULI_LOOP_WEI)+"\n")



    ########################L2 -> L1 ratio########
    f.write("    "*depth + "WEI_LINE *= " + str(hardware_config["WEI_L2_L1_BW_RATIO"])+"\n")

    ##############################################

    ###########################################            
    #写wei
    #######################################
    cache_depth = depth

    

    if("SPARSE_DIRECT" == df_d["DATAFLOW"]):

        from Generate_Verilog import gen_macro_file

        MACRO_CFG = gen_macro_file(hardware_config, meta_config)

        f.write("    "*depth + "WEI_LINE *= "+str(MACRO_CFG["WEI_WINDOW_"+str(df_d["ID"])])+" \n")
        f.write("    "*depth + "ACT_LINE *= "+str(MACRO_CFG["ACT_WINDOW_"+str(df_d["ID"])])+"\n")

    if True:    
        f.write("    "*depth + "wei_ddr_idx = 0\n")
        for var in df_d["LOOP"]:
            if(not var in SHI_LOOP_WEI):
                continue
            if(var == "X" and df_d["TXX"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "Y" and df_d["TYY"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "N" and df_d["TNN"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "I" and df_d["TII"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            else:
                f.write("    "*depth + MAPPING[var]+"\n")
            depth += 1

        inner_cache_depth = depth
        #f.write("    "*depth + "wei_dim = np.zeros("+ "*".join(WULI_LOOP_WEI)+").astype('int')\n")
        if(hardware_config["multicast"] == True):
            f.write("    "*depth + "wei_dim = np.zeros("+ "*".join([multicast[w] for w in WULI_LOOP_WEI])+").astype('int')\n")
        else:
            f.write("    "*depth + "wei_dim = np.zeros("+ "*".join(WULI_LOOP_WEI)+").astype('int')\n")
        for var in WULI_LOOP_WEI:
            f.write("    "*depth + WULI_MAPPING[var]+"\n")
            depth += 1

        

        #f.write("    "*depth + INNER_WEI + "\n")
        #f.write("    "*depth + "wei_ddr_idx += weight_precision\n")
        #f.write("    "*depth + "if(wei_ddr_idx >= WEI_LINE):\n")
        #depth += 1
        f.write("    "*depth + "wei_dim["+gen_index(WULI_LOOP_WEI, df_d)+"] = " + INNER_WEI + "\n")
        #f.write("    "*depth + "wei_data_f.write('"+ddr_line_break+"')"+"\n")
        #f.write("    "*depth + "wei_ddr_idx = 0\n")
        #depth -= 1
        #f.write("    "*depth + "else:\n")
        #depth += 1
        #f.write("    "*depth + INNER_WEI + "\n")   
        depth = inner_cache_depth
        #f.write("    "*depth + "print(wei_dim)\n")
        f.write("    "*depth + "for wei in wei_dim:\n")
        depth += 1

        #WEI INNER LOOP ORDER --> TI, TN, KY, KX
        #for var in WULI_LOOP_WEI:
        #    f.write("    "*depth + WULI_MAPPING[var]+"\n")
        #    depth += 1
            
        #f.write("    "*depth + "wei = wei_dim["+gen_index(WULI_LOOP_WEI, df_d)+"]\n")
        f.write("    "*depth + "wei_ddr_idx += weight_precision\n")

        #if wei<0, 需要改成正的
        f.write("    "*depth + "if(wei < 0 ):\n")
        f.write("    "*(depth+1) + "wei = wei + (1<<weight_precision) \n")

        f.write("    "*depth + "wei_data_f.write(hex(wei)[2:].zfill(weight_precision//4))\n")
        if(wei_encoding == "SPARSE_MAP"):
            f.write("    "*depth + 'wei_sparse_map_f.write(str(int(wei != 0))) \n') #(TODOS) for floating point? use epsilon criterion? check the mantissa
                
        f.write("    "*depth + "if(wei_ddr_idx >= WEI_LINE):\n")
        depth += 1

        f.write("    "*depth + "wei_data_f.write('"+ddr_line_break+"')"+"\n")
        if(wei_encoding == "SPARSE_MAP"):
            f.write("    "*depth + "wei_sparse_map_f.write('"+ddr_line_break+"')"+"\n")
     
        f.write("    "*depth + "wei_ddr_idx = 0\n")


        depth -= 1
        f.write("    "*depth + "else:\n")
        depth += 1
        f.write("    "*depth + "pass\n") 
        depth -= 1
        depth = inner_cache_depth
        
        depth = cache_depth

    #############################
    #写act如果有的话
    ##############################
        multicast = {
                    "TI": "TI",
                    "TX": "(TX+TKX-1)",
                    "TY": "(TY+TKY-1)",
                    "TN": "TN",
                    "TB": "TB",
                    "TKX":"TKX",
                    "TKY": "TKY",
                    "KX": "KX",
                    "KY": "KY",
                    "WINO_KX": "(TX+TKX-1)",
                    "WINO_KY": "(TY+TKY-1)",
                    "TX_FULL": "(TX+TKX-1)",
                    "TY_FULL": "(TY+TKY-1)",
                }


    #SYSTOLIC 改变ACT_LINE, WEI_LINE
    al = df_d["SYSTOLIC"]["ACT_LOAD"]
    ge = []
    #SYSTOLIC 的改变
    #SYSTOLIC 的改变
    if(al["TX"] != -1):
        multicast["TX"] = str(al["TX"])
        ge.append("TX")
    if(al["TY"] != -1):
        multicast["TY"] = str(al["TY"])
        ge.append("TY")
    if(al["TB"] != -1):
        multicast["TB"] =  str(al["TB"])
        ge.append("TB")
    if(al["TKY"] != -1):
        multicast["TKY"] = str(al["TKY"])
        ge.append("TKY")
    if(al["TKX"] != -1):
        multicast["TKX"] = str(al["TKX"])
        ge.append("TKX")
    
    #Reorder the WULI_LOOP_WEI to make systolic
    for wlw in WULI_LOOP_ACT:
        if(wlw not in ge):
            ge.append(wlw)

    WULI_LOOP_ACT = ge

    if(hardware_config["multicast"] == True):
        f.write("    "*depth + "ACT_LINE *= act_precision*"+"*".join([multicast[w] for w in WULI_LOOP_ACT])+"\n") 
    else:
        f.write("    "*depth + "ACT_LINE *= act_precision*"+"*".join(WULI_LOOP_ACT)+"\n")





    f.write("    "*depth + "act_ddr_idx = 0\n")
    #f.write("    "*depth + "wei_ddr_idx = 0\n")
    f.write("    "*depth + "kkx = 0\n") #kkx init
    f.write("    "*depth + "kky = 0\n")
    f.write("    "*depth + "act_ddr_idx = 0\n")


    #SYSTOLIC INTER-PE SETTINGS
    if(df_d.get("SYSTOLIC", {}).get("ACT_X_INTER", "NONE") != "NONE"):
        #remove KX from the activation loop
        if("KX" in SHI_LOOP_ACT):
            SHI_LOOP_ACT.remove("KX")
        if("TKX" in WULI_LOOP_ACT):
            WULI_LOOP_ACT.remove("TKX")

        LIM_X = "(X+PADDING*2)//STRIDE"
        ##LIM_Y = "Y+PADDING*2"
        MAPPING["X"]   =  "for xxx in range(0, "+LIM_X+", TXX):"
        MAPPING_NO_SECONDARY_TILING["X"] = "for xx in range(0, "+LIM_X+", TX):"
        
    #added REMOVE_DUPLICATE_ROWS
    if(REMOVE_DUPLICATE_ROWS):
        f.write("    "*depth + "visited = [False]*(X*Y*I)\n")
    if(runtime_config["FIRST_LAYER"]):
        for var in df_d["LOOP"]:
            if(not var in SHI_LOOP_ACT):
                continue
            if(var == "X" and df_d["TXX"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "Y" and df_d["TYY"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "N" and df_d["TNN"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            elif(var == "I" and df_d["TII"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"\n")
            else:
                f.write("    "*depth + MAPPING[var]+"\n")
            depth += 1

        inner_cache_depth = depth
        f.write("    "*depth + "kx = kkx\n")
        f.write("    "*depth + "ky = kky\n")
        if(hardware_config["multicast"] == True):

            f.write("    "*depth + "act_dim = np.zeros("+ "*".join([multicast[w] for w in WULI_LOOP_ACT])+").astype('int')\n")
        else:
            f.write("    "*depth + "act_dim = np.zeros("+ "*".join(WULI_LOOP_ACT)+").astype('int')\n")


        #f.write("    "*depth + "print(xx,yy,kkx,kky,ii,bb)\n")

        if(REMOVE_DUPLICATE_ROWS):
            f.write("    "*depth + "if(visited[ii*X*Y+(xx+kkx)*Y + (yy+kky)]):\n")
            f.write("    "*depth + "    continue\n")
        for var in WULI_LOOP_ACT:
            f.write("    "*depth + WULI_MAPPING[var]+"\n")
            depth += 1
        f.write("    "*depth + "if((x+kx) >= X or (y+ky) >= Y):\n") #TEMPORARY HACK (TODOS) to take care of edge cases
        f.write("    "*(depth+1)+"continue\n")
        #f.write("    "*depth + "if(visited[(x+kx)*Y + (y+ky)]):\n")
        #f.write("    "*depth + "    continue\n")
        #f.write("    "*depth + "print(x, y, kx, ky)\n")
        f.write("    "*depth + "tempus = " + INNER_ACT + "\n")

        f.write("    "*depth + "act_dim["+gen_index(WULI_LOOP_ACT, df_d)+"] = " + INNER_ACT + "\n")  
        #f.write("    "*depth + "print(act_dim, x, y, kx, ky, x+kx, y+ky)\n")
        depth = inner_cache_depth
        #f.write("    "*depth + "print(act_dim, x, y, kx, ky, x+kx, y+ky)\n")
        f.write("    "*depth + "for act in act_dim:\n")
        depth += 1
        f.write("    "*depth + "act_ddr_idx += act_precision\n")

        #if act<0, 需要改成正的
        f.write("    "*depth + "if(act < 0 ):\n")
        f.write("    "*(depth+1) + "act = act + (1<<act_precision) \n")
                
        f.write("    "*depth + "act_data_f.write(hex(act)[2:].zfill(act_precision//4))\n")
        if(act_encoding == "SPARSE_MAP"):
            f.write("    "*depth + 'act_sparse_map_f.write(str(int(act != 0))) \n') #(TODOS) for floating point? use epsilon criterion? check the mantissa
           
        
        f.write("    "*depth + "if(act_ddr_idx >= ACT_LINE):\n")
        depth += 1
        #f.write("    "*depth + "act_data_f.write()\n")
        f.write("    "*depth + "act_data_f.write('"+ddr_line_break+"')"+"\n")
        if(act_encoding == "SPARSE_MAP"):
            f.write("    "*depth + "act_sparse_map_f.write('"+ddr_line_break+"')"+"\n")

 
 
            
        f.write("    "*depth + "act_ddr_idx = 0\n")
        depth -= 1
        f.write("    "*depth + "else:\n")
        depth += 1
        f.write("    "*depth + "pass\n")
        depth -= 1
        #f.write("    "*depth + "visited[(x+kx)*Y + (y+ky)] = True\n")
        depth -= 1
        if(REMOVE_DUPLICATE_ROWS):
            f.write("    "*depth + "visited[ii*X*Y + (xx+kx)*Y + (yy+ky)] = True\n")
        depth = cache_depth


    depth = 1
    #if(runtime_config["FIRST_LAYER"]):


    #Trailing zeros
    f.write("    "*depth + "while(act_ddr_idx < ACT_LINE):\n")
    depth += 1
    f.write("    "*depth + "act_data_f.write(hex(0)[2:].zfill(act_precision//4))\n")
    if(act_encoding == "SPARSE_MAP"):
        f.write("    "*depth + 'act_sparse_map_f.write(str(0)) \n')
    f.write("    "*depth + "act_ddr_idx += act_precision\n")
    depth -= 1

    f.write("    "*depth + "while(wei_ddr_idx < WEI_LINE):\n")
    depth += 1
    f.write("    "*depth + "wei_data_f.write(hex(0)[2:].zfill(weight_precision//4))\n")
    if(wei_encoding == "SPARSE_MAP"):
        f.write("    "*depth + 'wei_sparse_map_f.write(str(0)) \n')
    f.write("    "*depth + "wei_ddr_idx += weight_precision\n")
    depth -= 1

        

    f.write("    "*depth + "act_data_f.close()\n")    
    f.write("    "*depth + "wei_data_f.close()\n")
    if(wei_encoding == "SPARSE_MAP"):
        f.write("    "*depth + 'wei_sparse_map_f.close()\n')
    else:
        pass

    if(act_encoding == "SPARSE_MAP"):
        f.write("    "*depth + 'act_sparse_map_f.close()\n')
    else:
        pass

    f.close()

    ###################################
    #4. 执行
    ###################################     
    import sys
    from pathlib import Path
    sys.path.append(meta_config["dossier"]+"/"+meta_config["tc"])
    from utils import order_dataflows

    from dataflow_gen_tc import dataflow_gen_tc
    
    #meta_config["dossier"]+"/"+meta_config["tc"] + "/dataflow_gen.py
    dataflow_gen_tc(hardware_config, runtime_config)


#Ceshi
def L1_simulator():
    pass


def DMA_simulator():
    pass

#Zhu
if __name__ == "__main__":
    
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
                    "TX": 2, "TY": 1, "TKX": 1, "TKY": 1, "TI": 1, "TN": 1, "TB":1,
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



                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                    "REMOVE_DUPLICATE_ROWS": True,
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


    import numpy as np
    
    IN_CHANNELS = 3
    OUT_CHANNELS = 1
    KX = 3
    KY = 3
    INPUT_X = 6
    INPUT_Y = 6
    INPUT_BATCH = 1
    
    act = np.arange(0, IN_CHANNELS*INPUT_X*INPUT_Y*INPUT_BATCH).reshape([INPUT_BATCH, IN_CHANNELS, INPUT_X, INPUT_Y])
    weight = np.arange(0, IN_CHANNELS*KX*KY*OUT_CHANNELS).reshape([OUT_CHANNELS, IN_CHANNELS, KX, KY])

    runtime_config = {
        "DDR_CLK": 40, #in ns
        "CORE_CLK": 40, #in ns

        "Operation": "CONV2D", #CONV2D, CONV2D_ACT, CONV2D_ACT_POOL2D, POOL2D
        "Operation_Params": {
            "KX": KX,
            "KY": KY,
            "X": INPUT_X,
            "Y": INPUT_Y,
            "I": IN_CHANNELS,
            "N": OUT_CHANNELS,
            "B": INPUT_BATCH,

            "STRIDE": 1,
            "PADDING": 0,
        },
        #If given will be the actual weights, otherwise is random
        #Can be sparsely random or densely random
        "WEIGHTS": weight,#
        "INPUTS": act,#CHW
        "WEI_PREC": "INT8",
        "ACT_PREC": "INT8",
        

        "BURST": 4,
        "DRAM_DELAY": 4,


        "FIRST_LAYER": True
       # "I2XY_OPTIMIZATION": True, #for the compiler to do, NVDLA does this. TI (i.e. 32) >> 3, so TI --> TX, TI --> TY,   不用改架构, 虽然是TI=32, 实际是TX = 4, TY = 8 
    }



    meta_config = {
        "dossier": "MyAccelerator",
        "tc": "tc1",
    }



    ########################################################################################

    gen_buf(hardware_config, runtime_config, meta_config)
    
    
    
