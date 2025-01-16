import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import GET_PSUM_LOOP_FILTERS
from utils import order_dataflows

from utils import generate_counter_window

import numpy as np


def loop2index(variables, fd=None, multicast=True, pre = "" , post=""):
    df_d = fd
    if True:
        if(True):
            if (True):
                mini_carte = {
                    "B": "(("+pre+"bb"+post+"/"+str(df_d["TB"])+")>> TB_shift)",
                    "N": ""+pre+"nnn"+post+"/"+str(df_d["TNN"]),
                    "X": ""+pre+"xxx"+post+"/"+str(df_d["TXX"]),
                    "Y": ""+pre+"yyy"+post+"/"+str(df_d["TYY"]),
                    "KX": "(("+pre+"kkx"+post+"/"+str(df_d["TKX"])+")>> TKX_shift)",
                    "KY": "(("+pre+"kky"+post+"/"+str(df_d["TKY"])+")>> TKY_shift)",
                    "I":  ""+pre+"iii"+post+"/"+str(df_d["TII"]),
                    "TXX": "(("+pre+"xx"+post+"/"+str(df_d["TX"])+")>> TX_shift)",
                    "TYY": "(("+pre+"yy"+post+"/"+str(df_d["TY"])+")>> TY_shift)",
                    "TNN":  "(("+pre+"nn"+post+"/"+str(df_d["TN"])+")>> TN_shift)",
                    "TII":  "(("+pre+"ii"+post+"/"+str(df_d["TI"])+")>> TI_shift)",
                }
                mini_carte_no_secondary = {
                    "N": "(("+pre+"nn"+post+"/"+str(df_d["TN"])+")>> TN_shift)",
                    "I": "(("+pre+"ii"+post+"/"+str(df_d["TI"])+")>> TI_shift)",
                    "X": "(("+pre+"xx"+post+"/"+str(df_d["TX"])+")>> TX_shift)",
                    "Y": "(("+pre+"yy"+post+"/"+str(df_d["TY"])+")>> TY_shift)",
                }

                
                cast = {
                    "B": "((batch/"+str(df_d["TB"])+")>> TB_shift)",
                    "N" : "(nc+"+str(df_d["TNN"])+"-1)/"+str(df_d["TNN"]),
                    "X": "(x-fkx+1 +"+str(df_d["TXX"])+"-1)/"+str(df_d["TXX"]),
                    "Y": "(y-fky+1 + "+str(df_d["TYY"])+"-1)/"+str(df_d["TYY"]),
                    "KX": "(((fkx+"+str(df_d["TKX"])+"-1)/"+str(df_d["TKX"])+")>> TKX_shift)",
                    "KY": "(((fky+"+str(df_d["TKY"])+"-1)/"+str(df_d["TKY"])+")>> TKY_shift)",
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
            input  [`WEI_BUF_DATA*"+str(hardware_config["WEI_L2_L1_BW_RATIO"]) + "-1 :0] wei_L2_buf_read_data, \n\
                \n\
            output reg act_L2_buf_read_ready, \n\
            input  act_L2_buf_read_valid, \n\
            output reg [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_L2_buf_read_addr, \n\
            input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, \n\
                \n\
            output reg act_L1_buf_write_en,\n\
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_write_addr, \n\
            output  [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, \n\
                \n\
            output  reg wei_L1_buf_write_en,\n\
            output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr, \n\
            output  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, \n\
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
        input pe_array_start,\n\
        input pe_array_ready,\n\
        input pe_array_last,\n\
            \n\
        input ACC_stalled,\n\
            \n\
        output [5:0] jia_sys_jie, \n\
        output [5:0] yi_sys_jie, \n\
            \n\
        output reg ACCUM_stall,\n\
            \n\
        input inter_pe_sparse_stall\n\
        );\n"


    s += "reg wei_done, act_done;\n"

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

        #PIPELINE
        # weights
        # addr_cnt_en ---> L2 READ -> read_valid -> L1 WRITE -> L1 READ WEI
        # activations
        # addr_cnt_en ---> L2 READ -> read_valid -> L1 WRITE -> L1 ACT ADDR -> L1 READ ACT



        ###########################
        # COUNTER FEATURE 1 - energy save if there are continuous reads
        ###########################

        
        #####ADD FEATURE TO REDUCE SOME ENERGY
        # IF THE READ IS THE SAME , DONT NEED TO ENABLE
        if("COUNTER" in hardware_config):
            if(hardware_config["COUNTER"].get("WEI_L1_GATE_SAME_READ", False)):
                s += "reg [31:0] wei_L1_prev_addr;\n"
                s += "always@(posedge clk or negedge rst_n) begin\n\
                        if (~rst_n) wei_L1_prev_addr <= 1;\n\
                        else begin if(wei_initial_L1_read& ~L1_READ_wei_stall) begin\n\
                            wei_L1_prev_addr <= wei_L1_buf_read_addr_pre;\n\
                        end end\n\
                    end\n"
            
            if(hardware_config["COUNTER"].get("ACT_L1_GATE_SAME_READ", False)):
                s += "reg [31:0] act_L1_prev_addr;\n"
                s += "always@(posedge clk or negedge rst_n) begin\n\
                        if (~rst_n) wei_L1_prev_addr <= 1;\n\
                        else begin if(wei_initial_L1_read& ~L1_READ_act_stall) begin\n\
                            act_L1_prev_addr <= act_L1_buf_read_addr;\n\
                        end\n\
                        end\n\
                    end\n"

        s += "wire wei_L1_yi_addr;\n"
        s += "wire act_L1_yi_addr;\n"

        if("COUNTER" in hardware_config):
            if(hardware_config["COUNTER"].get("WEI_L1_GATE_SAME_READ", False)):
                s += "assign wei_L1_yi_addr = ~(wei_L1_prev_addr == wei_L1_buf_read_addr_pre);\n"
            else:
                s += "assign wei_L1_yi_addr = 1;\n"

            if(hardware_config["COUNTER"].get("ACT_L1_GATE_SAME_READ", False)):
                s += "assign act_L1_buf_read_en = ~(act_L1_prev_addr == act_L1_buf_read_addr);\n"
            else:
                s += "assign act_L1_yi_addr = 1;\n"
                
        else:
            s += "assign wei_L1_yi_addr = 1;\n"
            s += "assign act_L1_yi_addr = 1;\n"
                            


        ##############################################################################
        from utils import SYSTOLIC_WEIGHT_LOAD_CYCLES, SYSTOLIC_ACT_LOAD_CYCLES, SYSTOLIC_WEI_LOOP_ORDER

        WEI_SYS_CYCLES = SYSTOLIC_WEIGHT_LOAD_CYCLES(hardware_config, df_d)


        s += "reg [" + str(int(np.log2(WEI_SYS_CYCLES))+1) + ":0] systolic_wei_load;\n"

        s += "reg [" + str(int(np.log2(WEI_SYS_CYCLES))+1) + ":0] systolic_wei_load_nxt;\n"
        
        #Weighth Systolic logic
        if(WEI_SYS_CYCLES > 1):

            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                        systolic_wei_load <= 0;\n\
                    end else begin \n\
                        if(wei_initial_L2_read & ~L2_READ_wei_stall) begin \n\
                            systolic_wei_load <= systolic_wei_load + 1;\n\
                        end else begin\n\
                            if(systolic_wei_load > 0) begin \n\
                                if(systolic_wei_load + 1 == " + str(WEI_SYS_CYCLES) + ")begin\n\
                                    systolic_wei_load <= 0;\n\
                                end else begin \n\
                                    systolic_wei_load <= systolic_wei_load + 1;\n\
                                end\n\
                            end\n\
                        end \n\
                    end\n\
                  end\n"

            
        else:
            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) systolic_wei_load <= 0;\n\
                    else systolic_wei_load <= 0;\n\
                end\n"

        s += "always@(posedge clk or negedge rst_n) begin \n\
                    if (~rst_n) systolic_wei_load_nxt <= 0;\n\
                    else systolic_wei_load_nxt <= systolic_wei_load;\n\
              end\n"
        

        

        ##############################################################################
        
        ##############################################################################
        #   WEIGHT
        ##############################################################################
        #######INITIAL LOGIC
        s += "reg initial_mac = 0;\n"
        s += "reg wei_initial_L1_read = 0;\n"
        s += "reg wei_initial_L1_write = 0;\n"
        s += "reg wei_initial_L2_read = 0;\n"
        
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) wei_initial_L2_read <= 0;\n\
                else begin\n\
                    if(wei_initial_L2_read == 0) wei_initial_L2_read <= addr_cnt_en;\n\
                end\n\
            end\n"

        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) wei_initial_L1_write <= 0;\n\
                else begin\n\
                    if(wei_initial_L1_write == 0) wei_initial_L1_write <= wei_L2_buf_read_valid;\n\
                end\n\
            end\n"

        # asssume write 1 cycle, read next cycle
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) wei_initial_L1_read <= 0;\n\
                else begin\n\
                    if(wei_initial_L1_read == 0) wei_initial_L1_read <= wei_initial_L1_write;\n\
                end\n\
            end\n"

        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    initial_mac <= 0;\n\
                end else begin\n\
                    if(initial_mac == 0) begin\n\
                        initial_mac <= wei_initial_L1_read;\n\
                    end\n\
                    end\n\
              end\n"


        #counter for L2 -> L1 when the bandwidth don't match
        s += "wire [5:0] L2_L1_wei_jie;\n"
            
        s += "reg [" + str(int(np.log2(WEI_SYS_CYCLES))+1) + ":0] wei_jie;\n"
        
        ######STALLING
        s += "reg L2_READ_wei_stall, L1_WRITE_wei_stall, L1_READ_wei_stall, MAC_stall;\n"

        #(TODOS) there are more stalls we can add
        s += "reg stall_from_mac;\n\
              always@(*) begin\n\
                  stall_from_mac =    initial_mac& (inter_pe_sparse_stall | ~pe_array_last)  & ~accum_done;\n\
                  L2_READ_wei_stall = (stall_from_mac | L2_L1_wei_jie > 0 | systolic_wei_load > 0 ) & ~accum_done ;\n\
                  L1_WRITE_wei_stall = (stall_from_mac | systolic_wei_load_nxt > 0)& ~accum_done;\n\
                  L1_READ_wei_stall = stall_from_mac & ~accum_done;\n\
                  MAC_stall       = (systolic_wei_load_nxt > 0 | wei_jie > 0);\n\
              end\n"

        s += "always@(posedge clk) begin\n\
                ACCUM_stall <= ~mac_en;\n\
              end\n"
        #ACC_stalled& ~accum_done & 

        #######WEIGHT ENABLES
        #NEED L2 READ STOP LOGIC （WEI_DONE, ACT_DONE)

        s += "reg wei_L1_buf_read_en_pre;\n"

        s += "reg wei_L1_buf_read_en_val;\n"

        s += "always@(*) begin\n\
                wei_L2_buf_read_ready = wei_initial_L2_read & (~L2_READ_wei_stall | systolic_wei_load > 0 | systolic_wei_load_nxt>0) & ~wei_done;\n\
                wei_L1_buf_write_en   = wei_initial_L1_write& (~L1_WRITE_wei_stall| systolic_wei_load_nxt>0) & ~wei_done;\n\
                    \n\
                wei_L1_buf_read_en_pre    = wei_L1_yi_addr& wei_initial_L1_read& ~L1_READ_wei_stall;\n\
                wei_L1_buf_read_en        = wei_L1_buf_read_en_val;\n\
                mac_en = initial_mac & ~MAC_stall ;\n\
            end\n"
        

        ######ADDRESSING
        #(TODOS) change for sparsity

        #This addressing is only used by the reading side, we don't need to pipeline this !
        s += "reg L2_READ_act_stall, L1_WRITE_act_stall, L1_READ_act_stall;\n"
                
        s += generate_counter_window(fd=df_d, WINDOW=2, kx_alias = "fkx", ky_alias = "fky")
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
                        if(wei_initial_L1_write& ~L1_WRITE_act_stall)begin\n\
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


        #WEIGHT ADDRESS

        s += "reg [31:0] wei_L2_buf_tiled_addr;\n"
        s += "reg [31:0] wei_L1_buf_read_tiled_addr;\n"
        s += "reg [31:0] wei_L1_buf_write_tiled_addr;\n"

        #
        s += "always@(*) begin\n\
                wei_L2_buf_tiled_addr ="+loop2index(wei_loop_order, fd = fd, pre="")+";\n\
              end\n"

        #addr - wei_L2
        s += "reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_read_addr_pre;\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin \n\
                    wei_L2_buf_read_addr_pre <= 0;\n\
                    wei_L1_buf_write_tiled_addr <= 0;\n\
                end else begin\n\
                    if(wei_initial_L2_read & ~L2_READ_wei_stall) begin\n\
                      wei_L2_buf_read_addr_pre <= wei_L2_buf_read_addr_pre + 1;\n\
                      wei_L1_buf_write_tiled_addr <= wei_L2_buf_tiled_addr;\n\
                    end\n\
                end\n\
              end\n"

        


        s += "always@(*) begin\n\
                wei_L2_buf_read_addr = (systolic_wei_load > 0) ? (wei_L2_buf_read_addr_pre-1)*"+str(WEI_SYS_CYCLES)+" + systolic_wei_load : wei_L2_buf_read_addr_pre*"+str(WEI_SYS_CYCLES)+";\n\
              end\n"
        

        

        #addr - wei_L1_write
        
        s += "reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr_pre;\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    wei_L1_buf_write_addr_pre <= 0;\n\
                    wei_L1_buf_read_tiled_addr <= 0;\n\
                end else begin\n\
                    if(wei_initial_L1_write& ~L1_WRITE_wei_stall) begin\n\
                        wei_L1_buf_read_tiled_addr <= wei_L1_buf_write_tiled_addr;\n\
                        wei_L1_buf_write_addr_pre <= wei_L1_buf_write_addr_pre + 1;\n\
                    end\n\
                end\n\
              end\n"


        s += "always@(*) begin\n\
                    //wei_L1_buf_write_addr = wei_L1_buf_write_addr_pre*"+str(WEI_SYS_CYCLES)+" + systolic_wei_load_nxt;\n\
                    wei_L1_buf_write_addr = (systolic_wei_load_nxt > 0) ? (wei_L1_buf_write_addr_pre-1)*"+str(WEI_SYS_CYCLES)+" + systolic_wei_load_nxt : \
                                        wei_L1_buf_write_addr_pre*"+str(WEI_SYS_CYCLES)+";\n\
              end\n"

        s += "reg [31:0] wei_L1_buf_read_addr_pre;\n"
        s += "reg [31:0] wei_L1_buf_read_addr_val;\n"
        
        #addr - wei_L1_read

        s += "always@(posedge clk) begin\n\
                if(~rst_n) wei_L1_buf_read_addr_pre <= 0;\n\
                else begin\n\
                    if(wei_L1_buf_read_en) wei_L1_buf_read_addr_pre <= "+loop2index(wei_loop_order, fd = fd, pre="", post="")+";\n\
                end\n\
              end\n"


        s += "always@(*) begin\n\
                //wei_L1_buf_read_addr_pre <= "+loop2index(wei_loop_order, fd = fd, pre="", post="")+";//wei_L1_buf_read_tiled_addr;\n\
                wei_L1_buf_read_addr <= wei_L1_buf_read_addr_val ;\n\
              end\n"

        #data - weight data
        #(SYSTOLIC from L2 to L1 TODOS)
        '''
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    L2_L1_wei_jie <= 0; \n\
                end else begin \n\
                        if(L2_L1_wei_jie == 0 & wei_L2_buf_read_valid) begin \n\
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % "+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"; \n\
                        end else if(wei_L1_buf_write_en) begin \n\
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % "+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"; \n\
                        end \n\
                end \n\
              end\n"



        s += "always@(posedge clk) begin\n"
        for idx, jie in enumerate(range(hardware_config["WEI_L2_L1_BW_RATIO"]-1, -1, -1)):
            s += "if(L2_L1_wei_jie == " + str(idx) + " & ( wei_L1_buf_write_en | wei_L2_buf_read_valid ) ) begin\n\
                      wei_L1_buf_write_data <= wei_L2_buf_read_data[`WEI_BUF_DATA*"+str(jie+1)+"-1:`WEI_BUF_DATA*"+str(jie)+"];\n\
                  end\n"
        s += "end\n"

        '''


        ##############################################################
        #  SYSTOLIC FEATURE WEIGHT
        #  1. Systolic Loading
        ##############################################################

        #We systolic load

        # READ_ADDRESS
        # 0              1               2
        # 0*3 + 0 1 2    1*3 + 0 1 2     2*3 + 0 1 2

        s += "reg stall_from_wei_sys_load;\n"


        if(WEI_SYS_CYCLES > 1):


            s += "reg [31:0] wei_jie_addr;\n"


            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                        wei_jie <= 0;\n\
                    end else begin \n\
                        if(wei_L1_buf_read_en_pre) begin \n\
                            wei_jie <= wei_jie + 1;\n\
                        end else begin\n\
                            if(wei_jie > 0) begin \n\
                                if(wei_jie + 1 == " + str(WEI_SYS_CYCLES) + ")begin\n\
                                    wei_jie <= 0;\n\
                                end else begin \n\
                                    wei_jie <= wei_jie + 1;\n\
                                end\n\
                            end\n\
                        end \n\
                    end\n\
                  end\n"

            s += "always@(*) begin\n\
                  wei_L1_buf_read_en_val = wei_L1_buf_read_en_pre | wei_jie >= 1;\n\
                  wei_L1_buf_read_addr_val = wei_L1_buf_read_addr_pre * "+str(WEI_SYS_CYCLES) +" + wei_jie ;\n\
              end\n"
        else:
            s += "always@(*) begin\n\
                stall_from_wei_sys_load = 0;\n\
                wei_L1_buf_read_en_val = wei_L1_buf_read_en_pre;\n\
                wei_L1_buf_read_addr_val = wei_L1_buf_read_addr_pre;\n\
                wei_jie = 0;\n\
                end\n"
            
        s += "assign jia_sys_jie = wei_jie;\n"
            
        ##############################################################
        #  SYSTOLIC FEATURE
        #  2. Systolic casting .. 
        ##############################################################




        ##############################################################################
        #   ACTIVATION
        ##############################################################################

        inter_x = df_d.get("SYSTOLIC",{}).get("ACT_X_INTER", "NONE")
        inter_y = df_d.get("SYSTOLIC",{}).get("ACT_Y_INTER", "NONE")
        ######STALLING

        
        #(TODOS) there are more stalls we can add
        s += "always@(*) begin\n\
                  L2_READ_act_stall = stall_from_mac;\n\
                  L1_WRITE_act_stall = stall_from_mac;\n\
                  L1_READ_act_stall = stall_from_mac;\n\
              end\n"
        
        ######ACT_ENABLES (TODOS)
        s += "always@(*) begin\n\
                act_L2_buf_read_ready = wei_initial_L2_read  & ~L2_READ_act_stall & ~act_done;\n\
                act_L1_buf_write_en   = wei_initial_L1_write & ~L1_WRITE_act_stall & ~act_done ;\n\
                act_L1_buf_read_en    = act_L1_yi_addr&  wei_initial_L1_read  & ~L1_READ_act_stall   ;\n\
            end\n"        

        #s += "always@(posedge clk

        #ACT ADDRESS


        s += "reg [`MAX_X_LOG-1:0] ACT_L1_WRITE_xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] ACT_L1_WRITE_yy;\n"
        s += "reg [`MAX_KX_LOG-1:0] ACT_L1_WRITE_kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0] ACT_L1_WRITE_kky;\n"
        s += "reg [`MAX_N_LOG-1:0] ACT_L1_WRITE_nn;\n"
        s += "reg [`MAX_I_LOG-1:0] ACT_L1_WRITE_ii;\n"
        s += "reg [`MAX_B_LOG-1:0] ACT_L1_WRITE_bb;\n"
        
        
        s += "reg [`MAX_X_LOG-1:0] ACT_L1_READ_xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] ACT_L1_READ_yy;\n"
        s += "reg [`MAX_KX_LOG-1:0] ACT_L1_READ_kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0] ACT_L1_READ_kky;\n"
        s += "reg [`MAX_N_LOG-1:0] ACT_L1_READ_nn;\n"
        s += "reg [`MAX_I_LOG-1:0] ACT_L1_READ_ii;\n"
        s += "reg [`MAX_B_LOG-1:0] ACT_L1_READ_bb;\n"

        
        #addr - act_L2
        if(inter_x == "L2" and inter_y == "L2"):
            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                        act_L2_buf_read_addr <= 0;\n\
                    end else begin\n\
                        if(wei_initial_L2_read & ~L2_READ_act_stall) begin\n\
                          act_L2_buf_read_addr <= act_L2_buf_read_addr + 1;\n\
                          ACT_L1_WRITE_xx <= xx;\n\
                          ACT_L1_WRITE_yy  <= yy;\n\
                          ACT_L1_WRITE_kkx <= kkx;\n\
                          ACT_L1_WRITE_kky <= kky;\n\
                          ACT_L1_WRITE_nn  <= nn;\n\
                          ACT_L1_WRITE_bb  <= bb;\n\
                          ACT_L1_WRITE_ii  <= ii;\n\
                        end\n\
                    end\n\
                  end\n"
        else:
            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                        act_L2_buf_read_addr <= 0;\n\
                    end else begin\n\
                        if(wei_initial_L2_read & ~L2_READ_act_stall) begin\n\
                          act_L2_buf_read_addr <= act_L2_buf_read_addr + 1;\n\
                          ACT_L1_WRITE_xx <= xx;\n\
                          ACT_L1_WRITE_yy  <= yy;\n\
                          ACT_L1_WRITE_kkx <= kkx;\n\
                          ACT_L1_WRITE_kky <= kky;\n\
                          ACT_L1_WRITE_nn  <= nn;\n\
                          ACT_L1_WRITE_bb  <= bb;\n\
                          ACT_L1_WRITE_ii  <= ii;\n\
                        end\n\
                    end\n\
                  end\n"            
        
        
        #addr - act_L1_write
        s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    act_L1_buf_write_addr <= 0;\n\
                end else begin\n\
                    if(wei_initial_L1_write& ~L1_WRITE_act_stall) begin\n\
                        act_L1_buf_write_addr <= act_L1_buf_write_addr + 1;\n\
                          ACT_L1_READ_xx <= ACT_L1_WRITE_xx;\n\
                          ACT_L1_READ_yy  <= ACT_L1_WRITE_yy;\n\
                          ACT_L1_READ_kkx <= ACT_L1_WRITE_kkx;\n\
                          ACT_L1_READ_kky <= ACT_L1_WRITE_kky;\n\
                          ACT_L1_READ_nn  <= ACT_L1_WRITE_nn;\n\
                    end\n\
                end\n\
              end\n"


        #addr - act_L1_read_addr

        # solution 1. act_L1_read_addr = virt_buf[act_tile], virt_buf[act_tile]++


        if(inter_x == "NONE" and inter_y == "NONE" or inter_x == "L2" and inter_y == "L2"):
        
            s += "wire [31:0] index_table_addr;\n"
            s += "reg [31:0] loop_idx;\n"
            s += "reg cond1, cond2, cond3, cond4;\n"
            INDEX_ROWS = 1024 #TODOS
            INDEX_ROWS_LOG = int(np.log2(INDEX_ROWS))
            #s += "reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] index_table [0:"+str(INDEX_ROWS)+"];\n"
            s += "reg reuse;\n"


            pre = ""
            post = ""
            if("TXX" in fd["LOOP"]):
                x_idx="("+pre+"kkx"+post+"+"+pre+"xx"+post+"+"+pre+"xxx"+post+")"
            else:
                x_idx="("+pre+"kkx"+post+"+"+pre+"xx"+post+")"

            if("TYY" in fd["LOOP"]):
                y_idx="("+pre+"kky"+post+"+"+pre+"yy"+post+"+"+pre+"yyy"+post+")"
            else:
                y_idx="("+pre+"kky"+post+"+"+pre+"yy"+post+")"

            if("TII" in fd["LOOP"]):
                i_idx="("+pre+"ii"+post+"+"+pre+"iii"+post+")"
            else:
                i_idx="("+pre+"ii"+post+")"

            s += "assign index_table_addr  = ("+pre+"bb"+post+")*ic*(x)*(y) + "+i_idx+"*(y)*(x)+"+x_idx+"*(y) + "+y_idx+";\n"
            
            pre = ""

            LIM_X = "((x + padding_x*2 - fkx + 1) / stride  )"
            LIM_Y = "((y + padding_y*2 - fky + 1) / stride  )"
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
            
            if(Y_FKY):#TODOS
                cond_1 = "("+pre+"xx"+post+" == 0 & "+pre+"yy"+post+" > 0 & fky >= "+TY+"  & "+pre+"kky"+post+" < fky - "+TY+")"
                cond_1_tou = "("+pre+"xx"+post+" == 0 & "+pre+"yy"+post+" > 0)"
                cond_1_wei = "(fky >= "+TY+"  & "+pre+"kky"+post+" < fky - "+TY+")"
            else:
                if("TYY" in df_d["LOOP"]):
                    cond_1_tou = "1"
                    cond_1_wei =  "( (("+pre+"kky"+post+" >= "+TY+") | ("+pre+"yyy"+post+" > 0)) & ("+pre+"yy"+post+" < " + TYY +"-"+ TY + ")   &  ("+pre+"yyy"+post+" + "+pre+"yy"+post+" +"+TY+"<= "+LIM_Y+" ))"
                else:
                    cond_1_tou = "1"
                    cond_1_wei =  "( ("+pre+"kky"+post+" >= "+TY+")   &  ("+pre+"yy"+post+" +"+TY+"< "+LIM_Y+" ))"

            if(X_FKX):
                if("TXX" in df_d["LOOP"]):#TODOS
                    cond_2_tou = "("+pre+"xx"+post+" > 0 & "+pre+"yy"+post+" == 0)"
                    cond_2_wei = "(fkx >= "+TX+" &("+pre+"kkx"+post+" < fkx - "+TX+"))"
                else: 
                    cond_2_tou = "("+pre+"xx"+post+" > 0 & "+pre+"yy"+post+" == 0)"
                    cond_2_wei = "(fkx >= "+TX+" &("+pre+"kkx"+post+" < fkx - "+TX+"))"
            else:
                if("TXX" in df_d["LOOP"]):
                    cond_2_tou = "1"
                    cond_2_wei =  "( (("+pre+"kkx"+post+" >= "+TX+") | ("+pre+"xxx"+post+" > 0)) & ("+pre+"xx"+post+" < " + TXX +"-"+ TX + ")   &  ("+pre+"xxx"+post+" + "+pre+"xx"+post+" +"+TX+"<= "+LIM_X+" ))"
                else:
                    cond_2_tou = "1"
                    cond_2_wei =  "( ("+pre+"kkx"+post+" >= "+TX+")   &  ("+pre+"xx"+post+" +"+TX+"< "+LIM_X+" ))"
                    
            cond_1 = cond_1_tou+"&"+cond_1_wei       
            cond_2 = cond_2_tou+"&"+cond_2_wei
            if(Y_FKY and X_FKX):
                cond_3_tou = "("+pre+"xx"+post+" > 0 & "+pre+"yy"+post+" > 0)"
            elif(Y_FKY and not X_FKX):
                cond_3_tou = "("+pre+"yy"+post+" > 0)"
            elif(not Y_FKY and X_FKX):
                cond_3_tou = "("+pre+"xx"+post+" > 0)"
            else:
                cond_3_tou = ""
            cond_3 = "("+cond_3_tou + "& (("+cond_2_wei+") | ("+cond_1_wei+"))   )"            
            cond_4 = ""+pre+"nn"+post+">0"
            s += "always@(*) begin \n\
                       cond1 <= "+cond_1+";\n\
                       cond2 <= "+cond_2+";\n\
                       cond3 <= "+cond_3+";\n\
                       cond4 <= "+cond_4+";\n\
                       reuse <= cond1 | cond2 | cond3 | cond4;\n\
                  end\n"            

            #MODULE INDEX TABLE
            s += "wire index_table_read_en;\n"
            s += "wire index_table_write_en;\n"

            s += "assign index_table_read_en = wei_initial_L1_write & ~L1_WRITE_act_stall & reuse ;\n"
            s += "assign index_table_write_en = wei_initial_L1_write & ~L1_WRITE_act_stall & ~reuse ;\n" 

            s += "reg [31:0] index_table_read_data;\n"

            s += "ADDR_TABLE addr_table (\n\
                .clk(clk),\n\
                .index_table_read_data(index_table_read_data),\n\
                .index_table_write_data(loop_idx),\n\
                .index_table_read_en(index_table_read_en),\n\
                .index_table_write_en(index_table_write_en),\n\
                .index_table_read_addr(index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0]),\n\
                .index_table_write_addr(index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0])\n\
    );\n"
            s += "reg reuse_save;\n"


            s += "always@(*) begin\n\
                    act_L1_buf_read_addr = reuse_save?index_table_read_data: loop_idx-1;\n\
                   end\n"

            '''
            #addr - act_L1_read
            s += "always@(posedge clk or negedge rst_n) begin\n\
              if(~rst_n) begin\n\
                    loop_idx <= 0;\n\
                    act_L1_buf_read_addr <= 0;\n\
              end else begin\n\
                if(wei_initial_L1_write& ~L1_WRITE_act_stall) begin \n\
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
            '''


            #addr - act_L1_read
            s += "always@(posedge clk or negedge rst_n) begin\n\
              if(~rst_n) begin\n\
                    loop_idx <= 0;\n\
                    reuse_save <= 0;\n\
              end else begin\n\
                if(wei_initial_L1_write& ~L1_WRITE_act_stall) begin \n\
                    if (reuse) begin\n\
                        reuse_save<=1;\n\
                        //act_L1_buf_read_addr <= index_table[index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0]] ;\n\
                    end else begin\n\
                        reuse_save<=0;\n\
                        //index_table[index_table_addr["+str(INDEX_ROWS_LOG)+"-1:0]] <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];//act_L1_buf_write_addr;\n\
                        //act_L1_buf_read_addr <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];\n\
                        loop_idx <= loop_idx+1;\n\
                    end\n\
                end\n\
              end\n\
            end\n"        


 
        #Solution 3. XY INTER_PE
        elif(inter_x == "L1" and inter_y == "L1"):
            pass
            #-->有可能有些tile需要多个周期的获取
        #Solution 4. inter_x == "L1", inter_y == "NONE"(....)
    
        else:
            print("not implm other IMG2COL or inter_pe methods")
            exit(0)
            

        
        #data - act data
        #(SYSTOLIC from L2 to L1 TODOS)
        #s += "always@(posedge clk) begin\n\
        #        act_L1_buf_write_data <= act_L2_buf_read_data;\n\
        #      end\n"
        


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

        TX = str(df_d["TX"]) + ">> TX_shift"
        TY = str(df_d["TY"]) + ">> TY_shift"
        TXX = str(df_d["TXX"])
        TYY = str(df_d["TYY"]) 
        TI = str(df_d["TI"]) 
        TN = str(df_d["TN"])
        TKX = str(df_d["TKX"]) 
        TKY = str(df_d["TKY"])        

             

        s += "wire [31:0] X_VOL = ("+TX+")<=fkx ?  x : ((x+("+TX+")-1)/("+TX+"))*fkx;\n"
        s += "wire [31:0] Y_VOL = ("+TY+")<=fky ?  y : ((y+("+TY+")-1)/("+TY+"))*fky;\n"
        
        s += "wire [31:0] ACT_VOL =X_VOL*Y_VOL*((ic+"+TI+"-1)/"+TI+"); //(x)*(y)*((ic+"+TI+"-1)/"+TI+");\n//(((x+("+TX+")-1)/("+TX+"))*((y+("+TY+")-1)/("+TY+"))*((ic+"+TI+"-1)/"+TI+"));\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                        act_done <= 0;\n\
                    end else begin \n\
                      if(act_L2_buf_read_addr > ACT_VOL)begin\n\
                        act_done <= 1;\n\
                    end\n\
                    end\n\
                end\n"

        s += "wire [31:0] WEI_VOL = ((fkx+"+TKX+"-1)/"+TKX+")*((fky+"+TKY+"-1)/"+TKY+")*((ic+"+TI+"-1)/"+TI+")*((nc+"+TN+"-1)/"+TN+");;\n"
        s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin\n\
                        wei_done <= 0;\n\
                    end else begin \n\
                      if(wei_L2_buf_read_addr_pre > WEI_VOL)begin\n\
                        wei_done <= 1;\n\
                    end\n\
                    end\n\
                end\n"
        
        '''
        #    input  wei_L2_buf_read_valid, \n\
        output reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_read_addr, \n\
        input  [`WEI_BUF_DATA -1 :0] wei_L2_buf_read_data, \n\
                \n\
        output  reg wei_L1_buf_write_en,\n\
        output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr, \n\
        output reg  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, \n\

        output reg  wei_L1_buf_read_en,\n\
        output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_read_addr, \n\

                
        output reg act_L2_buf_read_ready, \n\
        input  act_L2_buf_read_valid, \n\
        output reg [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_L2_buf_read_addr, \n\
        input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, \n\
                \n\
        output reg act_L1_buf_write_en,\n\
        output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_write_addr, \n\
        output reg [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, \n\
                \n\
                \n\
            output reg act_L1_buf_read_en,\n\
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_read_addr, \n\
                \n\
                \n\
            output reg mac_en,\n\
       '''

        s += "L2_interconnect_L1 L2lianjieL1(\n\
             .clk(clk),\n\
             .rst_n(rst_n),\n\
            .act_L1_buf_write_data(act_L1_buf_write_data), \n\
                 .wei_L1_buf_write_data(wei_L1_buf_write_data), \n\
                .act_L2_buf_read_data(act_L2_buf_read_data), \n\
             .wei_L2_buf_read_data(wei_L2_buf_read_data) ,\n\
                 \n\
            .L2_L1_wei_jie(L2_L1_wei_jie),\n\
            .wei_L2_buf_read_valid(wei_L2_buf_read_valid),\n\
            .wei_L1_buf_write_en(wei_L1_buf_write_en)\n\
	);\n"
        
    s += "endmodule\n"




    #ADDR_CNT --> ADDR_CNT + L2_INTERCONNECT_L1 + ACT_VIRTUAL_BUFFER
    #split address buffer
    #and interconnect (L2 -> L1 out)
    s += "module L2_interconnect_L1(\n\
             input clk,\n\
              input rst_n,\n\
            output reg [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, \n\
                 output reg  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, \n\
                input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, \n\
             input  [`WEI_BUF_DATA*"+str(hardware_config["WEI_L2_L1_BW_RATIO"])+" -1 :0] wei_L2_buf_read_data, \n\
                 \n\
            output reg [5:0] L2_L1_wei_jie,\n\
            input wei_L2_buf_read_valid,\n\
            input wei_L1_buf_write_en\n\
	);\n\
             always@(posedge clk) begin\n\
                act_L1_buf_write_data <= act_L2_buf_read_data;\n\
              end\n\n\
 		\n\
        //always@(posedge clk) begin\n\
         //       wei_L1_buf_write_data <= wei_L2_buf_read_data;\n\
         //     end\n\
	\n"
    s += "always@(posedge clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    L2_L1_wei_jie <= 0; \n\
                end else begin \n\
                        if(L2_L1_wei_jie == 0 & wei_L2_buf_read_valid) begin \n\
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % "+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"; \n\
                        end else if(wei_L1_buf_write_en) begin \n\
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % "+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"; \n\
                        end \n\
                end \n\
              end\n"



    s += "always@(posedge clk) begin\n"
    for idx, jie in enumerate(range(hardware_config["WEI_L2_L1_BW_RATIO"]-1, -1, -1)):
        s += "if(L2_L1_wei_jie == " + str(idx) + " & ( wei_L1_buf_write_en | wei_L2_buf_read_valid ) ) begin\n\
                      wei_L1_buf_write_data <= wei_L2_buf_read_data[`WEI_BUF_DATA*"+str(jie+1)+"-1:`WEI_BUF_DATA*"+str(jie)+"];\n\
                  end\n"
    s += "end\n"
    s += "endmodule\n"


    s += "module ADDR_TABLE(\n\
            input clk,\n\
            output reg [31:0] index_table_read_data,\n\
            input [31:0] index_table_write_data,\n\
            input  index_table_read_en,\n\
            input index_table_write_en,\n\
            input ["+str(INDEX_ROWS_LOG)+"-1:0] index_table_read_addr,\n\
	    input ["+str(INDEX_ROWS_LOG)+"-1:0] index_table_write_addr\n\
);\n\
    reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] index_table [0:"+str(INDEX_ROWS)+"];\n\
                always@(posedge clk) begin\n\
                    if(index_table_read_en)\n\
                        index_table_read_data = index_table[index_table_read_addr]  ;\n\
                end\n\
                 \n\
                always@(posedge clk) begin\n\
                    if(index_table_write_en)\n\
                        index_table[index_table_write_addr] = index_table_write_data ;\n\
                end\n\
            endmodule\n"
    
    f.write(s)
    f.close()
