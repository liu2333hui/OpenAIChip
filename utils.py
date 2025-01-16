def MAX_ADAPTIVE_RATIOS(hardware_config):
    w_ratios = []
    a_ratios = []
    for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
        for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:            
            if("INT" in wei_type and "INT" in act_type):
                wei_prec = wei_type.split("INT")[1]
                act_prec = act_type.split("INT")[1]
                #w_ratio = max_wei_prec // int(wei_prec)
                #a_ratio = max_act_prec // int(act_prec)
                w_ratios.append(int(wei_prec))
                a_ratios.append(int(act_prec))
    return max(w_ratios)//min(w_ratios), max(a_ratios)//min(a_ratios)

def SYSTOLIC_WEIGHT_LOAD_CYCLES(hardware_config, df_d):
    SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
        WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)

    wl = df_d["SYSTOLIC"]["WEIGHT_LOAD"]

    #SYSTOLIC 的改变
    #SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(df_d)
    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKX"] != -1):
        WEI_TKX = df_d["TKX"] // df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKX"]
    else:
        WEI_TKX = 1

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKY"] != -1):
        WEI_TKY = df_d["TKY"] // df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKY"]
    else:
        WEI_TKY = 1

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TN"] != -1):
        WEI_TN = df_d["TN"] // df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TN"]
    else:
        WEI_TN = 1

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TI"] != -1):
        WEI_TI = df_d["TI"] // df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TI"]
    else:
        WEI_TI = 1

    SYS_CYCLES = WEI_TKX*WEI_TKY*WEI_TN*WEI_TI
    return SYS_CYCLES    


def SYSTOLIC_WEIGHT_TILES(harware_config, df_d):

    df_d_copy = {}

    df_d_copy.update(df_d)
    
    #SYSTOLIC 的改变
    #SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(df_d)
    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKX"] != -1):
        df_d_copy["TKX"] = df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKX"]

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKY"] != -1):
        df_d_copy["TKY"] = df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TKY"]

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TN"] != -1):
        df_d_copy["TN"] = df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TN"]

    if(df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TI"] != -1):
        df_d_copy["TI"] = df_d["SYSTOLIC"]["WEIGHT_LOAD"]["TI"]

    #SYS_CYCLES = WEI_TKX*WEI_TKY*WEI_TN*WEI_TI
    return df_d_copy    
    

def SYSTOLIC_ACT_LOAD_CYCLES(hardware_config, df_d):
    #TODOS
    return {}

def SYSTOLIC_WEI_LOOP_ORDER(hardware_config, df_d):

    SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
        WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)

    wl = df_d["SYSTOLIC"]["WEIGHT_LOAD"]

    ge = []
    #SYSTOLIC 的改变
    if(wl["TKX"] != -1):
        ge.append("TKX")
    if(wl["TKY"] != -1):
        ge.append("TKY")
    if(wl["TN"] != -1):
        ge.append("TN")
    if(wl["TI"] != -1):
        multicast_line["TI"] = str(wl["TI"])
        ge.append("TI")

    #Reorder the WULI_LOOP_WEI to make systolic
    for wlw in WULI_LOOP_WEI:
        if(wlw not in ge):
            ge.append(wlw)

    return ge


def SYSTOLIC_ACT_LOOP_ORDER(hardware_config, df_d):
    #(TODOS)
    SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
        WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)

    wl = df_d["SYSTOLIC"]["WEIGHT_LOAD"]

    ge = []
    #SYSTOLIC 的改变
    if(wl["TKX"] != -1):
        ge.append("TKX")
    if(wl["TKY"] != -1):
        ge.append("TKY")
    if(wl["TN"] != -1):
        ge.append("TN")
    if(wl["TI"] != -1):
        multicast_line["TI"] = str(wl["TI"])
        ge.append("TI")

    #Reorder the WULI_LOOP_WEI to make systolic
    for wlw in WULI_LOOP_WEI:
        if(wlw not in ge):
            ge.append(wlw)

    return ge




def mult_cycles(hc,wei_prec,act_prec):
    if( hc["MULT_TYPE_INT_META"]["MULTICANT"] == "ACT"):
        CYC = act_prec / hc["MULT_TYPE_INT_META"]["RADIX"]
    else:
        CYC = wei_prec / hc["MULT_TYPE_INT_META"]["RADIX"]
    #hc["MULT_TYPE_INT_META"]["MULTICANT"]
    return CYC

############################
#MAPPING FUNCTIONS



def get_hard_limits_map(fd, kx_alias = "kx", ky_alias = "ky"):
    X_LIM = "(x - "+kx_alias+" + 1)"
    Y_LIM = "(y - "+ky_alias+" + 1)"
    
    return {
                    "TXX": X_LIM,
                    "TYY": Y_LIM,
                    "TNN": "nc",
                    "TII": "ic",

                    "X": X_LIM,
                    "Y": Y_LIM,
                    "N": "nc",
                    "I": "ic",

                    "KX": kx_alias,
                    "KY": ky_alias,
                    "B": "batch",
                }

def get_limits_map(fd, kx_alias = "kx", ky_alias = "ky"):
    X_LIM = "(x - "+kx_alias+" + 1)"
    Y_LIM = "(y - "+ky_alias+" + 1)"
    
    return   {
                    "TXX": str(fd["TXX"]),
                    "TYY": str(fd["TYY"]),
                    "TNN": str(fd["TNN"]),
                    "TII": str(fd["TII"]),

                    "X": X_LIM,
                    "Y": Y_LIM,
                    "N": "nc",
                    "I": "ic",

                    "KX": kx_alias,
                    "KY": ky_alias,
                    "B": "batch",
                }


def get_indices_map(fd):
    if True:
        indices_map = {
            "I": "iii",
            "N": "nnn",
            "X": "xxx" ,
            "Y": "yyy",
            "B": "bb ",
            "KX": "kkx",
            "KY": "kky",
            "TXX": "xx",
            "TYY": "yy",
            "TNN": "nn",
            "TII": "ii",
        }
        if(fd["TII"] == -1):
            indices_map["I"] = "ii"
        if(fd["TNN"] == -1):
            indices_map["N"] = "nn"
        if(fd["TYY"] == -1):
            indices_map["Y"] = "yy"
        if(fd["TXX"] == -1):
            indices_map["X"] = "xx"
    return indices_map    

############################
def analyze_floating(supported_dtypes):
    float_d = []


    P = 0
    E = 0
    M = 0
    
    
    for dt in supported_dtypes:
        if("FP" in dt):
            PREC = int(dt.split("FP")[1])
            
            #posits
            if("P" == dt[0] and "E" in dt and "M" in dt):
                P = int(dt.split("P")[1].split("E")[0])
                E = int(dt.split("E")[1].split("M")[0])
                M = int(dt.split("M")[1].split("_")[0])
                
            #floating exponent e mantissa
            elif("E" in dt and "M" in dt):
                P = 0
                E = int(dt.split("E")[1].split("M")[0])
                M = int(dt.split("M")[1].split("_")[0])
            elif("M" in dt):
                P = 0
                M = int(dt.split("M")[1].split("_")[0])
                E = PREC - M
            #special cas
            elif("FP16" == dt):
                P = 0
                E = 5
                M = 10
            elif("BFP16" == dt):
                P = 0
                E = 8
                M = 7
            elif("FP32" == dt):
                P = 0
                E = 8
                M = 23
            else:
                print("unsupported floating")
            #sign, posit regime, exponent, fraction
            float_d.append([1, P,E,M, PREC])
    return float_d



def order_dataflows(hardware_config):
    CONV2D = []
    # Reorder
    # CHINESE WINOGRAD/STRASSEN >SYSTOLIC > DEFAULT
    for idx, flows in enumerate(hardware_config["TILINGS"]["CONV2D"]):
        print(idx,flows)
        if(flows == "DEFAULT"):
            CONV2D.append(flows)
        else:
            insert_idx = -1
            dataflow = hardware_config["TILINGS"]["CONV2D"][flows]["DATAFLOW"]
            for c_idx,c in enumerate(CONV2D):
                if(dataflow == "DIRECT"):
                    if(c == "DEFAULT"):
                        insert_idx = c_idx
                        break
                    elif(c == "DIRECT"):
                        insert_idx = c_idx
                        break
                    elif("SYSTOLIC" or "DIAGONAL" in c):
                        continue
                    else:
                        continue
                elif("SYSTOLIC" or "DIAGONAL" in c):
                    if(c == "DEFAULT"):
                        insert_idx = c_idx
                        break
                    elif(c == "DIRECT"):
                        insert_idx = c_idx
                        break
                    elif("SYSTOLIC" or "DIAGONAL" in c):
                        insert_idx = c_idx
                        break
                    else:
                        continue
                else:
                    insert_idx = c_idx
                    break
                
            if(insert_idx == -1):
                CONV2D.append(flows)
            else:
                CONV2D.insert(insert_idx, flows)
    print(CONV2D)

    #(todos) FC, POOl flows?
    #for idx, flows in enumerate(hardware_config["TILINGS"]["LINEAR"]:
    # ...
    return CONV2D


def GET_PSUM_LOOP_FILTERS(hardware_config, df_d):
    LIM_X = "((X + PADDING*2 - KX + 1) // STRIDE  )"#"X+PADDING*2" #"((X + PADDING*2 - KX + 1) // STRIDE  )"
    LIM_Y = "((Y + PADDING*2 - KY + 1) // STRIDE  )"#"Y+PADDING*2" #"((Y + PADDING*2 - KY + 1) // STRIDE  )"
    #dataflow based partition 
    #SHI_LOOP_PSUM = ["N","TNN", "TI" ]

    SHI_LOOP_PSUM = ["B", "X", "Y", "N", "TNN", "TXX", "TYY" ]
    WULI_LOOP_PSUM = ["TN","TX", "TY", "TB" ]

    if("WINOGRAD" in df_d["DATAFLOW"]): #assume is multicast
        pass        
    elif("DIRECT" == df_d["DATAFLOW"]):
        #WULI_LOOP_ACT =  ["TB", "TI", "TN", "TX_FULL", "TY_FULL", "TKX", "TKY"]
        pass
    elif("SYSTOLIC_1D_A" == df_d["DATAFLOW"]):
        pass
    elif("SYSTOLIC_2D_A" == df_d["DATAFLOW"]):
        pass
    elif("SYSTOLIC_DIAG" == df_d["DATAFLOW"]):
        pass
    elif("SPARSE_DIRECT" == df_d["DATAFLOW"]):
        pass
    elif("SPARSE_WINOGRAD" in df_d["DATAFLOW"]):
        pass
    elif("SPARSE_SYSTOLIC" in df_d["DATAFLOW"]):
        pass

    return SHI_LOOP_PSUM, WULI_LOOP_PSUM


def GET_LOOP_FILTERS(hardware_config, df_d):
    LIM_X = "((X + PADDING*2 - KX + 1) // STRIDE  )"#"X+PADDING*2" #"((X + PADDING*2 - KX + 1) // STRIDE  )"
    LIM_Y = "((Y + PADDING*2 - KY + 1) // STRIDE  )"#"Y+PADDING*2" #"((Y + PADDING*2 - KY + 1) // STRIDE  )"
    #dataflow based partition 
    SHI_LOOP_WEI = ["KX", "KY", "N", "I", "TNN", "TII"]
    SHI_LOOP_ACT = ["B", "X", "Y", "I", "KX", "KY", "TYY", "TXX", "TII", ]
    INNER_WEI = "WEIGHTS[n][i][kx][ky]"  
    INNER_ACT = "INPUTS[b][i][x+kx][y+ky]" 
    WULI_LOOP_ACT =  ["TB", "TI", "TX", "TY"]#, "TKX", "TKY"]
    WULI_LOOP_WEI =  ["TI", "TN", "TKX", "TKY"]
        
    if("WINOGRAD" in df_d["DATAFLOW"]): #assume is multicast
        WULI_LOOP_ACT =  ["TB", "TI", "TX", "TY"]#, "TKX", "TKY"]
        if("WINO_PRE_WEIGHT" in df_d and df_d["WINO_PRE_WEIGHT"]):
            SHI_LOOP_WEI = ["N", "I", "TNN", "TII"]
            WULI_LOOP_WEI =  ["TI", "TN","WINO_KX", "WINO_KY"]
            #INNER_WEI = "hex(POST_WEIGHTS[n][i][x-xx][y-yy])[2:].zfill(weight_precision//4)"#直接
            #INNER_ACT = "hex(INPUTS[b][i][x][y])[2:].zfill(act_precision//4)" #(todos)
            INNER_WEI = "POST_WEIGHTS[n][i][kx][ky]"#[x-xx][y-yy]"  
            INNER_ACT = "INPUTS[b][i][x+kx][y+ky]" 
        else:
            WULI_LOOP_WEI = ["TI", "TN", "TKX", "TKY"]
                
    elif("DIRECT" == df_d["DATAFLOW"]):
        if(hardware_config["multicast"] == False):
            WULI_LOOP_ACT =  ["TB", "TI", "TN", "TX_FULL", "TY_FULL", "TKX", "TKY"]
            WULI_LOOP_WEI =  ["TB", "TI", "TN", "TX", "TY", "TKX", "TKY"]

    elif("SYSTOLIC_1D_A" == df_d["DATAFLOW"]):

        #tmp = []
        #for aa in WULI_LOOP_ACT:
        #    if(aa not in df_d["SYSTOLIC_VAR"]):
        #        tmp.append(aa)
        #WULI_LOOP_ACT = tmp

        #(TODOS HERE)<---
            
        #if systolic on the TX, TY, KX, KY we can 
        if(  df_d["SYSTOLIC_VAR"] == "X"):
            SHI_LOOP_ACT = ["B", "X", "Y", "I", "yy", "xx", "ii", "KY"]
            df_d["TX"] = 1
            df_d["TKX"] = 1
            WULI_LOOP_ACT = ["TB", "TI", "TX_FULL", "TY"]
            LIM_X = "X+PADDING*2"
        elif(df_d["SYSTOLIC_VAR"] == "Y"):
            SHI_LOOP_ACT = ["B", "X", "Y", "I", "yy", "xx", "ii", "KX"]
            df_d["TY"] = 1
            df_d["TKY"] = 1
                
            WULI_LOOP_ACT = ["TB", "TI", "TX", "TY_FULL"]
            LIM_Y = "Y+PADDING*2"
        else:
            print("Unsupported systolic config for now ")
            exit(-1)
        
        #["B", "X", "Y", "I", "yy", "xx", "ii", "KX", "KY"]
    elif("SYSTOLIC_2D_A" == df_d["DATAFLOW"]):
        SHI_LOOP_ACT = ["B", "X", "Y", "I", "yy", "xx", "ii"]
        df_d["TX"] = 1
        df_d["TKX"] = 1
        df_d["TY"] = 1
        df_d["TKY"] = 1
        #WULI_LOOP_ACT = ["TB", "TI", "TX_FULL", "TY_FULL"]
        LIM_X = "X+PADDING*2"
        LIM_Y = "Y+PADDING*2"
            
    elif("SYSTOLIC_DIAG" == df_d["DATAFLOW"]):
        pass


    elif("SPARSE_DIRECT" == df_d["DATAFLOW"]):
        pass
    elif("SPARSE_WINOGRAD" in df_d["DATAFLOW"]):
        pass
    elif("SPARSE_SYSTOLIC" in df_d["DATAFLOW"]):
        pass

    return SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
               WULI_LOOP_WEI, LIM_X, LIM_Y

#variables = ["TX", "TY"..]
#fd = 数据流
def gen_index(variables, fd=None, multicast=True,WINDOW=1,
              kx=None, ky=None,x=None,y=None,b=None,i=None,window=None,
              n=None, use_macros = False, mini_carte = None, cast = None, evaluate=False):
    if(mini_carte == None):
        mini_carte = {
        "TI": "(i-ii)",
        "TN": "(n-nn)",
        "KX": "kx",
        "KY": "ky",
        "TX": "(x-xx)",
        "TY": "(y-yy)",
        "TB" : "(b-bb)",
        "TKX": "(kx-kkx)",
        "TKY": "(ky-kky)",

        "WINO_KX": "kx",
        "WINO_KY": "ky",

        "TX_FULL": "(x-xx)",
        "TY_FULL": "(y-yy)",

        "WINDOW": "0"
    }

    #For winograd, wuli usage
    if(kx!=None):
        mini_carte["KX"] = str(kx)
        mini_carte["WINO_KX"] = str(kx)
        mini_carte["TKX"] = str(kx)
        if(x != None):
            mini_carte["TX"] = str(x) + "+" + str(kx)
            mini_carte["TX_FULL"] = str(x) + "+" + str(kx)
    if(ky != None):
        mini_carte["KY"] = str(ky)
        mini_carte["WINO_KY"] = str(ky)
        mini_carte["TKY"] = str(ky)
        if(y != None):
            mini_carte["TY"] = str(y) + "+" + str(ky)
            mini_carte["TY_FULL"] = str(y) + "+" + str(ky)
    if(b != None):
        mini_carte["TB"] = str(b)
    if(i != None):
        mini_carte["TI"] = str(i)
    if(n != None):
        mini_carte["TN"] = str(n)
    if(window != None):
        mini_carte["WINDOW"] = str(window)

    if(cast == None):        
        cast = {
                        "TI":"TI",
                        "TX": "(TX+TKX-1)",
                        "TY": "(TY+TKY-1)",
                        "TN": "TN",
                        "TB": "TB",
                        "TKX":"TKX",
                        "TKY": "TKY",
                        "WINO_KX": "(TX+TKX-1)",
                        "WINO_KY": "(TY+TKY-1)",

                        "TX_FULL": "(TX+TKX-1)",
                        "TY_FULL": "(TY+TKY-1)",
                        "WINDOW": str(WINDOW),
                    }
        if(use_macros):
            cast = {
                        "TI": str(fd["TI"]),
                        "TX": "("+str(fd["TX"])+"+"+str(fd["TKX"])+"-1)",
                        "TY": "("+str(fd["TY"])+"+"+str(fd["TKY"])+"-1)",
                        "TN": str(fd["TN"]),
                        "TB": str(fd["TB"]),
                        "TKX":str(fd["TKX"]),
                        "TKY": str(fd["TKY"]),
                        "WINO_KX": "("+str(fd["TX"])+"+"+str(fd["TKX"])+"-1)",
                        "WINO_KY": "("+str(fd["TY"])+"+"+str(fd["TKY"])+"-1)",

                        "TX_FULL": "("+str(fd["TX"])+"+"+str(fd["TKX"])+"-1)",
                        "TY_FULL": "("+str(fd["TY"])+"+"+str(fd["TKY"])+"-1)",
                        "WINDOW": str(WINDOW),
                    }        

    #print(cast, mini_carte)

    #print(variables)
    idx = ""
    var_len = 0
    #use qinjiushao algorithm to fast multiply indices
    for v_idx, v in enumerate(variables):
        if(v == "TKX" and "TX" in variables and "TKX" in variables):
            continue
        if(v == "TKY" and "TX" in variables and "TKX" in variables):
            continue
        var_len += 1
        if(multicast==False):
            idx += "*"+v+"+  "+mini_carte[v]+")"
        else:
            idx += "*"+str(cast[v])+"+  "+mini_carte[v]+")"
    idx ="(0"+ idx
    idx = (var_len - 1)*"(" +  idx
    
    return idx




def  calculate_wei_reuse(hardware_config):
    gen_constraints = hardware_config.get("GEN_CONSTRAINTS", {})
    hc = hardware_config
    for flows in hc["TILINGS"].get("CONV2D",{}):

        dataflows = hardware_config["TILINGS"]["CONV2D"][flows]
        fd = dataflows
        
        MAX_STRIDE = gen_constraints.get("MAX_STRIDE",2)
        MAX_KX = gen_constraints.get("MAX_KX",7)
        MAX_KY = gen_constraints.get("MAX_KY",7)
        MAX_X  = gen_constraints.get("MAX_X", 256)
        MAX_Y  = gen_constraints.get("MAX_Y", 256)
        MAX_N  = gen_constraints.get("MAX_N", 128)
        MAX_I  = gen_constraints.get("MAX_I", 128)
        MAX_B  = gen_constraints.get("MAX_B",1)
        MAX_PADDING_X = gen_constraints.get("MAX_PADDING_X",2)
        MAX_PADDING_Y = gen_constraints.get("MAX_PADDING_Y",2)
        
        MAX_STRIDE = dataflows.get("MAX_STRIDE", MAX_STRIDE)
        MAX_KX = dataflows.get("MAX_KX",MAX_KX)
        MAX_KY = dataflows.get("MAX_KY",MAX_KY)
        MAX_X  = dataflows.get("MAX_X", MAX_X)
        MAX_Y  = dataflows.get("MAX_Y", MAX_Y)
        MAX_N  = dataflows.get("MAX_N", MAX_N)
        MAX_I  = dataflows.get("MAX_I", MAX_I)
        MAX_B  = dataflows.get("MAX_B",MAX_B)
        MAX_PADDING_X = dataflows.get("MAX_PADDING_X",MAX_PADDING_X)
        MAX_PADDING_Y = dataflows.get("MAX_PADDING_Y",MAX_PADDING_Y)

        MIN_WEI_BUF_ROWS = []
        if(fd["DATAFLOW"] == "DIRECT" or "SPARSE_DIRECT" == fd["DATAFLOW"]):
            lv = 1 #率=1，数据重复的距离
            cun = []
            for ll in fd["LOOP"][::-1]:
                if(ll == "KY"):
                    lv *= max(1, MAX_KY//fd["TKY"])
                elif(ll == "KX"):
                    lv *= max(1, MAX_KY//fd["TKX"])
                elif(ll in ["B", "TXX", "TYY", "X", "Y"]):
                    if(ll == "B" and MAX_B == 1):#special case
                        continue
                    cun.append(lv)
                elif(ll == "TII"):
                    lv *= max(1, fd["TII"]//fd["TI"])
                elif(ll == "I"):
                    if(fd["TII"] == -1):
                        lv *= max(1, MAX_I)
                    else:
                        lv *= max(1, MAX_I//fd["TII"])
                elif(ll == "TNN"):                 
                    lv *= max(1, fd["TNN"]//fd["TN"])
                elif(ll == "N"):
                    if(fd["TNN"] == -1):
                        lv *= MAX_N
                    else:
                        lv *= max(1, MAX_N//fd["TNN"])
                print(ll, lv, cun)
            MIN_WEI_BUF_ROWS.append(max(cun))

            
            
        elif(fd["DATAFLOW"] == "WINOGRAD"):
            pass #Todos

        return max(MIN_WEI_BUF_ROWS)   

def calculate_psum_reuse(hardware_config):
    gen_constraints = hardware_config.get("GEN_CONSTRAINTS", {})
    hc = hardware_config
    for flows in hc["TILINGS"].get("CONV2D",{}):

        dataflows = hardware_config["TILINGS"]["CONV2D"][flows]
        fd = dataflows
        
        MAX_STRIDE = gen_constraints.get("MAX_STRIDE",2)
        MAX_KX = gen_constraints.get("MAX_KX",7)
        MAX_KY = gen_constraints.get("MAX_KY",7)
        MAX_X  = gen_constraints.get("MAX_X", 256)
        MAX_Y  = gen_constraints.get("MAX_Y", 256)
        MAX_N  = gen_constraints.get("MAX_N", 128)
        MAX_I  = gen_constraints.get("MAX_I", 128)
        MAX_B  = gen_constraints.get("MAX_B",1)
        MAX_PADDING_X = gen_constraints.get("MAX_PADDING_X",2)
        MAX_PADDING_Y = gen_constraints.get("MAX_PADDING_Y",2)
        
        MAX_STRIDE = dataflows.get("MAX_STRIDE", MAX_STRIDE)
        MAX_KX = dataflows.get("MAX_KX",MAX_KX)
        MAX_KY = dataflows.get("MAX_KY",MAX_KY)
        MAX_X  = dataflows.get("MAX_X", MAX_X)
        MAX_Y  = dataflows.get("MAX_Y", MAX_Y)
        MAX_N  = dataflows.get("MAX_N", MAX_N)
        MAX_I  = dataflows.get("MAX_I", MAX_I)
        MAX_B  = dataflows.get("MAX_B",MAX_B)
        MAX_PADDING_X = dataflows.get("MAX_PADDING_X",MAX_PADDING_X)
        MAX_PADDING_Y = dataflows.get("MAX_PADDING_Y",MAX_PADDING_Y)

        MIN_BUF_ROWS = []
        if(fd["DATAFLOW"] == "DIRECT"or "SPARSE_DIRECT" == fd["DATAFLOW"]):
            lv = 1 #率=1，数据重复的距离
            cun = []
            for ll in fd["LOOP"][::-1]:
                if(ll in ["KX", "KY", "I", "TII"]):
                    cun.append(lv)
                elif(ll == "TB"):
                    lv *= max(1, MAX_B//fd["TB"])    
                elif(ll == "TNN"):                 
                    lv *= max(1, fd["TNN"]//fd["TN"])
                elif(ll == "N"):
                    if(fd["TNN"] == -1):
                        lv *= MAX_N
                    else:
                        lv *= max(1, MAX_N//fd["TNN"])
                elif(ll == "TXX"):
                    lv *= max(1, fd["TXX"]//fd["TX"])
                elif(ll == "X"):
                    if(fd["TXX"] == -1):
                        lv *= MAX_X
                    else:
                        lv *= max(1, MAX_X//fd["TXX"])
                elif(ll == "TYY"):
                    lv *= max(1, fd["TYY"]//fd["TY"])
                elif(ll == "Y"):
                    if(fd["TYY"] == -1):
                        lv *= MAX_Y
                    else:
                        lv *= max(1, MAX_Y//fd["TYY"])
                
                                
                print(ll, lv, cun)
            MIN_BUF_ROWS.append(max(cun))

            
            
        elif(fd["DATAFLOW"] == "WINOGRAD"):
            pass #Todos

        return max(MIN_BUF_ROWS)

if __name__ == "__main__":
    #print(analyze_floating(supported_dtypes = ["INT8","INT16", "FP16"]))
    #print(analyze_floating(supported_dtypes = ["E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"]))

    hd = {"TILINGS": {
            "CONV2D": {
                "DEFAULT": {
                    #TX and TY should be multiple of WINO_TX and WINO_TY respectively
                    "DATAFLOW": "DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.
                    "TX": 2, "TY": 2,  "TKX": 1, "TKY": 1, "TI": 1, "TN": 1, "TB":1, "WINO_TX":2, "WINO_TY": 2,
                    "TXX": 8, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],
                    #les limites
                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                     "REMOVE_DUPLICATE_ROWS": True,
                        "WINO_PRE_WEIGHT": False,

                    "MAX_STRIDE": 1,
                    "MAX_KX": 3,
                    "MAX_KY": 3,
                    "MAX_X": 8,
                    "MAX_Y": 8,
                    "MAX_N": 2,
                    "MAX_I": 2,
                    "MAX_B": 1,
                    "MAX_PADDING_X": 2,
                    "MAX_PADDING_Y": 2,
                    
                }
            }
        },
            "GEN_CONSTRAINTS":{
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
           }
        }
    #MIN_WEI_BUF_ROWS = calculate_wei_reuse(hd)

    calculate_psum_reuse(hd)


def generate_counter_window(fd, WINDOW, kx_alias = "kx", ky_alias = "ky"):
    s = ""

    if True:
        if True:
            if True:
                index_map = {
                    "TXX": "xx",
                    "TYY": "yy",
                    "TNN": "nn",
                    "TII": "ii",

                    "X": "xxx",
                    "Y": "yyy",
                    "N": "nnn",
                    "I": "iii",

                    "KX": "kkx",
                    "KY": "kky",
                    "B": "bb",
                }
                #(TODOS) look at the accumulator code
                move_map = {
                    "TXX": str(fd["TX"]),
                    "TYY": str(fd["TY"]),
                    "TNN": str(fd["TN"]),
                    "TII": str(fd["TI"]),

                    "X": str(fd["TXX"]),
                    "Y": str(fd["TYY"]),
                    "N": str(fd["TNN"]),
                    "I": str(fd["TII"]),

                    "KX": str(fd["TKX"]),
                    "KY": str(fd["TKY"]),
                    "B":  str(fd["TB"]),
                }
                #I think the TXXX, TYYY these tilings (for the L2) can be done on the higher system level !
                #For example, if there are multiple cores
                #We can then do some kind of tiling for the multiple cores
                #TODOS
                X_LIM = "(x - "+kx_alias+" + 1)"
                Y_LIM = "(y - "+ky_alias+" + 1)"
                lim_map = {
                    "TXX": str(fd["TXX"]),
                    "TYY": str(fd["TYY"]),
                    "TNN": str(fd["TNN"]),
                    "TII": str(fd["TII"]),

                    "X": X_LIM,
                    "Y": Y_LIM,
                    "N": "nc",
                    "I": "ic",

                    "KX": kx_alias,
                    "KY": ky_alias,
                    "B": "batch",
                }

                lim_map_hard_limit = {
                    "TXX": X_LIM,
                    "TYY": Y_LIM,
                    "TNN": "nc",
                    "TII": "ic",

                    "X": X_LIM,
                    "Y": Y_LIM,
                    "N": "nc",
                    "I": "ic",

                    "KX": kx_alias,
                    "KY": ky_alias,
                    "B": "batch",
                }

                prec_map = {
                    "TXX": "MAX_X_LOG",
                    "TYY": "MAX_Y_LOG",
                    "TNN": "MAX_N_LOG",
                    "TII": "MAX_I_LOG",

                    "X": "MAX_X_LOG",
                    "Y": "MAX_Y_LOG",
                    "N": "MAX_N_LOG",
                    "I": "MAX_I_LOG",

                    "KX": "MAX_KX_LOG",
                    "KY": "MAX_KY_LOG",
                    "B": "MAX_B_LOG",
                }

                if(fd["TXX"] == -1):
                    index_map["X"] = "xx"
                    move_map["X"] = str(fd["TX"])+"*stride"
                if(fd["TYY"] == -1):
                    index_map["Y"] = "yy"
                    move_map["Y"] = str(fd["TY"])+"*stride"
                if(fd["TII"] == -1):
                    index_map["I"] = "ii"
                    move_map["I"] = str(fd["TI"])
                if(fd["TNN"] == -1):
                    index_map["N"] = "nn"
                    move_map["N"] = str(fd["TN"])
                
                #GENERATE ARRAY OF ADDRESSES BASED ON A BASE ONE
                #DETECT OVER LIMIT MUX
                #By getting all addresses for each block, we will be able to get the maximum power of the sparsity unit
                #WINDOW = fd["SPARSITY"]["WINDOW"] #do we do something with multiple windows? like WEI_WINDOW, ACT_WINDOW?
                for lp in fd["LOOP"][::-1]:
                    for wu in range(WINDOW):         
                        cur_reg = index_map[lp] + "_"+str(wu)
                        s += "reg [`"+prec_map[lp]+"-1:0] "+ cur_reg + ";\n"
                        s += "reg [`"+prec_map[lp]+"-1:0] "+ cur_reg + "_chu;\n"
                        #s += "reg [`"+prec_map[lp]+"-1:0] "+ cur_reg + "_ru;\n"

                    cur_reg = index_map[lp] + "_"+str(0)
                    s += "always@(*) begin\n\
                              "+cur_reg+" = "+index_map[lp]+";\n\
                          end\n"
                    
                    for wu in range(WINDOW-1):
                        cur_reg = index_map[lp] + "_"+str(wu)
                        next_reg = index_map[lp]+"_"+str(wu+1)
                        s += "always@(*) begin\n"
                        s += "\tif(  ("+cur_reg+"_chu >= " + lim_map_hard_limit[lp] + " ) | ("+cur_reg+"_chu >= " + lim_map[lp] + " ) ) \n\
\t\t"+next_reg+" = 0;\n\
\telse  \n\
\t\t"+next_reg+" = "+cur_reg+"_chu ; \n\
\tend\n"
                       
                
                for wu in range(WINDOW):
                    lp = fd["LOOP"][::-1][0]
                    cur_reg = index_map[lp] + "_"+str(wu)
                    next_reg = index_map[lp]+"_"+str(wu+1)
                    s += "always@(*) begin\n\
\t\t"+ cur_reg +"_chu ="+cur_reg+"+"+move_map[lp]+";\n\
\tend\n"
                             
                    for idx,lp in enumerate(fd["LOOP"][::-1][1:]):
                        shang_lp = fd["LOOP"][::-1][idx]
                             
                        shang_reg = index_map[shang_lp] + "_"+str(wu)
                        cur_reg = index_map[lp] + "_"+str(wu)

                        next_reg = index_map[lp] + "_"+str(wu+1)
                             
                        s += "always@(*) begin\n"
                        tiaojian = []
                        for prev_idx in range(idx+1):
                            shang_lp = fd["LOOP"][::-1][prev_idx]
                            shang_reg = index_map[shang_lp]+"_"+str(wu)
                            cond = "( ("+shang_reg+"+"+move_map[shang_lp]+" >= " + lim_map_hard_limit[shang_lp] + " ) | ("+shang_reg+"+"+move_map[shang_lp]+" >= " + lim_map[shang_lp] + " ) )"
                            tiaojian.append(cond)
                              
                        #s += "\tif(  ("+shang_reg+"+"+move_map[shang_lp]+" >= " + lim_map_hard_limit[shang_lp] + " ) | ("+shang_reg+"+"+move_map[shang_lp]+" >= " + lim_map[shang_lp] + " ) ) \n\
                        s += "\tif(" + "&".join(tiaojian) + ")\
\t\t"+ cur_reg +"_chu = "+cur_reg+"+"+move_map[lp]+";\n\
\telse  \n\
\t\t"+cur_reg+ "_chu = "+cur_reg+"; \n\
end\n"
                        
    return s

