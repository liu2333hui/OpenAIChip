import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import GET_PSUM_LOOP_FILTERS
from utils import order_dataflows

from utils import generate_counter_window

import numpy as np


def loop2index(variables, fd=None, multicast=True, pre = "" ):
    df_d = fd
    if True:
        if(True):
            if (True):
                mini_carte = {
                    "B": "(("+pre+"bb/"+str(df_d["TB"])+")>> TB_shift)",
                    "N": ""+pre+"nnn/"+str(df_d["TNN"]),
                    "X": ""+pre+"xxx/"+str(df_d["TXX"]),
                    "Y": ""+pre+"yyy/"+str(df_d["TYY"]),
                    "KX": "(("+pre+"kkx/"+str(df_d["TKX"])+")>> TKX_shift)",
                    "KY": "(("+pre+"kky/"+str(df_d["TKY"])+")>> TKY_shift)",
                    "I":  ""+pre+"iii/"+str(df_d["TII"]),
                    "TXX": "(("+pre+"xx/"+str(df_d["TX"])+")>> TX_shift)",
                    "TYY": "(("+pre+"yy/"+str(df_d["TY"])+")>> TY_shift)",
                    "TNN":  "(("+pre+"nn/"+str(df_d["TN"])+")>> TN_shift)",
                    "TII":  "(("+pre+"ii/"+str(df_d["TI"])+")>> TI_shift)",
                }
                mini_carte_no_secondary = {
                    "N": "(("+pre+"nn/"+str(df_d["TN"])+")>> TN_shift)",
                    "I": "(("+pre+"ii/"+str(df_d["TI"])+")>> TI_shift)",
                    "X": "(("+pre+"xx/"+str(df_d["TX"])+")>> TX_shift)",
                    "Y": "(("+pre+"yy/"+str(df_d["TY"])+")>> TY_shift)",
                }

                
                cast = {
                    "B": "((batch/"+str(df_d["TB"])+")>> TB_shift)",
                    "N" : "(nc+"+str(df_d["TNN"])+"-1)/"+str(df_d["TNN"]),
                    "X": "(x-fkx+1 +"+str(df_d["TXX"])+"-1)/"+str(df_d["TXX"]),
                    "Y": "(y-fky+1 + "+str(df_d["TYY"])+"-1)/"+str(df_d["TYY"]),
                    "KX": "((fkx/"+str(df_d["TKX"])+")>> TKX_shift)",
                    "KY": "((fky/"+str(df_d["TKY"])+")>> TKY_shift)",
                    "I":  "(ic+"+str(df_d["TII"])+"-1)/"+str(df_d["TII"]),
                    
                    "TXX": "(((x-fkx+1+"+str(df_d["TX"])+"-1)" + "/"+str(df_d["TX"])+")>>TX_shift)",
                    "TYY": "(((y-fky+1+"+str(df_d["TY"])+"-1)" + "/"+str(df_d["TY"])+")>>TY_shift)",
                    "TII": "((ic+"+str(df_d["TI"])+"-1)/"+str(df_d["TI"])+")>> TI_shift)",
                    "TNN": "((nc+"+str(df_d["TN"])+"-1)/"+str(df_d["TN"])+")>> TN_shift)",
                }
                cast_no_secondary = {
                    "X": "((( x +  " + str(df_d["TX"]) + " -1 )/"+str(df_d["TX"])+") >> TX_shift)", #"(" + LIM_X+" + "+str(df_d["TX"])+"-1)/"+str(df_d["TX"]),
                    "Y":  "((( y + " + str(df_d["TY"]) + " -1 )/"+str(df_d["TY"])+") >> TY_shift)",#"(" + LIM_Y+" + "+str(df_d["TY"])+"-1)/"+str(df_d["TY"]),
                    "I": "(((ic+"+str(df_d["TI"])+"-1)/"+str(df_d["TI"])+")>> TI_shift)",
                    "N": "(((nc+"+str(df_d["TN"])+"-1)/"+str(df_d["TN"])+")>> TN_shift)",
                }
                
                idx = ""
                #use qinjiushao algorithm to fast multiply indices
                #for v_idx, var in enumerate(variables):
                loop_order = variables
                for var in loop_order:
                    v = var
                    if((var == "X" and df_d["TXX"] == -1) or
                       (var == "Y" and df_d["TYY"] == -1) or
                       (var == "N" and df_d["TNN"] == -1) or
                       (var == "I" and df_d["TII"] == -1)
                       ):
                        if(multicast==False):
                            idx += "*"+v+"+  "+mini_carte_no_secondary[v]+")"
                        else:
                            idx += "*"+cast_no_secondary[v]+"+  "+mini_carte_no_secondary[v]+")"
                    else:
                        if(multicast==False):
                            idx += "*"+v+"+  "+mini_carte[v]+")"
                        else:
                            idx += "*"+cast[v]+"+  "+mini_carte[v]+")"
                            
                idx ="(0"+ idx
                idx = (len(variables) - 1)*"(" +  idx
                print(idx)
                return idx


########################
# ADDRESS COUNTER
########################
def gen_addr_cnt(hardware_config, meta_config, macro_config):
    
    print("\n// GEN_ADDRESS_COUNTER VERILOG\n")


    f = open(meta_config["dossier"]+"/addr_cnt.v", "w")
    s = ""

    #We assume buffer data of L2 is same as L1 (TODOS)
    #Need to make L2 larger ...
    s += "module ADDR_CNT(\n\
            input clk,\n\
            input rst_n,\n\
                \n\
            input addr_cnt_en,\n\
            output reg operation_done,\n\
                \n\
        input [`MAX_PADDING_X_LOG-1:0] padding_x,\n\
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,\n\
            input [`MAX_STRIDE_LOG-1:0] stride,\n\
            input [`MAX_KX_LOG-1:0] fkx,\n\
            input [`MAX_KY_LOG-1:0] fky,\n\
            input  [`MAX_X_LOG-1:0] x,\n\
            input  [`MAX_Y_LOG-1:0] y,\n\
            input  [`MAX_N_LOG-1:0] nc,\n\
            input  [`MAX_I_LOG-1:0] ic,\n\
            input  [`MAX_B_LOG-1:0] batch,\n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
                \n\
            output reg wei_L2_buf_read_ready, \n\
            input  wei_L2_buf_read_valid, \n\
            output reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_read_addr, \n\
            input  [`WEI_BUF_DATA -1 :0] wei_L2_buf_read_data, \n\
                \n\
            output reg act_L2_buf_read_ready, \n\
            input  act_L2_buf_read_valid, \n\
            output reg [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_L2_buf_read_addr, \n\
            input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, \n\
                \n\
            output reg act_L1_buf_write_en,\n\
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_write_addr, \n\
            output reg [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, \n\
                \n\
            output  reg wei_L1_buf_write_en,\n\
            output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr, \n\
            output reg  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, \n\
                \n\
            output reg act_L1_buf_read_en,\n\
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_read_addr, \n\
                \n\
            output reg  wei_L1_buf_read_en,\n\
            output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_read_addr, \n\
                \n\
            output reg mac_en,\n\
            \n\
        output reg [`MAX_KX_LOG-1:0] kkx,\n\
        output reg [`MAX_KY_LOG-1:0] kky,\n\
        output reg [`MAX_X_LOG-1:0] xx,\n\
        output reg [`MAX_Y_LOG-1:0] yy, \n\
        output reg [`MAX_X_LOG-1:0] xxx,\n\
        output reg[`MAX_Y_LOG-1:0] yyy, \n\
        output  reg[`MAX_N_LOG-1:0] nn, \n\
        output reg[`MAX_I_LOG-1:0] ii, \n\
        output reg[`MAX_N_LOG-1:0] nnn, \n\
        output reg[`MAX_I_LOG-1:0] iii, \n\
        output reg[`MAX_B_LOG-1:0] bb,\n\
            \n\
        output reg [`MAX_KX_LOG-1:0] ACC_kkx,\n\
        output reg [`MAX_KY_LOG-1:0] ACC_kky,\n\
        output reg [`MAX_X_LOG-1:0] ACC_xx,\n\
        output reg [`MAX_Y_LOG-1:0] ACC_yy, \n\
        output reg [`MAX_X_LOG-1:0] ACC_xxx,\n\
        output reg[`MAX_Y_LOG-1:0] ACC_yyy, \n\
        output reg [`MAX_N_LOG-1:0] ACC_nn, \n\
        output reg[`MAX_I_LOG-1:0] ACC_ii, \n\
        output reg[`MAX_N_LOG-1:0] ACC_nnn, \n\
        output reg[`MAX_I_LOG-1:0] ACC_iii, \n\
        output reg[`MAX_B_LOG-1:0] ACC_bb,\n\
            \n\
        input accum_done,\n\
            \n\
        input pe_array_ready,\n\
        input pe_array_last\n\
        );\n"


    s += "reg done;\n"
    
    #ADDRESS COUNTER
    '''
    s += "reg [`MAX_KX_LOG-1:0] kkx;\n"
    s += "reg [`MAX_KY_LOG-1:0] kky;\n"
    s += "reg [`MAX_X_LOG-1:0] xx;\n"
    s += "reg [`MAX_Y_LOG-1:0] yy;\n"
    s += "reg [`MAX_X_LOG-1:0] xxx;\n"
    s += "reg [`MAX_Y_LOG-1:0] yyy;\n"
    s += "reg [`MAX_N_LOG-1:0] nn;\n"
    s += "reg [`MAX_I_LOG-1:0] ii;\n"
    s += "reg [`MAX_N_LOG-1:0] nnn;\n"
    s += "reg [`MAX_I_LOG-1:0] iii;\n"
    s += "reg [`MAX_B_LOG-1:0] bb;\n"

    '''

    ########################
    # LOOP
    ########################
    CONV2D = order_dataflows(hardware_config)
    for idx, flows in enumerate(CONV2D):
        fd = hardware_config["TILINGS"]["CONV2D"][flows]
        dataflow = fd["DATAFLOW"]
        df_d = fd

        from utils import GET_PSUM_LOOP_FILTERS, GET_LOOP_FILTERS
        SHI_LOOP_PSUM, WULI_LOOP_PSUM = GET_PSUM_LOOP_FILTERS(hardware_config, df_d)


        SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
                WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)
            
        wei_loop_order = []
        act_loop_order = []
        psum_loop_order = []
        loop_order = df_d["LOOP"]
        for l in loop_order:
            #print(l)
            if(l in SHI_LOOP_WEI):
                wei_loop_order.append(l)
            if(l in SHI_LOOP_ACT):
                act_loop_order.append(l)
            if(l in SHI_LOOP_PSUM):
                psum_loop_order.append(l)
        
                

        
        # ADAPTABILITY (BitFusion)
        #(TODOS) adapative precisions
        s += "reg [5:0] a_ratio;"
        s += "reg [5:0] w_ratio;"

        s += "reg [5:0] TX_lv;"
        s += "reg [5:0] TY_lv;"    
        s += "reg [5:0] TKX_lv;"    
        s += "reg [5:0] TKY_lv;"
        s += "reg [5:0] TN_lv;"
        s += "reg [5:0] TB_lv;"
        s += "reg [5:0] TI_lv;"

        s += "reg [3:0] TX_shift;"
        s += "reg [3:0] TY_shift;"    
        s += "reg [3:0] TKX_shift;"    
        s += "reg [3:0] TKY_shift;"
        s += "reg [3:0] TN_shift;"
        s += "reg [3:0] TB_shift;"
        s += "reg [3:0] TI_shift;"

        s += "always@(*) begin\n"
        max_wei_prec = macro_config[ "MAX_WEI_PRECISION_INT" ]
        max_act_prec = macro_config[ "MAX_ACT_PRECISION_INT" ]
        for wei_type in hardware_config["SUPPORTED_WEI_DTYPES"]:
            for act_type in hardware_config["SUPPORTED_ACT_DTYPES"]:
                if(not("INT" in wei_type and "INT" in act_type)):
                    continue
                wei_prec = wei_type.split("INT")[1]
                act_prec = act_type.split("INT")[1]
                w_ratio = max_wei_prec // int(wei_prec)
                a_ratio = max_act_prec // int(act_prec)

                gcd = int(np.gcd(w_ratio,a_ratio))
                s += "if(act_precision == "+act_prec+" &  wei_precision == "+wei_prec+") begin \n\
                        w_ratio ="+ str(max_wei_prec // int(wei_prec))+"; \n\
                        a_ratio ="+ str(max_act_prec // int(act_prec))+"; \n\
                        TX_lv = 1;\n\
                        TY_lv = 1;\n\
                        TKX_lv = 1;\n\
                        TKY_lv = 1;\n\
                        TN_lv = 1;\n\
                        TB_lv = 1;\n\
                        TI_lv = 1;\n\
                            \n\
                        TX_shift = 0;\n\
                        TY_shift = 0;\n\
                        TKX_shift = 0;\n\
                        TKY_shift = 0;\n\
                        TN_shift = 0;\n\
                        TB_shift = 0;\n\
                        TI_shift = 0;\n"                        
                lv = {}
                if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
                    lv[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] = lv.get(hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"], 1) * a_ratio//gcd
                                                                    
                if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
                    lv[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] = lv.get(hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"], 1) * w_ratio//gcd

                if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
                    lv[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] = lv.get(hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"], 1) * gcd         

                for lp in lv:
                    s += lp+"_lv = " + str(lv[lp]) + ";\n"
                    s += lp+"_shift = " + str(np.log2(lv[lp]))+ ";\n"

                s += "end\n"
        s += "end\n"




        ########################
        # Generate addresses for the L1, L2 buffers
        # Read and Write (L2 no write for now, that is outside the core)
        ########################

        ########################
        # 1. L1 hit/miss
        # 1.1. If Hit, dont need L2 interaction
        # 1.2. If MIss, need L2
        #
        # 2. Generate correct Addresses and timing and pipelining if possible
        ########################

        # 1. L1 hit/miss
        #(TODOS) assume L2_row = L1_row, otherwise need systolic or fifo
        from utils import get_indices_map, get_limits_map, get_hard_limits_map

        #(TODO)
        idx_map = get_indices_map(fd )
        lim_map = get_limits_map(fd, kx_alias = "fkx", ky_alias = "fky")
        print(lim_map)
        
        #s += "assign L1_wei_miss = "

        #get terms
        wei_reuse_terms = [{"MIN": "1"}]
        act_reuse_terms = [{"MIN": "1"}]

        loop_names = ["MIN"] + loop_order[::-1]
    
        for l in loop_order[::-1]:
            wei_d = dict(wei_reuse_terms[-1])
            if(l in SHI_LOOP_WEI):
                wei_d[l] = lim_map[l]
            wei_reuse_terms.append(wei_d)
            
            act_d = dict(act_reuse_terms[-1])
            if(l in SHI_LOOP_ACT):
                act_d[l] = lim_map[l]
            act_reuse_terms.append(act_d)

            
        #analysis
        WEI_REUSE_MAP = {
            "I": "0",
            "N": "0",
            "X": "1" ,
            "Y": "1",
            "B": "1",
            "KX": "0",
            "KY": "0",
            "TXX": "1",
            "TYY": "1",
            "TNN": "0",
            "TII": "0",
            "MIN": "1",
        }
        ACT_REUSE_MAP = {
            "I": "0",
            "N": "1",
            "X": "0" ,
            "Y": "0",
            "B": "0",
            "KX": "0",
            "KY": "0",
            "TXX": "0",
            "TYY": "0",
            "TNN": "1",
            "TII": "0",
            "MIN": "1",
        }
        s += "//reuse L1/L2 logic \n"
        for idx, wt in enumerate(wei_reuse_terms):
            KX_TERM = wt.get("KX", "1")
            KY_TERM = wt.get("KY", "1")
            if("TII" in wt and "I" not in wt):
                I_TERM = wt.get("TII", "1")
            else:
                I_TERM = wt.get("I", "1")

            if("TNN" in wt and "N" not in wt):
                N_TERM = wt.get("TNN", "1")
            else:
                N_TERM = wt.get("N", "1")

            fang ="*".join([I_TERM, N_TERM, KY_TERM, KX_TERM])

        
            s += "wire L1_wei_reuse_" + loop_names[idx] + ";\n"
            s += "assign L1_wei_reuse_" + loop_names[idx] + " = ( "+WEI_REUSE_MAP[loop_names[idx]]+" & ( "+ fang + " <= `WEI_BUF_ROWS)) ;\n"


        for idx, at in enumerate(act_reuse_terms):

            B_TERM = at.get("KY", "1")
            if("TII" in at and "I" not in at):
                I_TERM = at.get("TII", "1")
            else:
                I_TERM = at.get("I", "1")

            KX_TERM = at.get("KX", "1")
            KY_TERM = at.get("KY", "1")

            if("TYY" in at and "Y" not in at):
                Y_TERM = at.get("TYY", "1")
            else:
                Y_TERM = at.get("Y", "1")
                
            if("TXX" in at and "X" not in at):
                X_TERM = at.get("TXX", "1")
            else:
                X_TERM = at.get("X", "1")

            #Dont know if KX > TXX, so need this
            fang_cond0 = "("+ "*".join([I_TERM, B_TERM, Y_TERM, X_TERM])   + "<= `ACT_BUF_ROWS )"
            fang_cond1 = "("+ "*".join([I_TERM, B_TERM, Y_TERM, KX_TERM])  + "<= `ACT_BUF_ROWS )"
            fang_cond2 = "("+ "*".join([I_TERM, B_TERM, KY_TERM, X_TERM])  + "<= `ACT_BUF_ROWS )"
            fang_cond3 = "("+ "*".join([I_TERM, B_TERM, KY_TERM, KX_TERM]) + "<= `ACT_BUF_ROWS )"
            fang = "&".join([fang_cond0,fang_cond1,fang_cond2,fang_cond3])
        
            s += "wire L1_act_reuse_" + loop_names[idx] + ";\n"
            s += "assign L1_act_reuse_" + loop_names[idx] + " = ( "+ACT_REUSE_MAP[loop_names[idx]]+" & ( "+ fang + " )) ;\n"

        wei_terms = []
        act_terms = []
        for idx,l in enumerate(loop_order[::-1]):
            act_terms.append("(  L1_act_reuse_"+loop_names[idx+1]+" & (" + idx_map[l] + " > 0)  )")
            wei_terms.append("(  L1_wei_reuse_"+loop_names[idx+1]+" & (" + idx_map[l] + " > 0)  )")
            
        s += "wire L1_act_hit = " + "|".join(act_terms) + ";\n"
        s += "wire L1_wei_hit = " + "|".join(wei_terms) + ";\n"

        #"DEBUG"
        '''
        s += 'always@(negedge clk) begin \n\
                $display("-----------------------");\n\
                $display("xx\tyy\tkkx\tkky\tii\tnn\txxx\tyyy");\n\
                $display(xx,"\t",yy,"\t",kkx,"\t",kky,"\t",ii,"\t",nn,"\t",xxx,"\t",yyy);\n\
                $display("L1_act_hit", L1_act_hit);\n\
                $display("L1_wei_hit", L1_wei_hit);\n\
              end\n'
        '''
        #print(wei_d, act_d)
        #print(s)
        #exit()      
        #L1_wei_miss = (L1_wei_reuse_N & nn == 0) | (L1_wei_reuse_I & ii == 0) | (L1_wei_reuse_TNN & ) | (L1_wei_reuse_TII & )  


        ###############################
        ###########2. Generate Addresses

        ########################2.1 Pipelineing

        L2_DELAY = hardware_config["L2_READ_DELAY"]

        #Stage 1 (L2 read)
        pre = "L2_READ_"
        s += "reg [`MAX_KX_LOG-1:0]"+pre+"kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0]"+pre+"kky;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yy;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xxx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yyy;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"ii;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nnn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"iii;\n"
        s += "reg [`MAX_B_LOG-1:0] "+pre+"bb;\n"

        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"
        #s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"

        s += "reg L2_READ_en;\n"
        s += "assign addr_cnt_en_ = L2_READ_en;\n"#addr_cnt_en & (wei_L2_buf_read_addr > 0) & (act_L2_buf_read_addr > 0);\n"
        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "wei_addr;\n"
        s += "reg [`L2_ACT_BUF_ROWS_LOG2-1:0] " + pre + "act_addr;\n" #(TODOS) 用L2_BUF_ROWS

        s += "reg "+pre+"L1_act_hit;\n"
        s += "reg "+pre+"L1_wei_hit;\n"
        s += "reg "+pre+"done;\n"

        #Stage 2 (L1 write)
        pre = "L1_WRITE_"
        s += "reg [`MAX_KX_LOG-1:0]"+pre+"kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0]"+pre+"kky;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yy;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xxx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yyy;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"ii;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nnn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"iii;\n"
        s += "reg [`MAX_B_LOG-1:0] "+pre+"bb;\n"

        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"

        s += "reg L1_WRITE_en;\n"
        s += "reg L1_WRITE_state;\n" #0 not used, 1 is used
        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "wei_addr;\n"
        s += "reg [`L2_ACT_BUF_ROWS_LOG2-1:0] " + pre + "act_addr;\n" #(TODOS) 用L2_BUF_ROWS
        
        s += "reg "+pre+"L1_act_hit;\n"
        s += "reg "+pre+"L1_wei_hit;\n"
        s += "reg "+pre+"done;\n"
        #Stage 3 (L1 read)
        pre = "L1_READ_"
        s += "reg [`MAX_KX_LOG-1:0]"+pre+"kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0]"+pre+"kky;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yy;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xxx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yyy;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"ii;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nnn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"iii;\n"
        s += "reg [`MAX_B_LOG-1:0] "+pre+"bb;\n"


        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"

        
        s += "reg L1_READ_en;\n"
        s += "reg L1_READ_state;\n" #0 not used, 1 is used
        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "wei_addr;\n"
        s += "reg [`L2_ACT_BUF_ROWS_LOG2-1:0] " + pre + "act_addr;\n" #(TODOS) 用L2_BUF_ROWS

        
        s += "reg "+pre+"L1_act_hit;\n"
        s += "reg "+pre+"L1_wei_hit;\n"
        s += "reg "+pre+"done;\n"
        
        #Stage 4 (MAC UNIT)
        pre = "MAC_"
        s += "reg [`MAX_KX_LOG-1:0]"+pre+"kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0]"+pre+"kky;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yy;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xxx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yyy;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"ii;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nnn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"iii;\n"
        s += "reg [`MAX_B_LOG-1:0] "+pre+"bb;\n"


        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"


        s += "reg MAC_en;\n"
        s += "reg MAC_state;\n" #0 not used, 1 is used
        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "wei_addr;\n"
        s += "reg [`L2_ACT_BUF_ROWS_LOG2-1:0] " + pre + "act_addr;\n" #(TODOS) 用L2_BUF_ROWS

        s += "always@(*) begin\n"
        s += " mac_en = MAC_en;//L1_READ_en;\n"
        s += "end\n"
        
        s += "reg "+pre+"L1_act_hit;\n"
        s += "reg "+pre+"L1_wei_hit;\n"
        s += "reg "+pre+"done;\n"
        
        #Stage 5 PSUM/ACCUMULATOR related
        pre = "ACC_"
        '''
        s += "reg [`MAX_KX_LOG-1:0]"+pre+"kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0]"+pre+"kky;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yy;\n"
        s += "reg [`MAX_X_LOG-1:0] "+pre+"xxx;\n"
        s += "reg [`MAX_Y_LOG-1:0] "+pre+"yyy;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"ii;\n"
        s += "reg [`MAX_N_LOG-1:0] "+pre+"nnn;\n"
        s += "reg [`MAX_I_LOG-1:0] "+pre+"iii;\n"
        s += "reg [`MAX_B_LOG-1:0] "+pre+"bb;\n"
        '''


        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "tiled_wei_addr;\n"

        
        s += "reg ACC_en;\n"
        s += "reg ACC_state;\n"
        s += "reg [`L2_WEI_BUF_ROWS_LOG2-1:0] " + pre + "wei_addr;\n"
        s += "reg [`L2_ACT_BUF_ROWS_LOG2-1:0] " + pre + "act_addr;\n" #(TODOS) 用L2_BUF_ROWS
        
        s += "reg "+pre+"L1_act_hit;\n"
        s += "reg "+pre+"L1_wei_hit;\n"
        s += "reg "+pre+"done;\n"
        
        # Stage 1 L2_READ -> L1_WRITE
        pre = "L2_READ_"
        s += "always@(*) begin\n"
        s += " "+pre+"kkx = kkx;\n"
        s += " "+pre+"kky = kky;\n"
        s += " "+pre+"xx = xx;\n"
        s += " "+pre+"yy = yy;\n"
        s += " "+pre+"xxx = xxx;\n"
        s += " "+pre+"yyy = yyy;\n"
        s += " "+pre+"nn = nn;\n"
        s += " "+pre+"ii = ii;\n"
        s += " "+pre+"nnn = nnn;\n"
        s += " "+pre+"iii = iii;\n"
        s += " "+pre+"bb = bb;\n"

        s += pre+"en = addr_cnt_en ;\n"

        s += "" + pre + "tiled_wei_addr = "+ loop2index(wei_loop_order, fd = fd, pre=pre)+";\n"

        s += pre+"wei_addr = wei_L2_buf_read_addr;\n"
        s += pre+"act_addr = act_L2_buf_read_addr;\n"

        s += pre+"L1_act_hit = L1_act_hit;\n"
        s += pre+"L1_wei_hit = L1_wei_hit;\n"

        s += pre+"done = operation_done;\n"
        s += "end\n"

        #Stage 2 L1_WRITE -> L1_READ
        prev = pre
        pre = "L1_WRITE_"
        s += "always@(posedge clk or negedge rst_n) begin\n"
        s += "if(~rst_n) begin \n\
            "+pre+"state <= 0;\n\
            "+pre+"en <= 0;\n\
            "+pre+"done <= 0;\n\
               end else begin\n\
         "+pre+"kkx <= "+prev+"kkx;\n\
        "+pre+"kky <= "+prev+"kky;\n\
         "+pre+"xx <=  "+prev+"xx;\n\
         "+pre+"yy <=  "+prev+"yy;\n\
        "+pre+"xxx <= "+prev+"xxx;\n\
         "+pre+"yyy <= "+prev+"yyy;\n\
         "+pre+"nn <=  "+prev+"nn;\n\
         "+pre+"ii <=  "+prev+"ii;\n\
         "+pre+"nnn <= "+prev+"nnn;\n\
         "+pre+"iii <= "+prev+"iii;\n\
         "+pre+"bb <=  "+prev+"bb;\n\
         "+pre+"en <=  "+prev+"en;\n\
                \n\
        "+pre+"wei_addr <= "+prev+"wei_addr ;\n\
        "+pre+"act_addr <= "+prev+"act_addr ;\n\
        "+pre+"L1_act_hit <= "+prev+"L1_act_hit;\n\
        "+pre+"L1_wei_hit <= "+prev+"L1_wei_hit;\n\
                \n\
        "+pre+"done <= "+prev+"done;\n\
                \n\
        "+pre+"tiled_wei_addr <= "+prev+"tiled_wei_addr;\n\
                \n\
            end\n\
            end\n"

        #Stage 3 L1_READ -> L1_MAC
        prev = pre
        pre = "L1_READ_"
        s += "always@(posedge clk or negedge rst_n) begin\n"
        s += "if(~rst_n) begin \n\
            "+pre+"state <= 0;\n\
            "+pre+"en <= 0;\n\
            "+pre+"done <= 0;\n\
               end else begin\n\
         "+pre+"kkx <= "+prev+"kkx;\n\
        "+pre+"kky <= "+prev+"kky;\n\
         "+pre+"xx <=  "+prev+"xx;\n\
         "+pre+"yy <=  "+prev+"yy;\n\
        "+pre+"xxx <= "+prev+"xxx;\n\
         "+pre+"yyy <= "+prev+"yyy;\n\
         "+pre+"nn <=  "+prev+"nn;\n\
         "+pre+"ii <=  "+prev+"ii;\n\
         "+pre+"nnn <= "+prev+"nnn;\n\
         "+pre+"iii <= "+prev+"iii;\n\
         "+pre+"bb <=  "+prev+"bb;\n\
         "+pre+"en <=  "+prev+"en;\n\
                \n\
        "+pre+"wei_addr <= "+prev+"wei_addr ;\n\
        "+pre+"act_addr <= "+prev+"act_addr ;\n\
        "+pre+"L1_act_hit <= "+prev+"L1_act_hit;\n\
        "+pre+"L1_wei_hit <= "+prev+"L1_wei_hit;\n\
                \n\
        "+pre+"tiled_wei_addr <= "+prev+"tiled_wei_addr;\n\
                \n\
        "+pre+"done <= "+prev+"done;\n\
            end\n\
            end\n"

        #Stage 4 L1_READ -> L1_MAC
        prev = pre
        pre = "MAC_"
        s += "always@(posedge clk or negedge rst_n) begin\n"
        s += "if(~rst_n) begin \n\
            "+pre+"state <= 0;\n\
            "+pre+"en <= 0;\n\
            "+pre+"done <= 0;\n\
               end else begin\n\
         "+pre+"kkx <= "+prev+"kkx;\n\
        "+pre+"kky <= "+prev+"kky;\n\
         "+pre+"xx <=  "+prev+"xx;\n\
         "+pre+"yy <=  "+prev+"yy;\n\
        "+pre+"xxx <= "+prev+"xxx;\n\
         "+pre+"yyy <= "+prev+"yyy;\n\
         "+pre+"nn <=  "+prev+"nn;\n\
         "+pre+"ii <=  "+prev+"ii;\n\
         "+pre+"nnn <= "+prev+"nnn;\n\
         "+pre+"iii <= "+prev+"iii;\n\
         "+pre+"bb <=  "+prev+"bb;\n\
         "+pre+"en <=  "+prev+"en;\n\
                \n\
        "+pre+"wei_addr <= "+prev+"wei_addr ;\n\
        "+pre+"act_addr <= "+prev+"act_addr ;\n\
        "+pre+"L1_act_hit  <= "+prev+"L1_act_hit;\n\
        "+pre+"L1_wei_hit <= "+prev+"L1_wei_hit;\n\
            \n\
        "+pre+"tiled_wei_addr <= "+prev+"tiled_wei_addr;\n\
            \n\
        "+pre+"done <= "+prev+"done;\n\
                \n\
            end\n\
            end\n"

        
        #Stage 4 L1_READ -> L1_MAC
        prev = pre
        pre = "ACC_"
        s += "always@(*) begin\n\
         "+pre+"kkx <= "+prev+"kkx;\n\
        "+pre+"kky <= "+prev+"kky;\n\
         "+pre+"xx <=  "+prev+"xx;\n\
         "+pre+"yy <=  "+prev+"yy;\n\
        "+pre+"xxx <= "+prev+"xxx;\n\
         "+pre+"yyy <= "+prev+"yyy;\n\
         "+pre+"nn <=  "+prev+"nn;\n\
         "+pre+"ii <=  "+prev+"ii;\n\
         "+pre+"nnn <= "+prev+"nnn;\n\
         "+pre+"iii <= "+prev+"iii;\n\
         "+pre+"bb <=  "+prev+"bb;\n\
         "+pre+"en <=  "+prev+"en;\n\
                \n\
        "+pre+"wei_addr <= "+prev+"wei_addr ;\n\
        "+pre+"act_addr <= "+prev+"act_addr ;\n\
        "+pre+"L1_act_hit  <= "+prev+"L1_act_hit;\n\
        "+pre+"L1_wei_hit <= "+prev+"L1_wei_hit;\n\
            \n\
        "+pre+"tiled_wei_addr <= "+prev+"tiled_wei_addr;\n\
            \n\
        "+pre+"done <= "+prev+"done;\n\
                \n\
            end\n"


        
        s += generate_counter_window(fd=df_d, WINDOW=2, kx_alias = "fkx", ky_alias = "fky")

        ##############2.1. ADDRESS COUNTERS
        #DIRECT FLOW
        #(TODOS) FOR SPARSE FLOW, this index can "skip"


        s += "always@(posedge clk or negedge rst_n) begin\n\
                  if(~rst_n) begin\n\
                        kkx <= 0;\n\
                        kky <= 0;\n\
                        xx <= 0;\n\
                        yy <= 0;\n\
                        xxx <= 0;\n\
                        yyy <= 0;\n\
                        nn <= 0;\n\
                        ii <= 0;\n\
                        nnn <= 0;\n\
                        iii <= 0;\n\
                        bb <= 0;\n\
                   end else begin\n\
                        if(addr_cnt_en_ & ~operation_done)begin\n\
                                kkx <= kkx_1;\n\
                        kky <= kky_1;\n\
                        xx <= xx_1;\n\
                        yy <= yy_1;\n\
                        nn <= nn_1;\n\
                        ii <= ii_1;\n\
                        bb <= bb_1;\n"
        if("TXX" in df_d["LOOP"]):
            s += "xxx <= xxx_1;\n"
        if("TYY" in df_d["LOOP"]):
            s += "yyy <= yyy_1;\n"
        if("TNN" in df_d["LOOP"]):
            s += "nnn <= nnn_1;\n"
        if("TII" in df_d["LOOP"]):
            s += "iii <= iii_1;\n"
            
        s += "          end\n\
                   end\n\
              end\n"



        
        ########################2.2. L2 BUFFERS

        s += "always@(*) begin\n\
                wei_L2_buf_read_ready <= ~done & L2_READ_en & ~L1_wei_hit;\n\
                act_L2_buf_read_ready <=~done & L2_READ_en & ~L1_act_hit;\n\
            end\n"

        ####One counter for read_addr (from L1 to )
        ####(TODOS) assume the SRAM (L2) takes one cycle to read a result
        #### Will adjust in the future to take into account multi-cycle reads ...
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                         act_L2_buf_read_addr <= 0; \n\
                    end else begin \n\
                        if(~done &L2_READ_en & ~L1_act_hit)begin\n\
                         act_L2_buf_read_addr <= act_L2_buf_read_addr + 1; \n\
                        end\n\
                    end\n\
              end\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                         wei_L2_buf_read_addr <= 0; \n\
                    end else begin \n\
                        if(~done &L2_READ_en & ~L1_wei_hit)begin\n\
                         wei_L2_buf_read_addr <= wei_L2_buf_read_addr + 1;\n\
                        end\n\
                    end\n\
              end\n"

        #Data pipeline
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin \n\
                   act_L1_buf_write_data <= 0; \n\
                   wei_L1_buf_write_data <= 0; \n\
                end else begin\n\
                act_L1_buf_write_data <= act_L2_buf_read_data;\n\
                wei_L1_buf_write_data <= wei_L2_buf_read_data;\n\
                end \n\
              end\n"

        ########################2.3. L1 BUFFERS

        #(PATCH)
        s += "wire L1_act_done;\n"

        s += "reg act_done, wei_done;\n"


        #L1 BUFFER WRITE
        #(TODOS) STALLING due to stalls in the MLTIPLIER PIPELINE
        ####Another counter for write_addr (from L2 to L1),(todos) should we split this into two for the future for power analysis ?
        s += "always@(*) begin\n\
                        \n\
                        wei_L1_buf_write_addr <=  L1_WRITE_wei_addr[`WEI_BUF_ROWS_LOG2-1:0];\n\
                        act_L1_buf_write_addr <=  L1_WRITE_act_addr[`ACT_BUF_ROWS_LOG2-1:0];\n\
                        wei_L1_buf_write_en  <= ~done & L1_WRITE_en & ~L1_WRITE_L1_wei_hit & wei_L2_buf_read_valid ;\n\
                        act_L1_buf_write_en  <=  ~L1_act_done & ~done &L1_WRITE_en & ~L1_WRITE_L1_act_hit & act_L2_buf_read_valid & ~act_done;\n\
                        wei_L1_buf_read_en   <=  L1_READ_en;\n\
                        act_L1_buf_read_en   <=  L1_READ_en;\n\
                        \n\
                  end\n"        



        #L1 BUFFER READ


        ###########2.0 Preparation 
        TX = str(df_d["TX"]) + ">> TX_shift"
        TY = str(df_d["TY"]) + ">> TY_shift"
        TXX = str(df_d["TXX"])
        TYY = str(df_d["TYY"]) 
        TI = str(df_d["TI"]) 


        Y_FKY = False
        X_FKX = False
        for idx,l in enumerate(df_d["LOOP"][::-1]):
            if(l == "KX"):
                KX_IDX = idx
            if(l == "KY"):
                KY_IDX = idx
            if((l == "Y" and "TYY" not in df_d["LOOP"]) or l == "TYY"):
                Y_IDX = idx
            if((l == "X" and "TXX" not in df_d["LOOP"]) or l == "TXX"):
                X_IDX = idx

        Y_FKY = (Y_IDX > KY_IDX)
        X_FKX = (X_IDX > KX_IDX)

        #print("COND",X_IDX,Y_IDX,KX_IDX,KY_IDX,Y_FKY,X_FKX, LIM_Y, LIM_X)

        #(TODOS)
        pre = "L1_WRITE_"
        LIM_X = "((x + padding_x*2 - fkx + 1) / stride  )"
        LIM_Y = "((y + padding_y*2 - fky + 1) / stride  )"

        
        if(Y_FKY):#TODOS
            cond_1 = "("+pre+"xx == 0 & "+pre+"yy > 0 & fky >= "+TY+"  & "+pre+"kky < fky - "+TY+")"
            cond_1_tou = "("+pre+"xx == 0 & "+pre+"yy > 0)"
            cond_1_wei = "(fky >= "+TY+"  & "+pre+"kky < fky - "+TY+")"
        else:
            if("TYY" in df_d["LOOP"]):
                cond_1_tou = "1"
                cond_1_wei =  "( (("+pre+"kky >= "+TY+") | ("+pre+"yyy > 0)) & ("+pre+"yy < " + TYY +"-"+ TY + ")   &  ("+pre+"yyy + "+pre+"yy +"+TY+"<= "+LIM_Y+" ))"
            else:
                cond_1_tou = "1"
                cond_1_wei =  "( ("+pre+"kky >= "+TY+")   &  ("+pre+"yy +"+TY+"< "+LIM_Y+" ))"

            #cond_1 = "( ("+pre+"kky >= "+TY+") & ("+pre+"yy +"+TY+"< "+LIM_Y+"))"
            #cond_1_tou = "1"
            #cond_1_wei = cond_1

        
        if(X_FKX):
            if("TXX" in df_d["LOOP"]):#TODOS
                cond_2_tou = "("+pre+"xx > 0 & "+pre+"yy == 0)"
                cond_2_wei = "(fkx >= "+TX+" &("+pre+"kkx < fkx - "+TX+"))"
            else: 
                cond_2_tou = "("+pre+"xx > 0 & "+pre+"yy == 0)"
                cond_2_wei = "(fkx >= "+TX+" &("+pre+"kkx < fkx - "+TX+"))"
        else:
            if("TXX" in df_d["LOOP"]):
                cond_2_tou = "1"
                cond_2_wei =  "( (("+pre+"kkx >= "+TX+") | ("+pre+"xxx > 0)) & ("+pre+"xx < " + TXX +"-"+ TX + ")   &  ("+pre+"xxx + "+pre+"xx +"+TX+"<= "+LIM_X+" ))"
            else:
                cond_2_tou = "1"
                cond_2_wei =  "( ("+pre+"kkx >= "+TX+")   &  ("+pre+"xx +"+TX+"< "+LIM_X+" ))"

        cond_1 = cond_1_tou+"&"+cond_1_wei       
        cond_2 = cond_2_tou+"&"+cond_2_wei

        
        if(Y_FKY and X_FKX):
            cond_3_tou = "("+pre+"xx > 0 & "+pre+"yy > 0)"
        elif(Y_FKY and not X_FKX):
            cond_3_tou = "("+pre+"yy > 0)"
        elif(not Y_FKY and X_FKX):
            cond_3_tou = "("+pre+"xx > 0)"
        else:
            cond_3_tou = ""
            
        cond_3 = "("+cond_3_tou + "& (("+cond_2_wei+") | ("+cond_1_wei+"))   )"
        '''
        if(Y_FKY and X_FKX):
            cond_3 = "("+pre+"xx > 0 & "+pre+"yy > 0 & (((fkx >= "+TX+") &("+pre+"kkx < fkx - "+TX+")) | ( ( fky >= "+TY+") &( "+pre+"kky < fky - "+TY+"))) ) "
        elif(Y_FKY and not X_FKX):
            cond_3 = "("+pre+"xx > 0 & "+pre+"yy > 0 & (("+pre+"kkx >= "+TX+")   &  ("+pre+"xx +"+TX+"< "+LIM_X+" )) | ( ( fky >= "+TY+") &( "+pre+"kky < fky - "+TY+"))) ) "
        elif(not Y_FKY and X_FKX):
            cond_3 = "("+pre+"xx > 0 & "+pre+"yy > 0 & (((fkx >= "+TX+") &("+pre+"kkx < fkx - "+TX+")) | ("+pre+"kky >= "+TY+" & ("+pre+"yy +"+TY+"< "+LIM_Y+") ) )"
        else:
            cond_3 = "("+pre+"xx > 0 & "+pre+"yy > 0 & ((("+pre+"kkx >= "+TX+")   &  ("+pre+"xx +"+TX+"< "+LIM_X+" ) ) | (( "+pre+"kky >= "+TY+") & ("+pre+"yy +"+TY+"< "+LIM_Y+") ) ) )"
        '''
        cond_4 = ""+pre+"nn>0"

        #f.write("$display("+cond_1+","+cond_2+","+cond_3+","+cond_4+");\n")
        #(THE INDEX TABLE FOR ACTIVATION REUSE)
        #(TODOS) How to size this buffer ?
        INDEX_ROWS = 1024
        INDEX_ROWS_LOG = int(np.log2(INDEX_ROWS))
        s += "reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] index_table [0:"+str(INDEX_ROWS)+"];\n"
        s += "reg reuse;\n"
        #read from buffer
        prev = "L1_WRITE_"
        pre = "L1_READ_"

        for i in range(1024):
            s += "wire [ `ACT_BUF_ROWS_LOG2  - 1 :0] index_table_d"+str(i)+";\n"
            s += "assign index_table_d"+str(i)+" = index_table["+str(i)+"];\n"



        s += "wire [31:0] index_table_addr;\n"
        s += "assign index_table_addr  = ("+prev+"bb)*ic*(x)*(y) + ("+prev+"ii)*(y)*(x)+("+prev+"kkx+"+prev+"xx+"+prev+"xxx)*(y) + ("+prev+"kky+"+prev+"yy+"+prev+"yyy);\n"
        s += "reg [31:0] index_table_out;\n"

        s += "reg [31:0] loop_idx;\n"

        #Don't waste cycles
        s += "wire [31:0] x_size = x ;\n"
        s += "wire [31:0] y_size = y ;\n"
        s += "wire [31:0] ic_size = (ic < "+str(fd["TI"])+") ?  1 : ic / "+str(fd["TI"]) + ";\n"

        s += "reg L1_done;\n"
        
        s += "assign L1_act_done = loop_idx >= (ic_size*x_size*y_size);\n" 

        s += "always@(posedge clk or negedge rst_n) begin\n\
            if(~rst_n) begin\n\
                loop_idx <= 0;\n\
            end else begin\n\
            if(~L1_done &L1_WRITE_en) begin \n\
            if (reuse) begin\n\
                act_L1_buf_read_addr <= index_table[index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0]] ;\n\
            end else begin\n\
                index_table[index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0]] <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];//act_L1_buf_write_addr;\n\
                act_L1_buf_read_addr <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];\n\
                loop_idx <= loop_idx+1;\n\
                end\n\
            end\n\
          end\n\
        end\n"

        s += "reg cond1, cond2, cond3, cond4;\n"


        #s += "reg [] 
            
        s += "always@(*) begin \n\
                   //wei_L1_buf_read_addr = "+ loop2index(wei_loop_order, fd = fd, pre=pre)+";\n\
                   wei_L1_buf_read_addr = L1_READ_tiled_wei_addr;\n\
                   cond1 <= "+cond_1+";\n\
                   cond2 <= "+cond_2+";\n\
                   cond3 <= "+cond_3+";\n\
                   cond4 <= "+cond_4+";\n\
                   reuse <= cond1 | cond2 | cond3 | cond4;\n\
              end\n"
        #reuse = " + "|".join([cond_1,cond_2,cond_3,cond_4]) + ";\n\

        if(df_d["DATAFLOW"] == "SPARSE_DIRECT"):
            if(df_d["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
                s += "wei_sm_read_en = ~done &1;\n"
                s+="wei_sm_read_addr = " + loop2index(wei_loop_order, fd = fd) + ";\n"
                #(TODOS) buffer for this ?
                #s+='$display("wei_sparse_map_addr = ", wei_sm_read_addr);\n')
            else:#(TODOS, like CSS?)
                pass





        ############################
        #3. DONE LOGIC for this unit
        s += "assign fkx_done =  (fkx < ("+str(df_d["TKX"])+">> TKX_shift) )|(kkx+ ("+str(df_d["TKX"])+">> TKX_shift) >= fkx);\n"
        s += "assign fky_done =  (fky < ("+str(df_d["TKY"])+">> TKY_shift) )|(kky+ (" + str(df_d["TKY"]) + ">> TKY_shift) >= fky);\n"
        s += "assign ic_done = (ic < ("+str(df_d["TI"])+">> TI_shift) )| (iii+ii + ("+str(df_d["TI"])+">> TI_shift)  >= ic  );\n"
        s += "assign nc_done =  (nc < ("+str(df_d["TN"])+">> TN_shift) )| (nnn+nn + ("+str(df_d["TN"])+">> TN_shift)  >= nc  );\n"
        s += "assign b_done =  (bb < ("+str(df_d["TB"])+">> TN_shift) )| (bb + ("+str(df_d["TB"])+">> TB_shift)  >= nc  );\n"
        s += "assign x_done =  (x < ("+str(df_d["TX"])+">> TN_shift) )| (xxx+xx + ("+str(df_d["TX"])+">> TX_shift)  >= x -fkx+1 );\n"
        s += "assign y_done =  (y < ("+str(df_d["TY"])+">> TN_shift) )| (yyy+yy + ("+str(df_d["TY"])+">> TY_shift)  >= y -fky+1 );\n"

        s += "always@(*) begin\n"
        s += "operation_done = (fkx_done) & (fky_done) & (ic_done) & (nc_done) & (x_done) & (y_done) & (b_done);\n"
        s += "end\n"

        '''
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                        wei_done <= 0;\n\
                    end else begin \n\
                      if(wei_done <= 0 )\n\
                        wei_done <= 1;\n\
                    end\n\
                end\n"
        '''

        s += "wire [31:0] ACT_VOL = (x-("+TX+")+1)*(y-("+TY+")+1)*((ic+"+TI+"-1)/"+TI+");\n//(((x+("+TX+")-1)/("+TX+"))*((y+("+TY+")-1)/("+TY+"))*((ic+"+TI+"-1)/"+TI+"));\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                        act_done <= 0;\n\
                    end else begin \n\
                      if(L2_READ_act_addr > ACT_VOL)begin\n\
                        act_done <= 1;\n\
                    end\n\
                    end\n\
                end\n"
        

        s += "always@(posedge clk or negedge rst_n) begin \n\
                if(~rst_n) done <= 0; \n\
                else begin \n\
                    if(operation_done) begin\n\
                        done <= 1; \n\
                    end\n\
                end\n\
              end\n"

        s += "always@(posedge clk or negedge rst_n) begin \n\
                if(~rst_n) L1_done <= 0; \n\
                else begin \n\
                    if(done) begin\n\
                        L1_done <= 1; \n\
                    end\n\
                end\n\
              end\n"

    s += "endmodule"

    f.write(s)
    f.close()
