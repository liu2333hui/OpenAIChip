module DLA_CORE( 
            input ddr_clk,
            input core_clk,
            input rst_n,
                
            input addr_cnt_en,
            output operation_done,
                
            output wei_buf_read_ready, 
            input  wei_buf_read_valid, 
            input [`WEI_BUF_DATA*1-1:0] wei_buf_read_data,
            output [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr, 
                
            output act_buf_read_ready, 
            input  act_buf_read_valid, 
            input [`ACT_BUF_DATA-1:0] act_buf_read_data,
            output [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr, 
                
        input [`MAX_PADDING_X_LOG-1:0] padding_x,
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,
            input [`MAX_STRIDE_LOG-1:0] stride,
            input [`MAX_KX_LOG-1:0] fkx,
            input [`MAX_KY_LOG-1:0] fky,
            input  [`MAX_X_LOG-1:0] x,
            input  [`MAX_Y_LOG-1:0] y,
            input  [`MAX_N_LOG-1:0] nc,
            input  [`MAX_I_LOG-1:0] ic,
            input  [`MAX_B_LOG-1:0] batch,
                
            input int_inference, 
            input [5:0] wei_precision,
            input [5:0] act_precision,
            input [5:0] wei_mantissa,
            input [5:0] act_mantissa,
            input [5:0] wei_exponent,
            input [5:0] act_exponent,
            input [5:0] wei_regime,
            input [5:0] act_regime,
                
            output  out_buf_write_ready, 
            input out_buf_write_valid, 
            output [`PSUM_BUF_DATA-1:0] out_buf_write_data,
            output [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, 
            
            output result_done,
            
input [`WEI_BUF_DATA-1:0] jia_buf,
input [`ACT_BUF_DATA-1:0] yi_buf,
output [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi,
output [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,
output [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,
output [`PSUM_BUF_DATA - 1:0] zi_buf,
output [`PSUM_BUF_DATA - 1:0] psum_zi_buf,
output reg wei_L1_write_en,
output reg wei_L1_read_en,
output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_read_addr,
output reg [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_L1_write_addr,
output reg [`WEI_BUF_DATA  - 1 :0] wei_L1_write_data,
output reg act_L1_write_en,
output reg act_L1_read_en,
output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_read_addr,
output reg [`ACT_BUF_ROWS_LOG2  - 1 :0] act_L1_write_addr,
output reg [`ACT_BUF_DATA  - 1 :0] act_L1_write_data,
output [`REQUIRED_PES - 1:0] pe_valid,
output [`REQUIRED_PES - 1:0] pe_ready,
output [`REQUIRED_PES - 1:0] pe_last,
output [`REQUIRED_PES - 1:0] pe_start,
input [3:0] OP_TYPE,
input [3:0] SYSTOLIC_OP,
output psum_write_en,
output psum_read_en,
output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr,
output [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr,
output [ `PSUM_BUF_DATA  - 1 :0] psum_write_data,
input [ `PSUM_BUF_DATA - 1 :0] psum_read_data,
input  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data,
output accum_en,
output [`MAX_KX_LOG-1:0] kkx,
output [`MAX_KY_LOG-1:0] kky,
output [`MAX_X_LOG-1:0] xx,
output [`MAX_Y_LOG-1:0] yy,
output [`MAX_X_LOG-1:0] xxx,
output [`MAX_Y_LOG-1:0] yyy,
output [`MAX_N_LOG-1:0] nn,
output [`MAX_I_LOG-1:0] ii,
output [`MAX_N_LOG-1:0] nnn,
output [`MAX_I_LOG-1:0] iii,
output [`MAX_B_LOG-1:0] bb,
output mac_en,
output [`REQUIRED_PES-1:0] pe_en
);
wire accum_done;
wire mult_done;
wire pre_mult_done;
wire pe_all_ready = &pe_ready ;
wire pe_all_last = &pe_last;
wire pe_all_start = &pe_start;
wire tile_done;
wire ACCUM_stall;
wire ACC_stalled;
wire [5:0] jia_sys_jie;
wire [5:0] yi_sys_jie;
wire inter_pe_sparse_stall;
assign mult_done = pe_all_ready & ~ACCUM_stall;
assign pre_mult_done = pe_all_last & ~ACCUM_stall;
assign tile_done = mult_done & ~inter_pe_sparse_stall;
assign pe_en = {`REQUIRED_PES{mac_en & ~accum_done}} ;
assign pe_valid = {`REQUIRED_PES{mac_en & ~accum_done }} ;
wire [`MAX_KX_LOG-1:0] ACC_kkx;
wire [`MAX_KY_LOG-1:0] ACC_kky;
wire [`MAX_X_LOG-1:0] ACC_xx;
wire [`MAX_Y_LOG-1:0] ACC_yy;
wire [`MAX_X_LOG-1:0] ACC_xxx;
wire [`MAX_Y_LOG-1:0] ACC_yyy;
wire [`MAX_N_LOG-1:0] ACC_nn;
wire [`MAX_I_LOG-1:0] ACC_ii;
wire [`MAX_N_LOG-1:0] ACC_nnn;
wire [`MAX_I_LOG-1:0] ACC_iii;
wire [`MAX_B_LOG-1:0] ACC_bb;
ADDR_CNT addr_cnt(
            .addr_cnt_en(addr_cnt_en),
            .operation_done(operation_done),
                
            .clk(core_clk),
            .rst_n(rst_n),
            
            .stride(stride), 
            .fkx(fkx),
            .fky(fky),
            .x(x),
            .y(y), 
            .nc(nc), 
            .ic(ic), 
            .batch(batch),
            .padding_x(padding_x),
            .padding_y(padding_y),
                
            .wei_L2_buf_read_ready(wei_buf_read_ready), 
            .wei_L2_buf_read_valid(wei_buf_read_valid), 
            .wei_L2_buf_read_addr(wei_buf_read_addr), 
            .wei_L2_buf_read_data(wei_buf_read_data),
                
            .act_L2_buf_read_ready(act_buf_read_ready), 
            .act_L2_buf_read_valid(act_buf_read_valid), 
            .act_L2_buf_read_addr(act_buf_read_addr), 
            .act_L2_buf_read_data(act_buf_read_data),
                
            .act_L1_buf_write_addr(act_L1_write_addr), 
            .act_L1_buf_write_en(act_L1_write_en)  , 
            .act_L1_buf_write_data(act_L1_write_data)  ,
                
            .wei_L1_buf_write_addr(wei_L1_write_addr), 
            .wei_L1_buf_write_en(wei_L1_write_en)  , 
            .wei_L1_buf_write_data(wei_L1_write_data), 
                
            .act_L1_buf_read_addr(act_L1_read_addr), 
            .act_L1_buf_read_en(act_L1_read_en)  , 
                
            .wei_L1_buf_read_addr(wei_L1_read_addr), 
            .wei_L1_buf_read_en(wei_L1_read_en),   
                
            .mac_en(mac_en), 
                
            .accum_done(result_done), 
                
            .wei_precision(wei_precision),
            .act_precision(act_precision),
                
        .xxx(xxx[`MAX_X_LOG-1:0]),
        .yyy(yyy[`MAX_Y_LOG-1:0]),
        .xx(xx[`MAX_X_LOG-1:0]),
        .yy(yy[`MAX_Y_LOG-1:0]),
        .bb(bb[`MAX_B_LOG-1:0]),
        .nn(nn[`MAX_N_LOG-1:0]),
        .ii(ii[`MAX_I_LOG-1:0]),
        .nnn(nnn[`MAX_N_LOG-1:0]),
        .iii(iii[`MAX_I_LOG-1:0]),
        .kkx(kkx[`MAX_KX_LOG-1:0]),
        .kky(kky[`MAX_KY_LOG-1:0]),
            
        .ACC_xxx(ACC_xxx[`MAX_X_LOG-1:0]),
        .ACC_yyy(ACC_yyy[`MAX_Y_LOG-1:0]),
        .ACC_xx(ACC_xx[`MAX_X_LOG-1:0]),
        .ACC_yy(ACC_yy[`MAX_Y_LOG-1:0]),
        .ACC_bb(ACC_bb[`MAX_B_LOG-1:0]),
        .ACC_nn(ACC_nn[`MAX_N_LOG-1:0]),
        .ACC_ii(ACC_ii[`MAX_I_LOG-1:0]),
        .ACC_nnn(ACC_nnn[`MAX_N_LOG-1:0]),
        .ACC_iii(ACC_iii[`MAX_I_LOG-1:0]),
        .ACC_kkx(ACC_kkx[`MAX_KX_LOG-1:0]),
        .ACC_kky(ACC_kky[`MAX_KY_LOG-1:0]),
            
        .pe_array_start(pe_all_start),
        .pe_array_ready(pe_all_ready),
        .pe_array_last(pe_all_last),
            
        .ACC_stalled(ACC_stalled),
            
        .jia_sys_jie(jia_sys_jie),
        .yi_sys_jie(yi_sys_jie),
            
        .ACCUM_stall(ACCUM_stall),
            
        .inter_pe_sparse_stall(inter_pe_sparse_stall)
        );
OUTPUT_MAPPING_PE omp(
        .clk(core_clk),
        .rst_n(rst_n), 
            
        .zi(zi),
        .zi_buf(zi_buf),
        
        .stride(stride), 
        .kx(fkx),
        .ky(fky),
        .x(x),
        .y(y), 
        .nc(nc), 
        .ic(ic), 
        .batch(batch),
        .padding_x(padding_x),
        .padding_y(padding_y),
        .OP_TYPE(OP_TYPE),
        .SYSTOLIC_OP(SYSTOLIC_OP),
                .int_inference(int_inference),
        .wei_precision(wei_precision),
        .act_precision(act_precision),
        .mult_done(mult_done),
        
        .tile_done(tile_done),
        .add_tree_ready(accum_en)
    );

PE_ARRAY pe_array(
            .clk(core_clk),
            .rst_n(rst_n),
            .en(pe_en),
            .int_inference(int_inference),
            .wei_precision(wei_precision),
            .act_precision(act_precision),
            
            .wei_mantissa(wei_mantissa),
            .act_mantissa(act_mantissa),
            .wei_exponent(wei_exponent),
            .act_exponent(act_exponent),
            .wei_regime(wei_regime),
            .act_regime(act_regime),
            
            .jia(jia),
            .yi(yi),
            .zi(zi),
            .valid(pe_valid),
            .ready(pe_ready),
            .last(pe_last),
            .start(pe_start),
            
            .pe_all_ready(pe_all_ready)
        );
ACCUM accum(
        .clk(core_clk),
        .rst_n(rst_n),
        .accum_en(accum_en),
            
        .stride(stride), 
        .fkx(fkx),
        .fky(fky),
        .x(x),
        .y(y), 
        .nc(nc), 
        .ic(ic), 
        .batch(batch),
        .padding_x(padding_x),
        .padding_y(padding_y),
        .psum_write_en(psum_write_en),
            .psum_read_en(psum_read_en),
            .psum_read_addr(psum_read_addr),
            .psum_write_addr(psum_write_addr),
            .psum_write_data(psum_write_data),
            
            .psum_read_data(psum_read_data),
            .zi_buf(zi_buf),
            
         .int_inference(int_inference),
        .wei_precision(wei_precision),
        .act_precision(act_precision),
            
            .out_buf_write_ready(out_buf_write_ready), 
            .out_buf_write_valid(out_buf_write_valid), 
            .out_buf_write_data(out_buf_write_data),
            .out_buf_write_addr(out_buf_write_addr), 
            
            .ACC_stalled(ACC_stalled),
            
            .accum_done(accum_done),
            
        .result_done(result_done)
); INTER_PE inter_pe(
.clk(core_clk),
        .rst_n(rst_n), 
        .jia_buf(jia_buf),
        .jia(jia),
        .yi_buf(yi_buf),
        .yi(yi),
        
        .xxx(xxx[`MAX_X_LOG-1:0]),
        .yyy(yyy[`MAX_Y_LOG-1:0]),
        .xx(xx[`MAX_X_LOG-1:0]),
        .yy(yy[`MAX_Y_LOG-1:0]),
        .bb(bb[`MAX_B_LOG-1:0]),
        .nn(nn[`MAX_N_LOG-1:0]),
        .ii(ii[`MAX_I_LOG-1:0]),
        .nnn(nnn[`MAX_N_LOG-1:0]),
        .iii(iii[`MAX_I_LOG-1:0]),
        .kkx(kkx[`MAX_KX_LOG-1:0]),
        .kky(kky[`MAX_KY_LOG-1:0]),
        
        .stride(stride), 
        .kx(fkx),
        .ky(fky),
        .x(x),
        .y(y), 
        .nc(nc), 
        .ic(ic), 
        .batch(batch),
        .padding_x(padding_x),
        .padding_y(padding_y),
        .OP_TYPE(OP_TYPE),
        .SYSTOLIC_OP(SYSTOLIC_OP),
        .int_inference(int_inference),
        .wei_precision(wei_precision),
        .act_precision(act_precision),
                
        .wei_sys_en(wei_L1_read_en), 
        .act_sys_en(act_L1_read_en), 
                
         .jia_sys_jie(jia_sys_jie),
        .yi_sys_jie(yi_sys_jie),
                
        .mac_en(mac_en), 
                
        .sparse_stall(inter_pe_sparse_stall),
                
        .mult_done(pe_all_ready),
        .pre_mult_done(pre_mult_done)
    );
wire [`MAX_ELEMENT_UNITS*`MAX_OUT_PRECISION-1:0] element_buf_data;
wire [5 : 0] element_buf_addr;
wire element_buf_data_ready;
wire [3:0] element_operation;
wire [5:0] output_precision;
wire [5:0] input_precision;
ELEMENT_UNIT element_unit(
            .clk(clk),
            .rst_n(rst_n),
            .output_precision(output_precision),
            .input_precision(input_precision),
                
            .out_buf_write_ready(out_buf_write_ready),
            .out_buf_write_valid(out_buf_write_valid),
            .out_buf_write_data(out_buf_write_data),
            .out_buf_write_addr(out_buf_write_addr), 
                
            .element_buf_data(element_buf_data),
            .element_buf_addr(element_buf_addr), 
            .element_buf_data_ready(element_buf_data_ready),
                
            .element_operation(element_operation)
        );
endmodule
