
from Generate_DDR_Xin import trouve_df, get_dataflow_meta, get_prec, GET_LOOP_FILTERS

from Generate_Verilog import gen_hardware, gen_macro_file#(hardware_config, meta_config)
    
import numpy as np
    
from Generate_DDR_Xin import gen_buf


def gen_tb_L2_1_level(hardware_config, runtime_config, meta_config, macro_config):
    
    f = open(meta_config["dossier"]+"/"+meta_config["tc"] + "/L2_1_tb.v", "w")
    s = ""
    

    s += "module L2_level_tb();\n"


    #L2 ADDRESS ROWS IS ACTUALLY MORE ! (TODOS)
    #ACT_L2_BUF_ROWS_LOG2 (L2)
    #ACT_BUF_ROWS_LOG2 (L1)

    s += "\n\
            reg ddr_clk;\n\
            reg core_clk;\n\
            reg rst_n;\n\
                \n\
            wire wei_buf_read_ready; \n\
            reg  wei_buf_read_valid; \n\
            reg [`WEI_BUF_DATA*"+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"-1:0] wei_buf_read_data;\n\
            wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr; \n\
                \n\
            wire act_buf_read_ready; \n\
            reg  act_buf_read_valid; \n\
            reg [`ACT_BUF_DATA - 1:0] act_buf_read_data;\n\
            wire [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr; \n\
                \n\
            reg [`MAX_PADDING_X_LOG-1:0] padding_x;\n\
            reg [`MAX_PADDING_Y_LOG-1:0] padding_y;\n\
            reg [`MAX_STRIDE_LOG-1:0] stride;\n\
            reg [`MAX_KX_LOG-1:0] fkx;\n\
            reg [`MAX_KY_LOG-1:0] fky;\n\
            reg  [`MAX_X_LOG-1:0] x;\n\
            reg  [`MAX_Y_LOG-1:0] y;\n\
            reg  [`MAX_N_LOG-1:0] nc;\n\
            reg  [`MAX_I_LOG-1:0] ic;\n\
            reg  [`MAX_B_LOG-1:0] batch;\n\
                \n\
            reg int_inference;\n\
            reg [5:0] wei_precision;\n\
            reg [5:0] act_precision;\n\
            reg [5:0] wei_mantissa;\n\
            reg [5:0] act_mantissa;\n\
            reg [5:0] wei_exponent;\n\
            reg [5:0] act_exponent;\n\
            reg [5:0] wei_regime;\n\
            reg [5:0] act_regime;\n\
                \n\
            wire  out_buf_write_ready; \n\
            reg out_buf_write_valid;\n\
            wire [`PSUM_BUF_DATA-1:0] out_buf_write_data;\n\
            wire [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr; \n"

    s += "reg addr_cnt_en;\n"
    s += "wire operation_done;\n"

    #L2 buffer "simulation"
    #(TODOS) sizing both ways, L2_ROWS, L2_ROWS_LOG2
    s += "reg [`WEI_BUF_DATA*"+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"  - 1: 0] L2_WEI [0:`L2_WEI_BUF_ROWS];\n"
    s += "reg [`ACT_BUF_DATA*"+str(hardware_config["ACT_L2_L1_BW_RATIO"])+"  - 1: 0] L2_ACT [0:`L2_ACT_BUF_ROWS];\n"

    s += "wire [`WEI_BUF_DATA  - 1: 0] wei0;\n"
    s += "assign wei0 = L2_WEI[0];\n"
    s += "wire [`WEI_BUF_DATA  - 1: 0] wei1;\n"
    s += "assign wei1 = L2_WEI[1];\n"

    s += "wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_addr;\n"
    s += "assign wei_L2_buf_addr = wei_buf_read_addr;\n"
    
    #L2 logic
    s += "always@(negedge core_clk) begin \n\
               if(wei_buf_read_ready)begin\n\
                    wei_buf_read_data <=  L2_WEI[wei_L2_buf_addr]; \n\
                    wei_buf_read_valid <= #(0) 1;\n\
               end \n\
               else begin\n\
                    wei_buf_read_valid <= 0;\n\
               end\n\
          end\n"
    
    s += "always@(negedge core_clk) begin \n\
               if(act_buf_read_ready)begin\n\
                    act_buf_read_data <= #(0) L2_ACT[act_buf_read_addr]; \n\
                    act_buf_read_valid = #(0) 1;\n\
               end \n\
               else begin\n\
                    act_buf_read_valid = 0;\n\
               end\n\
          end\n"


    s += "wire [`WEI_BUF_DATA-1:0] jia_buf;\n"
    s += "wire [`ACT_BUF_DATA-1:0] yi_buf;\n"

    s += "wire wei_L1_write_en;\n"
    s += "wire wei_L1_read_en;\n"
    s += "wire [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_read_addr;\n"
    s += "wire  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_L1_write_addr;\n"
    s += "wire [`WEI_BUF_DATA  - 1 :0] wei_L1_write_data;\n"

    s += "wire act_L1_write_en;\n"
    s += "wire act_L1_read_en;\n"
    s += "wire [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_read_addr;\n"
    s += "wire  [`ACT_BUF_ROWS_LOG2  - 1 :0] act_L1_write_addr;\n"
    s += "wire [`ACT_BUF_DATA  - 1 :0] act_L1_write_data;\n"


    s += "wire psum_write_en;\n"
    s += "wire psum_read_en;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;\n"
    s += "wire [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;\n"
    s += "wire [ `PSUM_BUF_DATA - 1 :0] psum_read_data;\n"
    


    s += "WEI_BUF wei_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(core_clk),\n\
            .read_en(wei_L1_read_en),\n\
            .read_addr(wei_L1_read_addr),\n\
            .read_data(jia_buf),\n\
            .write_en(wei_L1_write_en),\n\
            .write_addr(wei_L1_write_addr),\n\
            .write_data(wei_L1_write_data)\n\
        );\n"

    s += "ACT_BUF act_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(core_clk),\n\
            .read_en(act_L1_read_en),\n\
            .read_addr(act_L1_read_addr),\n\
            .read_data(yi_buf),\n\
            .write_en(act_L1_write_en),\n\
            .write_addr(act_L1_write_addr),\n\
            .write_data(act_L1_write_data)\n\
        );\n"


    if(hardware_config["ACCUMULATOR"]["DOUBLE_CLOCK"]):
        s += "PSUM_BUF psum_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(~core_clk),\n\
            .write_clk(core_clk),\n\
            .read_en(psum_read_en),\n\
            .read_addr(psum_read_addr),\n\
            .read_data(psum_read_data),\n\
            .write_en(psum_write_en),\n\
            .write_addr(psum_write_addr),\n\
            .write_data(psum_write_data)\n);\n"
    else:
        s += "PSUM_BUF psum_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(~core_clk),\n\
            .write_clk(~core_clk),\n\
            .read_en(psum_read_en),\n\
            .read_addr(psum_read_addr),\n\
            .read_data(psum_read_data),\n\
            .write_en(psum_write_en),\n\
            .write_addr(psum_write_addr),\n\
            .write_data(psum_write_data)\n);\n"

    #############################################
    # SPARSE MAP (TODOS)
    #############################################
    
    #Sparsity Modules
    WEI_SM_EN = False
    ACT_SM_EN = False
    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        s += "reg wei_sm_write_en;\n"
        s += "reg wei_sm_read_en;\n"
        s += "reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_read_addr;\n"
        s += "reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_write_addr;\n"
        s += "reg [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_write_data;\n"
        
        s += "wire [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_read_data;\n"


        s += "WEI_SPARSITY_MAP_BUF wei_sm_buf(\n\
                    .rst_n(rst_n),\n\
                    .read_clk(core_clk),\n\
                    .write_clk(ddr_clk),\n\
                    .read_en(wei_sm_read_en),\n\
                    .read_addr(wei_sm_read_addr),\n\
                    .read_data(wei_sm_read_data),\n\
                    .write_en(wei_sm_write_en),\n\
                    .write_addr(wei_sm_write_addr),\n\
                    .write_data(wei_sm_write_data)\n\
                );\n"
        WEI_SM_EN = True

    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] >0):
        s += "wire [ `ACT_SPARSITY_MAP_BUF_DATA - 1:0] act_sm_read_data;\n"
        s += "reg act_sm_write_en;\n"
        s += "reg act_sm_read_en;\n"
        s += "reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_read_addr;\n"
        s += "reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_write_addr;\n"
        s += "reg [ `ACT_SPARSITY_MAP_BUF_DATA  - 1 :0] act_sm_write_data;\n"

        s += "ACT_SPARSITY_MAP_BUF act_sm_buf(\n\
                    .rst_n(rst_n),\n\
                    .read_clk(core_clk),\n\
                    .write_clk(ddr_clk),\n\
                    .read_en(act_sm_read_en),\n\
                    .read_addr(act_sm_read_addr),\n\
                    .read_data(act_sm_read_data),\n\
                    .write_en(act_sm_write_en),\n\
                    .write_addr(act_sm_write_addr),\n\
                    .write_data(act_sm_write_data)\n\
                );\n"
        ACT_SM_EN = True


    #operation_done <== counter
    #result_done <== ACCUMUALTOR DONE
    #DLA Core With L1 registers
    s += "DLA_CORE dla_core( \n\
            .ddr_clk(ddr_clk),\n\
            .core_clk(core_clk),\n\
            .rst_n(rst_n),\n\
                \n\
            .addr_cnt_en(addr_cnt_en),\n\
            .result_done(operation_done),\n\
                \n\
            .wei_buf_read_ready(wei_buf_read_ready), \n\
            .  wei_buf_read_valid(wei_buf_read_valid), \n\
            . wei_buf_read_data(wei_buf_read_data),\n\
            .wei_buf_read_addr(wei_buf_read_addr), \n\
                \n\
            . act_buf_read_ready(act_buf_read_ready), \n\
            .  act_buf_read_valid(act_buf_read_valid), \n\
            .act_buf_read_data(act_buf_read_data),\n\
            .act_buf_read_addr(act_buf_read_addr), \n\
                \n\
            .padding_x(padding_x),\n\
            .padding_y(padding_y),\n\
            .stride(stride),\n\
            .fkx(fkx),\n\
            .fky(fky),\n\
            .x(x),\n\
            .y(y),\n\
            .nc(nc),\n\
            .ic(ic),\n\
            .batch(batch),\n\
                \n\
            .int_inference(int_inference),\n\
            .wei_precision(wei_precision),\n\
            .act_precision(act_precision),\n\
            .wei_mantissa(wei_mantissa),\n\
            .act_mantissa(act_mantissa),\n\
            .wei_exponent(wei_exponent),\n\
            .act_exponent(act_exponent),\n\
            .wei_regime(wei_regime),\n\
            .act_regime(act_regime),\n\
                \n\
            .out_buf_write_ready(out_buf_write_ready), \n\
            .out_buf_write_valid(out_buf_write_valid), \n\
            .out_buf_write_data(out_buf_write_data),\n\
            .out_buf_write_addr(out_buf_write_addr) ,\n"

    if(WEI_SM_EN):
        s += ".wei_sm_write_en(wei_sm_write_en),\n"
        s += ".wei_sm_read_en(wei_sm_read_en),\n"
        s += ".wei_sm_read_addr(wei_sm_read_addr),\n"
        s += ".wei_sm_write_addr(wei_sm_write_addr),\n"
        s += ".wei_sm_write_data(wei_sm_write_data),\n"
            
        s += ".wei_sm_read_data(wei_sm_read_data),\n"
    if(ACT_SM_EN):
        s += ".act_sm_read_data(act_sm_read_data),\n"
        s += ".act_sm_write_en(act_sm_write_en),\n"
        s += ".act_sm_read_en(act_sm_read_en),\n"
        s += ".act_sm_read_addr(act_sm_read_addr),\n"
        s += ".act_sm_write_addr(act_sm_write_addr),\n"
        s += ".act_sm_write_data(act_sm_write_data),\n"
            
    s += ".jia_buf(jia_buf),\n\
            .wei_L1_read_en(wei_L1_read_en),\n\
            .wei_L1_read_addr(wei_L1_read_addr),\n\
            .wei_L1_write_en(wei_L1_write_en),\n\
            .wei_L1_write_addr(wei_L1_write_addr),\n\
            .wei_L1_write_data(wei_L1_write_data),\n\
            .act_L1_read_en(act_L1_read_en),\n\
            .act_L1_read_addr(act_L1_read_addr),\n\
            .yi_buf(yi_buf),\n\
            .act_L1_write_en(act_L1_write_en),\n\
            .act_L1_write_addr(act_L1_write_addr),\n\
            .act_L1_write_data(act_L1_write_data),\n\
            .psum_read_en(psum_read_en),\n\
            .psum_read_addr(psum_read_addr),\n\
            .psum_read_data(psum_read_data),\n\
            .psum_write_en(psum_write_en),\n\
            .psum_write_addr(psum_write_addr),\n\
            .psum_write_data(psum_write_data)\n"

        
    s+=");\n"


    
    
    ##############################################
    # 1. Load Weights/Acts into L2
    # 2. Clock, VCD, Reset
    # 3. enable the module to start and Wait until all complete
    ##############################################

    

    ###################################
    ##1. READ WEIGHTS/ACTS/SPARSE_MAPS
    ###################################
    #假设数据已经从DMA拷贝过来了
    #wei_buf.buf.memh("./dossier"+"/tc/weight.txt")
    s += "initial begin\n"
    s += '$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights.txt", L2_WEI);\n'
    s += '$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation.txt", L2_ACT);\n'
    #f.write('$readmemh("weights.txt", wei_buf.mem);\n')
    #f.write('$readmemh("activation.txt", act_buf.mem);\n')

    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        s += '$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights_sparse_map.txt", wei_sm_buf.mem);\n'
        
    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] > 0):        
        s += '$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation_sparse_map.txt", act_sm_buf.mem);\n'
    
    s += "end\n"
    #act_buf.buf.memh("./dossier"+"/tc/act.txt")
    #psum_buf dont need memh



    ############################
    # 2 Shizhong, VCD
    ############################
    s += "`define CORE_CLK " + str(runtime_config['CORE_CLK'])+"\n"
    s += "`define DDR_CLK " + str(runtime_config['DDR_CLK'])+"\n"
    
    s += "initial begin\n\
    core_clk = 1'b1;\n\
    forever begin\n\
        #(`CORE_CLK/2); core_clk = ~core_clk;\n\
    end\n\
    end\n"

    s +=  "initial begin\n\
    ddr_clk = 1'b1;\n\
    forever begin\n\
    #(`DDR_CLK/2); ddr_clk = ~ddr_clk;\n\
    end\n\
    end\n"

    s += "initial begin\n"
    #f.write("initial begin\n")


    #FSDB
    


    #0.
    s += '$dumpfile("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/l2_tc.vcd");\n'
    s += '$dumpvars(0, L2_level_tb);\n'
    
    s += 'end;\n'

    ############################
    # 3 Runtime
    ############################    

    wei_prec, act_prec, psum_prec, floating = get_prec(runtime_config)
    from utils import mult_cycles
    
    #mult_cycles(hardware_config)
    MC = mult_cycles(hardware_config,wei_prec,act_prec)
    
    max_cycles = runtime_config['Operation_Params']['KX']*runtime_config['Operation_Params']['KY']*runtime_config['Operation_Params']['X']*runtime_config['Operation_Params']['Y']\
                         *runtime_config['Operation_Params']['I']*runtime_config['Operation_Params']['N']*runtime_config['Operation_Params']['B'] * MC
    if(floating):
        int_inference = "0"
    else:
        int_inference = "1"
        
    #TIME_OUT
    s += "initial begin\n\
                #(`CORE_CLK*"+str(max_cycles)+");\n\
                $finish;\n\
          end\n"


    #RUNTIME
    delay = 0
    
    s += "initial begin\n\
        rst_n = 0;\n\
        addr_cnt_en = 0;\n\
            \n\
        #(`CORE_CLK*2);\n\
        rst_n = 1;\n\
            \n\
            \n\
        #(`CORE_CLK*"+str(delay)+");\n\
            \n\
        wei_precision = "+str(wei_prec) + ";\n\
        act_precision = "+str(act_prec) + ";\n\
        int_inference = "+str(int_inference) + ";\n\
            \n\
        stride = "+str(runtime_config['Operation_Params']['STRIDE']) +";\n\
        fkx = " + str(runtime_config['Operation_Params']['KX']) +";\n\
        fky = " + str(runtime_config['Operation_Params']['KY']) +";\n\
        x = " + str(runtime_config['Operation_Params']['X']) +";\n\
        y = " + str(runtime_config['Operation_Params']['Y']) +";\n\
        ic = " + str(runtime_config['Operation_Params']['I']) +";\n\
        nc = " + str(runtime_config['Operation_Params']['N']) +";\n\
        batch = " + str(runtime_config['Operation_Params']['B']) +";\n\
        padding_x = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n\
        padding_y = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n\
            \n\
        addr_cnt_en = 1;\n\
            \n\
        @(posedge operation_done)\n\
        #(2*`CORE_CLK);\n\
        $finish;\n\
          end\n"
    s += "endmodule"
    

    f.write(s)

    f.close()





def gen_tb_L2_level(hardware_config, runtime_config, meta_config, macro_config):
    
    f = open(meta_config["dossier"]+"/"+meta_config["tc"] + "/L2_tb.v", "w")
    s = ""
    

    s += "module L2_level_tb();\n"


    #L2 ADDRESS ROWS IS ACTUALLY MORE ! (TODOS)
    #ACT_L2_BUF_ROWS_LOG2 (L2)
    #ACT_BUF_ROWS_LOG2 (L1)

    s += "\n\
            reg ddr_clk;\n\
            reg core_clk;\n\
            reg rst_n;\n\
                \n\
            wire wei_buf_read_ready; \n\
            reg  wei_buf_read_valid; \n\
            reg [`WEI_BUF_DATA-1:0] wei_buf_read_data;\n\
            wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr; \n\
                \n\
            wire act_buf_read_ready; \n\
            reg  act_buf_read_valid; \n\
            reg [`ACT_BUF_DATA - 1:0] act_buf_read_data;\n\
            wire [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr; \n\
                \n\
            reg [`MAX_PADDING_X_LOG-1:0] padding_x;\n\
            reg [`MAX_PADDING_Y_LOG-1:0] padding_y;\n\
            reg [`MAX_STRIDE_LOG-1:0] stride;\n\
            reg [`MAX_KX_LOG-1:0] fkx;\n\
            reg [`MAX_KY_LOG-1:0] fky;\n\
            reg  [`MAX_X_LOG-1:0] x;\n\
            reg  [`MAX_Y_LOG-1:0] y;\n\
            reg  [`MAX_N_LOG-1:0] nc;\n\
            reg  [`MAX_I_LOG-1:0] ic;\n\
            reg  [`MAX_B_LOG-1:0] batch;\n\
                \n\
            reg int_inference;\n\
            reg [5:0] wei_precision;\n\
            reg [5:0] act_precision;\n\
            reg [5:0] wei_mantissa;\n\
            reg [5:0] act_mantissa;\n\
            reg [5:0] wei_exponent;\n\
            reg [5:0] act_exponent;\n\
            reg [5:0] wei_regime;\n\
            reg [5:0] act_regime;\n\
                \n\
            wire  out_buf_write_ready; \n\
            reg out_buf_write_valid;\n\
            wire [`PSUM_BUF_DATA-1:0] out_buf_write_data;\n\
            wire [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr; \n"

    s += "reg addr_cnt_en;\n"
    s += "wire operation_done;\n"

    #L2 buffer "simulation"
    #(TODOS) sizing both ways, L2_ROWS, L2_ROWS_LOG2
    s += "reg [`WEI_BUF_DATA*  - 1: 0] L2_WEI [0:`L2_WEI_BUF_ROWS];\n"
    s += "reg [`ACT_BUF_DATA  - 1: 0] L2_ACT [0:`L2_ACT_BUF_ROWS];\n"

    s += "wire [`WEI_BUF_DATA  - 1: 0] wei0;\n"
    s += "assign wei0 = L2_WEI[0];\n"
    s += "wire [`WEI_BUF_DATA  - 1: 0] wei1;\n"
    s += "assign wei1 = L2_WEI[1];\n"

    s += "wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_addr;\n"
    s += "assign wei_L2_buf_addr = wei_buf_read_addr;\n"
    
    #L2 logic
    s += "always@(negedge core_clk) begin \n\
               if(wei_buf_read_ready)begin\n\
                    wei_buf_read_data <=  L2_WEI[wei_L2_buf_addr]; \n\
                    wei_buf_read_valid <= #(0) 1;\n\
               end \n\
               else begin\n\
                    wei_buf_read_valid <= 0;\n\
               end\n\
          end\n"
    
    s += "always@(negedge core_clk) begin \n\
               if(act_buf_read_ready)begin\n\
                    act_buf_read_data <= #(0) L2_ACT[act_buf_read_addr]; \n\
                    act_buf_read_valid = #(0) 1;\n\
               end \n\
               else begin\n\
                    act_buf_read_valid = 0;\n\
               end\n\
          end\n"


    #operation_done <== counter
    #result_done <== ACCUMUALTOR DONE
    #DLA Core With L1 registers
    s += "DLA_CORE dla_core( \n\
            .ddr_clk(ddr_clk),\n\
            .core_clk(core_clk),\n\
            .rst_n(rst_n),\n\
                \n\
            .addr_cnt_en(addr_cnt_en),\n\
            .result_done(operation_done),\n\
                \n\
            .wei_buf_read_ready(wei_buf_read_ready), \n\
            .  wei_buf_read_valid(wei_buf_read_valid), \n\
            . wei_buf_read_data(wei_buf_read_data),\n\
            .wei_buf_read_addr(wei_buf_read_addr), \n\
                \n\
            . act_buf_read_ready(act_buf_read_ready), \n\
            .  act_buf_read_valid(act_buf_read_valid), \n\
            .act_buf_read_data(act_buf_read_data),\n\
            .act_buf_read_addr(act_buf_read_addr), \n\
                \n\
            .padding_x(padding_x),\n\
            .padding_y(padding_y),\n\
            .stride(stride),\n\
            .fkx(fkx),\n\
            .fky(fky),\n\
            .x(x),\n\
            .y(y),\n\
            .nc(nc),\n\
            .ic(ic),\n\
            .batch(batch),\n\
                \n\
            .int_inference(int_inference),\n\
            .wei_precision(wei_precision),\n\
            .act_precision(act_precision),\n\
            .wei_mantissa(wei_mantissa),\n\
            .act_mantissa(act_mantissa),\n\
            .wei_exponent(wei_exponent),\n\
            .act_exponent(act_exponent),\n\
            .wei_regime(wei_regime),\n\
            .act_regime(act_regime),\n\
                \n\
            .out_buf_write_ready(out_buf_write_ready), \n\
            .out_buf_write_valid(out_buf_write_valid), \n\
            .out_buf_write_data(out_buf_write_data),\n\
            .out_buf_write_addr(out_buf_write_addr) \n\
        );\n"


    ##############################################
    # 1. Load Weights/Acts into L2
    # 2. Clock, VCD, Reset
    # 3. enable the module to start and Wait until all complete
    ##############################################

    

    ###################################
    ##1. READ WEIGHTS/ACTS/SPARSE_MAPS
    ###################################
    #假设数据已经从DMA拷贝过来了
    #wei_buf.buf.memh("./dossier"+"/tc/weight.txt")
    s += "initial begin\n"
    s += '$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights.txt", L2_WEI);\n'
    s += '$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation.txt", L2_ACT);\n'
    #f.write('$readmemh("weights.txt", wei_buf.mem);\n')
    #f.write('$readmemh("activation.txt", act_buf.mem);\n')

    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        s += '$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights_sparse_map.txt", wei_sm_buf.mem);\n'
        
    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] > 0):        
        s += '$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation_sparse_map.txt", act_sm_buf.mem);\n'
    
    s += "end\n"
    #act_buf.buf.memh("./dossier"+"/tc/act.txt")
    #psum_buf dont need memh



    ############################
    # 2 Shizhong, VCD
    ############################
    s += "`define CORE_CLK " + str(runtime_config['CORE_CLK'])+"\n"
    s += "`define DDR_CLK " + str(runtime_config['DDR_CLK'])+"\n"
    
    s += "initial begin\n\
    core_clk = 1'b1;\n\
    forever begin\n\
        #(`CORE_CLK/2); core_clk = ~core_clk;\n\
    end\n\
    end\n"

    s +=  "initial begin\n\
    ddr_clk = 1'b1;\n\
    forever begin\n\
    #(`DDR_CLK/2); ddr_clk = ~ddr_clk;\n\
    end\n\
    end\n"

    s += "initial begin\n"
    #f.write("initial begin\n")

    #0.
    s += '$dumpfile("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/l2_tc.vcd");\n'
    s += '$dumpvars(0, L2_level_tb);\n'
    
    s += 'end;\n'

    ############################
    # 3 Runtime
    ############################    

    wei_prec, act_prec, psum_prec, floating = get_prec(runtime_config)
    max_cycles = runtime_config['Operation_Params']['KX']*runtime_config['Operation_Params']['KY']*runtime_config['Operation_Params']['X']*runtime_config['Operation_Params']['Y']\
                         *runtime_config['Operation_Params']['I']*runtime_config['Operation_Params']['N']*runtime_config['Operation_Params']['B']
    if(floating):
        int_inference = "0"
    else:
        int_inference = "1"
        
    #TIME_OUT
    s += "initial begin\n\
                #(`CORE_CLK*"+str(max_cycles)+");\n\
                $finish;\n\
          end\n"


    #RUNTIME
    delay = 0
    
    s += "initial begin\n\
        rst_n = 0;\n\
        addr_cnt_en = 0;\n\
            \n\
        #(`CORE_CLK*2);\n\
        rst_n = 1;\n\
            \n\
            \n\
        #(`CORE_CLK*"+str(delay)+");\n\
            \n\
        wei_precision = "+str(wei_prec) + ";\n\
        act_precision = "+str(act_prec) + ";\n\
        int_inference = "+str(int_inference) + ";\n\
            \n\
        stride = "+str(runtime_config['Operation_Params']['STRIDE']) +";\n\
        fkx = " + str(runtime_config['Operation_Params']['KX']) +";\n\
        fky = " + str(runtime_config['Operation_Params']['KY']) +";\n\
        x = " + str(runtime_config['Operation_Params']['X']) +";\n\
        y = " + str(runtime_config['Operation_Params']['Y']) +";\n\
        ic = " + str(runtime_config['Operation_Params']['I']) +";\n\
        nc = " + str(runtime_config['Operation_Params']['N']) +";\n\
        batch = " + str(runtime_config['Operation_Params']['B']) +";\n\
        padding_x = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n\
        padding_y = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n\
            \n\
        addr_cnt_en = 1;\n\
            \n\
        @(negedge operation_done)\n\
        #(1*`CORE_CLK);\n\
        $finish;\n\
          end\n"
    s += "endmodule"
    

    f.write(s)

    f.close()

    
    
###################################################################################################################
def gen_tb_L1_level(hardware_config, runtime_config, meta_config):
    
    f = open(meta_config["dossier"]+"/"+meta_config["tc"] + "/L1_tb.v", "w")


    f.write("module L1_level_tb();\n")

    ############################
    # 1. Signals + XiaoMokuai
    ############################

    #1.0 普遍
    f.write("reg ddr_clk;\n")
    f.write("reg core_clk;\n")
    f.write("reg rst_n;\n")

    #carte-tou
    f.write("wire [`WEI_BUF_DATA-1:0] jia_buf;\n")
    f.write("wire [`ACT_BUF_DATA-1:0] yi_buf;\n")
    f.write("wire [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi;\n")

    #carte-wei
    f.write("wire [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;\n")
    f.write("wire [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;\n")
    f.write("wire [`PSUM_BUF_DATA - 1:0] zi_buf;\n")#todos
    f.write("reg [`PSUM_BUF_DATA - 1:0] psum_zi_buf;\n")#todos


    #padding

    f.write("reg [3:0] padding;\n")
    f.write("reg [`MAX_STRIDE_LOG-1:0] stride;\n")
    f.write("reg [`MAX_KX_LOG-1:0] fkx;\n")
    f.write("reg [`MAX_KY_LOG-1:0] fky;\n")
    f.write("reg [`MAX_X_LOG-1:0] x;\n")
    f.write("reg [`MAX_Y_LOG-1:0] y;\n")
    f.write("reg [`MAX_N_LOG-1:0] nc;\n")
    f.write("reg [`MAX_I_LOG-1:0] ic;\n")
    f.write("reg [`MAX_B_LOG-1:0] batch;\n")

    f.write("reg [15:0] loop_idx;\n")
    f.write("reg [15:0] cha_y;\n")
    f.write("reg [15:0] cha_x;\n")

    f.write("reg [`MAX_PADDING_X_LOG-1:0] padding_x;\n")
    f.write("reg [`MAX_PADDING_Y_LOG-1:0] padding_y;\n")
    f.write("reg [3:0] OP_TYPE;\n")
    f.write("reg [3:0] SYSTOLIC_OP;\n")

    f.write("reg int_inference;\n")
    f.write("reg [`REQUIRED_PES-1:0] pe_en;\n")
    f.write("reg [5:0] wei_precision;\n")
    f.write("reg [5:0] act_precision;\n")
    f.write("reg [5:0] wei_mantissa;\n")
    f.write("reg [5:0] act_mantissa;\n")
    f.write("reg [5:0] wei_exponent;\n")
    f.write("reg [5:0] act_exponent;\n")
    f.write("reg [5:0] wei_regime;\n")
    f.write("reg [5:0] act_regime;\n")


    f.write("reg [`REQUIRED_PES - 1:0] pe_valid;\n")
    f.write("wire [`REQUIRED_PES - 1:0] pe_ready;\n")

    #(TODOS)
    f.write("reg [16-1:0] index_table [0:1024];\n")
    

    f.write("reg [31:0] psum_xx;\n")
    f.write("reg [31:0] psum_yy;\n")
    f.write("reg [31:0] psum_nn;\n")
    f.write("reg [31:0] psum_ii;\n")
    f.write("reg [31:0] psum_iii;\n")
    f.write("reg [31:0] psum_xxx;\n")
    f.write("reg [31:0] psum_yyy;\n")
    f.write("reg [31:0] psum_nnn;\n")
    f.write("reg [31:0] psum_kkx;\n")
    f.write("reg [31:0] psum_kky;\n")
    f.write("reg [31:0] psum_bb;\n")


    #MOVED AFTER SPARSITY TO TAKE CARE OF THE SPARSITY MAP INPUT    
    #1.1. PE (PE_ARRAY + INTER_PE)
    '''
    f.write("INTER_PE inter_pe(\n\
        .clk(core_clk),\n\
        .jia_buf(jia_buf),\n\
        .jia(jia),\n\
        .yi_buf(yi_buf),\n\
        .yi(yi),\n\
        \n\
        .stride(stride), \n\
        .kx(fkx),\n\
        .ky(fky),\n\
        .x(x),\n\
        .y(y), \n\
        .nc(nc), \n\
        .ic(ic), \n\
        .batch(batch),\n\
        .padding_x(padding_x),\n\
        .padding_y(padding_y),\n\
        .OP_TYPE(OP_TYPE),\n\
        .SYSTOLIC_OP(SYSTOLIC_OP),\n\
        .int_inference(int_inference),\n\
        .wei_precision(wei_precision),\n\
        .act_precision(act_precision)\n\
        \n\
        .xxx(psum_xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(psum_yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(psum_xx[`MAX_X_LOG-1:0]),\n\
        .yy(psum_yy[`MAX_Y_LOG-1:0]),\n\
        .bb(psum_bb[`MAX_B_LOG-1:0]),\n\
        .nn(psum_nn[`MAX_N_LOG-1:0]),\n\
        .ii(psum_ii[`MAX_I_LOG-1:0]),\n\
        .nnn(psum_nnn[`MAX_N_LOG-1:0]),\n\
        .iii(psum_iii[`MAX_I_LOG-1:0]),\n\
        .kkx(psum_kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(psum_kky[`MAX_KY_LOG-1:0])\n\
    );\n\n")
    '''
    
    #adder tree method
    f.write("OUTPUT_MAPPING_PE omp(\n\
        .clk(core_clk),\n\
        .zi(zi),\n\
        .zi_buf(zi_buf),\n\
        \n\
        .stride(stride), \n\
        .kx(fkx),\n\
        .ky(fky),\n\
        .x(x),\n\
        .y(y), \n\
        .nc(nc), \n\
        .ic(ic), \n\
        .batch(batch),\n\
        .padding_x(padding_x),\n\
        .padding_y(padding_y),\n\
        .OP_TYPE(OP_TYPE),\n\
        .SYSTOLIC_OP(SYSTOLIC_OP),\n\
                .int_inference(int_inference),\n\
        .wei_precision(wei_precision),\n\
        .act_precision(act_precision)\n\
    );\n\n")

    #debugging winograd and other flows
    #f.write("$monitor(inter_pe.wino_w_"+)
    
    
    f.write("PE_ARRAY pe_array(\n\
            .clk(core_clk),\n\
            .rst_n(rst_n),\n\
            .en(pe_en),\n\
            .int_inference(int_inference),\n\
            .wei_precision(wei_precision),\n\
            .act_precision(act_precision),\n\
            \n\
            .wei_mantissa(wei_mantissa),\n\
            .act_mantissa(act_mantissa),\n\
            .wei_exponent(wei_exponent),\n\
            .act_exponent(act_exponent),\n\
            .wei_regime(wei_regime),\n\
            .act_regime(act_regime),\n\
            \n\
            .jia(jia),\n\
            .yi(yi),\n\
            .zi(zi),\n\
            .valid(pe_valid),\n\
            .ready(pe_ready)\n\
        );\n")
    
    #1.2. BUFFERS
    #Write is from DDR/L2, use fast clock.
    #Read is from L1 and PE, use core_clk
    f.write("reg wei_write_en;\n")
    f.write("reg wei_read_en;\n")
    f.write("reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_read_addr;\n")
    f.write("reg  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_write_addr;\n")
    f.write("reg [`WEI_BUF_DATA  - 1 :0] wei_write_data;\n")

    f.write("WEI_BUF wei_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(ddr_clk),\n\
            .read_en(wei_read_en),\n\
            .read_addr(wei_read_addr),\n\
            .read_data(jia_buf),\n\
            .write_en(wei_write_en),\n\
            .write_addr(wei_write_addr),\n\
            .write_data(wei_write_data)\n\
        );\n")

    f.write("reg act_write_en;\n")
    f.write("reg act_read_en;\n")
    f.write("reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_read_addr;\n")
    f.write("reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_write_addr;\n")
    f.write("reg [ `ACT_BUF_DATA  - 1 :0] act_write_data;\n")

    f.write("ACT_BUF act_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(ddr_clk),\n\
            .read_en(act_read_en),\n\
            .read_addr(act_read_addr),\n\
            .read_data(yi_buf),\n\
            .write_en(act_write_en),\n\
            .write_addr(act_write_addr),\n\
            .write_data(act_write_data)\n\
        );\n")




    f.write("reg [31:0] loop_cnt;\n")


    #debug
    f.write("reg [31:0] acc_state;\n")
    #



    f.write("reg psum_write_en;\n")
    f.write("reg psum_read_en;\n")
    f.write("reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;\n")
    f.write("reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;\n")
    f.write("reg [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;\n")
    f.write("reg [ `PSUM_BUF_DATA - 1 :0] psum_read_data;\n")
    f.write("reg  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data;\n")

    '''
    f.write("ACCUM accum(\n\
            .psum_write_en(psum_write_en),\n\
            .psum_read_en(psum_read_en),\n\
            .psum_read_addr(psum_read_addr),\n\
            .psum_write_addr(psum_write_addr),\n\
            .psum_write_data(psum_write_data),\n\
            .psum_read_data(psum_read_data),\n\
            );\n")
    '''

    f.write("wire accum_en;\n")
    f.write("assign accum_en = |pe_ready ;\n")
    f.write("ACCUM accum(\n\
        .clk(core_clk),\n\
        .rst_n(rst_n),\n\
        .accum_en(accum_en),\n\
            \n\
        .stride(stride), \n\
        .fkx(fkx),\n\
        .fky(fky),\n\
        .x(x),\n\
        .y(y), \n\
        .nc(nc), \n\
        .ic(ic), \n\
        .batch(batch),\n\
        .padding_x(padding_x),\n\
        .padding_y(padding_y),\n\
        .psum_write_en(psum_write_en),\n\
            .psum_read_en(psum_read_en),\n\
            .psum_read_addr(psum_read_addr),\n\
            .psum_write_addr(psum_write_addr),\n\
            .psum_write_data(psum_write_data),\n\
            \n\
            .psum_read_data(psum_read_data),\n\
            .zi_buf(zi_buf),\n\
            \n\
         .int_inference(int_inference),\n\
        .wei_precision(wei_precision),\n\
        .act_precision(act_precision)\n\
        ); ")

    
    #USE THE PSUM_BUF as a dual port SRAM, this way we get the write/read in one wr/rd cycle :D
    f.write("PSUM_BUF psum_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(~core_clk),\n\
            .write_clk(core_clk),\n\
            .read_en(psum_read_en),\n\
            .read_addr(psum_read_addr),\n\
            .read_data(psum_read_data),\n\
            .write_en(psum_write_en),\n\
            .write_addr(psum_write_addr),\n\
            .write_data(psum_write_data)\n);\n")




    ############################
    # 2. Shizhong
    ############################
    f.write("`define CORE_CLK " + str(runtime_config['CORE_CLK'])+"\n")
    f.write("`define DDR_CLK " + str(runtime_config['DDR_CLK'])+"\n")
    
    f.write("initial begin\n\
    core_clk = 1'b0;\n\
    forever begin\n\
    #(`CORE_CLK/2); core_clk = ~core_clk;\n\
    end\n\
    end\n")

    f.write("initial begin\n\
    ddr_clk = 1'b0;\n\
    forever begin\n\
    #(`DDR_CLK/2); ddr_clk = ~ddr_clk;\n\
    end\n\
    end\n")

    ############################
    # 3. 复位和Shuju 传递
    ############################

    f.write("initial begin\n")
    #f.write("initial begin\n")

    #0.
    f.write('$dumpfile("tc.vcd");\n')
    f.write('$dumpvars(0, L1_level_tb);\n')
    
    f.write('end;\n')

    
    ###############################################
    # 3. BEGIN ACT/WEI/PSUM COUNTERS
    ###############################################
    df = trouve_df(hardware_config, runtime_config)
    df_d = get_dataflow_meta(hardware_config, df)


    ###################################
    ##3.1.1 SPARSITY
    ###################################
    WEI_SM_EN = False
    ACT_SM_EN = False    
    if(df_d["DATAFLOW"] == "SPARSE_DIRECT"): #(TODOS, if exists a sparse flow)

        
        if(df_d["SPARSITY"]["ACT_ENCODING"] == "SPARSE_MAP"):
            f.write("wire [ `ACT_SPARSITY_MAP_BUF_DATA - 1:0] act_sm_read_data;\n")
            f.write("reg act_sm_write_en;\n")
            f.write("reg act_sm_read_en;\n")
            f.write("reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_read_addr;\n")
            f.write("reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_write_addr;\n")
            f.write("reg [ `ACT_SPARSITY_MAP_BUF_DATA  - 1 :0] act_sm_write_data;\n")

            f.write("ACT_SPARSITY_MAP_BUF act_sm_buf(\n\
                    .rst_n(rst_n),\n\
                    .read_clk(core_clk),\n\
                    .write_clk(ddr_clk),\n\
                    .read_en(act_sm_read_en),\n\
                    .read_addr(act_sm_read_addr),\n\
                    .read_data(act_sm_read_data),\n\
                    .write_en(act_sm_write_en),\n\
                    .write_addr(act_sm_write_addr),\n\
                    .write_data(act_sm_write_data)\n\
                );\n")
            ACT_SM_EN = True

        if(df_d["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
            f.write("wire [ `WEI_SPARSITY_MAP_BUF_DATA - 1:0] wei_sm_read_data;\n")
            
            f.write("reg wei_sm_write_en;\n")
            f.write("reg wei_sm_read_en;\n")
            f.write("reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_read_addr;\n")
            f.write("reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_write_addr;\n")
            f.write("reg [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_write_data;\n")

            f.write("WEI_SPARSITY_MAP_BUF wei_sm_buf(\n\
                    .rst_n(rst_n),\n\
                    .read_clk(core_clk),\n\
                    .write_clk(ddr_clk),\n\
                    .read_en(wei_sm_read_en),\n\
                    .read_addr(wei_sm_read_addr),\n\
                    .read_data(wei_sm_read_data),\n\
                    .write_en(wei_sm_write_en),\n\
                    .write_addr(wei_sm_write_addr),\n\
                    .write_data(wei_sm_write_data)\n\
                );\n")
            WEI_SM_EN = True

    #Interconnection between the L1 buffers (srams) and the PE unit
    inter_pe_template = "INTER_PE inter_pe(\n"

    if(WEI_SM_EN):
        inter_pe_template += ".jia_sparse_map(wei_sm_read_data),\n"

    if(ACT_SM_EN):
        inter_pe_template += ".yi_sparse_map(act_sm_read_data),\n"
        
    inter_pe_template += ".clk(core_clk),\n\
        .jia_buf(jia_buf),\n\
        .jia(jia),\n\
        .yi_buf(yi_buf),\n\
        .yi(yi),\n\
        \n\
        .xxx(psum_xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(psum_yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(psum_xx[`MAX_X_LOG-1:0]),\n\
        .yy(psum_yy[`MAX_Y_LOG-1:0]),\n\
        .bb(psum_bb[`MAX_B_LOG-1:0]),\n\
        .nn(psum_nn[`MAX_N_LOG-1:0]),\n\
        .ii(psum_ii[`MAX_I_LOG-1:0]),\n\
        .nnn(psum_nnn[`MAX_N_LOG-1:0]),\n\
        .iii(psum_iii[`MAX_I_LOG-1:0]),\n\
        .kkx(psum_kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(psum_kky[`MAX_KY_LOG-1:0]),\n\
        \n\
        .stride(stride), \n\
        .kx(fkx),\n\
        .ky(fky),\n\
        .x(x),\n\
        .y(y), \n\
        .nc(nc), \n\
        .ic(ic), \n\
        .batch(batch),\n\
        .padding_x(padding_x),\n\
        .padding_y(padding_y),\n\
        .OP_TYPE(OP_TYPE),\n\
        .SYSTOLIC_OP(SYSTOLIC_OP),\n\
        .int_inference(int_inference),\n\
        .wei_precision(wei_precision),\n\
        .act_precision(act_precision));\n"
    f.write(inter_pe_template)
            


    ###################################
    ##3.1.2 ADAPTIVE
    ###################################

    from Generate_Verilog import gen_macro_file
    macro = gen_macro_file(hardware_config, meta_config)

    wei_prec, act_prec, psum_prec, floating = get_prec(runtime_config)
    #改变TB, TN...由于
    if("ADAPTIVE" in hardware_config["MULT_TYPE_INT"] and not floating ):
        max_wei_prec = macro[ "MAX_WEI_PRECISION_INT" ]
        max_act_prec = macro[ "MAX_ACT_PRECISION_INT" ]
        
        w_ratio = max_wei_prec//wei_prec
        a_ratio = max_act_prec//act_prec
        import numpy as np
        gcd = np.gcd(w_ratio,a_ratio)
        if("ADAPTIVE_MIXED_AAW" in hardware_config["MULT_TYPE_INT_META"] and w_ratio < a_ratio):
            df_d[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_AAW"]] *= a_ratio//gcd
            
        if("ADAPTIVE_MIXED_WWA" in hardware_config["MULT_TYPE_INT_META"] and a_ratio < w_ratio):
            df_d[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_MIXED_WWA"]] *= w_ratio//gcd

        if("ADAPTIVE_UNIFORM_WA" in hardware_config["MULT_TYPE_INT_META"]):
            df_d[hardware_config["MULT_TYPE_INT_META"]["ADAPTIVE_UNIFORM_WA"]] *= gcd

            
        #f.write("    "*depth + hardware_config["MULT_TYPE_INT_META"][ + "\n")
    if("ADAPTIVE" in hardware_config["MULT_TYPE_INT"] and floating ):
        pass



    ###################################
    ##READ WEIGHTS/ACTS/SPARSE_MAPS
    ###################################
    #假设数据已经从DMA拷贝过来了
    #wei_buf.buf.memh("./dossier"+"/tc/weight.txt")
    f.write("initial begin\n")
    f.write('$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights.txt", wei_buf.mem);\n')
    f.write('$readmemh("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation.txt", act_buf.mem);\n')
    #f.write('$readmemh("weights.txt", wei_buf.mem);\n')
    #f.write('$readmemh("activation.txt", act_buf.mem);\n')

    if(WEI_SM_EN):
        f.write('$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/weights_sparse_map.txt", wei_sm_buf.mem);\n')
        
    if(ACT_SM_EN):        
        f.write('$readmemb("'+meta_config["dossier"]+"/"+meta_config["tc"]  +'/activation_sparse_map.txt", act_sm_buf.mem);\n')
    
    f.write("end\n")
    #act_buf.buf.memh("./dossier"+"/tc/act.txt")
    #psum_buf dont need memh


    #############################################################################################
    
    
    from utils import GET_PSUM_LOOP_FILTERS
    SHI_LOOP_PSUM, WULI_LOOP_PSUM = GET_PSUM_LOOP_FILTERS(hardware_config, df_d)

    #from Generate_ import GET_LOOP_FILTERS
    SHI_LOOP_WEI, SHI_LOOP_ACT, INNER_WEI, INNER_ACT, WULI_LOOP_ACT,\
            WULI_LOOP_WEI, LIM_X, LIM_Y = GET_LOOP_FILTERS(hardware_config, df_d)
    #print("SHI_LOOP_ACT",SHI_LOOP_ACT)
    
    loop_order = df_d["LOOP"]
    wei_loop_order = []
    act_loop_order = []
    psum_loop_order = []




    LIM_X = LIM_X.replace("PADDING","padding_x") \
                     .replace("KX", "fkx") \
                     .replace("KY", "fky")\
                     .replace("STRIDE", "stride")\
                     .replace("X", "x")\
                     .replace("Y", "y")\
                     .replace("//","/")
    LIM_Y = LIM_Y.replace("PADDING","padding_y")\
                     .replace("KX", "fkx")\
                     .replace("KY", "fky")\
                     .replace("STRIDE", "stride")\
                     .replace("X", "x")\
                     .replace("Y", "y")\
                     .replace("//","/")                 

        #实际上每个都会有自己的独特的loop，这里直接写入
        #LIM_X = "((x + padding_x*2 - fkx + 1) / stride  )"
        #LIM_Y = "((y + padding_y*2 - fky + 1) / stride  )"

    MAPPING = {
            "B": "for (integer bb = 0; bb < batch; bb += "+str(df_d["TB"])+")",# in range(0, B , TB):",
            "KX": "for (integer kkx = 0; kkx < fkx; kkx += "+str(df_d["TKX"])+")",#"for kkx in range(0, KX, TKX):",
            "KY": "for (integer kky = 0; kky < fky; kky += "+str(df_d["TKY"])+")",#"for kky in range(0, KY, TKY):",

            "X": "for(integer xxx = 0; xxx < x - fkx + 1; xxx += " + str(df_d["TXX"]) + ")",#"for xxx in range(0, "+LIM_X+", TXX):",
            "Y": "for(integer yyy = 0; yyy < y - fky + 1; yyy += " + str(df_d["TYY"]) + ")",#"for yyy in range(0, "+LIM_Y+", TYY):",
            "N": "for(integer nnn = 0; nnn < nc; nnn += " + str(df_d["TNN"]) + ")",#"for nnn in range(0, N, TNN):",
            "I": "for(integer iii = 0; iii < ic; iii += " + str(df_d["TII"]) + ")",#"for iii in range(0, I , TII):",

            "TNN": "for(integer nn = nnn; nn < nnn + "+str(df_d["TNN"])+"; nn += " + str(df_d["TN"]) + ")",#"for nn in range(nnn, min(nnn+TNN, N), TN):",
            "TII": "for(integer ii = iii; ii < iii + "+str(df_d["TII"])+"; ii += " + str(df_d["TI"]) + ")",# in range(iii, min(iii+TII, I), TI):",
            "TXX": "for(integer xx = xxx; xx < xxx + "+str(df_d["TXX"])+"; xx += " + str(df_d["TX"]) + ")",#"for xx in range(xxx, min(xxx+TXX, "+LIM_X+" , TX+TKX-1):",
            "TYY": "for(integer yy = yyy; yy < yyy + "+str(df_d["TYY"])+"; yy += " + str(df_d["TY"]) + ")",#"yy": #"for yy in range(yyy, min(yyy+TYY, "+LIM_Y+", TY+TKY-1):",
        }

    MAPPING_NO_SECONDARY_TILING = {
            "X": "for(integer xx = 0; xx < x - fkx + 1; xx += " + str(df_d["TX"]) + ")",#"for xxx in range(0, "+LIM_X+", TXX):",
            "Y": "for(integer yy = 0; yy < y - fky + 1; yy += " + str(df_d["TY"]) + ")",#"for yyy in range(0, "+LIM_Y+", TYY):",
            "N": "for(integer nn = 0; nn < nc; nn += " + str(df_d["TN"]) + ")",#"for nnn in range(0, N, TNN):",
            "I": "for(integer ii = 0; ii < ic; ii += " + str(df_d["TI"]) + ")",#"for iii in range(0, I , TII):",


           # "X": "for xx in range(0, "+LIM_X+", TX+TKX-1):",
           # "Y": "for yy in range(0, "+LIM_Y+", TY+TKY-1):",
           # "N": "for nn in range(0, N, TN):",
           #"I": "for ii in range(0, I , TI):",
        }
        


    if("REMOVE_DUPLICATE_ROWS" in df_d):
        REMOVE_DUPLICATE_ROWS = df_d["REMOVE_DUPLICATE_ROWS"]
    else:
        REMOVE_DUPLICATE_ROWS= hardware_config["REMOVE_DUPLICATE_ROWS"]



        
    for l in loop_order:
        #print(l)
        if(l in SHI_LOOP_WEI):
            wei_loop_order.append(l)
        if(l in SHI_LOOP_ACT):
            act_loop_order.append(l)
        if(l in SHI_LOOP_PSUM):
            psum_loop_order.append(l)

    print(wei_loop_order, act_loop_order)
    #f.write("$display("+str(LIM_X)+");\n")

    #calculate cha if we want to reduce the access #
    if(REMOVE_DUPLICATE_ROWS):
        cha_s = ""
        f.write(cha_s)

    #(TODOS systolic WINOGRAD)
    if("WINOGRAD" in df_d["DATAFLOW"]):
        print("HERE")
        f.write("cha_y = 0; cha_x = 0;\n")
        f.write("act_read_addr = loop_idx;\n")
        f.write("loop_idx = loop_idx+ 1;\n")


    def head(delay = 0):
        #3.1. WEI/ACT COUNTERS
        f.write("initial begin\n")
        f.write('rst_n = 0;\n')
        
        f.write('loop_cnt = 0;\n')
        f.write('#(`CORE_CLK*2);\n')
        f.write('rst_n = 1;\n')

        
        f.write('#(`CORE_CLK*'+str(delay)+');\n')

        ########################
        #3.0 准备工作
        #CONV MAPPING


        #先硬写，之后可以用其它方式写入
        wei_prec, act_prec, psum_prec, floating = get_prec(runtime_config)
        f.write("wei_precision = "+str(wei_prec) + ";\n")
        f.write("act_precision = "+str(act_prec) + ";\n")
        #f.write("wei_precision = "+str(wei_prec) + ";\n")
        
        f.write("stride = "+str(runtime_config['Operation_Params']['STRIDE']) +";\n")
        f.write("fkx = " + str(runtime_config['Operation_Params']['KX']) +";\n")
        f.write("fky = " + str(runtime_config['Operation_Params']['KY']) +";\n")
        f.write("x = " + str(runtime_config['Operation_Params']['X']) +";\n")
        f.write("y = " + str(runtime_config['Operation_Params']['Y']) +";\n")
        f.write("ic = " + str(runtime_config['Operation_Params']['I']) +";\n")
        f.write("nc = " + str(runtime_config['Operation_Params']['N']) +";\n")
        f.write("batch = " + str(runtime_config['Operation_Params']['B']) +";\n")
        f.write("padding_x = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n")
        f.write("padding_y = "+ str(runtime_config['Operation_Params']['PADDING']) +";\n")

        f.write("loop_idx = 0;\n")
        
        #开始数据传递

        #print(df_d)
        
        
        depth = 1
        
        for var in loop_order:
            #f.write(MAPPING_VERILOG[l]+"begin\n")
            if(var == "X" and df_d["TXX"] == -1):
                f.write(MAPPING_NO_SECONDARY_TILING[var]+"begin\n")
            elif(var == "Y" and df_d["TYY"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"begin\n")
            elif(var == "N" and df_d["TNN"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"begin\n")
            elif(var == "I" and df_d["TII"] == -1):
                f.write("    "*depth + MAPPING_NO_SECONDARY_TILING[var]+"begin\n")
            else:
                f.write("    "*depth + MAPPING[var]+"begin\n")
            depth += 1

        ###############################   
        #中间
        #CORE_CLK*(DELAY_READ)
        ###############################

        for var in loop_order:
            if(var == "TXX"):
                f.write("psum_xxx = xxx;\n")
            if(var == "TYY"):
                f.write("psum_yyy = yyy;\n")
            if(var == "X"):
                f.write("psum_xx = xx;\n")
            if(var == "Y"):
                f.write("psum_yy = yy;\n")
            if(var == "TNN"):
                f.write("psum_nnn = nnn;\n")
            if(var == "TII"):
                f.write("psum_iii = iii;\n")
            if(var == "B"):
                f.write("psum_bb = bb;\n")
            if(var == "KX"):
                f.write("psum_kkx = kkx;\n")
            if(var == "KY"):
                f.write("psum_kky = kky;\n")
            if(var == "N"):
                f.write("psum_nn = nn;\n")
            if(var == "I"):
                f.write("psum_ii = ii;\n")

            
        f.write("if(nn >= nc) begin\nend\n")
        f.write("else if(ii >= ic) begin\nend\n")
        f.write("else if(xx >= "+LIM_X+") begin\nend\n")
        f.write("else if(yy >= "+LIM_Y+") begin\nend\n")
        f.write("else begin\n")
        '''
        f.write("if(x  >= "+LIM_X+") continue;\n")
        f.write("if(y  >= "+LIM_Y+") continue;\n")
        f.write("if(n  >= nc) continue;\n")
        f.write("if(i  >= ic) continue;\n")
        f.write("if(b  >= batch) continue;\n")
        f.write("if(kx  >= fkx) continue;\n")
        f.write("if(ky  >= fky) continue;\n")    
        '''
        if('KX' in loop_order):
            f.write('$display("\tnn\tii\txx\tyy\tkkx\tkky\tbb");\n')
            f.write("$display(nn, ii, xx, yy, kkx, kky, bb);\n")
        else:
            f.write('$display("\tnn\tii\txx\tyy\tbb");\n')
            f.write("$display(nn, ii, xx, yy, bb);\n")



    def tail():


        f.write("end\n")
        
        for l in loop_order:
            f.write("end\n")

        
        f.write("#(`CORE_CLK);\n")
        f.write("#(`CORE_CLK);\n")
        f.write("#(`CORE_CLK);\n")
        f.write("#(`CORE_CLK);\n")
        f.write("#(`CORE_CLK);\n")        
        f.write("$finish;\n")

        
        f.write("end\n")
        
        
    def loop2index(variables, fd=None, multicast=True, pre = "" ):
        if(True):
            #print(REMOVE_DUPLICATE_ROWS)
            mini_carte = {
                "B": "bb/"+str(df_d["TB"]),
                "N": "nnn/"+str(df_d["TNN"]),
                "X": "xxx/"+str(df_d["TXX"]),
                "Y": "yyy/"+str(df_d["TYY"]),
                "KX": "kkx/"+str(df_d["TKX"]),
                "KY": "kky/"+str(df_d["TKY"]),
                "I":  "iii/"+str(df_d["TII"]),
                "TXX": "xx/"+str(df_d["TX"]),
                "TYY": "yy/"+str(df_d["TY"]),
                "TNN":  "nn/"+str(df_d["TN"]),
                "TII":  "ii/"+str(df_d["TI"]),
            }
            mini_carte_no_secondary = {
                "N": "nn/"+str(df_d["TN"]),
                "I": "ii/"+str(df_d["TI"]),
                "X": "xx/"+str(df_d["TX"]),
                "Y": "yy/"+str(df_d["TY"]),
            }

            
            
            cast = {
                "B": "batch/"+str(df_d["TB"]),
                "N" : "nc/"+str(df_d["TNN"]),
                "X": LIM_X+"/"+str(df_d["TXX"]),
                "Y": LIM_Y+"/"+str(df_d["TYY"]),
                "KX": "fkx/"+str(df_d["TKX"]),
                "KY": "fky/"+str(df_d["TKY"]),
                "I":  "ic/"+str(df_d["TII"]),
                
                "TXX": "(x-fkx+1)" + "/"+str(df_d["TX"]),
                "TYY": "(y-fky+1)" + "/"+str(df_d["TY"]),
                "TII": "ic" + "/"+str(df_d["TI"]),
                "TNN": "nc" + "/"+str(df_d["TN"]),
            }
            cast_no_secondary = {
                "X": "(( x +  " + str(df_d["TX"]) + " -1 )/"+str(df_d["TX"])+")", #"(" + LIM_X+" + "+str(df_d["TX"])+"-1)/"+str(df_d["TX"]),
                "Y":  "(( y + " + str(df_d["TY"]) + " -1 )/"+str(df_d["TY"])+")",#"(" + LIM_Y+" + "+str(df_d["TY"])+"-1)/"+str(df_d["TY"]),
                "I": "ic/"+str(df_d["TI"]),
                "N": "nc/"+str(df_d["TN"]),
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

    ##############################################################
    #3.0 WEI/ACT/PSUM COUNTERS
    head(delay = 0)
    ##############################################################

    if(df_d["DATAFLOW"] == "DIRECT" or df_d["DATAFLOW"] == "SPARSE_DIRECT"):
        TX = str(df_d["TX"])
        TY = str(df_d["TY"])

        #print(df_d['TX'])
        #print("TX", TX)
        #f.write("$display(kkx, fkx, "+TX+", fkx-"+TX+",(kkx < fkx - " + TX +"));")

        #(y+fky) or use ...
        #   (y//TY*fky) (i.e. whichever is larger,  y fky > TY   fky < TY  =.... ==> (TODOS) min(y, y//TY*fky) )

        #如果 [Y....FKY]
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

        print("COND",X_IDX,Y_IDX,KX_IDX,KY_IDX,Y_FKY,X_FKX, LIM_Y, LIM_X)

        if(Y_FKY):
            cond_1 = "(xx == 0 & yy > 0 & fky >= "+TY+"  & kky < fky - "+TY+")"
        else:
            cond_1 = "( (kky >= "+TY+") & (yy +"+TY+"< "+LIM_Y+"))"
        
        if(X_FKX):
            cond_2 = "(xx > 0 & yy == 0 &fkx >= "+TX+" &(kkx < fkx - "+TX+"))"
        else:
            cond_2 =  "( (kkx >= "+TX+")   &  (xx +"+TX+"< "+LIM_X+" ))"

        if(Y_FKY and X_FKX):
            cond_3 = "(xx > 0 & yy > 0 & (((fkx >= "+TX+") &(kkx < fkx - "+TX+")) | ( ( fky >= "+TY+") &( kky < fky - "+TY+"))) ) "
        elif(Y_FKY and not X_FKX):
            cond_3 = "(xx > 0 & yy > 0 & ((kkx >= "+TX+")   &  (xx +"+TX+"< "+LIM_X+" )) | ( ( fky >= "+TY+") &( kky < fky - "+TY+"))) ) "
        elif(not Y_FKY and X_FKX):
            cond_3 = "(xx > 0 & yy > 0 & (((fkx >= "+TX+") &(kkx < fkx - "+TX+")) | (kky >= "+TY+" & (yy +"+TY+"< "+LIM_Y+") ) )"
        else:
            cond_3 = "(xx > 0 & yy > 0 & (((kkx >= "+TX+")   &  (xx +"+TX+"< "+LIM_X+" ) ) | (( kky >= "+TY+") & (yy +"+TY+"< "+LIM_Y+") ) ) )"

        cond_4 = "nn>0"

        f.write("$display("+cond_1+","+cond_2+","+cond_3+","+cond_4+");\n")
        f.write("if (" + "|".join([cond_1,cond_2,cond_3,cond_4]) + ") begin\n")
        
        #f.write("if( (xx == 0 & yy > 0 & fky >= "+TY+"  & kky < fky - "+TY+")   |    (xx > 0 & yy == 0 &fkx >= "+TX+" &(kkx < fkx - "+TX+")) | \
        #    (xx > 0 & yy > 0 & (((fkx >= "+TX+") &(kkx < fkx - "+TX+")) | ( ( fky >= "+TY+") &( kky < fky - "+TY+"))) ) | (nn>0) ) begin\n")
        f.write('   $display("REUSE", (bb)*ic*x*y + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy));\n')
        f.write("   index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] = index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)];\n")
        f.write("   act_read_addr = index_table[(bb)*ic*x*y + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] ;\n")
        f.write("end else begin\n")
        f.write("   index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] = loop_idx;\n")
        f.write("   act_read_addr = loop_idx;\n")
        f.write("loop_idx = loop_idx + 1;\n")
        f.write("end\n")
        
        #f.write("$display(nn, ii, xx, yy, kkx, kky, bb);\n")
        f.write("   $display(index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)]);\n")

    if(df_d["DATAFLOW"] == "SPARSE_DIRECT"):
        if(df_d["SPARSITY"]["WEI_ENCODING"] == "SPARSE_MAP"):
            f.write("wei_sm_read_en = 1;\n")
            f.write("wei_sm_read_addr = " + loop2index(wei_loop_order) + ";\n")
            f.write('$display("wei_sparse_map_addr = ", wei_sm_read_addr);\n')
        else:#(TODOS, like CSS?)
            pass
        
     
    #WEI/ACT addr
    f.write("wei_read_addr = "+loop2index(wei_loop_order)+";\n")
    f.write("wei_read_en = 1;\n")
    f.write("act_read_en = 1;\n")
    f.write("int_inference = 1;\n") #todos should change
    f.write("pe_en = {`REQUIRED_PES {1'b1}};\n")
    f.write("pe_valid = {`REQUIRED_PES {1'b1}};\n")
    
    f.write('$display("wei_read_addr = ", wei_read_addr);\n')
    f.write('$display("%h",wei_buf.mem[wei_read_addr]);\n')
    #f.write("$display(act_read_addr);\n")
    f.write('$display("act_read_addr = ", act_read_addr);\n')
    f.write('$display("%h",act_buf.mem[act_read_addr]);\n')
    f.write("$display(loop_idx);\n")

    

    

    #f.write("psum_zi_buf = zi_buf;\n")
    #PSUM addr timing
    TKX = str(df_d["TKX"])
    TI = str(df_d["TI"])    
    TKY = str(df_d["TKY"])
    #f.write('$display("psum_write_addr =  ",'+loop2index(psum_loop_order)+");\n")
    #f.write('$display("psum_read_addr  =  ",'+loop2index(psum_loop_order)+");\n")


    #########################
    #CLK
        
    f.write('#(`CORE_CLK);\n')

    f.write("loop_cnt = loop_cnt + 1;\n")
    #########################


    
    
    #f.write('$display("psum_write_addr = ", psum_read_addr "\n')

    tail()
    ############################
    # 4. 其他的？
    ############################
    
    f.write("endmodule\n")

    f.close()

    g = open("script.sh","w")

    #1. iverilog
    g.write("iverilog pe_array.v L1_tb.v macro.vh PE.v BUFFER.v\n" )
    g.write("vvp a.out")
    #g.write("analyze vcd")
    
    #2. vcs

    #3. text format
    
    
    g.close()
    
if __name__=="__main__":


    #weight = weight % 3
    IN_CHANNELS  = 8
    OUT_CHANNELS = 8
    KX = 2
    KY = 2
    INPUT_X = 8
    INPUT_Y = 8
    INPUT_BATCH = 1
    STRIDE = 1
    PADDING = 0


    WEI_PREC = "INT16"
    ACT_PREC = "INT16"
    
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
        weight[(i+1)*4 % len(weight)] = 0

    
    weight *= 1
    act *= 1

    #exemple extreme
    #for i in range(IN_CHANNELS*KX*KY):
        #weight[i+IN_CHANNELS*KX*KY] = 0
    weight = weight.reshape([OUT_CHANNELS, IN_CHANNELS, KX, KY])
  
    ####################################
    from real_data import get_data
    #BASE = "real_weights/ResNet50_vd_QAT"
    #NETWORK = "resnet50_conv2"
    #IN_CHANNELS, OUT_CHANNELS, KX, KY, INPUT_X, INPUT_Y, INPUT_BATCH, STRIDE, PADDING, weight, act = get_data(BASE, NETWORK)

    

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

        "OUT_SCALE": 0.023,
        "OUT_PREC": ACT_PREC,

        "BURST": 4,
        "DRAM_DELAY": 4,

        "FIRST_LAYER": True,

        "SPARSITY_EN": True,#如果没有，就用已有得dataflow.如果有，用Sparsity版本的dataflow
       # "I2XY_OPTIMIZATION": True, #for the compiler to do, NVDLA does this. TI (i.e. 32) >> 3, so TI --> TX, TI --> TY,   不用改架构, 虽然是TI=32, 实际是TX = 4, TY = 8 
    }


    hardware_config = {
        "SUPPORTED_WEI_DTYPES": [WEI_PREC],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#, E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16" ,"FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_ACT_DTYPES": [ACT_PREC],#, "INT16","FP8"],#["INT8","INT16", "FP16"],#,"E4M3_FP8","E5M2_FP8","BFP16",  "E7M8_FP16", "FP16", "FP32"], #INT and FloatingPoint variants
        "SUPPORTED_OUT_DTYPES": [ACT_PREC], #Pooling and activation precision
        

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


        #向量加法等 2D的算法
        "VECTOR_UNIT": {

            "ADD_UNIT": 0, #Vector wise add , Used in ResNet
            "MULT_UNIT": 0, #Vector wise multiply


           "POOL":{
               "TX": 1, "TY": 1, "TN": 1, "TKX": 1, "TKY": 1, 
               "LOOP": ["N","Y","X","TKY","TKX"],
               "POOL_UNIT": False,
               
            },
           
            "FUSED_WITH_TENSOR_UNIT": False, #(TODOS, trade energy for lower area)

            "SPARSITY": {
                #TODOS
            }
        },


        #Activations/ Batch_norm, scaling , 1D的算法
        #Can actually be independent of the PE ARRAY
        #(i.e.)
        "ELEMENT_UNIT": {
            "BATCH_NORM_UNIT": 0, #Batchnorm
            "ACTIVATION_UNIT": 0, #Non-relu simple activations, like tanh, sigmoid, 
            "RELU_UNIT": 0, #Relu activation
            "ADD_UNIT": 0, #Bias addition-like 
            "MULT_SCALE_UNIT": 0, #Scaler, quantization, scaling etc.

            "FUSED_WITH_TENOSR_UNIT": False, #(TODOS, trade energy for lower area)

            "SPARSITY": {
                #TODOS
            }
        },

        #Used in networks like U-Net ...
        "RESCALE_UNIT": {
            #TODOS
        },
        
        "TILINGS": {
            #Convolution of 2D type
            "CONV2D": {
                "DEFAULT": {
                    "ID": "0",

                    #DIRECT --> DIRECT CONV
                    #SPARSE_DIRECT_LARGE_TILING --> STRUCTRUED SPARSITY
                    #SPARSE_DIRECT_WINDOW       --> UNSTRUCTURED SPARSITY
                    #WINOGRAD --> WINOGRAD CONVOLUTION
                    #(TODOS) SPARSE_WINOGRAD --> STRUCTURED SPARSITY
                    
                    "DATAFLOW": "DIRECT",#"SPARSE_DIRECT_LARGE_TILING", #SPARSE_DIRECT_LARGE_TILING"SPARSE_DIRECT", #SPARSE_DIRECT_LARGE_TILING # SPARSE_DIRECT/SPARSE_DIRECT_WINDOW #SPARSE_DIRECT#WINOGRAD"DIRECT", #DIRECT, DIRECT_1D_SYSTOLIC, IMG2COL, WINOGRAD etc.

                    #SPARSE_DIRECT_LARGE_TILINGS is structured sparsity, don't need to save address ( to ideal)
                    #SPARSE_DIRECT_WINDOW        is un-structured sparsity, need to save the address of each element potentially to do accumulation (is much faster, closer to ideal)
                    # pour le methode "SPARSE LARGE TILINGS", la capicite de la memoire est dependent sur c'est nombres et parametres ici
                    
                    "TX": 1, "TY": 1,  "TKX": 1, "TKY": 1, "TI":4, "TN": 4, "TB":1,
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

                        #RE_USE at the L1_interconnect_PE stage
                        #OR L2_interconnect_L1 stage

                        #TODOS
                        #NONE --> extra data used
                        #L2 --> IMG2COL shifting in (i.e. DaVinci)
                        #L1 --> INTER_PE activation shifting (i.e. DaDianNao)
                        "ACT_X_INTER": "NONE", #L2, L1 compact_act --> L1 expanded, Further reduce
                        "ACT_Y_INTER": "NONE", #L2, L1 compact act, L1 expanded, Further reduce memory
                   
                    },
                    



                    ########################################
                    #WORK IN PROGRESS
                    #les limites
                    "PE_BUF": "NONE", #NONE, BUFFER, PING_PONG
                    "REMOVE_DUPLICATE_ROWS": True,

                    #Sparsity specific
                    "SPARSITY": {
                        "WEI_ENCODING":"SPARSE_MAP", #NONE, SPARSE_MAP, CSR, etc.
                        "ACT_ENCODING":"SPARSE_MAP", #(TODO) NONE, SPARSE_MAP (HAO), (TODO) CSR  

                        #1. SPARSE WINDOW (unstructured sparsity)
                        "WEI_WINDOW"  :4, #How many to look ahead,
                        "ACT_WINDOW"  :4, #Will affect the buffer
                        "WINDOW_MULTICAST":True,  #If remove, each window (i.e. if input image overlap) will only contain necessary data

                        "LOAD_BALANCE": None, #Weight Re-order, Shuffler, greedy-approaches etc. (TODOS)
                        "WINDOW_GROUP" : ["TX"], #Can do by tile, TX, TI, TN, 数组也可以 ["TX", "TY"],


                        #2. SPARSE TILING (structured sparsity)
                        #The real tiling, PE tiling
                        "SPARSE_TILING": { #应该比Tiling要小一倍
                            # les numeros ici nous donnent la taille et grandeur de la grille de la multiplication
                                #会影响accum
                                  "TX": 1, "TY": 1,  "TN": 2, "TB":1,

                                #不会大影响accum
                                  "TKX": 1, "TKY": 1, "TI": 2, 
                        },

                        "GROUPING_POLICY": "STRUCTURED",#UNSTRUCTURED


                        "VALUE_SPARSITY": "ACT",#WEI, ACT, WEI_ACT, ACT_WEI,  PSUM, etc.

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
            "ACT_L1_READ_DELAY": 1,

            "PSUM_BUFFER":16*1024*8,#16KBytes
            "PSUM_BANKS": 1,

            "PSUM_BUFFER_ON_MAX_LAYER": 0, #True,False
        
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

            #


            #API of the srams see examples in srams/L1_SRAMS fake ones
            "SRAMS": {
                "L1_SRAM": None,#"srams/srams_2p",#REG, or name of SRAM ts6n40lpa512x72m2m_130a_tt1p1v25c.v
                "L2_SRAM": None,
                "L1_SRAM_UNITS": [[512,16], [512,16]],
            },

            #
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
    
    gen_hardware(hardware_config, meta_config)

    print("GEN_SOFTWARE")
    gen_buf(hardware_config, runtime_config, meta_config)

    print("GEN TESTBENCH")

    #Generate test for L1 + PEs
    gen_tb_L1_level(hardware_config, runtime_config, meta_config)

    #Generate test for L2
    gen_tb_L2_1_level(hardware_config, runtime_config, meta_config, macro_config = MACRO_CFG)
    #gen_tb_L2_level(hardware_config, runtime_config, meta_config, macro_config = MACRO_CFG)
    #gen_tb_L2_1_level
    #Generate test for ^  + ACC

    #Generate test for ^ + DMA

    #Generate test for ^ + SDP + PDP + ...

    #Generate test for ^ + multicore...

    
    #TESTING PURPOSES
    
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
    #print(act)
    #print(weight)
