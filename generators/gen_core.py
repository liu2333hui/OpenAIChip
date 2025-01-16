import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import GET_PSUM_LOOP_FILTERS
from utils import order_dataflows

from utils import generate_counter_window

import numpy as np

#######################################
#   L1 buffer and PE and other logic
#######################################
def gen_core_v2(hardware_config, meta_config, macro_config):
    
    print("\n// GEN_CORE VERILOG\n")
    f = open(meta_config["dossier"]+"/core.v", "w")

    #COVER WINOGRAD CASE
    WINOGRAD_EN = False
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):
        WINOGRAD_EN = True

    #COVER SPARSITY BITMAP CASE
    #Sparsity Modules
    WEI_SM_EN = False
    ACT_SM_EN = False
    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        WEI_SM_EN = True

    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] >0):
        ACT_SM_EN = True
        
        
    s = "module DLA_CORE( \n\
            input ddr_clk,\n\
            input core_clk,\n\
            input rst_n,\n\
                \n\
            input addr_cnt_en,\n\
            output operation_done,\n\
                \n\
            output wei_buf_read_ready, \n\
            input  wei_buf_read_valid, \n\
            input [`WEI_BUF_DATA*"+str(hardware_config["WEI_L2_L1_BW_RATIO"])+"-1:0] wei_buf_read_data,\n\
            output [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr, \n\
                \n\
            output act_buf_read_ready, \n\
            input  act_buf_read_valid, \n\
            input [`ACT_BUF_DATA-1:0] act_buf_read_data,\n\
            output [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr, \n\
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
                \n\
            input int_inference, \n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
            input [5:0] wei_mantissa,\n\
            input [5:0] act_mantissa,\n\
            input [5:0] wei_exponent,\n\
            input [5:0] act_exponent,\n\
            input [5:0] wei_regime,\n\
            input [5:0] act_regime,\n\
                \n\
            output  out_buf_write_ready, \n\
            input out_buf_write_valid, \n\
            output [`PSUM_BUF_DATA-1:0] out_buf_write_data,\n\
            output [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, \n\
            \n\
            output result_done,\n\
            \n"
    #carte-tou
    s += "input [`WEI_BUF_DATA-1:0] jia_buf,\n"
    s += "input [`ACT_BUF_DATA-1:0] yi_buf,\n"


    if(not WINOGRAD_EN):
        s += "output [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi,\n"
    else:
        s += "output [`WINO_MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi,\n"

    #carte-wei

    if(not WINOGRAD_EN):
        s += "output [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n"
        s += "output [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n"
    else:
        s += "output [`WINO_MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n"
        s += "output [`WINO_MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n"

    
    s += "output [`PSUM_BUF_DATA - 1:0] zi_buf,\n"
    s += "output [`PSUM_BUF_DATA - 1:0] psum_zi_buf,\n"


    s += "output reg wei_L1_write_en,\n"
    s += "output reg wei_L1_read_en,\n"
    s += "output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_read_addr,\n"
    s += "output reg [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_L1_write_addr,\n"
    s += "output reg [`WEI_BUF_DATA  - 1 :0] wei_L1_write_data,\n"

    s += "output reg act_L1_write_en,\n"
    s += "output reg act_L1_read_en,\n"
    s += "output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_read_addr,\n"
    s += "output reg [`ACT_BUF_ROWS_LOG2  - 1 :0] act_L1_write_addr,\n"
    s += "output reg [`ACT_BUF_DATA  - 1 :0] act_L1_write_data,\n"


    if(WEI_SM_EN):
        s += "output reg wei_sm_write_en,\n"
        s += "output reg wei_sm_read_en,\n"
        s += "output reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_read_addr,\n"
        s += "output reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_write_addr,\n"
        s += "output reg [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_write_data,\n"
            
        s += "input [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_read_data,\n"
    if(ACT_SM_EN):
        s += "input  [ `ACT_SPARSITY_MAP_BUF_DATA - 1:0] act_sm_read_data,\n"
        s += "output reg act_sm_write_en,\n"
        s += "output reg act_sm_read_en,\n"
        s += "output reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_read_addr,\n"
        s += "output reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_sm_write_addr,\n"
        s += "output reg [ `ACT_SPARSITY_MAP_BUF_DATA  - 1 :0] act_sm_write_data,\n"            

            
    
    s += "output [`REQUIRED_PES - 1:0] pe_valid,\n"
    s += "output [`REQUIRED_PES - 1:0] pe_ready,\n"
    s += "output [`REQUIRED_PES - 1:0] pe_last,\n"
    s += "output [`REQUIRED_PES - 1:0] pe_start,\n"

    s += "input [3:0] OP_TYPE,\n"
    s += "input [3:0] SYSTOLIC_OP,\n"
    s += "output psum_write_en,\n"
    s += "output psum_read_en,\n"
    s += "output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr,\n"
    s += "output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr,\n"
    s += "output [ `PSUM_BUF_DATA  - 1 :0] psum_write_data,\n"
    s += "input [ `PSUM_BUF_DATA - 1 :0] psum_read_data,\n"
    s += "input  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data,\n"
    s += "output accum_en,\n"
    s += "output [`MAX_KX_LOG-1:0] kkx,\n"
    s += "output [`MAX_KY_LOG-1:0] kky,\n"
    s += "output [`MAX_X_LOG-1:0] xx,\n"
    s += "output [`MAX_Y_LOG-1:0] yy,\n"
    s += "output [`MAX_X_LOG-1:0] xxx,\n"
    s += "output [`MAX_Y_LOG-1:0] yyy,\n"
    s += "output [`MAX_N_LOG-1:0] nn,\n"
    s += "output [`MAX_I_LOG-1:0] ii,\n"
    s += "output [`MAX_N_LOG-1:0] nnn,\n"
    s += "output [`MAX_I_LOG-1:0] iii,\n"
    s += "output [`MAX_B_LOG-1:0] bb,\n"    
    s += "output mac_en,\n"
    s += "output [`REQUIRED_PES-1:0] pe_en\n"



    
    s += ");\n"

    #ALIAS

    '''
    #carte-tou
    s += "wire [`WEI_BUF_DATA-1:0] jia_buf;\n"
    s += "wire [`ACT_BUF_DATA-1:0] yi_buf;\n"
    s += "wire [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi;\n"

    #carte-wei
    s += "wire [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;\n"
    s += "wire [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;\n"
    s += "wire [`PSUM_BUF_DATA - 1:0] zi_buf;\n"
    s += "wire [`PSUM_BUF_DATA - 1:0] psum_zi_buf;\n"


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

    
    s += "wire [`REQUIRED_PES - 1:0] pe_valid;\n"
    s += "wire [`REQUIRED_PES - 1:0] pe_ready;\n"
    s += "wire [`REQUIRED_PES - 1:0] pe_ready;\n"

    s += "reg [3:0] OP_TYPE;\n"
    s += "reg [3:0] SYSTOLIC_OP;\n"
    

    s += "wire psum_write_en;\n"
    s += "wire psum_read_en;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;\n"
    s += "wire [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;\n"
    s += "wire [ `PSUM_BUF_DATA - 1 :0] psum_read_data;\n"
    s += "reg  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data;\n"

    s += "wire accum_en;\n"
    s += "assign accum_en = |pe_ready ;\n"
    #(TODOS)
    s += "wire [`MAX_KX_LOG-1:0] kkx;\n"
    s += "wire [`MAX_KY_LOG-1:0] kky;\n"
    s += "wire [`MAX_X_LOG-1:0] xx;\n"
    s += "wire [`MAX_Y_LOG-1:0] yy;\n"
    s += "wire [`MAX_X_LOG-1:0] xxx;\n"
    s += "wire [`MAX_Y_LOG-1:0] yyy;\n"
    s += "wire [`MAX_N_LOG-1:0] nn;\n"
    s += "wire [`MAX_I_LOG-1:0] ii;\n"
    s += "wire [`MAX_N_LOG-1:0] nnn;\n"
    s += "wire [`MAX_I_LOG-1:0] iii;\n"
    s += "wire [`MAX_B_LOG-1:0] bb;\n"    


    ####Connecting logic
    s += "wire mac_en;\n"
    s += "wire [`REQUIRED_PES-1:0] pe_en;\n"

    '''
    s += "wire accum_done;\n"
    s += "wire mult_done;\n"    
    s += "wire pre_mult_done;\n"
    
    s += "wire pe_all_ready = &pe_ready ;\n"
    s += "wire pe_all_last = &pe_last;\n"
    s += "wire pe_all_start = &pe_start;\n"

    s += "wire tile_done;\n"

    s += "wire ACCUM_stall;\n" #stalled due to the MAC unit stalling


    s += "wire ACC_stalled;\n"


    s += "wire [5:0] jia_sys_jie;\n"
    s += "wire [5:0] yi_sys_jie;\n"


    s += "wire inter_pe_sparse_stall;\n"


    
    
    s += "assign mult_done = pe_all_ready & ~ACCUM_stall;\n"
    s += "assign pre_mult_done = pe_all_last & ~ACCUM_stall;\n"
    
    s += "assign tile_done = mult_done & ~inter_pe_sparse_stall;\n"

    
    s += "assign pe_en = {`REQUIRED_PES{mac_en & ~accum_done}} ;\n"
    s += "assign pe_valid = {`REQUIRED_PES{mac_en & ~accum_done }} ;\n"
    #TODOS, power gating
    #(TODOS for STRIPES)
    
    #ALIAS (TODOS with different size of the weight? L2->L1 mapping)
    #s += "assign wei_L1_write_data = wei_buf_read_data;\n"
    #s += "assign act_L1_write_data = act_buf_read_data;\n"

    s += "wire [`MAX_KX_LOG-1:0] ACC_kkx;\n"
    s += "wire [`MAX_KY_LOG-1:0] ACC_kky;\n"
    s += "wire [`MAX_X_LOG-1:0] ACC_xx;\n"
    s += "wire [`MAX_Y_LOG-1:0] ACC_yy;\n"
    s += "wire [`MAX_X_LOG-1:0] ACC_xxx;\n"
    s += "wire [`MAX_Y_LOG-1:0] ACC_yyy;\n"
    s += "wire [`MAX_N_LOG-1:0] ACC_nn;\n"
    s += "wire [`MAX_I_LOG-1:0] ACC_ii;\n"
    s += "wire [`MAX_N_LOG-1:0] ACC_nnn;\n"
    s += "wire [`MAX_I_LOG-1:0] ACC_iii;\n"
    s += "wire [`MAX_B_LOG-1:0] ACC_bb;\n"    


    #(TODOS) is operation_done based onl on the address_counter? Or the accumulator is beter ?
    s += "ADDR_CNT addr_cnt(\n\
            .addr_cnt_en(addr_cnt_en),\n\
            .operation_done(operation_done),\n\
                \n\
            .clk(core_clk),\n\
            .rst_n(rst_n),\n\
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
                \n\
            .wei_L2_buf_read_ready(wei_buf_read_ready), \n\
            .wei_L2_buf_read_valid(wei_buf_read_valid), \n\
            .wei_L2_buf_read_addr(wei_buf_read_addr), \n\
            .wei_L2_buf_read_data(wei_buf_read_data),\n\
                \n\
            .act_L2_buf_read_ready(act_buf_read_ready), \n\
            .act_L2_buf_read_valid(act_buf_read_valid), \n\
            .act_L2_buf_read_addr(act_buf_read_addr), \n\
            .act_L2_buf_read_data(act_buf_read_data),\n\
                \n\
            .act_L1_buf_write_addr(act_L1_write_addr), \n\
            .act_L1_buf_write_en(act_L1_write_en)  , \n\
            .act_L1_buf_write_data(act_L1_write_data)  ,\n\
                \n\
            .wei_L1_buf_write_addr(wei_L1_write_addr), \n\
            .wei_L1_buf_write_en(wei_L1_write_en)  , \n\
            .wei_L1_buf_write_data(wei_L1_write_data), \n\
                \n\
            .act_L1_buf_read_addr(act_L1_read_addr), \n\
            .act_L1_buf_read_en(act_L1_read_en)  , \n\
                \n\
            .wei_L1_buf_read_addr(wei_L1_read_addr), \n\
            .wei_L1_buf_read_en(wei_L1_read_en),   \n\
                \n\
            .mac_en(mac_en), \n\
                \n\
            .accum_done(result_done), \n\
                \n\
            .wei_precision(wei_precision),\n\
            .act_precision(act_precision),\n\
                \n\
        .xxx(xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(xx[`MAX_X_LOG-1:0]),\n\
        .yy(yy[`MAX_Y_LOG-1:0]),\n\
        .bb(bb[`MAX_B_LOG-1:0]),\n\
        .nn(nn[`MAX_N_LOG-1:0]),\n\
        .ii(ii[`MAX_I_LOG-1:0]),\n\
        .nnn(nnn[`MAX_N_LOG-1:0]),\n\
        .iii(iii[`MAX_I_LOG-1:0]),\n\
        .kkx(kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(kky[`MAX_KY_LOG-1:0]),\n\
            \n\
        .ACC_xxx(ACC_xxx[`MAX_X_LOG-1:0]),\n\
        .ACC_yyy(ACC_yyy[`MAX_Y_LOG-1:0]),\n\
        .ACC_xx(ACC_xx[`MAX_X_LOG-1:0]),\n\
        .ACC_yy(ACC_yy[`MAX_Y_LOG-1:0]),\n\
        .ACC_bb(ACC_bb[`MAX_B_LOG-1:0]),\n\
        .ACC_nn(ACC_nn[`MAX_N_LOG-1:0]),\n\
        .ACC_ii(ACC_ii[`MAX_I_LOG-1:0]),\n\
        .ACC_nnn(ACC_nnn[`MAX_N_LOG-1:0]),\n\
        .ACC_iii(ACC_iii[`MAX_I_LOG-1:0]),\n\
        .ACC_kkx(ACC_kkx[`MAX_KX_LOG-1:0]),\n\
        .ACC_kky(ACC_kky[`MAX_KY_LOG-1:0]),\n\
            \n\
        .pe_array_start(pe_all_start),\n\
        .pe_array_ready(pe_all_ready),\n\
        .pe_array_last(pe_all_last),\n\
            \n\
        .ACC_stalled(ACC_stalled),\n\
            \n\
        .jia_sys_jie(jia_sys_jie),\n\
        .yi_sys_jie(yi_sys_jie),\n\
            \n\
        .ACCUM_stall(ACCUM_stall),\n\
            \n\
        .inter_pe_sparse_stall(inter_pe_sparse_stall)\n\
        );\n"



    
    #PSUM MAPPING
    s += "OUTPUT_MAPPING_PE omp(\n\
        .clk(core_clk),\n\
        .rst_n(rst_n), \n\
            \n\
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
        .act_precision(act_precision),\n\
        .mult_done(mult_done),\n\
        \n\
        .tile_done(tile_done),\n\
        .add_tree_ready(accum_en)\n\
    );\n\n"

    s += "PE_ARRAY pe_array(\n\
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
            .ready(pe_ready),\n\
            .last(pe_last),\n\
            .start(pe_start),\n\
            \n\
            .pe_all_ready(pe_all_ready)\n\
        );\n"




    '''
    #L1 BUFFERS / SCRATCHPADS
    s += "WEI_BUF wei_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(ddr_clk),\n\
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
            .write_clk(ddr_clk),\n\
            .read_en(act_L1_read_en),\n\
            .read_addr(act_L1_read_addr),\n\
            .read_data(yi_buf),\n\
            .write_en(act_L1_write_en),\n\
            .write_addr(act_L1_write_addr),\n\
            .write_data(act_L1_write_data)\n\
        );\n"


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
    '''
    
    #ACCUMULATOR BLOCK
    s += "ACCUM accum(\n\
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
        .act_precision(act_precision),\n\
            \n\
            .out_buf_write_ready(out_buf_write_ready), \n\
            .out_buf_write_valid(out_buf_write_valid), \n\
            .out_buf_write_data(out_buf_write_data),\n\
            .out_buf_write_addr(out_buf_write_addr), \n\
            \n\
            .ACC_stalled(ACC_stalled),\n\
            \n\
            .accum_done(accum_done),\n\
            \n\
        .result_done(result_done)\n"
    
    '''
            \n\
        .xxx(ACC_xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(ACC_yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(ACC_xx[`MAX_X_LOG-1:0]),\n\
        .yy(ACC_yy[`MAX_Y_LOG-1:0]),\n\
        .bb(ACC_bb[`MAX_B_LOG-1:0]),\n\
        .nn(ACC_nn[`MAX_N_LOG-1:0]),\n\
        .ii(ACC_ii[`MAX_I_LOG-1:0]),\n\
        .nnn(ACC_nnn[`MAX_N_LOG-1:0]),\n\
        .iii(ACC_iii[`MAX_I_LOG-1:0]),\n\
        .kkx(ACC_kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(ACC_kky[`MAX_KY_LOG-1:0]),\
        
        '''
    s += "); "

    #Sparsity Logic
    if(WEI_SM_EN):
        s += "always@(*) begin\n\
                 wei_sm_read_addr  = wei_L1_read_addr;\n\
                 wei_sm_write_addr = wei_L1_write_addr;\n\
                 wei_sm_write_en = wei_L1_write_en & 0;//不写现在(todos)\n\
                 wei_sm_read_en = wei_L1_read_en;\n\
              end\n"
        

    if(ACT_SM_EN):
        s += "always@(*) begin\n\
                 act_sm_read_addr  = act_L1_read_addr;\n\
                 act_sm_write_addr = act_L1_write_addr;\n\
                 act_sm_write_en = act_L1_write_en & 0;//不写现在(todos)\n\
                 act_sm_read_en = act_L1_read_en;\n\
              end\n"

    #print(WEI_SM_EN, ACT_SM_EN)
    #exit(0)
    
    inter_pe_template = "INTER_PE inter_pe(\n"
    if(WEI_SM_EN):
        inter_pe_template += ".jia_sparse_map(wei_sm_read_data),\n"

    if(ACT_SM_EN):
        inter_pe_template += ".yi_sparse_map(act_sm_read_data),\n"
    inter_pe_template += ".clk(core_clk),\n\
        .rst_n(rst_n), \n\
        .jia_buf(jia_buf),\n\
        .jia(jia),\n\
        .yi_buf(yi_buf),\n\
        .yi(yi),\n\
        \n\
        .xxx(xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(xx[`MAX_X_LOG-1:0]),\n\
        .yy(yy[`MAX_Y_LOG-1:0]),\n\
        .bb(bb[`MAX_B_LOG-1:0]),\n\
        .nn(nn[`MAX_N_LOG-1:0]),\n\
        .ii(ii[`MAX_I_LOG-1:0]),\n\
        .nnn(nnn[`MAX_N_LOG-1:0]),\n\
        .iii(iii[`MAX_I_LOG-1:0]),\n\
        .kkx(kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(kky[`MAX_KY_LOG-1:0]),\n\
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
        .act_precision(act_precision),\n\
                \n\
        .wei_sys_en(wei_L1_read_en), \n\
        .act_sys_en(act_L1_read_en), \n\
                \n\
         .jia_sys_jie(jia_sys_jie),\n\
        .yi_sys_jie(yi_sys_jie),\n\
                \n\
        .mac_en(mac_en), \n\
                \n\
        .sparse_stall(inter_pe_sparse_stall),\n\
                \n\
        .mult_done(pe_all_ready),\n\
        .pre_mult_done(pre_mult_done)\n\
    );\n"
    s += inter_pe_template    



    #ELEMENT ACTIVATION UNIT
    s+= "wire [`MAX_ELEMENT_UNITS*`MAX_OUT_PRECISION-1:0] element_buf_data;\n"
    s+= "wire [5 : 0] element_buf_addr;\n"
    s+= "wire element_buf_data_ready;\n"
    s+= "wire [3:0] element_operation;\n"

    s+= "wire [5:0] output_precision;\n"
    s+= "wire [5:0] input_precision;\n"
    

    s += "ELEMENT_UNIT element_unit(\n\
            .clk(clk),\n\
            .rst_n(rst_n),\n\
            .output_precision(output_precision),\n\
            .input_precision(input_precision),\n\
                \n\
            .out_buf_write_ready(out_buf_write_ready),\n\
            .out_buf_write_valid(out_buf_write_valid),\n\
            .out_buf_write_data(out_buf_write_data),\n\
            .out_buf_write_addr(out_buf_write_addr), \n\
                \n\
            .element_buf_data(element_buf_data),\n\
            .element_buf_addr(element_buf_addr), \n\
            .element_buf_data_ready(element_buf_data_ready),\n\
                \n\
            .element_operation(element_operation)\n\
        );\n"




    #POOLING ELELEMENT-WISE UNIT
    






    s += "endmodule\n"
    
    f.write(s)
    f.close()




def gen_core_v1(hardware_config, meta_config, macro_config):
    
    print("\n// GEN_CORE VERILOG\n")
    f = open(meta_config["dossier"]+"/core.v", "w")


    s = "module DLA_CORE( \n\
            input ddr_clk,\n\
            input core_clk,\n\
            input rst_n,\n\
                \n\
            input addr_cnt_en,\n\
            output operation_done,\n\
                \n\
            output wei_buf_read_ready, \n\
            input  wei_buf_read_valid, \n\
            input [`WEI_BUF_DATA-1:0] wei_buf_read_data,\n\
            output [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr, \n\
                \n\
            output act_buf_read_ready, \n\
            input  act_buf_read_valid, \n\
            input [`ACT_BUF_DATA-1:0] act_buf_read_data,\n\
            output [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr, \n\
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
                \n\
            input int_inference, \n\
            input [5:0] wei_precision,\n\
            input [5:0] act_precision,\n\
            input [5:0] wei_mantissa,\n\
            input [5:0] act_mantissa,\n\
            input [5:0] wei_exponent,\n\
            input [5:0] act_exponent,\n\
            input [5:0] wei_regime,\n\
            input [5:0] act_regime,\n\
                \n\
            output  out_buf_write_ready, \n\
            input out_buf_write_valid, \n\
            output [`PSUM_BUF_DATA-1:0] out_buf_write_data,\n\
            output [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, \n\
            \n\
            output result_done,\n\
            \n"
    #carte-tou
    s += "output [`WEI_BUF_DATA-1:0] jia_buf,\n"
    s += "output [`ACT_BUF_DATA-1:0] yi_buf,\n"
    s += "output [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi,\n"

    #carte-wei
    s += "output [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,\n"
    s += "output [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,\n"
    s += "output [`PSUM_BUF_DATA - 1:0] zi_buf,\n"
    s += "output [`PSUM_BUF_DATA - 1:0] psum_zi_buf,\n"


    s += "output wei_L1_write_en,\n"
    s += "output wei_L1_read_en,\n"
    s += "output [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_read_addr,\n"
    s += "output  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_L1_write_addr,\n"
    s += "output [`WEI_BUF_DATA  - 1 :0] wei_L1_write_data,\n"

    s += "output act_L1_write_en,\n"
    s += "output act_L1_read_en,\n"
    s += "output [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_read_addr,\n"
    s += "output  [`ACT_BUF_ROWS_LOG2  - 1 :0] act_L1_write_addr,\n"
    s += "output [`ACT_BUF_DATA  - 1 :0] act_L1_write_data,\n"

    
    s += "output [`REQUIRED_PES - 1:0] pe_valid,\n"
    s += "output [`REQUIRED_PES - 1:0] pe_ready,\n"

    s += "input [3:0] OP_TYPE,\n"
    s += "input [3:0] SYSTOLIC_OP,\n"
    s += "output psum_write_en,\n"
    s += "output psum_read_en,\n"
    s += "output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr,\n"
    s += "output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr,\n"
    s += "output [ `PSUM_BUF_DATA  - 1 :0] psum_write_data,\n"
    s += "output [ `PSUM_BUF_DATA - 1 :0] psum_read_data,\n"
    s += "input  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data,\n"
    s += "output accum_en,\n"
    s += "output [`MAX_KX_LOG-1:0] kkx,\n"
    s += "output [`MAX_KY_LOG-1:0] kky,\n"
    s += "output [`MAX_X_LOG-1:0] xx,\n"
    s += "output [`MAX_Y_LOG-1:0] yy,\n"
    s += "output [`MAX_X_LOG-1:0] xxx,\n"
    s += "output [`MAX_Y_LOG-1:0] yyy,\n"
    s += "output [`MAX_N_LOG-1:0] nn,\n"
    s += "output [`MAX_I_LOG-1:0] ii,\n"
    s += "output [`MAX_N_LOG-1:0] nnn,\n"
    s += "output [`MAX_I_LOG-1:0] iii,\n"
    s += "output [`MAX_B_LOG-1:0] bb,\n"    
    s += "output mac_en,\n"
    s += "output [`REQUIRED_PES-1:0] pe_en\n"
    s += ");\n"

    #ALIAS

    '''
    #carte-tou
    s += "wire [`WEI_BUF_DATA-1:0] jia_buf;\n"
    s += "wire [`ACT_BUF_DATA-1:0] yi_buf;\n"
    s += "wire [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi;\n"

    #carte-wei
    s += "wire [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;\n"
    s += "wire [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;\n"
    s += "wire [`PSUM_BUF_DATA - 1:0] zi_buf;\n"
    s += "wire [`PSUM_BUF_DATA - 1:0] psum_zi_buf;\n"


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

    
    s += "wire [`REQUIRED_PES - 1:0] pe_valid;\n"
    s += "wire [`REQUIRED_PES - 1:0] pe_ready;\n"

    s += "reg [3:0] OP_TYPE;\n"
    s += "reg [3:0] SYSTOLIC_OP;\n"
    

    s += "wire psum_write_en;\n"
    s += "wire psum_read_en;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;\n"
    s += "wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;\n"
    s += "wire [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;\n"
    s += "wire [ `PSUM_BUF_DATA - 1 :0] psum_read_data;\n"
    s += "reg  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data;\n"

    s += "wire accum_en;\n"
    s += "assign accum_en = |pe_ready ;\n"
    #(TODOS)
    s += "wire [`MAX_KX_LOG-1:0] kkx;\n"
    s += "wire [`MAX_KY_LOG-1:0] kky;\n"
    s += "wire [`MAX_X_LOG-1:0] xx;\n"
    s += "wire [`MAX_Y_LOG-1:0] yy;\n"
    s += "wire [`MAX_X_LOG-1:0] xxx;\n"
    s += "wire [`MAX_Y_LOG-1:0] yyy;\n"
    s += "wire [`MAX_N_LOG-1:0] nn;\n"
    s += "wire [`MAX_I_LOG-1:0] ii;\n"
    s += "wire [`MAX_N_LOG-1:0] nnn;\n"
    s += "wire [`MAX_I_LOG-1:0] iii;\n"
    s += "wire [`MAX_B_LOG-1:0] bb;\n"    


    ####Connecting logic
    s += "wire mac_en;\n"
    s += "wire [`REQUIRED_PES-1:0] pe_en;\n"

    '''
    s += "assign accum_en = |pe_ready & ~ACCUM_stall;\n"
    s += "assign pe_en = {`REQUIRED_PES{mac_en}};\n"
    s += "assign pe_valid = {`REQUIRED_PES{mac_en}};\n"
    #TODOS, power gating
    
    
    #ALIAS (TODOS with different size of the weight? L2->L1 mapping)
    #s += "assign wei_L1_write_data = wei_buf_read_data;\n"
    #s += "assign act_L1_write_data = act_buf_read_data;\n"

    #(TODOS) is operation_done based onl on the address_counter? Or the accumulator is beter ?
    s += "ADDR_CNT addr_cnt(\n\
            .addr_cnt_en(addr_cnt_en),\n\
            .operation_done(operation_done),\n\
                \n\
            .clk(core_clk),\n\
            .rst_n(rst_n),\n\
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
                \n\
            .wei_L2_buf_read_ready(wei_buf_read_ready), \n\
            .wei_L2_buf_read_valid(wei_buf_read_valid), \n\
            .wei_L2_buf_read_addr(wei_buf_read_addr), \n\
            .wei_L2_buf_read_data(wei_buf_read_data),\n\
                \n\
            .act_L2_buf_read_ready(act_buf_read_ready), \n\
            .act_L2_buf_read_valid(act_buf_read_valid), \n\
            .act_L2_buf_read_addr(act_buf_read_addr), \n\
            .act_L2_buf_read_data(act_buf_read_data),\n\
                \n\
            .act_L1_buf_write_addr(act_L1_write_addr), \n\
            .act_L1_buf_write_en(act_L1_write_en)  , \n\
            .act_L1_buf_write_data(act_L1_write_data)  ,\n\
                \n\
            .wei_L1_buf_write_addr(wei_L1_write_addr), \n\
            .wei_L1_buf_write_en(wei_L1_write_en)  , \n\
            .wei_L1_buf_write_data(wei_L1_write_data), \n\
                \n\
            .act_L1_buf_read_addr(act_L1_read_addr), \n\
            .act_L1_buf_read_en(act_L1_read_en)  , \n\
                \n\
            .wei_L1_buf_read_addr(wei_L1_read_addr), \n\
            .wei_L1_buf_read_en(wei_L1_read_en),   \n\
                \n\
            .mac_en(mac_en), \n\
                \n\
            .wei_precision(wei_precision),\n\
            .act_precision(act_precision),\n\
                \n\
        .xxx(xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(xx[`MAX_X_LOG-1:0]),\n\
        .yy(yy[`MAX_Y_LOG-1:0]),\n\
        .bb(bb[`MAX_B_LOG-1:0]),\n\
        .nn(nn[`MAX_N_LOG-1:0]),\n\
        .ii(ii[`MAX_I_LOG-1:0]),\n\
        .nnn(nnn[`MAX_N_LOG-1:0]),\n\
        .iii(iii[`MAX_I_LOG-1:0]),\n\
        .kkx(kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(kky[`MAX_KY_LOG-1:0])\
        );\n"



    
    #PSUM MAPPING
    s += "OUTPUT_MAPPING_PE omp(\n\
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
    );\n\n"

    s += "PE_ARRAY pe_array(\n\
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
        );\n"




    
    #L1 BUFFERS / SCRATCHPADS
    s += "WEI_BUF wei_buf(\n\
            .rst_n(rst_n),\n\
            .read_clk(core_clk),\n\
            .write_clk(ddr_clk),\n\
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
            .write_clk(ddr_clk),\n\
            .read_en(act_L1_read_en),\n\
            .read_addr(act_L1_read_addr),\n\
            .read_data(yi_buf),\n\
            .write_en(act_L1_write_en),\n\
            .write_addr(act_L1_write_addr),\n\
            .write_data(act_L1_write_data)\n\
        );\n"


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

    
    #ACCUMULATOR BLOCK
    s += "ACCUM accum(\n\
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
        .act_precision(act_precision),\n\
            \n\
            .out_buf_write_ready(out_buf_write_ready), \n\
            .out_buf_write_valid(out_buf_write_valid), \n\
            .out_buf_write_data(out_buf_write_data),\n\
            .out_buf_write_addr(out_buf_write_addr), \n\
            \n\
        .result_done(result_done)\n\
        ); "

    #Sparsity Modules
    WEI_SM_EN = False
    ACT_SM_EN = False
    if("WEI_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
        s += "reg wei_sm_write_en;\n"
        s += "reg wei_sm_read_en;\n"
        s += "reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_read_addr;\n"
        s += "reg [ `WEI_BUF_ROWS_LOG2  - 1 :0] wei_sm_write_addr;\n"
        s += "reg [ `WEI_SPARSITY_MAP_BUF_DATA  - 1 :0] wei_sm_write_data;\n"


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

    if("ACT_SPARSITY_MAP_BUF_DATA" in macro_config and macro_config["ACT_SPARSITY_MAP_BUF_DATA"] > 0):

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
        .xxx(xxx[`MAX_X_LOG-1:0]),\n\
        .yyy(yyy[`MAX_Y_LOG-1:0]),\n\
        .xx(xx[`MAX_X_LOG-1:0]),\n\
        .yy(yy[`MAX_Y_LOG-1:0]),\n\
        .bb(bb[`MAX_B_LOG-1:0]),\n\
        .nn(nn[`MAX_N_LOG-1:0]),\n\
        .ii(ii[`MAX_I_LOG-1:0]),\n\
        .nnn(nnn[`MAX_N_LOG-1:0]),\n\
        .iii(iii[`MAX_I_LOG-1:0]),\n\
        .kkx(kkx[`MAX_KX_LOG-1:0]),\n\
        .kky(kky[`MAX_KY_LOG-1:0]),\n\
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
    s += inter_pe_template    


    s += "endmodule\n"
    
    f.write(s)
    f.close()
