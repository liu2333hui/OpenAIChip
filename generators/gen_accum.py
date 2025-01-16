import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import GET_PSUM_LOOP_FILTERS
from utils import order_dataflows

from utils import generate_counter_window

import numpy as np
def gen_accum(hardware_config, meta_config, macro_config):
    
    print("\n// GEN_ACCUMULATION VERILOG\n")
    f = open(meta_config["dossier"]+"/accumulator.v", "w")
    
    #Consider use the ACCUM for other functions (pooling, zi_buf and another buf, directly from jia_buf, yi_buf ?)
    s = "module ACCUM(\n\
        input clk,\n\
        input rst_n,\n\
        input accum_en,\n\
            \n\
        input [`MAX_STRIDE_LOG-1:0] stride, \n\
        input [`MAX_KX_LOG-1:0] fkx,\n\
        input [`MAX_KY_LOG-1:0] fky,\n\
        input [`MAX_X_LOG-1:0] x,\n\
        input [`MAX_Y_LOG-1:0] y, \n\
        input [`MAX_N_LOG-1:0] nc, \n\
        input [`MAX_I_LOG-1:0] ic, \n\
        input [`MAX_B_LOG-1:0] batch,\n\
        input [`MAX_PADDING_X_LOG-1:0] padding_x,\n\
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,\n\
            \n\
        input [`PSUM_BUF_DATA - 1:0] zi_buf,\n\
            \n\
        output reg psum_write_en,\n\
        output reg psum_read_en,\n\
        output reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr,\n\
        output reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr,\n\
        output reg [ `PSUM_BUF_DATA  - 1 :0] psum_write_data,\n\
        input [ `PSUM_BUF_DATA - 1 :0] psum_read_data,\n\
            \n\
            input int_inference,\n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
                \n\
            output reg result_done,\n\
                \n\
            output out_buf_write_ready, \n\
            input out_buf_write_valid, \n\
            output reg [`PSUM_BUF_DATA-1:0] out_buf_write_data,\n\
            output reg [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, \n\
                \n\
            output accum_done,\n\
            output reg ACC_stalled \n"
    '''
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
        input [`MAX_B_LOG-1:0] bb\n\
    '''
    s += "); \n\
             \n\
                //LOOP DIFFERENT DATAFLOWS(TODOS) \n"

    s += "wire acc_done;\n"
    s += "assign accum_done = acc_done;\n"
    s += "reg done_done;\n"
    #accum
    s += "reg accum_en_;\n\
        always@(*) begin\n\
            accum_en_ = accum_en;\n\
        end\n"
    
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

    
    CONV2D = order_dataflows(hardware_config)
    print(CONV2D)
    for idx, flows in enumerate(CONV2D):
        fd = hardware_config["TILINGS"]["CONV2D"][flows]
        dataflow = fd["DATAFLOW"]
        df_d = fd

        #DEBUG
        for i in range(fd["TX"]*fd["TY"]*fd["TN"]*fd["TB"]):
            s += "wire [`MAX_ACC_PRECISION_INT-1:0] zi_buf_%d;\n" %(i)
            s += "assign zi_buf_%d = zi_buf[(%d+1)*`MAX_ACC_PRECISION_INT -1 : %d*`MAX_ACC_PRECISION_INT];\n" %(i, i,i)
            s += "wire [`MAX_ACC_PRECISION_INT-1:0] acc_buf_%d;\n" %(i)
            s += "assign acc_buf_%d = psum_read_data[(%d+1)*`MAX_ACC_PRECISION_INT -1 : %d*`MAX_ACC_PRECISION_INT];\n" %(i, i,i)
            s += "wire signed [`MAX_ACC_PRECISION_INT-1:0] write_dat_%d;\n" %(i)
            s += "assign write_dat_%d = psum_write_data[(%d+1)*`MAX_ACC_PRECISION_INT -1 : %d*`MAX_ACC_PRECISION_INT];\n" %(i, i,i)


                
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

        
        if("DIRECT" == dataflow or dataflow == "SPARSE_DIRECT" or dataflow == "WINOGRAD" or dataflow == "SPARSE_DIRECT_LARGE_TILING"):
            SHI_LOOP_PSUM, WULI_LOOP_PSUM = GET_PSUM_LOOP_FILTERS(hardware_config, df_d)

            #s += "if(int_inference) begin\n"
            s += "\n\n"

    
            loop_order = df_d["LOOP"]
            psum_loop_order = []
            for l in loop_order:
                if(l in SHI_LOOP_PSUM):
                    psum_loop_order.append(l)

            print(psum_loop_order)

            '''
            ######################################
            #(TODOS, move to idx_gen.v)
            psum_map = {
                "TXX": "xx",
                "X"  : "xxx",
                "TYY": "yy",
                "Y"  : "yyy",
                "TNN" : "nn",
                "N"  : "nnn",
                "B"  : "bb",

                "KX": "kkx",
                "KY": "kky",

                "TII": "ii",
                "I": "iii",
            }
            psum_map_no_sec = {
                "X"  : "xx",
                "Y"  : "yy",
                "N"  : "nn",

                "I"  : "ii",
            }
            incr_map = {
                "TXX": "TX",
                "TYY": "TY",
                "TNN":"TN",
                "X":"TXX",
                "Y": "TYY",
                "N":"TNN",
                "B": "TB",

                "TII":"TI",                
                "I":"TII",

                "KX":"TKX",
                "KY":"TKY",
            }
            incr_map_no_sec = {
                "X": "TX",
                "Y": "TY",
                "N" : "TN",

                "I": "TI",
            }
            lim_map = {
                "X": "x - fkx + 1",
                "Y": "y - fky + 1",
                "N": "nc",
                "I": "ic",
                "B": "batch",

                "TXX": "xxx+"+str(df_d["TXX"]),
                "TYY": "yyy+"+str(df_d["TYY"]),

    
                "KX": "fkx",
                "KY": "fky",
                
            }
            abs_lim_map = {
                "X": "x - fkx + 1",
                "Y": "y - fky + 1",
                "N": "nc",
                "I": "ic",
                "B": "batch",

                "TXX": "x - fkx + 1",
                "TYY": "y - fky + 1",

                "KX": "fkx",
                "KY": "fky",
            }

            #loop_order,psum_loop_order
            for idx,ll in enumerate(loop_order[::-1]):
                if(idx == 0):
                    trig = "clk"
                else:
                    trig = prev

                
                prev = ll+"_flag"
                
                #(todos with the precision)
                pm = psum_map[ll]
                incr = incr_map[ll]
                if(    (ll == "X" and df_d["TXX"] == -1)  or  (ll == "Y" and df_d["TYY"] == -1) or  (ll == "I" and df_d["TII"] == -1)  or  (ll == "N" and df_d["TNN"] == -1)   ):
                    pm = psum_map_no_sec[ll]
                    incr = incr_map_no_sec[ll]

                incr_val = str(df_d[incr])
                if(incr in ["TX", "TY", "TN","TI","TB","TKX","TKY"]):
                    incr_val += "*"+incr+"_lv"

                s += "//"+str(idx) + ll + "\n"
                s += "\t"*3+"reg [31:0]"+pm+";\n\
                    reg " +ll+"_flag;\n\
                      always@(posedge "+trig+" or negedge rst_n) begin\n\
                          if(~rst_n) begin \n\
                              "+pm+" = 0 ;  \n\
                            " + prev + " = 0 ; \n\
                        end else begin\n\
                        if(accum_en_)begin\n\
                         if(("+pm +"< "+lim_map[ll]+"-"+ incr_val+")|( "+pm+"<"+abs_lim_map[ll]+"-"+ incr_val+")) begin\n\
                             " +  pm + " = " + pm + "+" + incr_val +"; \n\
                            " + prev + " = 0;\n\
                        end else begin \n\
                             " + pm + "  = 0;\n\
                            " + prev + " = 1;\n\
                       end   end  end end\n\n"

        else:
            pass #(TODOS)

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

        s += generate_counter_window(fd=df_d, WINDOW=2, kx_alias = "fkx", ky_alias = "fky")

        
        s += "always@(posedge clk or negedge rst_n) begin\n\
                  if(~rst_n) begin\n\
                        kkx = 0;\n\
                        kky = 0;\n\
                        xx = 0;\n\
                        yy = 0;\n\
                        xxx = 0;\n\
                        yyy = 0;\n\
                        nn = 0;\n\
                        ii = 0;\n\
                        nnn = 0;\n\
                        iii = 0;\n\
                        bb = 0;\n\
                   end else begin\n\
                        if(psum_read_en)begin\n\
                                kkx = kkx_1;\n\
                        kky = kky_1;\n\
                        xx = xx_1;\n\
                        yy = yy_1;\n\
                        nn = nn_1;\n\
                        ii = ii_1;\n\
                        bb = bb_1;\n"
        if("TXX" in df_d["LOOP"]):
            s += "xxx = xxx_1;\n"
        if("TYY" in df_d["LOOP"]):
            s += "yyy = yyy_1;\n"
        if("TNN" in df_d["LOOP"]):
            s += "nnn = nnn_1;\n"
        if("TII" in df_d["LOOP"]):
            s += "iii = iii_1;\n"
            
        s += "          end\n\
                   end\n\
              end\n"
                
            
        #######
        def loop2index(variables, fd=None, multicast=True, pre = "" ):
            if(True):
                #print(REMOVE_DUPLICATE_ROWS)
                mini_carte = {
                    "B": "((bb/"+str(df_d["TB"])+")>> TB_shift)",
                    "N": "nnn/"+str(df_d["TNN"]),
                    "X": "xxx/"+str(df_d["TXX"]),
                    "Y": "yyy/"+str(df_d["TYY"]),
                    "KX": "((kkx/"+str(df_d["TKX"])+")>> TKX_shift)",
                    "KY": "((kky/"+str(df_d["TKY"])+")>> TKY_shift)",
                    "I":  "iii/"+str(df_d["TII"]),
                    "TXX": "((xx/"+str(df_d["TX"])+")>> TX_shift)",
                    "TYY": "((yy/"+str(df_d["TY"])+")>> TY_shift)",
                    "TNN":  "((nn/"+str(df_d["TN"])+")>> TN_shift)",
                    "TII":  "((ii/"+str(df_d["TI"])+")>> TI_shift)",
                }
                mini_carte_no_secondary = {
                    "N": "((nn/"+str(df_d["TN"])+")>> TN_shift)",
                    "I": "((ii/"+str(df_d["TI"])+")>> TI_shift)",
                    "X": "((xx/"+str(df_d["TX"])+")>> TX_shift)",
                    "Y": "((yy/"+str(df_d["TY"])+")>> TY_shift)",
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
                    "TII": "(((ic +"+str(df_d["TI"])+"-1)/"+str(df_d["TI"])+")>> TI_shift)",
                    "TNN": "((nc" + "/"+str(df_d["TN"])+"-1)>> TN_shift)",
                }
                cast_no_secondary = {
                    "X": "((( x-fkx+1 +  " + str(df_d["TX"]) + " -1 )/"+str(df_d["TX"])+") >> TX_shift)", #"(" + LIM_X+" + "+str(df_d["TX"])+"-1)/"+str(df_d["TX"]),
                    "Y":  "((( x-fkx+1 + " + str(df_d["TY"]) + " -1 )/"+str(df_d["TY"])+") >> TY_shift)",#"(" + LIM_Y+" + "+str(df_d["TY"])+"-1)/"+str(df_d["TY"]),
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
                            idx += "*"+v+"+  "+pre+mini_carte_no_secondary[v]+")"
                        else:
                            idx += "*"+cast_no_secondary[v]+"+  "+pre+mini_carte_no_secondary[v]+")"
                    else:
                        if(multicast==False):
                            idx += "*"+v+"+  "+pre+mini_carte[v]+")"
                        else:
                            idx += "*"+cast[v]+"+  "+pre+mini_carte[v]+")"
                            
                idx ="(0"+ idx
                idx = (len(variables) - 1)*"(" +  idx
                print(idx)
                return idx
        s += "wire start; \n\
               reg    start_; \n"
        #s += "reg start_;\n"
        s += "always@(posedge clk) begin\n\
                if(accum_en_)\n\
                start_ <= start;\n\
              end\n"
        

        #Should this be seperated ? i.e.
        #zi_buf[0] + psum_read_data[0] = psum_write_Data[0] ...




        s += "wire done, ic_done, fkx_done, fky_done;\n"
        #GET THE FINAL RESULT FIFO
        #We will double buffer it so no loss in time
        s += "reg [ `PSUM_BUF_ROWS_LOG2 - 1 : 0] psum_res [0:`PSUM_BUF_ROWS -1];\n"
        s += "reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_addr;\n"
        s += "reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_raddr_addr;\n"
        s += "reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_raddr;\n"

        s += "assign start = (ii == 0 & kkx == 0 & kky == 0);\n"
        #unfortunately, code below will kill synthesis
        '''
        s += "always@(posedge clk) begin\n\
              if(accum_en_)begin\n\
                if(done)begin\n\
                    psum_res[psum_res_addr] <= psum_res_addr;\n\
                    psum_res_addr<=psum_res_addr +  1;\n\
                    psum_res_raddr<=psum_res[0];\n\
                    psum_res_raddr_addr<=0;\n\
                end else begin \n\
                    psum_res_addr<=0;\n\
                end\n\
                    \n\
                if(start) begin\n\
                        psum_res_raddr<=psum_res[psum_res_raddr_addr+1];\n\
                        psum_res_raddr_addr<=psum_res_raddr_addr + 1;\n\
                end else begin \n\
                    //psum_res_addr = 0;\n\
                end \n\
              end\n\
            end\n"
        '''



        


        #######################################
        #ADDRESSING
        #PIPELINE
        #
        # zi_buf -> zi_buf_ ->  
        #                     write0 -> write1 -> write0 ->
        #read0 -> read1   ->  read0 -> read1  ->
        #######################################
        
        s += "reg [`MAX_X_LOG-1:0] SUM_xx;\n"
        s += "reg [`MAX_Y_LOG-1:0] SUM_yy;\n"
        s += "reg [`MAX_KX_LOG-1:0] SUM_kkx;\n"
        s += "reg [`MAX_KY_LOG-1:0] SUM_kky;\n"
        s += "reg [`MAX_N_LOG-1:0] SUM_nn;\n"
        s += "reg [`MAX_I_LOG-1:0] SUM_ii;\n"
        s += "reg [`MAX_B_LOG-1:0] SUM_bb;\n"

        s += "reg [ `PSUM_BUF_DATA  - 1 :0] zi_buf_p1;"
        s += "reg [ `PSUM_BUF_DATA  - 1 :0] zi_buf_p2;"

        s += "reg psum_read_en_p1;\n"
        s += "reg psum_read_en_p2;\n"        

        s += "reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr_p1;\n"
        s += "reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr_p2;\n"


        #STALL LOGIC
        #Becuase we have an inherent RAW hazard and WAR hazards

        s += "reg RAW_stall, RAW_STALL2;\n"

        s += "reg result_done_;\n"
        if(True):
            summing = ""
            if(hardware_config["ACCUMULATOR"]["MERGED_REG_ADD"]):          
                summing += "psum_write_data <= (stalled? zi_buf_p2: zi_buf_p1) + psum_read_data; \n"
            else:
                for n in range(int(fd["TN"])):
                    for b in range(int(fd["TB"])):
                        for x in range(int(fd["TX"])):
                            for y in range(int(fd["TY"])):
                                idx = (y +  (int(fd["TY"]))*(x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   0*int(fd["TN"])))))
                                #s += "$display(psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]);\n"
                                #psum.append( "\t,psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]")
                                idx_s = "[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]"
                                summing += "psum_write_data"+idx_s+" <= (stalled? zi_buf_p2"+idx_s+": zi_buf_p1"+idx_s+") + psum_read_data"+idx_s+"; \n"
        s += "always@(posedge clk) begin\n\
                if(~rst_n) begin\n\
                      SUM_xx <= 0;\n\
                      SUM_yy  <= 0;\n\
                      SUM_kkx <= 0;\n\
                      SUM_kky <= 0;\n\
                      SUM_nn  <= 0;\n\
                      SUM_bb  <= 0;\n\
                      SUM_ii  <= 0;\n\
                end else begin \n\
                if(accum_en_ & ~RAW_stall) begin\n\
                      SUM_xx <= xx;\n\
                      SUM_yy  <= yy;\n\
                      SUM_kkx <= kkx;\n\
                      SUM_kky <= kky;\n\
                      SUM_nn  <= nn;\n\
                      SUM_bb  <= bb;\n\
                      SUM_ii  <= ii;\n\
                end\n\
              end\n\
            end\n"

        #########
        # PIPELINE_ADD=0 + DOUBLE_CLOCK=0 
        # read        0  -   0      ...
        # add/write      0      0
        # ->case 2
        # read        0  1  0  ...
        # add/write      0  1
        #########
        if(hardware_config["ACCUMULATOR"]["DOUBLE_CLOCK"] == False and hardware_config["ACCUMULATOR"]["PIPELINED_ADD"] == False):

            s += "always@(*) begin\n\
                        RAW_stall = (psum_read_addr == psum_write_addr) &psum_write_en& ~start;\n\
                  end\n"
            #stalls
            s += "reg accum_en_next;\n"
            s += "always@(posedge clk) begin \n\
                        accum_en_next <= accum_en_;\n\
                  end\n"
            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) begin \n\
                           RAW_STALL2 <= 0; \n\
                    end else begin \n\
                    if(accum_en_next)\n\
                        RAW_STALL2 <= (psum_read_addr == psum_write_addr) & psum_write_en & ~start;\n\
                    end\n\
                  end\n"

            s += "always@(*) begin\n\
                        ACC_stalled <= RAW_stall;\n\
                  end\n"


            #read
            s += "always@(posedge clk) begin\n\
                    psum_read_addr_p1 <= "+loop2index(psum_loop_order)+";\n\
                    psum_read_addr_p2 <= psum_read_addr;\n\
                end\n"

            s += "always@(*) begin\n\
                    psum_read_addr <= "+loop2index(psum_loop_order)+";//read_stalled?  psum_read_addr_p2 : "+loop2index(psum_loop_order)+";\n\
                end\n"
            
            s += "always@(*) begin\n\
                    psum_read_en <= accum_en_ & ~RAW_stall;\n\
                end\n"
                
            s += "always@(posedge clk) begin\n\
                    //if(psum_read_en) begin\n\
                        zi_buf_p1 <= zi_buf;\n\
                        zi_buf_p2 <= zi_buf_p1;\n\
                    //end\n\
                end\n"

            #write
            s += "reg stalled, read_stalled;\n"
            s += "always@(posedge clk) begin\n\
                        stalled <= 0;//RAW_STALL2;\n\
                        read_stalled <= RAW_stall;\n\
                end\n"

            s += "reg start__;\n"
            s += "always@(posedge clk) begin \n\
                    start__ <= start_;\n\
                  end\n"

            
            s += "reg result_done__;\n"
            s += "always@(posedge clk or negedge rst_n) begin \n\
                    if(~rst_n) result_done__ <= 0;\n\
                    else result_done__ <= result_done_;\n\
                  end\n"
            
            s += "always@(*) begin \n\
                if(psum_read_en) begin \n\
                    if( start_ & ~result_done__ ) begin\n\
                    psum_write_data <= stalled? zi_buf_p2: zi_buf_p1; \n\
                end else begin\n\
                       "+summing+" \n\
                end\n\
              end\n\
            end\n"
            
            s += "always@(posedge clk) begin\n\
                    psum_write_en <= psum_read_en;\n\
                  end\n"

            s += "always@(posedge clk) begin\n\
                    psum_write_addr <= psum_read_addr;\n\
                  end\n"

            
            #write
    
        #########
        # PIPELINE_ADD=0 + DOUBLE_CLOCK=1
        # read        0  0      ...
        # add/write      0  0
        # ->case 2
        # read        0  1  0  ...
        # add/write      0  1
        #########
        elif(hardware_config["ACCUMULATOR"]["DOUBLE_CLOCK"] == True and hardware_config["ACCUMULATOR"]["PIPELINED_ADD"] == False):
            pass

        #########
        # PIPELINE_ADD=1 + DOUBLE_CLOCK=1
        # read        0  0      ...
        # add/write      0  0
        # ->case 2
        # read        0  1  0  ...
        # add/write      0  1
        #########
        elif(hardware_config["ACCUMULATOR"]["DOUBLE_CLOCK"] == True and hardware_config["ACCUMULATOR"]["PIPELINED_ADD"] == True):
            pass

        #########
        # PIPELINE_ADD=1 + DOUBLE_CLOCK=0 
        # read        0  0      ...
        # add/write      0  0
        # ->case 2
        # read        0  1  0  ...
        # add/write      0  1
        #########
        elif(hardware_config["ACCUMULATOR"]["DOUBLE_CLOCK"] == False and hardware_config["ACCUMULATOR"]["PIPELINED_ADD"] == True):
            pass
            
        '''
        #READ
        s += "always@(*) begin\n\
                psum_read_addr = "+loop2index(psum_loop_order)+";\n\
            end\n"
        s += "always@(*) begin\n\
                psum_read_en <= accum_en_;\n\
            end\n"     


        s += "always@(posedge clk) begin\n\
                psum_read_addr_p1 <= psum_read_addr;\n\
              end\n"

        s += "always@(posedge clk) begin\n\
                psum_read_en_p1 <= accum_en_;\n\
            end\n"
        
        s += "always@(posedge clk) begin\n\
                zi_buf_p1 <= zi_buf;\n\
                zi_buf_p2 <= zi_buf_p1;\n\
              end\n"
        

        #ADD  (can be pipelined or simple)
        s += "always@(posedge clk) begin\n\
                      SUM_xx <= xx;\n\
                      SUM_yy  <= yy;\n\
                      SUM_kkx <= kkx;\n\
                      SUM_kky <= kky;\n\
                      SUM_nn  <= nn;\n\
                      SUM_bb  <= bb;\n\
                      SUM_ii  <= ii;\n\
              end\n"


        #if(hardware_config["
        s += "always@(posedge clk) begin \n\
                 if(((SUM_ii == 0 & SUM_kkx == 0 & SUM_kky == 0 )) ) begin\n\
                    psum_write_data <= zi_buf_p1; \n\
                end else begin\n"

        if(hardware_config["ACCUMULATOR"]["MERGED_REG_ADD"]):          
            s += "psum_write_data <= zi_buf_p1 + psum_read_data; \n"
        else:
            for n in range(int(fd["TN"])):
                for b in range(int(fd["TB"])):
                    for x in range(int(fd["TX"])):
                        for y in range(int(fd["TY"])):
                            idx = (y +  (int(fd["TY"]))*(x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   0*int(fd["TN"])))))
                            #s += "$display(psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]);\n"
                            #psum.append( "\t,psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]")
                            idx_s = "[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]"
                            s += "psum_write_data"+idx_s+" <= zi_buf_p1"+idx_s+" + psum_read_data"+idx_s+"; \n"
        s += "end\n\
                 end\n"

        s += "always@(posedge clk) begin\n\
                psum_read_addr_p2 <= psum_read_addr_p1;\n\
              end\n"

        s += "always@(posedge clk) begin\n\
                psum_read_en_p2 <= psum_read_en_p1;\n\
            end\n"
        
        #WRITE
        s += "always@(*) begin\n\
                psum_write_en <= psum_read_en_p2;\n\
              end\n"

        s += "always@(*) begin\n\
                psum_write_addr <= psum_read_addr_p2;\n\
              end\n"
        '''
        

            
        
        #DONE LOGIC
        
        
        s += "assign done = ic_done & fkx_done & fky_done & accum_en;\n"
        s += "assign fkx_done =  (fkx < ("+str(df_d["TKX"])+">> TKX_shift) )|(kkx+ ("+str(df_d["TKX"])+">> TKX_shift) >=  fkx);\n"
        s += "assign fky_done =  (fky < ("+str(df_d["TKY"])+">> TKY_shift) )|(kky+ (" + str(df_d["TKY"]) + ">> TKY_shift) >=  fky);\n"
        s += "assign ic_done = (ic < ("+str(df_d["TI"])+">> TI_shift) )| (iii+ii + ("+str(df_d["TI"])+">> TI_shift)  >=  ic  );\n"

        s += "wire nc_done, b_done, x_done, y_done;\n"
        s += "assign nc_done =  (nc < ("+str(df_d["TN"])+">> TN_shift) )| (nnn+nn + ("+str(df_d["TN"])+">> TN_shift)  >= nc  );\n"
        s += "assign b_done =  (bb < ("+str(df_d["TB"])+">> TB_shift) )| (bb + ("+str(df_d["TB"])+">> TB_shift)  >= nc  );\n"
        s += "assign x_done =  (x < ("+str(df_d["TX"])+">> TX_shift) )| (xxx+xx + ("+str(df_d["TX"])+">> TX_shift)  >= x -fkx+1 );\n"
        s += "assign y_done =  (y < ("+str(df_d["TY"])+">> TY_shift) )| (yyy+yy + ("+str(df_d["TY"])+">> TY_shift)  >= y -fky+1 );\n"

        s += "assign acc_done = fkx_done&  fky_done&ic_done&nc_done&b_done&x_done&y_done& accum_en;\n"
        
        #s += "reg result_done;\n"
        
        s += "always@(posedge clk or negedge rst_n) begin\n\
            if(~rst_n) begin \n\
                  result_done_ <= 0;  \n\
            end else begin\n\
                if(acc_done) begin\n\
                   result_done_ <=  acc_done ;   \n\
                end\n\
            end\n\
              end\n"

        
        #donel ogic
        s += "always@(posedge clk) begin\n\
                result_done <= result_done_;//result_done_ & ~start;\n\
            end\n"

        s += "reg first = 0;\n"

        s += "assign out_buf_write_ready = start & first & ~out_buf_write_valid;\n"
        
        s += "always@(posedge clk) begin\n\
                if(start & first) begin\n\
                   out_buf_write_data = psum_read_data; \n\
                   //out_buf_write_ready = 1;\n\
                end\n\
              end\n"

        s += "always@(posedge clk or negedge rst_n) begin\n\
               if(~rst_n) begin\n\
                    out_buf_write_addr = 0;\n\
                end else begin\n\
                if(out_buf_write_valid) begin;\n\
                    out_buf_write_addr = out_buf_write_addr + 1;\n\
                    //out_buf_write_ready = 0;\n\
                end\n\
                end\n\
              end\n"


        


        
        s += "always@(posedge clk)begin\n\
                if(done) begin\n\
                    first = 1;\n\
                end \n\
                end\n"

        s += "always@(posedge clk) begin\n\
                    done_done <= done;\n\
            end\n"

        s += "reg done_done_done;"


        s += "always@(posedge clk) begin\n\
                    done_done_done = done_done;\n\
            end\n"        
        
        #DEBUGGING
        s += "always@(negedge clk) begin\n\
                if(done_done) begin\n\
            $display(\"PSUM_DONE\");\n\
                //, \"t%h\",zi_buf + psum_read_data, \"\t%h\",zi_buf, psum_write_data, \"\t%h\",psum_read_data);  \n\
                    //  ;\n"
        s+= "$display("
        psum=[]
        yin = -1

        #We shall generate some kind of mask, saying which data is actually valid dat, and we send it to the RUBICK unit (转换顺序)
        for n in range(int(fd["TN"])):
            for b in range(int(fd["TB"])):
                for x in range(int(fd["TX"])):
                    for y in range(int(fd["TY"])):
                        #yin += 1
                        idx = (y +  (int(fd["TY"]))*(x    +  (int(fd["TX"]))*(b   +  int(fd["TB"])*(n     +   0*int(fd["TN"])))))
                        #s += "$display(psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]);\n"
                        #psum.append( "\t,psum_write_data[("+str(idx)+"+1)*`MAX_ACC_PRECISION-1:("+str(idx)+")*`MAX_ACC_PRECISION]")
                        psum.append("\"\t%d\", write_dat_"+str(idx))
        s += ','.join(psum)
        s += ");\n"     
                    #$display(psum_write_data); \n\
                    #$writememh(\""+meta_config["dossier"]+"/"+meta_config["tc"]  +'/outputs.txt' + "\",  psum_buf.mem, 0) ;\n\
        s += "\
                end\n\
              end\n\
            "
        
        #s+="end\n"
                    
    s += "\n\
        endmodule\n"

    f.write(s)
    f.close()

    print(s)
if __name__ == "__main__":
    hardware_config = {
        "SUPPORTED_WEI_DTYPES": ["INT4", "INT8","FP8"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_ACT_DTYPES": ["INT4", "INT8","FP8"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants

        #############SPARSITY###############
        "ACT_ZERO_GATING": False,
        "WEI_ZERO_GATING": False,

        ##############PE AND MULTIPLIER TYPE########################
        "MULT_TYPE_INT": "BITFUSION_TXTY_TN",#ADAPTIVE_TI",#"ADAPTIVE_TXTY_TN",#ADAPTIVE_TXTY_TN is like outer product, ADAPTIVE_TI is like inner product
        ##ADAPTIVE_TXTY_TN#BASIC is verilog *, ADAPTIVE/BitFusion, BitSerial is from Stripes work, BitPragmatic is from Pragmatic Work, Bit
        "MULT_TYPE_FP": "BASIC", #BASIC is verilog *, ADAPTIVE (meaning if max precision is 16, want 8 bit, will have double throughput)
        "MULT_TYPE_INT_META": {"MIN_MULT_TYPE": "BASIC", #BASIC, LUT, SHIFT_ACC, only applies to BITFUSION/ADAPTIVE MULT_TYPES
                               "RADIX": 2},#Only apply for shifting multipliers

        #(TODOS) new framework
        # "MULT_TYPE_INT": {"type": "ADAPTIVE", "DIMENSIONS": "TXTY_TN"}
        # "MULT_TYPE_FLOAT": {"type": "BitSerial", "VARIANT": "BITPRAGMATIC"}
        # "MULT_TYPE_INT": {"type": "BASIC"}
        "REMOVE_DUPLICATE_ROWS": False,

        "UNIFIED_ACC_COUNTER": False,#(TODOS), ACC and WEI/ACT COUNTER CAN BE RE-USED
        
        ##############TILING and ALGORITHMIC DATAFLOW###############
        "TILINGS": {
            #Convolution of 2D type
            "CONV2D": {
                "DEFAULT": {
                    #TX and TY should be multiple of WINO_TX and WINO_TY respectively
                    "DATAFLOW": "DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.
                    "TX": 2, "TY": 2,  "TKX": 1, "TKY": 1, "TI": 2, "TN": 1, "TB":1, "WINO_TX":2, "WINO_TY": 2,
                    "TXX": 8, "TYY": -1, "TII": -1, "TNN": -1,
                    "LOOP": ["B",  "I", "X", "Y", "N","TXX", "KX", "KY"],

                    #les limites
                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                     "REMOVE_DUPLICATE_ROWS": True,
                        "WINO_PRE_WEIGHT": False,
                    
                }
            }
         
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
            "WEI_BUFFER": 16*8,#16Bytes

            "WEI_BANKS": 8, #For saving power and energy (TODOS)
            "WEI_BUFFER_ON_MAX_LAYER": True, #True,False
        
            "ACT_BUFFER": 16*1024*8,#4KBytes
            "ACT_BANKS": 8, #For saving power and energy

            "PSUM_BUFFER":16*8, #4KBytes
            "PSUM_BANKS": 8,

            "PSUM_BUFFER_ON_MAX_LAYER": True, #True,False

            ## EITHER:
            ## 1. Give WEI_BUFFER_SIZE, will get rows dynamically
            ## 2. Give WEI_ROWS       , will get buffer size dynamically
            ## 3. Give Largest dimensions of the convolution, will get buffer rows and rows dynamically

            "ALIGNED_L1_DATA": False,
    
            #general constraints
            #CONSTRAINTS FOR MAX SIZE, if is -1, will default to 16
            #和缓存可能有约束性质的冲突(todos)
            "GEN_CONSTRAINTS":{
                "MAX_STRIDE": 5,
                "MAX_KX": 3,
                "MAX_KY": 3,
                "MAX_X": 64,
                "MAX_Y": 64,
                "MAX_N": 2,
                "MAX_I": 2,
                "MAX_B": 1,
                "MAX_PADDING_X": 1,
                "MAX_PADDING_Y": 1,
                #GROUPS? DILATION?
            },
        
            #DDR (in bits), BURST IS THE NUMBER FETCHED IN A ROW WITHOUT STALLING,so BURST+1 CYCLES FOR BURST OF DATA
            "DDR_WIDTH": 128,
            "DDR_MAX_BURST": 4,
    }


    meta_config = {
        "dossier": "../MyAccelerator",
        "tc": "tc1",
    }

    from Generate_Verilog import gen_macro_file
    MACRO_CFG = gen_macro_file(hardware_config, meta_config)
    gen_accum(hardware_config, meta_config, MACRO_CFG)
