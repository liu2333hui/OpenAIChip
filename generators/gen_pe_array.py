import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import order_dataflows
import numpy as np
from utils import gen_index, GET_LOOP_FILTERS

            
def get_pe_idx(idx, pe_type):
    #return "`MAX_PSUM_PRECISION*"+str(idx)+" + `pe_type  -1:`MAX_PSUM_PRECISION*"+str(idx)
    #return "`MAX_PSUM_PRECISION*("+str(idx)+"+1) -1:`MAX_PSUM_PRECISION*"+str(idx)
    return "`"+pe_type+"*("+str(idx)+"+1) -1:`"+pe_type+"*"+str(idx)


def parse_dataflows(flows, dataflow):

    print(flows, dataflow)
    s = ""

    s += flows
        
    if("WINOGRAD" in dataflow):
        #exception, stride = 2 see UManitoba
        if("STRIDE_2" in dataflow):
            s += "&& stride <= 2"
        else:
            s += "&& stride == 1"

    return s  

def gen_pe_array(hardware_config, meta_config, macro_config):
    print("\n// GEN_PE VERILOG\n")

    print(macro_config["REQUIRED_PES"])

    
    f = open(meta_config["dossier"]+"/pe_array.v", "w")
    s = ""


    REQUIRED_PES = macro_config["REQUIRED_PES"]

    #COVER WINOGRAD CASE
    WINOGRAD_EN = False
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):
        WINOGRAD_EN = True

    s += "module PE_ARRAY(\n\
            input clk,\n\
            input rst_n,\n\
            input ["+str(REQUIRED_PES)+"-1:0] en,\n\
            input int_inference,\n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
            \n\
            input [5:0] wei_mantissa,\n\
            input [5:0] act_mantissa,\n\
            input [5:0] wei_exponent,\n\
            input [5:0] act_exponent,\n\
            input [5:0] wei_regime,\n\
            input [5:0] act_regime,\n"

    if(not WINOGRAD_EN):
        s += "input  [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n\
              input  [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n\
              output [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi,\n"
    else:
        s += "input  [`WINO_MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n\
              input  [`WINO_MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n\
              output [`WINO_MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi,\n"
        
    s += "input ["+str(REQUIRED_PES)+"-1:0] valid,\n\
            output ["+str(REQUIRED_PES)+"-1:0] ready,\n\
            output ["+str(REQUIRED_PES)+"-1:0] last,\n\
            output ["+str(REQUIRED_PES)+"-1:0] start,\n\
            \n\
            input pe_all_ready\n\
        );\n\
"

    #s += "reg [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;\n"
    #s += "reg [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;\n"

    if(not WINOGRAD_EN):
        s += "wire [`MAX_PSUM_PRECISION_INT*`REQUIRED_PES-1:0] zi_int;\n"
    else:
        s += "wire [`WINO_MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi_int;\n"

    s += "wire [`MAX_PSUM_PRECISION_FP*`REQUIRED_PES-1:0] zi_fp;\n"

    #s += "reg ["+str(REQUIRED_PES)+"-1:0] valid;\n"
    #s += "reg ["+str(REQUIRED_PES)+"-1:0] ready;\n"


    s += "wire ["+str(REQUIRED_PES)+"-1:0] ready_int;\n"
    s += "wire ["+str(REQUIRED_PES)+"-1:0] ready_fp;\n"
    s += "wire ["+str(REQUIRED_PES)+"-1:0] last_int;\n"
    s += "wire ["+str(REQUIRED_PES)+"-1:0] last_fp;\n"        
    s += "wire ["+str(REQUIRED_PES)+"-1:0] start_int;\n"
    s += "wire ["+str(REQUIRED_PES)+"-1:0] start_fp;\n"
    
    #MAX_ACT_PRECISION_INT= macro_config["MAX_ACT_PRECISION_INT"]
    #MAX_WEI_PRECISION_INT = macro_config["MAX_WEI_PRECISION_INT"]
    #MAX_ACT_PRECISION_FP= macro_config["MAX_ACT_PRECISION_FP"]
    #MAX_WEI_PRECISION_FP = macro_config["MAX_WEI_PRECISION_FP"]    
    ##MAX_PSUM_PRECISION_FP = macro_config["MAX_PSUM_PRECISION_FP"]    
    #MAX_PSUM_PRECISION_INT = macro_config["MAX_PSUM_PRECISION_INT"]    

    #Q: #PEs, gating
    #1. 创造REQUIRED_PES的乘法器
    #1.1 ints
    hc = hardware_config
    s += "//Binding for input PES\n"

    s += "wire [`REQUIRED_PES-1:0] zero_gate;\n"

    s += "wire [`REQUIRED_PES-1:0] zero_gate_int;\n"
    
    s += "wire [`REQUIRED_PES-1:0] zero_gate_fp;\n"
    #"+str(p)+"
    #s += "genvar p;\n"

    
    if(not WINOGRAD_EN):
        MAX_PSUM_NAME = "MAX_PSUM_PRECISION_INT"
    else:
        MAX_PSUM_NAME = "WINO_MAX_PSUM_PRECISION_INT"
        
    if( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0):
        for p in range(macro_config["REQUIRED_PES"]):

            if(WINOGRAD_EN):
                s += "\n\
                wire [`WINO_MAX_PSUM_PRECISION_INT-1:0] zi_"+str(p)+" ;\n\
                wire [`WINO_MAX_ACT_PRECISION_INT-1:0]  yi_"+str(p)+" ;\n\
                wire [`WINO_MAX_WEI_PRECISION_INT-1:0]  jia_"+str(p)+" ;\n"
                s += "assign yi_"+str(p)+" = yi["+get_pe_idx(str(p), "WINO_MAX_ACT_PRECISION_INT")+"];\n\
                    assign jia_"+str(p)+" =jia["+get_pe_idx(str(p), "WINO_MAX_WEI_PRECISION_INT")+"];\n\
                    //wire zero_gate_int"+str(p)+";\n"
            else:
                s += "\n\
                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_"+str(p)+" ;\n\
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_"+str(p)+" ;\n\
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_"+str(p)+" ;\n"
                s += "assign yi_"+str(p)+" = yi["+get_pe_idx(str(p), "MAX_ACT_PRECISION_INT")+"];\n\
                    assign jia_"+str(p)+" =jia["+get_pe_idx(str(p), "MAX_WEI_PRECISION_INT")+"];\n\
                    assign zi_"+str(p)+" =zi_int["+get_pe_idx(str(p), MAX_PSUM_NAME)+"];\n\
                    //wire zero_gate_int"+str(p)+";\n"

            if(hc["ACT_ZERO_GATING"] == False and hc["WEI_ZERO_GATING"] == False):
                s += "assign zero_gate_int["+str(p)+"] = 1'b0;\n"
            elif(hc["ACT_ZERO_GATING"] == False and hc["WEI_ZERO_GATING"] == True):
                s += "assign zero_gate_int["+str(p)+"] = valid["+str(p)+"]&(jia_"+str(p)+" == 0);\n"
            elif(hc["ACT_ZERO_GATING"] == True and hc["WEI_ZERO_GATING"] == False):
                s += "assign zero_gate_int["+str(p)+"] = valid["+str(p)+"]&(yi_"+str(p)+" == 0);\n"
            else:
                s += "assign zero_gate_int["+str(p)+"]  = valid["+str(p)+"]&(yi_"+str(p)+" == 0) | (jia_"+str(p)+" == 0);\n"   
            
            
            if(not WINOGRAD_EN):
                wei_precision = "wei_precision"
                act_precision = "act_precision"
            else:
                wei_precision = "wei_precision + `MU"
                act_precision = "act_precision + `MU"                
                    
            s += "MULT_INT mult_"+str(p)+" (.clk(clk),.rst_n(rst_n),\n\
                        .en(en["+str(p)+"]"+" & int_inference   & ~zero_gate_int["+str(p)+"]),\n\
                        .wei_precision(wei_precision),.act_precision(act_precision),\n\
                        .jia(jia_"+str(p)+"),.yi(yi_"+str(p)+"),.zi(zi_int["+get_pe_idx(str(p), MAX_PSUM_NAME)+"]),\n\
                        .valid(valid["+str(p)+"]),.ready(ready_int["+str(p)+"]),.last(last_int["+str(p)+"]), .start(start_int["+str(p)+"]),\n\
                        .pe_all_ready(pe_all_ready));\n"

        #endgenerate\n"

    #1.2 FLOATS
    if( macro_config["MAX_WEI_PRECISION_FP"] != 0 and macro_config["MAX_ACT_PRECISION_FP"] != 0):

        for p in range(macro_config["REQUIRED_PES"]):
            s += "wire [`MAX_PSUM_PRECISION_FP-1:0] zi_fp_"+str(p)+" ;\n\
                wire [`MAX_ACT_PRECISION_FP-1:0]  yi_fp_"+str(p)+" ;\n\
                wire [`MAX_WEI_PRECISION_FP-1:0]  jia_fp_"+str(p)+" ;\n\
                assign yi_fp_"+str(p)+" = yi["+get_pe_idx(str(p), "MAX_ACT_PRECISION_FP")+"];\n\
                assign jia_fp_"+str(p)+" =jia["+get_pe_idx(str(p), "MAX_WEI_PRECISION_FP")+"];\n\
                //wire zero_gate_fp_p;\n"
            if(hc["ACT_ZERO_GATING"] == False and hc["WEI_ZERO_GATING"] == False):
                s += "assign zero_gate_fp["+str(p)+"] = 1'b0;\n"
            elif(hc["ACT_ZERO_GATING"] == False and hc["WEI_ZERO_GATING"] == True):
                s += "assign zero_gate_fp["+str(p)+"] = (jia_fp_"+str(p)+" == 0);\n"
            elif(hc["ACT_ZERO_GATING"] == True and hc["WEI_ZERO_GATING"] == False):
                s += "assign zero_gate_fp["+str(p)+"] = (yi_fp_"+str(p)+" == 0);\n"
            else:
                s += "assign zero_gate_fp["+str(p)+"]  = (yi_fp_"+str(p)+" == 0) | (jia_fp_"+str(p)+" == 0);\n"   
                    
            s += "MULT_FP mult_fp_"+str(p)+" (.clk(clk),.rst_n(rst_n),\n\
                        .en(en["+str(p)+"] &  ~int_inference  &  ~zero_gate_fp["+str(p)+"]),\n\
                        .wei_precision(wei_precision),.act_precision(act_precision),\n\
                    .wei_mantissa(wei_mantissa),.act_mantissa(act_mantissa),\n\
                    .wei_exponent(wei_exponent),.act_exponent(act_exponent),\n\
                    .wei_regime(wei_regime),.act_regime(act_regime),\n\
                    .jia(jia_fp_"+str(p)+"),.yi(yi_fp_"+str(p)+"),.zi(zi_fp["+get_pe_idx(str(p), "MAX_PSUM_PRECISION_FP")+"]), \n\
                    .valid(valid["+str(p)+"]),.ready(ready_fp["+str(p)+"],.last(last_fp["+str(p)+"], .start(start_fp["+str(p)+"]),\n\
                        .pe_all_ready(pe_all_ready));\n"
           

        #endgenerate\n"
    #binding for output
    s += "//Binding for output zi + ready\n"

    #s += "   generate \n\"
    # for p in range(macro_config["REQUIRED_PES"]):
    #     s += "assign ready["+str(p)+"] = ready_fp["+str(p)+"] | ready_int["+str(p)+"];\n"

        
    if( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0
          and macro_config["MAX_WEI_PRECISION_FP"] != 0 and macro_config["MAX_ACT_PRECISION_FP"] != 0):
        for p in range(macro_config["REQUIRED_PES"]):
            s += "assign zi["+get_pe_idx(str(p), "MAX_PSUM_PRECISION")+"] =  int_inference? (zero_gate_int["+str(p)+"] ? 0  :  zi_int[\
                      "+      get_pe_idx(str(p), MAX_PSUM_NAME)+"]):\
                            ( zero_gate_fp["+str(p)+"] ? "+str(MAX_PSUM_PRECISION_FP)+"'d0  :  zi_fp["+get_pe_idx(str(p), "MAX_PSUM_PRECISION_FP")+"] )   ;  \n"
            s += "assign ready["+str(p)+"] = zero_gate["+str(p)+"]? 1: ready_fp["+str(p)+"] | ready_int["+str(p)+"];\n"
            s += "assign last["+str(p)+"] = zero_gate["+str(p)+"]? 1:last_fp["+str(p)+"] | last_int["+str(p)+"];\n"
            s += "assign start["+str(p)+"] = start_fp["+str(p)+"] | start_int["+str(p)+"];\n"
            s += "assign zero_gate["+str(p)+"] = zero_gate_fp["+str(p)+"] | zero_gate_int["+str(p)+"];\n"
            
    elif( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0
         ):
        for p in range(macro_config["REQUIRED_PES"]):
            s += "assign zi["+get_pe_idx(str(p), MAX_PSUM_NAME)+"] =  zero_gate_int["+str(p)+"] ? 0  :  zi_int["+get_pe_idx(str(p), MAX_PSUM_NAME)+"] ;  \n"
            s += "assign ready["+str(p)+"] = zero_gate["+str(p)+"]? 1: ready_int["+str(p)+"];\n"
            s += "assign last["+str(p)+"] =  zero_gate["+str(p)+"]? 1:last_int["+str(p)+"];\n"
            s += "assign start["+str(p)+"] =  start_int["+str(p)+"];\n"
            s += "assign zero_gate["+str(p)+"] = zero_gate_int["+str(p)+"];\n"
            
    elif( macro_config["MAX_WEI_PRECISION_FP"] != 0 and macro_config["MAX_ACT_PRECISION_FP"] != 0
         ):
        for p in range(macro_config["REQUIRED_PES"]):
            s += "assign zi["+get_pe_idx(str(p), "MAX_PSUM_PRECISION_FP")+"] =  zero_gate_fp["+str(p)+"] ? 0  :  zi_fp["+get_pe_idx(str(p), "MAX_PSUM_PRECISION_FP")+"] ;  \n"
            s += "assign ready["+str(p)+"] = zero_gate["+str(p)+"]? 1: ready_fp["+str(p)+"];\n"
            s += "assign last["+str(p)+"] = zero_gate["+str(p)+"] ? 1: last_fp["+str(p)+"];\n"
            s += "assign start["+str(p)+"] = start_fp["+str(p)+"];\n"
            s += "assign zero_gate["+str(p)+"] = zero_gate_fp["+str(p)+"] ;\n"                        
    else:
        print("NO PES!")
        exit()
    #s += "end\n"
    s += "endmodule\n"
    f.write(s)
    f.close()
    #generate inter-pe
    #gen_pe_internal_mapping(hardware_config, meta_config, macro_config)
    #generate extra-pe
    #gen_pe_external_mapping(hardware_config, meta_config, macro_config)
    #generate full PE with dataflow
    #gen_full_pe_mapping(hardware_config, meta_config, macro_config)

def gen_full_pe_mapping(hardware_config, meta_config, macro_config):
    pass


def gen_pe_output_mapping(hardware_config, meta_config, macro_config):
    s = ""
    #Q: jia_arr --??--> jia?
    #2. INTER-PE here, extra-PE is in another flow
    # if is multicast, do the multicasting here
    #f = open("inter_pe.v", "w")
    #This includes the ADDER UNITS to add partial sums before the accumulator
    #There is an accumulator (i.e. the PSUM_BUFFER)
    #This will continuously add vectors into it and then will after completion be sent to the DMA unit for sending back to the DRAM
    f = open(meta_config["dossier"]+"/output_mapping_pe.v", "w")


    #COVER WINOGRAD CASE
    WINOGRAD_EN = False
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):
        WINOGRAD_EN = True

        
    s = "module OUTPUT_MAPPING_PE(\n\
        input clk,\n\
           input rst_n, \n"
    if(not WINOGRAD_EN):
        s += "input signed [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi,\n"
    else:
        s += "input signed [`WINO_MAX_PSUM_PRECISION_INT*`REQUIRED_PES - 1:0] zi,\n"
    
    s += "output   reg  signed [`PSUM_BUF_DATA - 1:0] zi_buf,\n\
            \n\
        input [`MAX_STRIDE_LOG-1:0] stride, \n\
        input [`MAX_KX_LOG-1:0] kx,\n\
        input [`MAX_KY_LOG-1:0] ky,\n\
        input [`MAX_X_LOG-1:0] x,\n\
        input [`MAX_Y_LOG-1:0] y, \n\
        input [`MAX_N_LOG-1:0] nc, \n\
        input [`MAX_I_LOG-1:0] ic, \n\
        input [`MAX_B_LOG-1:0] batch,\n\
        input [`MAX_PADDING_X_LOG-1:0] padding_x,\n\
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,\n\
        input [3:0] OP_TYPE,\n\
        input [3:0] SYSTOLIC_OP,\n\
        \n\
            input int_inference,\n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
                \n\
        input mult_done, \n\
        input tile_done, \n\
        output reg add_tree_ready \n\
            );"


    CONV2D = order_dataflows(hardware_config)     
    #Q: 问题关于顺序，比如，一个层是i3kx3ky3,那应该是winograd还是direct呢？ (todos)
    for idx, flows in enumerate(CONV2D):
      
        s += "    //dataflow" + str(idx+1)+"\n"
        fd = hardware_config["TILINGS"]["CONV2D"][flows]
        dataflow = fd["DATAFLOW"]

        if(len(CONV2D) == 1):
            pass
        else:
            if(flows == "DEFAULT"):
                s += "    else begin\n"
            else:
                if(idx > 0):
                    s += "   else "
                s += "   if ("+parse_dataflows(flows, dataflow)+") begin\n"

        if("DIRECT" == dataflow):
            

            s += "always@(*) begin\n"
            s += "add_tree_ready = mult_done;\n"
    
            #    zi       --> todos --> zi_buf(psum)
            SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)

            #s += "if(int_inference) begin\n"
            
            max_wei_prec = macro_config[ "MAX_WEI_PRECISION_INT" ]
            max_act_prec = macro_config[ "MAX_ACT_PRECISION_INT" ]
            s += "\n\n"

            states = -1
            for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
                for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                    states += 1
                    
                    #print(fd)
                    if("INT" in wei_type and "INT" in act_type):
                        wei_prec = wei_type.split("INT")[1]
                        act_prec = act_type.split("INT")[1]
                        if(states == 0):
                            s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                        else:
                            s += "else if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                            
                        w_ratio = max_wei_prec // int(wei_prec)
                        a_ratio = max_act_prec // int(act_prec)
                        
                        s += "//" + str(w_ratio) + " , " + str(a_ratio) + "\n"
                        gcd = int(np.gcd(w_ratio,a_ratio))
                        #print(w_ratio,a_ratio,gcd)
                        if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                            tmp_aaw = a_ratio//gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
                                                                
                        if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                            tmp_wwa = w_ratio//gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

                        if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                            tmp_wa = gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd
                            


                        MAX_KX = macro_config["MAX_KX"]
                        MAX_KY = macro_config["MAX_KY"]
                        MAX_I  = macro_config["MAX_I"]
                        #like multi-cast but for accumulator.
                        #zi-->z_buf (accumulator)(TODOS)
                        inner_loop = -1
                        loop_idx_ = -1
                        
                        if("ACCUMULATE" in hardware_config):
                            s += "assign zi_buf = zi;\n"
                            pass
                        else:
                                                    
                            for n in range(int(fd["TN"])):
                                for b in range(int(fd["TB"])):
                                    for x in range(int(fd["TX"])):
                                        for y in range(int(fd["TY"])):
                                            
                                            yuan = []
                                            for kx in range(int(fd["TKX"])):
                                                for ky in range(int(fd["TKY"])):
                                                    for i in range(int(fd["TI"])):
                                                        inner_loop += 1
                                                        #idx = (y +  (int(fd["TY"]))*\
                                                        #        (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   int(fd["TN"]) *(i +\
                                                        #             int(fd["TI"])*(ky  + int(fd["TKY"])*(kx  + int(fd["TKX"])*0)))))))
                                                        idx = inner_loop
                                                        idx = str(idx)
                                                        yuan.append("zi[("+idx+"+1)*("+act_prec+"+"+wei_prec+")-1:("+idx+")*("+act_prec+"+"+wei_prec+")]")
                                            loop_idx_ += 1
                                            idx = loop_idx_
                                            

                                            #(y +  (int(fd["TY"]))*\
                                            #                    (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   0*int(fd["TN"])))))
                                            #print(y,x,b,n,idx)
                                            idx = str(idx)
                                            #TODOS `MAX_PSUM_PRECISION + ...多一点?, (MAX_PSUM_PRECISION + log2(TKX*TKY*TI))
                                            #s += "assign zi_buf[("+idx+"+1)*`MAX_ACC_PRECISION-1:("+idx+")*`MAX_ACC_PRECISION] = " + "+".join(yuan)+";\n"
                                            

                                            psum_prec = int(act_prec) +int(wei_prec) + int(np.log2(MAX_KX*MAX_KY*MAX_I))
                                            psum_prec = str(psum_prec)
                                            
                                            s += "zi_buf[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1:("+idx+")*("+psum_prec+")] = " + "+".join(yuan)+";\n"
                                            #s += "zi_buf[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1]
                                            
                                            if(int(psum_prec) > int( act_prec) + int( wei_prec)):
                                            #sign extend if necessary
                                                s += "zi_buf[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"] = \
                                                    {("+psum_prec+"-"+wei_prec+"-"+act_prec+"){zi_buf[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1]}};\n"
 
                                            #(TODOS) psum precision can be altered, i.e. maybe we just want 16 bits
                                            

                            if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] //= tmp_aaw
                                                                    
                            if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] //= tmp_wwa

                            if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] //= gcd
                                            
                            #s += "assign jia[("+loop_idx+"+1)*`MAX_WEI_PRECISION-1:("+loop_idx+")*`MAX_WEI_PRECISION] = \
                            #    jia_buf[("+jia_loop_idx+"+1)*`MAX_WEI_PRECISION-1:("+jia_loop_idx+")*`MAX_WEI_PRECISION];\n"
                            # s += "assign yi[("+loop_idx+"+1)*`MAX_ACT_PRECISION-1:("+loop_idx+")*`MAX_ACT_PRECISION] = \
                            #    yi_buf[("+yi_loop_idx+"+1)*`MAX_ACT_PRECISION-1:("+yi_loop_idx+")*`MAX_ACT_PRECISION];\n"
                            s += "    end\n"
                #(TODOS) if is floating?
            #s += "end\n"

            s += "else begin\n"
            s += "zi_buf = 0;\n"
            s += "end\n"
            
            s += "end\n"       
        elif("WINOGRAD" in dataflow and "STRIDE_2" in dataflow):
            pass 
        elif("WINOGRAD" == dataflow):
            #推动
            A_LOOP = ["TX", "TY", "TI", "TB"]
            W_LOOP = ["TN", "TI"] #Note, the TKX, TKY is altered into the TX, TY shape (i.e. prepare weights)
            #4. 后处理（就时A     W*C     AT) 的A和AT可能要处理一下在后端，还是留给ACC做？

            #    zi       --> todos --> zi_buf(psum)

            import wincnn

            s += "always@(*) begin\n\
                      add_tree_ready = mult_done;\n\
                  end\n"

            SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)
                
            #We assume TX == TY, TKX == TKY (todos)
            #print(df_d
            wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6],
                int(fd["WINO_TX"]), int(fd["TKX"]))
            MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])
            MU_A = max([gg.denominator for gg in np.array(wino_AT).reshape(-1)])
            wino_G = np.array(MU*wino_G).astype('int')
            wino_A = np.array(wino_AT).transpose()
            wino_GT = np.array(wino_G).transpose()
            wino_B = np.array(wino_BT).transpose()
            wino_BT = np.array(wino_BT)
            wino_AT = np.array(wino_AT)
            print(wino_G, wino_GT)
                      
            if("WINO_PRE_WEIGHT" in dataflow and dataflow["WINO_PRE_WEIGHT"]):
                # jia_buf(wei) --> jia
                pass
                # yi_buf(act)  --> todos -->  yi
            else:
            
                ##OUTPUT, AT*PSUM
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                            for o_x in range(int(fd["WINO_TX"])):
                                for i in range(int(fd["TI"])):
                                    for n in range(int(fd["TN"])):
                                        for b in range(int(fd["TB"])):
                                            s += "wire signed [`MAX_PSUM_PRECISION -1:0] wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+";\n"
                                            row = []
                                            for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):           
                                                loop_idx = (w_y +  (int(fd["WINO_TY"])+int(fd["TKY"])-1)*\
                                                        (w_x    +    (int(fd["WINO_TX"]) + int(fd["TKX"])-1)*(i   +  int(fd["TI"])*(n     +   int(fd["TN"]) *(b +\
                                                         xx//int(fd["WINO_TX"]) + int(fd["TX"])//int(fd["WINO_TX"])*(yy//int(fd["WINO_TY"]) +  int(fd["TY"])//int(fd["WINO_TY"])*0) )))))
                                                row.append("zi[("+str(loop_idx)+"+1)*`WINO_MAX_PSUM_PRECISION-1:"+str(loop_idx)+"*`WINO_MAX_PSUM_PRECISION] * "+str(wino_AT[o_x][w_x]))
                                            
                                            s += "assign wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+" = " + "+".join(row) + ";\n"
                                            
                                            
                ##OUTPUT, PSUM*A
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        for o_y in range(int(fd["WINO_TX"])):
                            for o_x in range(int(fd["WINO_TX"])):
                                for i in range(int(fd["TI"])):
                                    for n in range(int(fd["TN"])):
                                        for b in range(int(fd["TB"])):
                                            s += "wire signed [`WINO_MAX_PSUM_PRECISION -1:0] wino_psum_final_"+"_".join([str(jj) for jj in [xx, yy, o_x, o_y, b, i, n]])+";\n"
                                            row = []
                                            for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):           
                                                loop_idx = (w_y +  (int(fd["WINO_TY"])+int(fd["TKY"])-1)*\
                                                        (w_x    +    (int(fd["WINO_TX"]) + int(fd["TKX"])-1)*(i   +  int(fd["TI"])*(n     +   int(fd["TN"]) *(b +\
                                                         xx//int(fd["WINO_TX"]) + int(fd["TX"])//int(fd["WINO_TX"])*(yy//int(fd["WINO_TY"]) +  int(fd["TY"])//int(fd["WINO_TY"])*0) )))))
                                                row.append( "wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+ " * "+str(wino_A[w_y][o_y]))
                                            
                                            s += "assign wino_psum_final_"+"_".join([str(jj) for jj in [xx, yy, o_x, o_y, b, i, n]])+" = (" + "+".join(row) + ")/"+str(MU*MU)+";\n"
                                                                               

                
                #FINAL SCALING AND SEND TO OUTPUT (我们需要做加法吗？)
                s += "always@(*) begin\n"
                
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        for o_y in range(int(fd["WINO_TX"])):
                            for o_x in range(int(fd["WINO_TX"])):
                                    for n in range(int(fd["TN"])):
                                        for b in range(int(fd["TB"])):

                                            yuan = []
                                            for i in range(int(fd["TI"])):
                                                yuan.append("wino_psum_final_"+"_".join([str(jj) for jj in [xx, yy, o_x, o_y, b, i, n]])+"")


                                                
                                            psum_prec = int(act_prec) +int(wei_prec) + int(np.log2(MAX_KX*MAX_KY*MAX_I))
                                            psum_prec = str(psum_prec)
                                                                  

                                            #s += " zi_buf[("+str(loop_idx)+"+1)*-1:"+str(loop_idx)+"*`MAX_WEI_PRECISION] <= wino_w_final_"+"_".join([str(jj) for jj in [w_x, w_y, i, n]])+";\n"
                                            idx = (yy+o_y +  (int(fd["TY"]))*\
                                                                (xx+o_x   +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   0*int(fd["TN"])))))
                                            
                                            #print(y,x,b,n,idx)
                                            idx = str(idx)
                                            #TODOS `MAX_PSUM_PRECISION + ...多一点?, (MAX_PSUM_PRECISION + log2(TKX*TKY*TI))
                                            #s += "assign zi_buf[("+idx+"+1)*`MAX_ACC_PRECISION-1:("+idx+")*`MAX_ACC_PRECISION] = " + "+".join(yuan)+";\n"
                                            s += "zi_buf[("+idx+"+1)*`WINO_MAX_ACC_PRECISION-1:("+idx+")*`WINO_MAX_ACC_PRECISION] <= " + "+".join(yuan)+";\n"
                s += "end\n"
                
                
        elif("WINOGRAD_SYSTOLIC" in dataflow):
            pass

        #2.4. other ? like super pe ? (todos)
        #add any flows within this PE unit (tensor unit) such as linear layers, pooling etc. (todos)
        ######################################################
        #s += "    end\n"

        elif(dataflow == "SPARSE_DIRECT_LARGE_TILING"):

            st = fd["SPARSITY"]["SPARSE_TILING"]

            #wai_quan
            
            SPARSE_OUT = fd["TX"]*fd["TY"]*fd["TB"]*fd["TN"]

                                        
            MAX_KX = macro_config["MAX_KX"]
            MAX_KY = macro_config["MAX_KY"]
            MAX_I  = macro_config["MAX_I"]

            ADJUSTED_PREC = "(`MAX_PSUM_PRECISION_INT+%d)" % (int(np.log2(MAX_KX*MAX_KY*MAX_I)))
            
            s += "reg ["+str(SPARSE_OUT)+"*(%s) -1:0] zi_buffered;\n" % ( ADJUSTED_PREC )

            s += "reg xin_tile;\n"

            s += "always@(posedge clk or negedge rst_n) begin\n\
                      if(~rst_n) begin \n\
                            add_tree_ready <= 0; \n\
                      end else begin\n\
                          add_tree_ready   <= tile_done; \n\
                      end\n\
                     end\n"

            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                            xin_tile <= 0; \n\
                    end else begin \n\
                        if(mult_done) begin \n\
                            if(tile_done) begin \n\
                                xin_tile <= 1;\n\
                            end else begin \n\
                                xin_tile <= 0;\n\
                            end \n\
                        end \n\
                    end \n\
                  end\n"

            #直接映射
            if(st["TN"]*st["TB"]*st["TX"]*st["TY"] == fd["TN"]*fd["TB"]*fd["TX"]*fd["TY"]):

                
                ####################################ZI_BUFFERED --> ZI_SIGNED
                #z-terms
                s += "reg [%s*%s-1:0] zi_signed;\n" %("`REQUIRED_PES", ADJUSTED_PREC)
  
                s += "always@(* ) begin\n"
                      
                ############################ADAPTIVE
                SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                    WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)
                
                max_wei_prec = macro_config[ "MAX_WEI_PRECISION_INT" ]
                max_act_prec = macro_config[ "MAX_ACT_PRECISION_INT" ]
                s += "\n\n"

                states = -1
                for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
                    for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                        states += 1
                        
                        #print(fd)
                        if("INT" in wei_type and "INT" in act_type):
                            wei_prec = wei_type.split("INT")[1]
                            act_prec = act_type.split("INT")[1]
                            if(states == 0):
                                s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                            else:
                                s += "else if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                                
                            w_ratio = max_wei_prec // int(wei_prec)
                            a_ratio = max_act_prec // int(act_prec)
                            
                            s += "//" + str(w_ratio) + " , " + str(a_ratio) + "\n"
                            gcd = int(np.gcd(w_ratio,a_ratio))
                            #print(w_ratio,a_ratio,gcd)
                            if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                                tmp_aaw = a_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
                                                                    
                            if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                                tmp_wwa = w_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

                            if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                                tmp_wa = gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd
                                
                            ############################ADAPTIVE

                            #zi_buffered <= zi_buffered + 

                            loop_idx = 0

                            for n in range(int(st["TN"])):
                                for b in range(int(st["TB"])):
                                    for x in range(int(st["TX"])):
                                        for y in range(int(st["TY"])):
                                            idx = str(loop_idx)


                                            yuan = []
                                            inner_loop = loop_idx*int(st["TKX"])*int(st["TKY"])*int(st["TI"])
                                            for kx in range(int(st["TKX"])):
                                                for ky in range(int(st["TKY"])):
                                                    for i in range(int(st["TI"])):

                                                        idx = inner_loop
                                                        idx = str(idx)
                                                        #yuan.append("zi_signed[("+idx+"+1)*("+act_prec+"+"+wei_prec+")-1:("+idx+")*("+act_prec+"+"+wei_prec+")]")
                                                        


                                                        
                                                        psum_prec = int(act_prec) +int(wei_prec) + int(np.log2(MAX_KX*MAX_KY*MAX_I))
                                                        psum_prec = str(psum_prec)
                                                        buf_prec = str(int(act_prec) +int(wei_prec))
                                                        
                                                        zi_buffer = "zi[("+idx+"+1)*"+buf_prec+"-1:("+idx+")*"+buf_prec+"]"

                                                        zi_buf = "zi_signed[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1:("+idx+")*("+psum_prec+")]"
                                                        
                                                        s += zi_buf + " =  " +  zi_buffer +   "  ;\n"            
                                                        if(int(psum_prec) > int( act_prec) + int( wei_prec)):
                                                            #sign extend if necessary
                                                            s += "zi_signed[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"] = \
                                                                {("+psum_prec+"-"+wei_prec+"-"+act_prec+"){zi_signed[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1]}};\n"
                                                        inner_loop += 1
                                            loop_idx += 1


                            s += "end \n"
                            
                s += "end\n"




                ####################################ZI_SIGNED --> ZI_BUF
                
                s += "always@(posedge clk or negedge rst_n) begin\n\
                      if(~rst_n) begin \n\
                            zi_buffered <= 0; \n\
                      end else begin\n"

                SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                    WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)
                
                max_wei_prec = macro_config[ "MAX_WEI_PRECISION_INT" ]
                max_act_prec = macro_config[ "MAX_ACT_PRECISION_INT" ]
                s += "\n\n"

                states = -1
                for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
                    for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                        states += 1
                        
                        #print(fd)
                        if("INT" in wei_type and "INT" in act_type):
                            wei_prec = wei_type.split("INT")[1]
                            act_prec = act_type.split("INT")[1]
                            if(states == 0):
                                s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                            else:
                                s += "else if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                                
                            w_ratio = max_wei_prec // int(wei_prec)
                            a_ratio = max_act_prec // int(act_prec)
                            
                            s += "//" + str(w_ratio) + " , " + str(a_ratio) + "\n"
                            gcd = int(np.gcd(w_ratio,a_ratio))
                            #print(w_ratio,a_ratio,gcd)
                            if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                                tmp_aaw = a_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
                                                                    
                            if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                                tmp_wwa = w_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

                            if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                                tmp_wa = gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd
                                
                            ############################ADAPTIVE

                            #zi_buffered <= zi_buffered + 

                            loop_idx = 0

                            for n in range(int(st["TN"])):
                                for b in range(int(st["TB"])):
                                    for x in range(int(st["TX"])):
                                        for y in range(int(st["TY"])):
                                            idx = str(loop_idx)

                                            
                                            psum_prec = int(act_prec) +int(wei_prec) + int(np.log2(MAX_KX*MAX_KY*MAX_I))
                                            psum_prec = str(psum_prec)

                                            
                                            zi_buffer = "zi_buffered[("+idx+"+1)*"+psum_prec+"-1:("+idx+")*"+psum_prec+"]"
                                            
                                            

                                            yuan = []
                                            inner_loop = loop_idx*int(st["TKX"])*int(st["TKY"])*int(st["TI"])
                                            for kx in range(int(st["TKX"])):
                                                for ky in range(int(st["TKY"])):
                                                    for i in range(int(st["TI"])):

                                                        idx = inner_loop
                                                        idx = str(idx)
                                                        yuan.append("zi_signed[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")]")
                                                        inner_loop += 1
                                                        
                                            

                                            s += "if(mult_done) begin \n\
                                                   if(xin_tile == 1) begin \n\
                                                       "+zi_buffer+" <= "+  "+".join(yuan)+";\n\
                                                   end else begin \n\
                                                       "+zi_buffer+" <= "+ zi_buffer + " + " + "+".join(yuan)+";\n\
                                                   end\n"

                                            idx = str(loop_idx)
                                            #zi_buf = "zi_buf[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1:("+idx+")*("+psum_prec+")]"
                                            #zi_buf = "zi_buf[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")]"
                                            #s += zi_buf + " =  " +  zi_buffer +   "  ;\n"            
                                            #if(int(psum_prec) > int( act_prec) + int( wei_prec)):
                                            #    #sign extend if necessary
                                            #    s += "zi_buf[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"] = \
                                            #        {("+psum_prec+"-"+wei_prec+"-"+act_prec+"){zi_buf[("+idx+")*("+psum_prec+")+"+act_prec +"+"+ wei_prec+"-1]}};\n"
                                            loop_idx += 1

                                            s += "end\n"

                            s += "end \n"
                            
                s += "end \n"
                s += "end\n"

                #final map
                s += "always@(*) begin\n"
                s += "\n\n"
                states = -1
                for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
                    for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                        states += 1
                        if("INT" in wei_type and "INT" in act_type):
                            wei_prec = wei_type.split("INT")[1]
                            act_prec = act_type.split("INT")[1]
                            if(states == 0):
                                s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                            else:
                                s += "else if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                            w_ratio = max_wei_prec // int(wei_prec)
                            a_ratio = max_act_prec // int(act_prec)
                            s += "//" + str(w_ratio) + " , " + str(a_ratio) + "\n"
                            gcd = int(np.gcd(w_ratio,a_ratio))
                            if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                                tmp_aaw = a_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
                                                                    
                            if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                                tmp_wwa = w_ratio//gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

                            if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                                tmp_wa = gcd
                                fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd
                            loop_idx = 0
                            for n in range(int(st["TN"])):
                                for b in range(int(st["TB"])):
                                    for x in range(int(st["TX"])):
                                        for y in range(int(st["TY"])):
                                            idx = str(loop_idx)
                                            psum_prec = int(act_prec) +int(wei_prec) + int(np.log2(MAX_KX*MAX_KY*MAX_I))
                                            psum_prec = str(psum_prec)
                                            zi_buffer = "zi_buffered[("+idx+"+1)*"+psum_prec+"-1:("+idx+")*"+psum_prec+"]"
                                            zi_buf = "zi_buf[("+idx+"+1)*("+psum_prec+")-1:("+idx+")*("+psum_prec+")]"
                                            s += zi_buf + " =  " +  zi_buffer +   "  ;\n"
                                            loop_idx += 1
                                            #s += "end\n"
                            s += "end \n"
                s += "end\n"


            

            
            #乱序映射
            else:
                print("Not implt yet, non-structured sparsity")
                exit()
                
                    
            
                        

            
    #s += "end\n"
    

    s += "endmodule\n\n"
    
    print("\n// GEN_PE VERILOG - DONE\n")



    print(s)
    f.write(s)
    f.close()




###########################################################################################
#TODOS
#BUFFER -> GEN_PE_INTERNAL_MAPPING -> PE --> GEN_PE_OUT_MAPPING --> PSUM BUFFER
def gen_pe_input_mapping(hardware_config, meta_config, macro_config):
    s = ""
    #Q: jia_arr --??--> jia?
    #2. INTER-PE here, extra-PE is in another flow
    # if is multicast, do the multicasting here
    #f = open("inter_pe.v", "w")
    f = open(meta_config["dossier"]+"/input_mapping_pe.v", "w")


    #COVER WINOGRAD CASE
    WINOGRAD_EN = False
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):
        WINOGRAD_EN = True        
   
    s = "module INTER_PE(\n"


    #ADD SPARSITY MAP CONFIGURATION
    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        s += "input [`WEI_SPARSITY_MAP_BUF_DATA-1:0] jia_sparse_map,\n"
    
    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] > 0):
        s += "input [`ACT_SPARSITY_MAP_BUF_DATA-1:0] yi_sparse_map,\n"  
    
    s += "input clk,\n\
        input rst_n,\n\
        input [`WEI_BUF_DATA-1:0] jia_buf,\n"

    if(WINOGRAD_EN):
        s += "output reg [`WINO_MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n"
    else:
        s += "output reg [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n"
    s += "input [`ACT_BUF_DATA-1:0] yi_buf,\n"

    if(WINOGRAD_EN):
        s += "output reg [`WINO_MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n"
    else:
        s += "output reg [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n"

    s += "\n\
        input [`MAX_STRIDE_LOG-1:0] stride, \n\
        input [`MAX_KX_LOG-1:0] kx,\n\
        input [`MAX_KY_LOG-1:0] ky,\n\
        input [`MAX_X_LOG-1:0] x,\n\
        input [`MAX_Y_LOG-1:0] y, \n\
        input [`MAX_N_LOG-1:0] nc, \n\
        input [`MAX_I_LOG-1:0] ic, \n\
        input [`MAX_B_LOG-1:0] batch,\n\
        input [`MAX_PADDING_X_LOG-1:0] padding_x,\n\
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,\n\
        input [3:0] OP_TYPE,\n\
        input [3:0] SYSTOLIC_OP,\n\
            \n\
        input [`MAX_KX_LOG-1:0] kkx,\n\
        input [`MAX_KY_LOG-1:0] kky,\n\
        input [`MAX_X_LOG-1:0] xx,\n\
        input [`MAX_Y_LOG-1:0] yy, \n\
        input [`MAX_X_LOG-1:0] xxx,\n\
        input [`MAX_Y_LOG-1:0] yyy, \n\
        input [`MAX_N_LOG-1:0] nn, \n\
        input [`MAX_I_LOG-1:0] ii, \n\
        input [`MAX_N_LOG-1:0] nnn, \n\
        input [`MAX_I_LOG-1:0] iii, \n\
        input [`MAX_B_LOG-1:0] bb,\n\
            \n\
            input int_inference,\n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision, \n"

    s += "input wei_sys_en,\n\
          input act_sys_en,\n"

    s += "input [5:0] jia_sys_jie, \n\
          input [5:0] yi_sys_jie, \n"

    s += "output sparse_stall, \n"

    s += "input mac_en, \n"
    s += "output tile_done_flag, \n"

    s += "input mult_done,\n\
          input pre_mult_done\n"
    
    s += ");\n"

    
    CONV2D = order_dataflows(hardware_config)
    print(CONV2D)


    

    '''
    s += "// The dataflow (and reconfigurability)\n"
    #Q: jia_arr -- PING_PONG -->  jia
    #2. INTER-PE AND EXTRA-PE CONNECTIONS (assume double buffers in the flow)
    #otherwise it is not efficient!
            
    s += "reg [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia_systolic_buf;\n"
    s += "reg [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia_systolic_buf_mirror;\n"
    s += "reg [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi_systolic_buf;\n"
    s += "reg [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi_systolic_buf_mirror;\n"
    s += "reg [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi_systolic_buf;\n"
    #s += "reg [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi_systolic_buf_mirror;\n"
    s += "reg yinyang = 0;\n"


    # ping-pong mechanism to reduce latency, pipeline the memory access + mapping to MAC units
    s += "always@(*) begin\n\
            if(yinyang)begin\n\
                jia = jia_systolic_buf;\n\
                yi = yi_systolic_buf; \n\
            end else begin\n\
                jia = jia_systolic_buf_mirror;\n\
                yi = yi_systolic_buf_mirror;\n\
            end\n\
        end\n"

    #jia_arr --> jia_systolic_buf --> jia
    
    s += "always@(posedge clk) begin\n\
              yinyang <= ~yiyang;\n"
    '''

    #s += "always@(*) begin\n"

    print(CONV2D)       
    #Q: 问题关于顺序，比如，一个层是i3kx3ky3,那应该是winograd还是direct呢？ (todos)
    for idx, flows in enumerate(CONV2D):
      
        s += "    //dataflow" + str(idx+1)+"\n"
        fd = hardware_config["TILINGS"]["CONV2D"][flows]
        dataflow = fd["DATAFLOW"]

        if(len(CONV2D) == 1):
            pass
        else:
            if(flows == "DEFAULT"):
                s += "    else begin\n"
            else:
                if(idx > 0):
                    s += "   else "
                s += "   if ("+parse_dataflows(flows, dataflow)+") begin\n"


        ############################################
        # (SPARSE) DIRECT DATAFLOW
        #
        #  JIA_BUF --> jia_buf_loaded (direct/sparse direct) 
        #  JIA_BUF_0, JIA_BUF_1, ... --> jia_buf_loaded (systolic load)
        #  JIA_BUF -uncompress-> jia_buf_loaded (compressed direct/sparse direct)
        ############################################
        if("SPARSE_DIRECT_LARGE_TILING" == dataflow or "DIRECT" == dataflow):

            #其它的?

            ###################################
            # SYSTOLIC
            ###################################

            from utils import SYSTOLIC_WEIGHT_LOAD_CYCLES, SYSTOLIC_ACT_LOAD_CYCLES, SYSTOLIC_WEI_LOOP_ORDER

            WEI_SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(hardware_config, fd)

            # jia_buf(wei) --> todos --> jia
            # yi_buf(act)  --> todos -->  yi
            #    zi       --> todos --> zi_buf(psum)
            SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)
            
            # jia_buf --> jia
            #print(WULI_LOOP_WEI)
            
            #s += "always@(posedge clk) begin\n"
            
            #s += "if(int_inference) begin\n"
            
            max_wei_prec = macro_config[ "MAX_WEI_PRECISION_INT" ]
            max_act_prec = macro_config[ "MAX_ACT_PRECISION_INT" ]
            s += "\n\n"

                         
            from utils import SYSTOLIC_WEIGHT_TILES
                        

            #print(fd)
            #exit(0)
            #fd = SYSTOLIC_WEIGHT_TILES(hardware_config, fd)


            s += "reg [`WEI_BUF_DATA*"+str(WEI_SYS_CYCLES)+"-1:0] jia_buf_loaded;\n"
            #s += "reg [`ACT_BUF_DATA*"+str(ACT_SYS_CYCLES)+"-1:0] yi_buf_loaded;\n"

            s += "always@(posedge clk) begin\n"




            #
            if(WEI_SYS_CYCLES == 1):
                s += "jia_buf_loaded <= jia_buf;\n"
            else:

                for sys in range(WEI_SYS_CYCLES):
                    s += "if(jia_sys_jie == " + str(sys) + " & wei_sys_en) begin \n"
                    s += "  jia_buf_loaded["+str(sys+1)+"*`WEI_BUF_DATA-1:"+str(sys)+"*`WEI_BUF_DATA] <= jia_buf;\n"
                    s += "end\n"
                    
            s += "end\n"



            ###################################
            # ADAPTIVE
            ###################################



            from utils import MAX_ADAPTIVE_RATIOS

            max_quan, max_ru = MAX_ADAPTIVE_RATIOS(hardware_config)
            
            
            ###################################
            # SPARSITY
            ###################################

            #jia_buf(wei) --> jia_sparse --> jia
            #yi_buf(act)  --> yi_sparse  --> yi



            #(TODOS) systolic inter-pe ?

            SPARSE_PE = fd["TX"]*fd["TY"]*fd["TKX"]*fd["TKY"]*fd["TB"]*fd["TI"]*fd["TN"]
            
            s += "reg ["+str(SPARSE_PE)+"*`MAX_WEI_PRECISION_INT -1:0] jia_buffered;\n"
            s += "reg ["+str(SPARSE_PE)+"*`MAX_ACT_PRECISION_INT -1:0] yi_buffered;\n"


            #NONE/NONE_SPARSE_MAP, NONE_INDEXING_MAP (都是即使计算的)
            #SPARSE_MAP, INDEXING_MAP (已经算好的)
            if( "NONE" in fd["SPARSITY"]["WEI_ENCODING"]  and "WEI" in fd["SPARSITY"]["VALUE_SPARSITY"]):        
                SPARSE_PE = fd["TX"]*fd["TY"]*fd["TKX"]*fd["TKY"]*fd["TB"]*fd["TI"]*fd["TN"]
                if( fd["SPARSITY"]["WEI_ENCODING"] == "NONE_INDEXING_MAP"):
                    s += "reg ["+str(SPARSE_PE*max_quan)+" -1:0] jia_sparse_map;\n"
                else:
                    s += "reg ["+str(SPARSE_PE*max_quan)+" -1:0] jia_sparse_map;\n"
            else:
                s += "reg ["+str(SPARSE_PE*max_quan)+" -1:0] jia_sparse_map_buffered;\n"

            if( "NONE" in fd["SPARSITY"]["ACT_ENCODING"]and "ACT" in fd["SPARSITY"]["VALUE_SPARSITY"]):        
                SPARSE_PE = fd["TX"]*fd["TY"]*fd["TKX"]*fd["TKY"]*fd["TB"]*fd["TI"]*fd["TN"]
                if( fd["SPARSITY"]["ACT_ENCODING"] == "NONE_INDEXING_MAP"):
                    s += "reg ["+str(SPARSE_PE*max_ru)+" -1:0] yi_sparse_map;\n"
                else:
                    s += "reg ["+str(SPARSE_PE*max_ru)+" -1:0] yi_sparse_map;\n"
            else:
                s += "reg ["+str(SPARSE_PE*max_ru)+" -1:0] yi_sparse_map_buffered;\n"

            ###################################
            # LOOP
            ###################################

            if True: #DEBUG
                if True:
                    if True:
                        loop_idx_ = -1
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):
                                                    
                                        for kx in range(int(fd["TKX"])):
                                            for ky in range(int(fd["TKY"])):
                                                for i in range(int(fd["TI"])):

                                                    loop_idx_ += 1
                                                    s += "reg [`MAX_WEI_PRECISION-1:0] jia_buffered_"+str(loop_idx_)+";\n"
                                                    s += "reg [`MAX_ACT_PRECISION-1:0] yi_buffered_"+str(loop_idx_)+";\n"

                                                    
            s += "always@(*) begin \n"

            for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
                for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                    #print(fd)
                    if("INT" in wei_type and "INT" in act_type):
                        wei_prec = wei_type.split("INT")[1]
                        act_prec = act_type.split("INT")[1]
                        s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n"
                        w_ratio = max_wei_prec // int(wei_prec)
                        a_ratio = max_act_prec // int(act_prec)
                        
                        s += "//" + str(w_ratio) + " , " + str(a_ratio) + "\n"
                        gcd = int(np.gcd(w_ratio,a_ratio))
                        #print(w_ratio,a_ratio,gcd)
                        if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                            tmp_aaw = a_ratio//gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
                                                                
                        if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                            tmp_wwa = w_ratio//gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

                        if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                            tmp_wa = gcd
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd
                               
                    
                        #print(fd)
                        loop_idx_ = -1
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):
                                                    
                                        for kx in range(int(fd["TKX"])):
                                            for ky in range(int(fd["TKY"])):
                                                for i in range(int(fd["TI"])):

                                                    loop_idx_ += 1
                                                    #loop_idx = (y +  (int(fd["TY"]))*\
                                                    #    (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   int(fd["TN"]) *(i +\
                                                    #         int(fd["TI"])*(ky  + int(fd["TKY"])*(kx  + int(fd["TKX"])*0)))))))
                
                                                    #loop_idx = (y +  (int(fd["TY"]))*\
                                                    #    (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   int(fd["TN"]) *(i +\
                                                    #         int(fd["TI"])*(ky  + int(fd["TKY"])*(kx  + int(fd["TKX"])*0)))))))

                                                    #print(loop_idx)
                                                    loop_idx = "( " + str(fd["TKX"]*fd["TKY"]*fd["TI"]*fd["TN"]*fd["TB"]*fd["TX"]*fd["TY"]) + "-1 - " + str(loop_idx_)+")"
                                                    
                                                    jia_loop_idx = gen_index(WULI_LOOP_WEI, fd, ky=ky,kx=kx,i=i,n=n,use_macros=True)
                                                    yi_loop_idx =  gen_index(WULI_LOOP_ACT, fd, x=x,y=y,ky=ky,kx=kx,i=i,b=b,use_macros=True)
                                                    
                                                    s += "    jia_buffered[("+loop_idx+"+1)*"+wei_prec+"-1:("+loop_idx+")*"+wei_prec+"] = \
                                                        jia_buf_loaded[("+jia_loop_idx+"+1)*"+wei_prec+"-1:("+jia_loop_idx+")*"+wei_prec+"];\n"
                                                    s += "    yi_buffered[("+loop_idx+"+1)*"+act_prec+"-1:("+loop_idx+")*"+act_prec+"] = \
                                                        yi_buf[("+yi_loop_idx+"+1)*"+act_prec+"-1:("+yi_loop_idx+")*"+act_prec+"];\n"
 
                                                    #s += "end\n"
                                                    s += "   jia_buffered_"+str(eval(loop_idx))+" = jia_buffered[("+loop_idx+"+1)*"+wei_prec+"-1:("+loop_idx+")*"+wei_prec+"];\n"
                                                    s += "   yi_buffered_"+str(eval(loop_idx))+" = yi_buffered[("+loop_idx+"+1)*"+act_prec+"-1:("+loop_idx+")*"+act_prec+"];\n"



            
                                                    #需要从实际的JIA提取这个信息
                                                    if("SPARSE" in fd['DATAFLOW']):
                                                        if("NONE" in fd["SPARSITY"]["WEI_ENCODING"]  and "WEI" in fd["SPARSITY"]["VALUE_SPARSITY"]):        
                                                            s += "jia_sparse_map["+loop_idx+"] = ~(jia_buffered[("+loop_idx+"+1)*"+wei_prec+"-1:("+loop_idx+")*"+wei_prec+"] == 0 );\n"
                                                        elif(fd["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                                                            s += "jia_sparse_map_buffered["+loop_idx+"] = jia_sparse_map["+str(jia_loop_idx)+"];\n"
                                                            pass #Nothing to do as we already have it
                                                        else:
                                                            pass #Nothing to do as we already have it

                                                        if("NONE" in fd["SPARSITY"]["ACT_ENCODING"]  and "ACT" in fd["SPARSITY"]["VALUE_SPARSITY"]):
                                                            s += "yi_sparse_map["+loop_idx+"] = ~(yi_buffered[("+loop_idx+"+1)*"+act_prec+"-1:("+loop_idx+")*"+act_prec+"] == 0 );\n"
                                                        elif(fd["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
                                                            s += "yi_sparse_map_buffered["+loop_idx+"] = yi_sparse_map["+str(yi_loop_idx)+"];\n"
                                                            pass #Nothing to do as we already have it
                                                        else:
                                                            pass #Nothing to do as we already have it




                


                        if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] //= tmp_aaw
                                                                
                        if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] //= tmp_wwa

                        if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                            fd[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] //= gcd
                                        
                        #s += "assign jia[("+loop_idx+"+1)*`MAX_WEI_PRECISION-1:("+loop_idx+")*`MAX_WEI_PRECISION] = \
                        #    jia_buf[("+jia_loop_idx+"+1)*`MAX_WEI_PRECISION-1:("+jia_loop_idx+")*`MAX_WEI_PRECISION];\n"
                        # s += "assign yi[("+loop_idx+"+1)*`MAX_ACT_PRECISION-1:("+loop_idx+")*`MAX_ACT_PRECISION] = \
                        #    yi_buf[("+yi_loop_idx+"+1)*`MAX_ACT_PRECISION-1:("+yi_loop_idx+")*`MAX_ACT_PRECISION];\n"
                        s += "    end\n"
                #(TODOS) if is floating?
            #s += "end\n"

            #end of this dataflow
            s += "end\n"

            ###################################
            # BUFFERED
            ###################################

            if(dataflow == "DIRECT"):
                s += "always@(*) begin\n\
                            jia = jia_buffered;\n\
                            yi = yi_buffered;\n\
                    end\n"

                s += "assign sparse_stall = 0;\n"

            elif(dataflow == "SPARSE_DIRECT_LARGE_TILING"):

                #下个地址
                #s += "assign sparse_stall = 1;\n"

                st = fd["SPARSITY"]["SPARSE_TILING"] 
                PE = st["TX"]*st["TY"]*st["TKX"]*st["TKY"]*st["TB"]*st["TI"]*st["TN"]
                OUTER_PE = fd["TX"]*fd["TY"]*fd["TKX"]*fd["TKY"]*fd["TB"]*fd["TI"]*fd["TN"]
                
                PE_ADDR_LEN = int(np.log2(OUTER_PE)+1)


                #地址
                
                s += "reg sparse_tile_done;\n"
                s += "assign tile_done_flag = sparse_tile_done & mult_done;\n"

                end_conds = []
                for n in range(int(st["TN"])):
                    for b in range(int(st["TB"])):
                        for x in range(int(st["TX"])):
                            for y in range(int(st["TY"])):
                                #inner loop
                                inner_loop = 0
                                s += "reg ["+str(PE_ADDR_LEN)+"-1:0] gen_addr_%d_%d_%d_%d;\n" %(n, b, x, y)
                                s += "reg ["+str(PE_ADDR_LEN)+"-1:0] end_addr_%d_%d_%d_%d;\n" %(n, b, x, y)

                                end_conds.append(">= ")
                                gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                wei_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                
                                s += "always@(posedge clk or negedge rst_n) begin\n\
                                            if(~rst_n) begin\n\
                                                " + gen_addr + " <= 0;\n\
                                            end else begin \n\
                                                if(pre_mult_done) begin\n\
                                                    if(sparse_tile_done) begin\n\
                                                        " + gen_addr + " <= 0;\n\
                                                    end else begin\n\
                                                        " + gen_addr + " <= "+wei_addr+";\n\
                                                    end\n\
                                                end \n\
                                            end\n\
                                      end\n"
                                
                                for kx in range(int(st["TKX"])):
                                    for ky in range(int(st["TKY"])):
                                        for i in range( int(st["TI"])):
                                            s += "reg ["+str(PE_ADDR_LEN)+"-1:0] sparse_addr_%d_%d_%d_%d_%d_%d_%d;\n" %(n, b, x, y, kx, ky, i)
                                            inner_loop += 1

                


                #VALUE SPARSITY: W_sparsity
                ###################################################################################        
                #VALUE SPARSITY: W_sparsity
                ###################################################################################
                if(fd["SPARSITY"]["VALUE_SPARSITY"] == "WEI"):

                    #sparse_map --> addr_idx --> gen_addr, sparse_addr
                    #

     
                    #Step address
                    if(fd["SPARSITY"]["WEI_ENCODING"] in ["NONE", "SPARSE_MAP"]):
                        wai_quan = 0
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        prev = ""
                                        for kx in range(int(fd["TKX"])):
                                            for ky in range(int(fd["TKY"])):
                                                for i in range( int(fd["TI"])):


                                                    if(fd["SPARSITY"]["ADDRESS_GEN"] == "ADDERS"):
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] masked_addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        if(inner_loop == 0):
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = jia_sparse_map_buffered[%d] ;\n" %(n, b, x, y, kx, ky, i,   wai_quan)
                                                        else:
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = jia_sparse_map_buffered[%d] + %s;\n" %(n, b, x, y, kx, ky, i, wai_quan, prev)


                                                        s += "assign masked_addr_idx_%d_%d_%d_%d_%d_%d_%d = jia_sparse_map_buffered[%d] ?addr_idx_%d_%d_%d_%d_%d_%d_%d : 0;\n" %(n, b, x, y, kx, ky, i, wai_quan, \
                                                                                                                                                                       n, b, x, y, kx, ky, i )
                                                        
                                                        prev = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, kx, ky, i)

                                                    
                                                        #s += "sparse_addr_%d_%d_%d_%d_%d_%d_%d = ;\n" %(n, b, x, y, kx, ky, i)

                                                    elif(fd["SPARSITY"]["ADDRESS_GEN"] == "PREFIX"): #TODOS
                                                        pass

                                                    inner_loop += 1
                                                    wai_quan += 1
                    #index address
                    else:
                        pass #TODOS

                    #CROSSBAR 交通
                    #1.   st[TN] == fd[TN] ...

                    if(fd["SPARSITY"].get("GROUPING_POLICY", "STRUCTURED") == "STRUCTURED" and fd["TN"]*fd["TX"]*fd["TY"]*fd["TB"] == st["TN"]*st["TX"]*st["TY"]*st["TB"]):
                        wai_quan = 0
                        buffer_idx = 0
                        fang = fd["TKX"]*fd["TKY"]*fd["TI"]



                        #s += "assign sparse_tile_done = (end_addr == "+str(SPARSE_PE)+") ;\n"
                        end_tiaojian = []
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        last_elt = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, int(fd["TKX"])-1, int(fd["TKY"])-1, int(fd["TI"])-1)
                                        #end_tiaojian.append( "(%s == %d)" %(end_addr, fang))
                                        end_tiaojian.append( "(%s >= %s)" %(end_addr, last_elt))
                                        
                        s += "always@(posedge clk or negedge rst_n) begin\n\
                                 if(~rst_n) begin\n\
                                        sparse_tile_done <= 0; \n\
                                 end else begin \n\
                                         if(mult_done)\n\
                                        sparse_tile_done <= mac_en & "+"&".join(end_tiaojian)+" ;\n\
                                 end\n\
                               end\n"
                        #s += "assign sparse_tile_done = %s;\n" %("&".join(end_tiaojian))
                        s += "assign sparse_stall = ~sparse_tile_done;\n"


                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        for kx in range(int(st["TKX"])):
                                            for ky in range(int(st["TKY"])):
                                                for i in range( int(st["TI"])):
                                                    #SPARSE MAP
                                                    sp_n = n
                                                    sp_b = b
                                                    sp_x = x
                                                    sp_y = y
                                                        
                                                    sp_inner_loop = 0
                                                    for sp_kx in range(int(fd["TKX"])):
                                                        for sp_ky in range(int(fd["TKY"])):
                                                            for sp_i in range( int(fd["TI"])):

                                                                if(sp_inner_loop==0):
                                                                    s += ""
                                                                else:
                                                                    s += "else "
                                                                s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                                                                     sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                                                                     inner_loop+1, gen_addr)
                                                                #s += "    sparse_addr_%d_%d_%d_%d_%d_%d_%d <= ;\n" %(n, b, x, y, kx, ky, i)
                                                                #(TODOS) adapative
                                                                buffer_start = buffer_idx*fang
                                                                tou = "jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(wai_quan,wai_quan)
                                                                wei = "jia_buffered[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(buffer_start+sp_inner_loop,buffer_start+sp_inner_loop)

                                                                act_tou = "yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(wai_quan,wai_quan)
                                                                act_wei = "yi_buffered[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(buffer_start + sp_inner_loop,buffer_start+sp_inner_loop)

                                                                
                                                                s += "    %s <= %s;\n" %(tou, wei)
                                                                s += "    %s <= %s;\n" %(act_tou, act_wei)


                                                                s += "end\n"
                                                                sp_inner_loop += 1
                                                    s += "else begin\n"
                                                    s += "    jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "    yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "end\n"
                                                    inner_loop += 1
                                                    

                                                    wai_quan += 1

                                        buffer_idx += 1
                        s += "end\n"

                        #下个的逻辑
                        xia = st["TKX"]*st["TKY"]*st["TI"]
                        #print(xia)
                        #exit(0)
                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        #s += "if ( %s + %d >= %d) begin\n" %(gen_addr, xia, fang )
                                        #s += "    %s = %d;\n" %(gen_addr, fang )
                                        #s += "end else begin\n"

                                        #SPARSE MAP
                                        sp_n = n
                                        sp_b = b
                                        sp_x = x
                                        sp_y = y

                                        s += "%s = %s + %d; \n" %(end_addr, gen_addr, xia)

                                        '''
                                        sp_inner_loop = 0
                                        for sp_kx in range(int(fd["TKX"])):
                                            for sp_ky in range(int(fd["TKY"])):
                                                for sp_i in range( int(fd["TI"])):
                                                    if(sp_inner_loop==0):
                                                        s += ""
                                                    else:
                                                        s += "else "
                                                    s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                        sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                        xia, gen_addr)
                                                    s += "    %s = %d; \n" %(end_addr, sp_inner_loop)
                                                    s += "end\n"

                                                    sp_inner_loop += 1

                                        s += "else begin\n"
                                        s += "    %s = %d;\n" %(end_addr, fang )
                                        s += "end\n"
                                        '''
                                                    
                                        #s += "end\n"
                                            
                                        
                                        #s += "["+str(PE_ADDR_LEN)+"-1:0] gen_addr_%d_%d_%d_%d;\n" %(n, b, x, y)
                                        #s += "end_addr_%d_%d_%d_%d = (gen_addr_%d_%d_%d_%d < fang)?   gen_addr_%d_%d_%d_%d   :   ;\n" %(n, b, x, y)

                        s += "end\n"
                        

                    #2. POLICY = structured, st[TN] != fd[TN] ...
                    elif(fd["SPARSITY"].get("GROUPING_POLICY", "STRUCTURED") == "STRUCTURED" ):
                        print("STRUCTURED TILING SPARSITY with un-even outer loop not implm yet")
                        exit()
                    
                    #3. POLICY = unstructured,
                    else:
                        print("UNSTRUCTURED TILING SPARSITY not implm yet")
                        exit()
                    
                                            
                #pass #Cambricon-X/Tensor-Cores



                ###################################################################################        
                #VALUE SPARSITY: A_sparsity
                ###################################################################################
                elif(fd["SPARSITY"]["VALUE_SPARSITY"] == "ACT"):
                    #sparse_map --> addr_idx --> gen_addr, sparse_addr
                    #
                    #Step address
                    if(fd["SPARSITY"]["ACT_ENCODING"] in ["NONE", "SPARSE_MAP"]):
                        wai_quan = 0
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        prev = ""
                                        for kx in range(int(fd["TKX"])):
                                            for ky in range(int(fd["TKY"])):
                                                for i in range( int(fd["TI"])):


                                                    if(fd["SPARSITY"]["ADDRESS_GEN"] == "ADDERS"):
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] masked_addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        if(inner_loop == 0):
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = yi_sparse_map_buffered[%d] ;\n" %(n, b, x, y, kx, ky, i,   wai_quan)
                                                        else:
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = yi_sparse_map_buffered[%d] + %s;\n" %(n, b, x, y, kx, ky, i, wai_quan, prev)


                                                        s += "assign masked_addr_idx_%d_%d_%d_%d_%d_%d_%d = yi_sparse_map_buffered[%d] ?addr_idx_%d_%d_%d_%d_%d_%d_%d : 0;\n" %(n, b, x, y, kx, ky, i, wai_quan, \
                                                                                                                                                                       n, b, x, y, kx, ky, i )
                                                        
                                                        prev = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, kx, ky, i)

                                                    
                                                        #s += "sparse_addr_%d_%d_%d_%d_%d_%d_%d = ;\n" %(n, b, x, y, kx, ky, i)

                                                    elif(fd["SPARSITY"]["ADDRESS_GEN"] == "PREFIX"): #TODOS
                                                        pass

                                                    inner_loop += 1
                                                    wai_quan += 1
                    #index address
                    else:
                        pass #TODOS

                    #CROSSBAR 交通
                    #1.   st[TN] == fd[TN] ...

                    if(fd["SPARSITY"].get("GROUPING_POLICY", "STRUCTURED") == "STRUCTURED" and fd["TN"]*fd["TX"]*fd["TY"]*fd["TB"] == st["TN"]*st["TX"]*st["TY"]*st["TB"]):
                        wai_quan = 0
                        buffer_idx = 0
                        fang = fd["TKX"]*fd["TKY"]*fd["TI"]



                        #s += "assign sparse_tile_done = (end_addr == "+str(SPARSE_PE)+") ;\n"
                        end_tiaojian = []
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        last_elt = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, int(fd["TKX"])-1, int(fd["TKY"])-1, int(fd["TI"])-1)
                                        #end_tiaojian.append( "(%s == %d)" %(end_addr, fang))
                                        end_tiaojian.append( "(%s >= %s)" %(end_addr, last_elt))
                                        
                        s += "always@(posedge clk or negedge rst_n) begin\n\
                                 if(~rst_n) begin\n\
                                        sparse_tile_done <= 0; \n\
                                 end else begin \n\
                                         if(mult_done)\n\
                                        sparse_tile_done <= mac_en & "+"&".join(end_tiaojian)+" ;\n\
                                 end\n\
                               end\n"
                        #s += "assign sparse_tile_done = %s;\n" %("&".join(end_tiaojian))
                        s += "assign sparse_stall = ~sparse_tile_done;\n"


                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        for kx in range(int(st["TKX"])):
                                            for ky in range(int(st["TKY"])):
                                                for i in range( int(st["TI"])):
                                                    #SPARSE MAP
                                                    sp_n = n
                                                    sp_b = b
                                                    sp_x = x
                                                    sp_y = y
                                                        
                                                    sp_inner_loop = 0
                                                    for sp_kx in range(int(fd["TKX"])):
                                                        for sp_ky in range(int(fd["TKY"])):
                                                            for sp_i in range( int(fd["TI"])):

                                                                if(sp_inner_loop==0):
                                                                    s += ""
                                                                else:
                                                                    s += "else "
                                                                s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                                                                     sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                                                                     inner_loop+1, gen_addr)
                                                                #s += "    sparse_addr_%d_%d_%d_%d_%d_%d_%d <= ;\n" %(n, b, x, y, kx, ky, i)
                                                                #(TODOS) adapative
                                                                buffer_start = buffer_idx*fang
                                                                tou = "jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(wai_quan,wai_quan)
                                                                wei = "jia_buffered[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(buffer_start+sp_inner_loop,buffer_start+sp_inner_loop)

                                                                act_tou = "yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(wai_quan,wai_quan)
                                                                act_wei = "yi_buffered[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(buffer_start + sp_inner_loop,buffer_start+sp_inner_loop)

                                                                
                                                                s += "    %s <= %s;\n" %(tou, wei)
                                                                s += "    %s <= %s;\n" %(act_tou, act_wei)


                                                                s += "end\n"
                                                                sp_inner_loop += 1
                                                    s += "else begin\n"
                                                    s += "    jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "    yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "end\n"
                                                    inner_loop += 1
                                                    

                                                    wai_quan += 1

                                        buffer_idx += 1
                        s += "end\n"

                        #下个的逻辑
                        xia = st["TKX"]*st["TKY"]*st["TI"]
                        #print(xia)
                        #exit(0)
                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        #s += "if ( %s + %d >= %d) begin\n" %(gen_addr, xia, fang )
                                        #s += "    %s = %d;\n" %(gen_addr, fang )
                                        #s += "end else begin\n"

                                        #SPARSE MAP
                                        sp_n = n
                                        sp_b = b
                                        sp_x = x
                                        sp_y = y

                                        s += "%s = %s + %d; \n" %(end_addr, gen_addr, xia)

                                        '''
                                        sp_inner_loop = 0
                                        for sp_kx in range(int(fd["TKX"])):
                                            for sp_ky in range(int(fd["TKY"])):
                                                for sp_i in range( int(fd["TI"])):
                                                    if(sp_inner_loop==0):
                                                        s += ""
                                                    else:
                                                        s += "else "
                                                    s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                        sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                        xia, gen_addr)
                                                    s += "    %s = %d; \n" %(end_addr, sp_inner_loop)
                                                    s += "end\n"

                                                    sp_inner_loop += 1

                                        s += "else begin\n"
                                        s += "    %s = %d;\n" %(end_addr, fang )
                                        s += "end\n"
                                        '''
                                                    
                                        #s += "end\n"
                                            
                                        
                                        #s += "["+str(PE_ADDR_LEN)+"-1:0] gen_addr_%d_%d_%d_%d;\n" %(n, b, x, y)
                                        #s += "end_addr_%d_%d_%d_%d = (gen_addr_%d_%d_%d_%d < fang)?   gen_addr_%d_%d_%d_%d   :   ;\n" %(n, b, x, y)

                        s += "end\n"

                        
                    pass #Cnvltion
                #VALUE SPARSITY: WA_sparsity
                elif(fd["SPARSITY"]["VALUE_SPARSITY"] in  ["WEI_ACT", "ACT_WEI"]):
                    
                    #sparse_map --> addr_idx --> gen_addr, sparse_addr
                    #Step address
                    if(fd["SPARSITY"]["ACT_ENCODING"] in ["NONE", "SPARSE_MAP"]):
                        wai_quan = 0
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        prev = ""
                                        for kx in range(int(fd["TKX"])):
                                            for ky in range(int(fd["TKY"])):
                                                for i in range( int(fd["TI"])):


                                                    if(fd["SPARSITY"]["ADDRESS_GEN"] == "ADDERS"):
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        s += "wire ["+str(PE_ADDR_LEN)+"-1:0] masked_addr_idx_%d_%d_%d_%d_%d_%d_%d ;\n" %(n, b, x, y, kx, ky, i)
                                                        if(inner_loop == 0):
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = (jia_sparse_map_buffered[%d]& yi_sparse_map_buffered[%d]) ;\n" %(n, b, x, y, kx, ky, i,   wai_quan,wai_quan)
                                                        else:
                                                            s += "assign addr_idx_%d_%d_%d_%d_%d_%d_%d = (jia_sparse_map_buffered[%d]& yi_sparse_map_buffered[%d]) + %s;\n" %(n, b, x, y, kx, ky, i, wai_quan, wai_quan,prev)


                                                        s += "assign masked_addr_idx_%d_%d_%d_%d_%d_%d_%d =( jia_sparse_map_buffered[%d]& yi_sparse_map_buffered[%d]) ?addr_idx_%d_%d_%d_%d_%d_%d_%d : 0;\n" %(n, b, x, y, kx, ky, i, wai_quan,wai_quan, \
                                                                                                                                                                       n, b, x, y, kx, ky, i )
                                                        
                                                        prev = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, kx, ky, i)

                                                    
                                                        #s += "sparse_addr_%d_%d_%d_%d_%d_%d_%d = ;\n" %(n, b, x, y, kx, ky, i)

                                                    elif(fd["SPARSITY"]["ADDRESS_GEN"] == "PREFIX"): #TODOS
                                                        pass

                                                    inner_loop += 1
                                                    wai_quan += 1
                    #index address
                    else:
                        pass #TODOS

                    #CROSSBAR 交通
                    #1.   st[TN] == fd[TN] ...

                    if(fd["SPARSITY"].get("GROUPING_POLICY", "STRUCTURED") == "STRUCTURED" and fd["TN"]*fd["TX"]*fd["TY"]*fd["TB"] == st["TN"]*st["TX"]*st["TY"]*st["TB"]):
                        wai_quan = 0
                        buffer_idx = 0
                        fang = fd["TKX"]*fd["TKY"]*fd["TI"]



                        #s += "assign sparse_tile_done = (end_addr == "+str(SPARSE_PE)+") ;\n"
                        end_tiaojian = []
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        last_elt = "addr_idx_%d_%d_%d_%d_%d_%d_%d" %(n, b, x, y, int(fd["TKX"])-1, int(fd["TKY"])-1, int(fd["TI"])-1)
                                        #end_tiaojian.append( "(%s == %d)" %(end_addr, fang))
                                        end_tiaojian.append( "(%s >= %s)" %(end_addr, last_elt))
                                        
                        s += "always@(posedge clk or negedge rst_n) begin\n\
                                 if(~rst_n) begin\n\
                                        sparse_tile_done <= 0; \n\
                                 end else begin \n\
                                         if(mult_done)\n\
                                        sparse_tile_done <= mac_en & "+"&".join(end_tiaojian)+" ;\n\
                                 end\n\
                               end\n"
                        #s += "assign sparse_tile_done = %s;\n" %("&".join(end_tiaojian))
                        s += "assign sparse_stall = ~sparse_tile_done;\n"


                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        #inner loop
                                        inner_loop = 0
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        for kx in range(int(st["TKX"])):
                                            for ky in range(int(st["TKY"])):
                                                for i in range( int(st["TI"])):
                                                    #SPARSE MAP
                                                    sp_n = n
                                                    sp_b = b
                                                    sp_x = x
                                                    sp_y = y
                                                        
                                                    sp_inner_loop = 0
                                                    for sp_kx in range(int(fd["TKX"])):
                                                        for sp_ky in range(int(fd["TKY"])):
                                                            for sp_i in range( int(fd["TI"])):

                                                                if(sp_inner_loop==0):
                                                                    s += ""
                                                                else:
                                                                    s += "else "
                                                                s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                                                                     sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                                                                     inner_loop+1, gen_addr)
                                                                #s += "    sparse_addr_%d_%d_%d_%d_%d_%d_%d <= ;\n" %(n, b, x, y, kx, ky, i)
                                                                #(TODOS) adapative
                                                                buffer_start = buffer_idx*fang
                                                                tou = "jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(wai_quan,wai_quan)
                                                                wei = "jia_buffered[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION]" %(buffer_start+sp_inner_loop,buffer_start+sp_inner_loop)

                                                                act_tou = "yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(wai_quan,wai_quan)
                                                                act_wei = "yi_buffered[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION]" %(buffer_start + sp_inner_loop,buffer_start+sp_inner_loop)

                                                                
                                                                s += "    %s <= %s;\n" %(tou, wei)
                                                                s += "    %s <= %s;\n" %(act_tou, act_wei)


                                                                s += "end\n"
                                                                sp_inner_loop += 1
                                                    s += "else begin\n"
                                                    s += "    jia[(%d+1)*`MAX_WEI_PRECISION-1:(%d)*`MAX_WEI_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "    yi[(%d+1)*`MAX_ACT_PRECISION-1:(%d)*`MAX_ACT_PRECISION] <= 0;\n" %(wai_quan,wai_quan)
                                                    s += "end\n"
                                                    inner_loop += 1
                                                    

                                                    wai_quan += 1

                                        buffer_idx += 1
                        s += "end\n"

                        #下个的逻辑
                        xia = st["TKX"]*st["TKY"]*st["TI"]
                        #print(xia)
                        #exit(0)
                        
                        s += "always@(*) begin\n"
                        for n in range(int(st["TN"])):
                            for b in range(int(st["TB"])):
                                for x in range(int(st["TX"])):
                                    for y in range(int(st["TY"])):
                                        gen_addr = "gen_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        end_addr = "end_addr_%d_%d_%d_%d" %(n, b, x, y)
                                        #s += "if ( %s + %d >= %d) begin\n" %(gen_addr, xia, fang )
                                        #s += "    %s = %d;\n" %(gen_addr, fang )
                                        #s += "end else begin\n"

                                        #SPARSE MAP
                                        sp_n = n
                                        sp_b = b
                                        sp_x = x
                                        sp_y = y

                                        s += "%s = %s + %d; \n" %(end_addr, gen_addr, xia)

                                        '''
                                        sp_inner_loop = 0
                                        for sp_kx in range(int(fd["TKX"])):
                                            for sp_ky in range(int(fd["TKY"])):
                                                for sp_i in range( int(fd["TI"])):
                                                    if(sp_inner_loop==0):
                                                        s += ""
                                                    else:
                                                        s += "else "
                                                    s += "if(masked_addr_idx_%d_%d_%d_%d_%d_%d_%d == (%d + %s)) begin\n" %(sp_n, sp_b, sp_x,\
                                                                                                        sp_y, sp_kx, sp_ky, sp_i, \
                                                                                                        xia, gen_addr)
                                                    s += "    %s = %d; \n" %(end_addr, sp_inner_loop)
                                                    s += "end\n"

                                                    sp_inner_loop += 1

                                        s += "else begin\n"
                                        s += "    %s = %d;\n" %(end_addr, fang )
                                        s += "end\n"
                                        '''
                                                    
                                        #s += "end\n"
                                            
                                        
                                        #s += "["+str(PE_ADDR_LEN)+"-1:0] gen_addr_%d_%d_%d_%d;\n" %(n, b, x, y)
                                        #s += "end_addr_%d_%d_%d_%d = (gen_addr_%d_%d_%d_%d < fang)?   gen_addr_%d_%d_%d_%d   :   ;\n" %(n, b, x, y)

                        s += "end\n"

                        

                    
                    pass #SparTEN/SCNN                    






                elif(fd["SPARSITY"]["VALUE_SPARSITY"] in ["PSUM"]):
                    pass



            
        ############################################
        # SPARSE DATAFLOW
        ############################################


        elif("SPARSE_DIRECT" == dataflow):
            # jia_buf(wei) --> todos --> jia
            # yi_buf(act)  --> todos -->  yi
            #    zi       --> todos --> zi_buf(psum)
            #There is an extra buffer, the sliding window


            #Cross-bar design with enabling
            #(TWO design choices, 1. using adder 2. using prefix buffer)

            #case(address):
            #    4'b0000: jia[] = jia_buf[0];\n
            #    4'b0001: jia[] = jia_buf[1];\n
            #    4'b0001: jia[] = jia_buf[2];\n
            #jia[] = jia_buf[]
            #...

            #calculate the expected window

            TKX = int(fd["TKX"])
            TKY =int(fd["TKY"])
            TI =int(fd["TI"])
            TN =int(fd["TN"])
            TX =int(fd["TX"])
            TY =int(fd["TY"])
            TB =  int(fd["TB"])
            
            #if(macro_config["WEI_SPARSITY_MAP_BUF_DATA"]):
            if(not hardware_config["multicast"]):
                wei_units = macro_config["WEI_WINDOW_"+str(fd["ID"])]*int(fd["TKX"])*int(fd["TKY"])*int(fd["TI"])*int(fd["TN"])*int(fd["TB"])*int(fd["TX"])*int(fd["TY"]) 
                act_units = macro_config["ACT_WINDOW_"+str(fd["ID"])]*int(fd["TKX"])*int(fd["TKY"])*int(fd["TI"])*int(fd["TN"])*int(fd["TB"])*int(fd["TX"])*int(fd["TY"]) 
            else:
                wei_units = macro_config["WEI_WINDOW_"+str(fd["ID"])]*TKX*TKY*TI*TN
                act_units = macro_config["ACT_WINDOW_"+str(fd["ID"])]*(TX+TKX-1)*(TY+TKY-1)*TI*TB

            #wei_units = macro_config["WEI_SPARSITY_MAP_BUF_DATA"]
            #act_units = macro_config
            wei_units_log = int(np.log2(wei_units))+1
            act_units_log = int(np.log2(act_units))+1




            #Doesn't mae sense to choose this one, very high cost!
            if(not hardware_config["multicast"]):
                pass #(TODOS)
            else:
                df_d = fd

                '''
                #GENERATE INDICES (generate n, n+1, n+2... n+win indices)
                #(0,0,0,0) --->  (0,0,0,0), (0,0,0,1), (0,0,1,0), (0,0,1,1)
                for w in range(str(df_d["SPARSITY"]["WINDOW"])):
                    s += "reg [-1:0] indices_bb_"+str(w)+";"
                    s += "reg [-1:0] indices_nn_"+str(w)+";"
                    s += "reg [-1:0] indices_ii_"+str(w)+";"
                    s += "reg [-1:0] indices_xx_"+str(w)+";"
                    s += "reg [-1:0] indices_yy_"+str(w)+";"
                    s += "reg [-1:0] indices_kx_"+str(w)+";"
                    s += "reg [-1:0] indices_ky_"+str(w)+";"
                '''

                
                
                ##############################
                #        BLOCK MAPPING
                #       0    0    0  
                #       1    1    1
                #       0    0    0
                #     
                ##############################

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
                X_LIM = "(x - kx + 1)"
                Y_LIM = "(y - ky + 1)"
                lim_map = {
                    "TXX": str(fd["TXX"]),
                    "TYY": str(fd["TYY"]),
                    "TNN": str(fd["TNN"]),
                    "TII": str(fd["TII"]),

                    "X": X_LIM,
                    "Y": Y_LIM,
                    "N": "nc",
                    "I": "ic",

                    "KX": "kx",
                    "KY": "ky",
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

                    "KX": "kx",
                    "KY": "ky",
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
                WINDOW = fd["SPARSITY"]["WEI_WINDOW"] #do we do something with multiple windows? like WEI_WINDOW, ACT_WINDOW?
                #(TODOS)
                
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
                        

                #WINDOW we can give it to the counter so that it can use this immediately
                SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                    WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)        
                #print(s)
                #exit()


                
                s += "wire [`MAX_KX_LOG-1:0] kx_lim;\n"
                s += "wire [`MAX_KY_LOG-1:0] ky_lim;\n"
                s += "wire [`MAX_X_LOG-1:0] x_lim;\n"
                s += "wire [`MAX_Y_LOG-1:0] y_lim;\n"
                s += "reg [`MAX_X_LOG-1:0] xx_lim;\n"
                s += "reg [`MAX_Y_LOG-1:0] yy_lim;\n"
                s += "wire [`MAX_N_LOG-1:0] n_lim;\n"
                s += "wire [`MAX_I_LOG-1:0] i_lim;\n"
                s += "reg [`MAX_N_LOG-1:0] nn_lim;\n"
                s += "reg [`MAX_I_LOG-1:0] ii_lim;\n"
                s += "wire [`MAX_B_LOG-1:0] b_lim;\n"


                cast = {
                                                                    "TII":"ii_lim",
                                                                    "TNN": "nn_lim",
                                                                    "TXX": "xx_lim",
                                                                    "TYY": "yy_lim",
                                                                    "I": "i_lim",
                                                                    "N":"n_lim",
                                                                    "X": "x_lim",
                                                                    "Y": "y_lim",
                                                                    "B": "b_lim",

                                                                    "KX": "kx_lim",
                                                                    "KY": "ky_lim",
                    }
                s += "assign kx_lim = (ky)/"+str(fd["TKX"])+";\n"
                s += "assign ky_lim = (ky)/"+str(fd["TKY"])+";\n"
                s += "assign b_lim = (batch)/"+str(fd["TB"])+";\n"

                #Parce qu'il y a des complexities de la generation d'address, on utilisera les "pre-fetch" moyenes dans la modele au system
                UPPER_Y = "(y-ky+1 + "+str(fd["TY"])+"-1)"
                UPPER_X = "(x-kx+1 + "+str(fd["TX"])+"-1)"
                if True:
                    if("TYY" not in fd["LOOP"]):
                        s += "assign y_lim = ("+UPPER_Y+"/%d" %(fd["TY"])+");"
                        
                        cast["Y"] = "y_lim"
                    else:
                        s += "assign y_lim = ("+UPPER_Y+"/%d" %(fd["TYY"])+");\n"
                        s += "always@(*)begin\n\
                            if((y - ky + 1) < "+str(fd["TYY"])+") begin\n\
                                 yy_lim = ("+UPPER_Y+"/%d" %(fd["TY"])+");\n\
                            end else begin\n\
                                 yy_lim = (%d/%d" %(fd["TYY"], fd["TY"])+");\n\
                            end\n\
                          end\n"

                    if("TXX" not in fd["LOOP"]):
                        s += "assign x_lim = "+UPPER_X+"/"+str(fd["TX"])+";\n"
                        
                        cast["X"] = "x_lim"
                    else:
                        s += "assign x_lim = ("+UPPER_X+")/"+str(fd["TXX"])+";\n"
                        s += "always@(*)begin\n\
                            if((x - kx + 1) < "+str(fd["TXX"])+") begin\n\
                                 xx_lim = (("+UPPER_X+")/%d" %(fd["TX"])+");\n\
                            end else begin\n\
                                 xx_lim = (%d/%d" %(fd["TXX"], fd["TX"])+");\n\
                            end\n\
                          end\n"
                    if("TNN" not in fd["LOOP"]):
                        s += "assign n_lim = (nc/%d" %(fd["TN"])+");\n"

                        cast["N"] = "n_lim"
                    else:
                        s += "assign n_lim = (nc/%d" %(fd["TNN"])+");\n"
                        s += "always@(*)begin\n\
                            if(nn < "+str(fd["TNN"])+") begin\n\
                                 nn_lim= (nc/%d" %(fd["TNN"])+");\n\
                            end else begin\n\
                                 nn_lim = (%d/%d" %(fd["TNN"],fd["TN"])+");\n\
                            end\n\
                          end\n"
                                                       
                    if("TII" not in fd["LOOP"]):
                        s += "assign i_lim = (ic/%d" %(fd["TI"])+");\n"
                        
                        cast["I"] = "i_lim"
                    else:
                        s += "assign i_lim = (ic/%d" %(fd["TII"])+");\n"
                        s += "always@(*)begin\n\
                            if(ii < "+str(fd["TII"])+") begin\n\
                                 ii_lim= (ic/%d" %(fd["TII"])+");\n\
                            end else begin\n\
                                 ii_lim = (%d/%d" %(fd["TNN"], fd["TI"])+");\n\
                            end\n\
                          end\n"

                wei_loop = []
                act_loop = []
                for lp in fd["LOOP"]:
                    if(lp in SHI_LOOP_WEI):
                        wei_loop.append(lp)
                    if(lp in SHI_LOOP_ACT):
                        act_loop.append(lp)
                print(wei_loop, act_loop)
                
                for wu in range(WINDOW):                    
                    #TODOS, is there better way ?
                    #We can pass the casting parameters via initialization, here we do some hacking
                    mini_carte = {
                                                                "TNN": "(nn_%d/%d" %(wu, fd["TN"])+")",
                                                                "TII": "(ii_%d/%d" %(wu, fd["TI"])+")",
                                                                "TXX": "(xx_%d/%d" %(wu, fd["TX"])+")",
                                                                "TYY": "(yy_%d/%d" %(wu, fd["TY"])+")",
                                                                "N"  : "(nnn_%d/%d" %(wu, fd["TNN"])+")",
                                                                "I"  : "(iii_%d/%d" %(wu, fd["TII"])+")",
                                                                "X": "(xxx_%d/%d" %(wu, fd["TXX"])+")",
                                                                "Y": "(yyy_%d/%d" %(wu, fd["TYY"])+")",
                                                                "B" : "(bb_%d/%d" %(wu, fd["TKY"])+")",
                                                                "KX": "(kkx_%d/%d" %(wu, fd["TKX"])+")",
                                                                "KY": "(kky_%d/%d" %(wu, fd["TKY"])+")",
                    }
        
 
                    if("TXX" not in fd["LOOP"]):
                        mini_carte["X"] = "(xx_%d/%d" %(wu, fd["TX"])+")"
                    if("TYY" not in fd["LOOP"]):
                        mini_carte["Y"] = "(yy_%d/%d" %(wu, fd["TY"])+")"
                    if("TNN" not in fd["LOOP"]):
                        mini_carte["N"] = "(nn_%d/%d" %(wu, fd["TN"])+")"
                    if("TII" not in fd["LOOP"]):
                        mini_carte["I"] = "(ii_%d/%d" %(wu, fd["TI"])+")"

                    #print(SHI_LOOP_WEI)
                    
                    window_wei_1oop_idx = gen_index(wei_loop, fd, mini_carte=mini_carte , cast=cast)
                    window_act_loop_idx = gen_index(act_loop, fd, mini_carte=mini_carte, cast=cast)
                    #print(mini_carte, cast)
                    #print(wei_loop, act_loop)
                    #print(window_wei_1oop_idx, window_act_loop_idx)
                    #print("\n")
                    #The word-size to be determined (TODOS)
                    s += "wire [31:0] wei_wu_"+str(wu) + ";\n"
                    s += "wire [31:0] act_wu_" +str(wu)+";\n"
                    s += "assign wei_wu_"+str(wu) + " = " + window_wei_1oop_idx + ";\n"
                    s += "assign act_wu_"+str(wu) + " = " + window_act_loop_idx + ";\n"                                  

                    s += "wire ["+str(int(np.log2(WINDOW)))+"-1:0] wei_wu_zeroed_"+str(wu)+";\n"
                    s += "assign wei_wu_zeroed_"+str(wu)+" = wei_wu_"+ str(wu) + " -  wei_wu_0 ;\n"

                                                       
                    s += "wire ["+str(int(np.log2(WINDOW)))+"-1:0] act_wu_zeroed_"+str(wu)+";\n"
                    s += "assign act_wu_zeroed_"+str(wu)+" = act_wu_"+ str(wu) + " -  act_wu_0 ;\n"
                
                # df_d = fd
                s += "reg ["+str(df_d["SPARSITY"]["WEI_WINDOW"]*TX*TY*TKX*TKY *TI*TB*TN)+"*`MAX_WEI_PRECISION -1:0] weight_window_value;" 
                s += "reg ["+str(df_d["SPARSITY"]["ACT_WINDOW"]*TX*TY*TKX*TKY *TI*TB*TN)+"*`MAX_ACT_PRECISION -1:0] act_window_value;" 

                s += "reg ["+str(df_d["SPARSITY"]["WEI_WINDOW"]*TX*TY*TKX*TKY *TI*TB*TN)+" -1:0] weight_window;" 
                s += "reg ["+str(df_d["SPARSITY"]["ACT_WINDOW"]*TX*TY*TKX*TKY *TI*TB*TN)+" -1:0] act_window;"


                JIA_BUF_LIM = wei_units
                YI_BUF_LIM =  act_units
                for kx in range(int(fd["TKX"])):
                    for ky in range(int(fd["TKY"])):
                        for i in range(int(fd["TI"])):
                            for n in range(int(fd["TN"])):
                                for b in range(int(fd["TB"])):
                                    for x in range(int(fd["TX"])):
                                        for y in range(int(fd["TY"])):                
                                            for wu in range(WINDOW):
                                                loop_idx = (y +  (int(fd["TY"]))*\
                                                            (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   int(fd["TN"]) *(i +\
                                                                 int(fd["TI"])*(ky  + int(fd["TKY"])*(kx  + int(fd["TKX"])*wu)))))))
                                                loop_idx = "( " + str(WINDOW*fd["TKX"]*fd["TKY"]*fd["TI"]*fd["TN"]*fd["TB"]*fd["TX"]*fd["TY"]) + "-1 - " + str(loop_idx)+")"
                                                loop_idx = eval(loop_idx)
                                                loop_idx = str(loop_idx)
                                                
                                                
                                                #MUX TO SELECT THE BLOCK
                                                s += "always@(*) begin\n"
                                                for mux_wu in range(WINDOW):
                                                    jia_loop_idx = eval(gen_index(["WINDOW"]+WULI_LOOP_WEI, fd, WINDOW=WINDOW,window=mux_wu, ky=ky,kx=kx,i=i,n=n,use_macros=True))
                                                    yi_loop_idx =  eval(gen_index(["WINDOW"]+WULI_LOOP_ACT, fd, WINDOW=WINDOW,window=mux_wu, x=x,y=y,ky=ky,kx=kx,i=i,b=b,use_macros=True))
                                                    jia_loop_idx = str(jia_loop_idx)
                                                    yi_loop_idx = str(yi_loop_idx)
                                                    if(mux_wu > 0):
                                                        s += "else "
                                                    #mux_wu_idx = jia_loop_idx# "( "+str(mux_wu)+"  + "+str(WINDOW)+"*(" + jia_loop_idx + ") )"
                                                    mux_wu_idx = "("+str(JIA_BUF_LIM)+"-1 - "  + jia_loop_idx+")"
                                                    s += "if (wei_wu_zeroed_"+str(wu) + "=="+str(mux_wu) + ") begin\n"
                                                    if(fd["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                                                        s += "    weight_window["+ loop_idx +"] = jia_sparse_map[ "  +  mux_wu_idx +  " ] ;\n"
                                                    s += "    weight_window_value[("+loop_idx+"+1)*`MAX_WEI_PRECISION - 1: "+loop_idx+"*`MAX_WEI_PRECISION] = \
                                                            jia_buf[("  + mux_wu_idx  + "+1)*`MAX_WEI_PRECISION-1:"  + mux_wu_idx   +  "*`MAX_WEI_PRECISION];\n"
                                                    s += "end\n"
                                                s += "end\n"


                                                #MUX TO SELECT THE BLOCK
                                                s += "always@(*) begin\n"
                                                for mux_wu in range(WINDOW):
                                                    jia_loop_idx = eval(gen_index(["WINDOW"]+WULI_LOOP_WEI, fd, WINDOW=WINDOW,window=mux_wu, ky=ky,kx=kx,i=i,n=n,use_macros=True))
                                                    yi_loop_idx =  eval(gen_index(["WINDOW"]+WULI_LOOP_ACT, fd, WINDOW=WINDOW,window=mux_wu, x=x,y=y,ky=ky,kx=kx,i=i,b=b,use_macros=True))

                                                    jia_loop_idx = str(jia_loop_idx)
                                                    yi_loop_idx = str(yi_loop_idx)
                                                    if(mux_wu > 0):
                                                        s += "else "
                                                    mux_wu_idx = "("+str(YI_BUF_LIM)+"-1 - "  + yi_loop_idx+")" # "( "+str(mux_wu)+"  + "+str(WINDOW)+"*(" + yi_loop_idx + ") )"
                                                    s += "if (act_wu_zeroed_"+str(wu) + "=="+str(mux_wu) + ") begin\n"
                                                    if(fd["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
                                                        s += "    act_window["+ loop_idx +"] = yi_sparse_map["+ mux_wu_idx +  " ] ;\n"
                                                    s += "    act_window_value[("+loop_idx+"+1)*`MAX_ACT_PRECISION - 1: "+loop_idx+"*`MAX_ACT_PRECISION] = \
                                                            yi_buf[("  + mux_wu_idx  + "+1)*`MAX_ACT_PRECISION-1:"  + mux_wu_idx   +  "*`MAX_ACT_PRECISION];\n"
                                                    s += "end\n"
                                                s += "end\n"

                                                
                                                
                                                '''
                                                s+="assign weight_window["+loop_idx+"] = \
                                                            jia_buf["+#TODOS+"] ;\n"
                                                s+="assign weight_window_value[("+loop_idx"+1)*`MAX_WEI_PRECISION - 1: "+loop_idx+"*`MAX_WEI_PRECISION] = \
                                                            jia_sparse_map["+#TODOS+"];\n"
                                                '''


                

                '''
                if(not fd["SPARSITY"]["WEI_VALUE_SPARSITY"] and not fd["SPARSITY"]["ACT_VALUE_SPARSITY"]):
                    #Compressed weight/act possibilites , NVDLA-like
                    pass
                elif(fd["SPARSITY"]["WEI_VALUE_SPARSITY"] and not fd["SPARSITY"]["ACT_VALUE_SPARSITY"]):
                    #Cambricon-X
                    #act_addr = "act_addr_"+
                    #wei_addr = "wei_addr_"+
                    pass
                elif(not fd["SPARSITY"]["WEI_VALUE_SPARSITY"] and fd["SPARSITY"]["ACT_VALUE_SPARSITY"]):
                    #Cnvlutin
                    pass
                else:
                    #Sparten, Ristretto
                    pass                
                #WEI_CROSSBAR
                #THE CROSSBAR will be determined by weight/activation/both schema
                #ACT

                '''
                '''
                
                for jia_idx in range(TX*TY*TKX*TKY *TI*TB*TN):
                    wu = 0
                    #s += "reg ["+str(TX*TY*TKX*TKY *TI*TB*TN)+"-1:0] wei_addr_"+str(wu) + ";\n"
                    s += "always@(*) begin\n"
                    s += "if (weight_window["+str(wu)+" ] == "+str(jia_idx+1)+") begin\n\
                                jia[("+str(jia_idx)+"+1)*`MAX_WEI_PRECISION-1:("+str(jia_idx)+")*`MAX_WEI_PRECISION] = \
                                 weight_window_value[("+str(wu)+"+1)*`MAX_WEI_PRECISION-1:("+str(wu)+")*`MAX_WEI_PRECISION]; \n\
                          end "
                    for wu in range(1, wei_units):
                        s += "else if (weight_window["+str(wu)+" ] == "+str(jia_idx+1)+") begin\n\
                                jia[("+str(jia_idx)+"+1)*`MAX_WEI_PRECISION-1:("+str(jia_idx)+")*`MAX_WEI_PRECISION] = \
                                 weight_window_value[("+str(wu)+"+1)*`MAX_WEI_PRECISION-1:("+str(wu)+")*`MAX_WEI_PRECISION]; \n\
                          end "
                    s += "\n else begin\n\
                            jia[("+str(jia_idx)+"+1)*`MAX_WEI_PRECISION-1:("+str(jia_idx)+")*`MAX_WEI_PRECISION] = 0;\n\
                        end\n"
                    s += "end\n"
                '''
                #ACT_CROSSBAR
                for au in range(act_units):
                    pass
                
                '''
                #addr_index = WINDOW_SIZE
                for kx in range(int(fd["TKX"])):
                    for ky in range(int(fd["TKY"])):
                        for i in range(int(fd["TI"])):
                            for n in range(int(fd["TN"])):
                                for b in range(int(fd["TB"])):
                                    for x in range(int(fd["TX"])):
                                        for y in range(int(fd["TY"])):
                                            
                                            loop_idx = (y +  (int(fd["TY"]))*\
                                                            (x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   int(fd["TN"]) *(i +\
                                                                 int(fd["TI"])*(ky  + int(fd["TKY"])*(kx  + int(fd["TKX"])*0)))))))
                                                        #print(loop_idx)
                                            loop_idx = "( " + str(fd["TKX"]*fd["TKY"]*fd["TI"]*fd["TN"]*fd["TB"]*fd["TX"]*fd["TY"]) + "-1 - " + str(loop_idx)+")"
                                                        
                                            
                                            act_addr = "act_addr_"+"_".join([str(s) for s in [kx,ky,i,n,b,x,y]])
                                            wei_addr = "wei_addr_"+"_".join([str(s) for s in [kx,ky,i,n,b,x,y]])
                                            s += "reg ["+str(wei_units_log)+"-1:0] "+wei_addr+";\n"
                                            s += "reg ["+str(act_units_log)+"-1:0] "+act_addr+";\n"

                                            #MUX WEI
                                            s += "always@(*)begin\n\
                                                case("+wei_addr+")\n"
                                            for wu in range(wei_units):#TODOS FOR ADAPTIVE PRECISION...
                                                s+= str(wu)+": jia[("+loop_idx+"+1)*`MAX_WEI_PRECISION-1:("+loop_idx+")*`MAX_WEI_PRECISION] = \
                                                       jia_buf[("+str(wu)+"+1)*`MAX_WEI_PRECISION-1:("+str(wu)+")*`MAX_WEI_PRECISION]; \n"
                                            #                "+wei_units+"; i = i + 1) begin\n\
                                            #               "+str(wei_units_log)+"'d i: jia[] \n\
                                            s += "endcase\n"
                                            s += "end\n"
                                            #MUX ACT
                                            s += "always@(*)begin\n\
                                                case("+act_addr+")\n"
                                            for wu in range(act_units):#TODOS FOR ADAPTIVE PRECISION...
                                                s+= str(wu)+": yi[("+loop_idx+"+1)*`MAX_ACT_PRECISION-1:("+loop_idx+")*`MAX_ACT_PRECISION] = \
                                                       jia_buf[("+str(wu)+"+1)*`MAX_ACT_PRECISION-1:("+str(wu)+")*`MAX_ACT_PRECISION]; \n"
                                            #                "+wei_units+"; i = i + 1) begin\n\
                                            #               "+str(wei_units_log)+"'d i: jia[] \n\
                                            s += "endcase\n"
                                            s += "end\n"
            '''
                
            '''
            for kx in range(int(fd["TKX"])):
                for ky in range(int(fd["TKY"])):
                    for i in range(int(fd["TI"])):
                        for n in range(int(fd["TN"])):
                            for b in range(int(fd["TB"])):
                                for x in range(int(fd["TX"])):
                                    for y in range(int(fd["TY"])):            
                                        s += "always@(*) begin\n\
                                                case(addr)\n\
                                                generate \n\
                                                   : jia[] \n\
                                                endgenerate \n\
                                              end\n"
            
            '''


        
        ############################################
        # WINOGRAD DATAFLOW
        ############################################
        elif("WINOGRAD" in dataflow and "STRIDE_2" in dataflow):
            pass 
        elif("WINOGRAD" in dataflow):
            #推动
            A_LOOP = ["TX", "TY", "TI", "TB"]
            W_LOOP = ["TN", "TI"] #Note, the TKX, TKY is altered into the TX, TY shape (i.e. prepare weights)
            #W_LOOP_FEI = ["TN", "TI", "TKX", "TKY"] (todos) winograd 权重是在计算时计算的

            #1. 便利A的输入，要做变换
            #2. 便利W的输入，（可选）变换 (todos)
            #3. 一个对一个element-wise 乘法
            #4. 后处理（就时A     W*C     AT) 的A和AT可能要处理一下在后端，还是留给ACC做？

            # jia_buf(wei) --> todos --> jia
            # yi_buf(act)  --> todos -->  yi
            #    zi       --> todos --> zi_buf(psum)

            import wincnn


            SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, fd)
                
            #We assume TX == TY, TKX == TKY (todos)
            wino_AT,wino_G,wino_BT,wino_f = wincnn.cookToomFilter([0,1,-1,2,-2, 3, -3, 4, -4, 5, -5, 6, -6],int(fd["WINO_TX"]), int(fd["TKX"]))
            MU = max([gg.denominator for gg in np.array(wino_G).reshape(-1)])
            MU_A = max([gg.denominator for gg in np.array(wino_AT).reshape(-1)])
            wino_G = np.array(MU*wino_G).astype('int')
            wino_A = np.array(wino_AT).transpose()
            wino_GT = np.array(wino_G).transpose()
            wino_B = np.array(wino_BT).transpose()
            wino_BT = np.array(wino_BT)
            wino_AT = np.array(wino_AT)
            print(wino_G, wino_GT)
                      
            if("WINO_PRE_WEIGHT" in dataflow and dataflow["WINO_PRE_WEIGHT"]):
                # jia_buf(wei) --> jia
                pass
                # yi_buf(act)  --> todos -->  yi
            else:
                # jia_buf(wei) --> (MAPPING) --> jia
                #G*WEI
                for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                    for ky in range(int(fd["TKY"])):
                        for i in range(int(fd["TI"])):
                            for n in range(int(fd["TN"])):  
                                s += "wire signed [`WINO_MAX_WEI_PRECISION + "+str(int(np.log2(MU)))+"-1:0] wino_w_"+"_".join([str(jj) for jj in [w_x, ky, i, n]])+";\n"
                                row = []
                                for kx in range(int(fd["TKX"])):
                                    #print(w_x, kx)
                                    idx = "*".join([str(jj) for jj in [fd["TKX"],fd["TKY"],fd["TI"],fd["TN"]]])+"-1-"+gen_index(WULI_LOOP_WEI, fd, ky=ky,kx=kx,i=i,n=n,use_macros=True)
                                    #row.append("$display(jia_buf[("+idx+"+1)*`MAX_WEI_PRECISION-1: "+idx+"*`MAX_WEI_PRECISION];\n")
                                    row.append("jia_buf[("+idx+"+1)*`MAX_WEI_PRECISION-1: ("+idx+")*`MAX_WEI_PRECISION] * "+str(wino_G[w_x][kx])) 
                                s += "assign wino_w_"+"_".join([str(jj) for jj in [w_x, ky, i, n]])+" = " + "+".join(row) + ";\n"
                
                #WEI*GT
                for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                    for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                        for i in range(int(fd["TI"])):
                            for n in range(int(fd["TN"])):  
                                s += "wire signed [`WINO_MAX_WEI_PRECISION + "+str(int(np.log2(MU)))+"-1:0] wino_w_final_"+"_".join([str(jj) for jj in [w_x, w_y, i, n]])+";\n"
                                row = []
                                #print(w_y, ky)
                                for ky in range(int(fd["TKY"])):
                                    row.append("wino_w_"+ "_".join([str(jj) for jj in [w_x, ky, i, n]]) +" * "+str(wino_GT[ky][w_y])) 
                                s += "assign wino_w_final_"+"_".join([str(jj) for jj in [w_x, w_y, i, n]])+" = " + "+".join(row) + ";\n"
                s += "\n\n"

                #BT*ACT
                #Larger loop for input
                print(WULI_LOOP_ACT)
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        
                        s += "\n"
                        for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                            for ky in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                                for i in range(int(fd["TI"])):
                                    for b in range(int(fd["TB"])):  
                                        s += "wire signed [`WINO_MAX_ACT_PRECISION -1:0] wino_a_"+"_".join([str(jj) for jj in [xx,yy,w_x, ky, b, i]])+";\n"
                                        row = []
                                        for kx in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                                            #print(w_x, kx)
                                            idx = "*".join([str(jj) for jj in [(fd["TX"]+fd["TKX"]-1),(fd["TY"]+fd["TKY"]-1),fd["TI"],fd["TB"]]])+"-1-" \
                                                +gen_index(WULI_LOOP_ACT, fd, x=xx,y=yy,ky=ky,kx=kx,i=i,b=b,use_macros=True)
                                            #row.append("$display(jia_buf[("+idx+"+1)*`MAX_WEI_PRECISION-1: "+idx+"*`MAX_WEI_PRECISION];\n")
                                            row.append("yi_buf[("+idx+"+1)*`MAX_ACT_PRECISION-1: ("+idx+")*`MAX_ACT_PRECISION] * "+str(wino_BT[w_x][kx])) 
                                        s += "assign wino_a_"+"_".join([str(jj) for jj in [xx,yy,w_x, ky, b, i]])+" = " + "+".join(row) + ";\n"
                                        
                #ACT*B
                #(TODOS)
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        s += "\n"
                        for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                            for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                                for i in range(int(fd["TI"])):
                                    for b in range(int(fd["TB"])):  
                                        s += "wire signed [`WINO_MAX_ACT_PRECISION -1:0] wino_a_final_"+"_".join([str(jj) for jj in [xx, yy, w_x, w_y, b, i]])+";\n"
                                        row = []
                                        #print(w_y, ky)
                                        for ky in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                                            #print(wino_BT
                                            row.append("wino_a_"+ "_".join([str(jj) for jj in [xx, yy, w_x, ky, b, i]]) +" * "+str(wino_B[ky][w_y])) 
                                        s += "assign wino_a_final_"+"_".join([str(jj) for jj in [xx,yy,w_x, w_y, b, i]])+" = " + "+".join(row) + ";\n"

                #(TODOS, can and should be combined)
                # wino_w_final_<--> jia
                # yi_buf(act)  --> todos -->  yi
                loop_idx = 0
                #remember this order of the physical tiling
                s += "always@(posedge clk) begin\n"
                for b in range(int(fd["TB"])):
                    for n in range(int(fd["TN"])):
                        for i in range(int(fd["TI"])):
                            for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):
                                for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                                        for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                                            #idx_w = gen_index(WULI_LOOP_WEI, fd, ky=w_y, kx=w_x, i=i, n=n,use_macros=True)        #multicast
                                            #idx_a = gen_index(WULI_LOOP_ACT, fd, x=xx,y=yy, ky=w_y,kx=w_x,i=i,b=b,use_macros=True)  #multicast
                                            #(TODOS: WHAT TO DO IF WE HAVE A MULTI_PRECISION FLOW ?)

                                            loop_idx = (w_y +  (int(fd["WINO_TY"])+int(fd["TKY"])-1)*\
                                                        (w_x    +    (int(fd["WINO_TX"]) + int(fd["TKX"])-1)*(i   +  int(fd["TI"])*(n     +   int(fd["TN"]) *(b +\
                                                         xx//int(fd["WINO_TX"]) + int(fd["TX"])//int(fd["WINO_TX"])*(yy//int(fd["WINO_TY"]) +  int(fd["TY"])//int(fd["WINO_TY"])*0) )))))                                            
                                            #print(loop_idx)                             
                                            s += " jia[("+str(loop_idx)+"+1)*`WINO_MAX_WEI_PRECISION-1:"+str(loop_idx)+"*`WINO_MAX_WEI_PRECISION] <= wino_w_final_"+"_".join([str(jj) for jj in [w_x, w_y, i, n]])+";\n"
                                            s += "yi [("+str(loop_idx)+"+1)*`WINO_MAX_ACT_PRECISION-1:"+str(loop_idx)+"*`WINO_MAX_ACT_PRECISION] <= wino_a_final_"+"_".join([str(jj) for jj in [xx,yy,w_x, w_y, b, i]])+";\n"
                                            #loop_idx += 1
                s += "end\n"
                '''
                ##OUTPUT, AT*PSUM
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):
                            for o_x in range(int(fd["WINO_TX"])):
                                for i in range(int(fd["TI"])):
                                    for n in range(int(fd["TN"])):
                                        for b in range(int(fd["TB"])):
                                            s += "wire signed [`MAX_PSUM_PRECISION -1:0] wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+";\n"
                                            row = []
                                            for w_x in range(int(fd["WINO_TX"])+int(fd["TKX"])-1):           
                                                loop_idx = (w_y +  (int(fd["WINO_TY"])+int(fd["TKY"])-1)*\
                                                        (w_x    +    (int(fd["WINO_TX"]) + int(fd["TKX"])-1)*(i   +  int(fd["TI"])*(n     +   int(fd["TN"]) *(b +\
                                                         xx//int(fd["WINO_TX"]) + int(fd["TX"])//int(fd["WINO_TX"])*(yy//int(fd["WINO_TY"]) +  int(fd["TY"])//int(fd["WINO_TY"])*0) )))))
                                                row.append("zi[("+str(loop_idx)+"+1)*`MAX_PSUM_PRECISION-1:"+str(loop_idx)+"*`MAX_PSUM_PRECISION] * "+str(wino_AT[o_x][w_x]))
                                            
                                            s += "assign wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+" = " + "+".join(row) + ";\n"
                                            
                                            
                ##OUTPUT, PSUM*A
                for xx in range(0, int(fd["TX"]) , int(fd["WINO_TX"])):
                    for yy in range(0, int(fd["TY"]) , int(fd["WINO_TY"])):
                        for o_y in range(int(fd["WINO_TX"])):
                            for o_x in range(int(fd["WINO_TX"])):
                                for i in range(int(fd["TI"])):
                                    for n in range(int(fd["TN"])):
                                        for b in range(int(fd["TB"])):
                                            s += "wire signed [`MAX_PSUM_PRECISION -1:0] wino_psum_final_"+"_".join([str(jj) for jj in [xx, yy, o_x, o_y, b, i, n]])+";\n"
                                            row = []
                                            for w_y in range(int(fd["WINO_TY"])+int(fd["TKY"])-1):           
                                                loop_idx = (w_y +  (int(fd["WINO_TY"])+int(fd["TKY"])-1)*\
                                                        (w_x    +    (int(fd["WINO_TX"]) + int(fd["TKX"])-1)*(i   +  int(fd["TI"])*(n     +   int(fd["TN"]) *(b +\
                                                         xx//int(fd["WINO_TX"]) + int(fd["TX"])//int(fd["WINO_TX"])*(yy//int(fd["WINO_TY"]) +  int(fd["TY"])//int(fd["WINO_TY"])*0) )))))
                                                row.append( "wino_psum_"+"_".join([str(jj) for jj in [xx, yy, o_x, w_y, b, i, n]])+ " * "+str(wino_A[w_y][o_y]))
                                            
                                            s += "assign wino_psum_final_"+"_".join([str(jj) for jj in [xx, yy, o_x, o_y, b, i, n]])+" = (" + "+".join(row) + ")/"+str(MU*MU)+";\n"
                '''                                                             

                #FINAL SCALING AND SEND TO OUTPUT (我们需要做加法吗？)
                
                        
                
        ############################################
        # SYSTOLIC DATAFLOW
        ############################################        
        elif("WINOGRAD_SYSTOLIC" in dataflow):
            pass




            



        
        #2.4. other ? like super pe ? (todos)
        #add any flows within this PE unit (tensor unit) such as linear layers, pooling etc. (todos)
        ######################################################
        #s += "    end\n"
    
    s += "endmodule\n\n"
    
    print("\n// GEN_PE VERILOG - DONE\n")



    print(s)
    f.write(s)
    f.close()
