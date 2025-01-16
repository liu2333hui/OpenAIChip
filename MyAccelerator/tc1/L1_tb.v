module L1_level_tb();
reg ddr_clk;
reg core_clk;
reg rst_n;
wire [`WEI_BUF_DATA-1:0] jia_buf;
wire [`ACT_BUF_DATA-1:0] yi_buf;
wire [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi;
wire [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;
wire [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;
wire [`PSUM_BUF_DATA - 1:0] zi_buf;
reg [`PSUM_BUF_DATA - 1:0] psum_zi_buf;
reg [3:0] padding;
reg [`MAX_STRIDE_LOG-1:0] stride;
reg [`MAX_KX_LOG-1:0] fkx;
reg [`MAX_KY_LOG-1:0] fky;
reg [`MAX_X_LOG-1:0] x;
reg [`MAX_Y_LOG-1:0] y;
reg [`MAX_N_LOG-1:0] nc;
reg [`MAX_I_LOG-1:0] ic;
reg [`MAX_B_LOG-1:0] batch;
reg [15:0] loop_idx;
reg [15:0] cha_y;
reg [15:0] cha_x;
reg [`MAX_PADDING_X_LOG-1:0] padding_x;
reg [`MAX_PADDING_Y_LOG-1:0] padding_y;
reg [3:0] OP_TYPE;
reg [3:0] SYSTOLIC_OP;
reg int_inference;
reg [`REQUIRED_PES-1:0] pe_en;
reg [5:0] wei_precision;
reg [5:0] act_precision;
reg [5:0] wei_mantissa;
reg [5:0] act_mantissa;
reg [5:0] wei_exponent;
reg [5:0] act_exponent;
reg [5:0] wei_regime;
reg [5:0] act_regime;
reg [`REQUIRED_PES - 1:0] pe_valid;
wire [`REQUIRED_PES - 1:0] pe_ready;
reg [16-1:0] index_table [0:1024];
reg [31:0] psum_xx;
reg [31:0] psum_yy;
reg [31:0] psum_nn;
reg [31:0] psum_ii;
reg [31:0] psum_iii;
reg [31:0] psum_xxx;
reg [31:0] psum_yyy;
reg [31:0] psum_nnn;
reg [31:0] psum_kkx;
reg [31:0] psum_kky;
reg [31:0] psum_bb;
OUTPUT_MAPPING_PE omp(
        .clk(core_clk),
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
        .act_precision(act_precision)
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
            .ready(pe_ready)
        );
reg wei_write_en;
reg wei_read_en;
reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_read_addr;
reg  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_write_addr;
reg [`WEI_BUF_DATA  - 1 :0] wei_write_data;
WEI_BUF wei_buf(
            .rst_n(rst_n),
            .read_clk(core_clk),
            .write_clk(ddr_clk),
            .read_en(wei_read_en),
            .read_addr(wei_read_addr),
            .read_data(jia_buf),
            .write_en(wei_write_en),
            .write_addr(wei_write_addr),
            .write_data(wei_write_data)
        );
reg act_write_en;
reg act_read_en;
reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_read_addr;
reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] act_write_addr;
reg [ `ACT_BUF_DATA  - 1 :0] act_write_data;
ACT_BUF act_buf(
            .rst_n(rst_n),
            .read_clk(core_clk),
            .write_clk(ddr_clk),
            .read_en(act_read_en),
            .read_addr(act_read_addr),
            .read_data(yi_buf),
            .write_en(act_write_en),
            .write_addr(act_write_addr),
            .write_data(act_write_data)
        );
reg [31:0] loop_cnt;
reg [31:0] acc_state;
reg psum_write_en;
reg psum_read_en;
reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;
reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;
reg [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;
reg [ `PSUM_BUF_DATA - 1 :0] psum_read_data;
reg  [ `PSUM_BUF_DATA - 1 : 0] psum_acc_data;
wire accum_en;
assign accum_en = |pe_ready ;
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
        .act_precision(act_precision)
        ); PSUM_BUF psum_buf(
            .rst_n(rst_n),
            .read_clk(~core_clk),
            .write_clk(core_clk),
            .read_en(psum_read_en),
            .read_addr(psum_read_addr),
            .read_data(psum_read_data),
            .write_en(psum_write_en),
            .write_addr(psum_write_addr),
            .write_data(psum_write_data)
);
`define CORE_CLK 10
`define DDR_CLK 40
initial begin
    core_clk = 1'b0;
    forever begin
    #(`CORE_CLK/2); core_clk = ~core_clk;
    end
    end
initial begin
    ddr_clk = 1'b0;
    forever begin
    #(`DDR_CLK/2); ddr_clk = ~ddr_clk;
    end
    end
initial begin
$dumpfile("tc.vcd");
$dumpvars(0, L1_level_tb);
end;
INTER_PE inter_pe(
.clk(core_clk),
        .jia_buf(jia_buf),
        .jia(jia),
        .yi_buf(yi_buf),
        .yi(yi),
        
        .xxx(psum_xxx[`MAX_X_LOG-1:0]),
        .yyy(psum_yyy[`MAX_Y_LOG-1:0]),
        .xx(psum_xx[`MAX_X_LOG-1:0]),
        .yy(psum_yy[`MAX_Y_LOG-1:0]),
        .bb(psum_bb[`MAX_B_LOG-1:0]),
        .nn(psum_nn[`MAX_N_LOG-1:0]),
        .ii(psum_ii[`MAX_I_LOG-1:0]),
        .nnn(psum_nnn[`MAX_N_LOG-1:0]),
        .iii(psum_iii[`MAX_I_LOG-1:0]),
        .kkx(psum_kkx[`MAX_KX_LOG-1:0]),
        .kky(psum_kky[`MAX_KY_LOG-1:0]),
        
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
        .act_precision(act_precision));
initial begin
$readmemh("MyAccelerator/tc1/weights.txt", wei_buf.mem);
$readmemh("MyAccelerator/tc1/activation.txt", act_buf.mem);
end
initial begin
rst_n = 0;
loop_cnt = 0;
#(`CORE_CLK*2);
rst_n = 1;
#(`CORE_CLK*0);
wei_precision = 16;
act_precision = 16;
stride = 1;
fkx = 2;
fky = 2;
x = 8;
y = 8;
ic = 8;
nc = 8;
batch = 1;
padding_x = 0;
padding_y = 0;
loop_idx = 0;
    for (integer bb = 0; bb < batch; bb += 1)begin
        for(integer nn = 0; nn < nc; nn += 4)begin
            for(integer ii = 0; ii < ic; ii += 4)begin
                for (integer kky = 0; kky < fky; kky += 1)begin
                    for (integer kkx = 0; kkx < fkx; kkx += 1)begin
for(integer xx = 0; xx < x - fkx + 1; xx += 1)begin
                            for(integer yy = 0; yy < y - fky + 1; yy += 1)begin
psum_bb = bb;
psum_nn = nn;
psum_ii = ii;
psum_kky = kky;
psum_kkx = kkx;
psum_xx = xx;
psum_yy = yy;
if(nn >= nc) begin
end
else if(ii >= ic) begin
end
else if(xx >= ((x + padding_x*2 - fkx + 1) / stride  )) begin
end
else if(yy >= ((y + padding_y*2 - fky + 1) / stride  )) begin
end
else begin
$display("	nn	ii	xx	yy	kkx	kky	bb");
$display(nn, ii, xx, yy, kkx, kky, bb);
$display(( (kky >= 1) & (yy +1< ((y + padding_y*2 - fky + 1) / stride  ))),( (kkx >= 1)   &  (xx +1< ((x + padding_x*2 - fkx + 1) / stride  ) )),(xx > 0 & yy > 0 & (((kkx >= 1)   &  (xx +1< ((x + padding_x*2 - fkx + 1) / stride  ) ) ) | (( kky >= 1) & (yy +1< ((y + padding_y*2 - fky + 1) / stride  )) ) ) ),nn>0);
if (( (kky >= 1) & (yy +1< ((y + padding_y*2 - fky + 1) / stride  )))|( (kkx >= 1)   &  (xx +1< ((x + padding_x*2 - fkx + 1) / stride  ) ))|(xx > 0 & yy > 0 & (((kkx >= 1)   &  (xx +1< ((x + padding_x*2 - fkx + 1) / stride  ) ) ) | (( kky >= 1) & (yy +1< ((y + padding_y*2 - fky + 1) / stride  )) ) ) )|nn>0) begin
   $display("REUSE", (bb)*ic*x*y + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy));
   index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] = index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)];
   act_read_addr = index_table[(bb)*ic*x*y + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] ;
end else begin
   index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)] = loop_idx;
   act_read_addr = loop_idx;
loop_idx = loop_idx + 1;
end
   $display(index_table[(bb)*ic*(x+fkx)*(y+fky) + (ii)*(y+fky)*(x+fkx)+(kkx+xx)*(y+fky) + (kky+yy)]);
wei_read_addr = ((((0*nc/4+  nn/4)*ic/4+  ii/4)*fky/1+  kky/1)*fkx/1+  kkx/1);
wei_read_en = 1;
act_read_en = 1;
int_inference = 1;
pe_en = {`REQUIRED_PES {1'b1}};
pe_valid = {`REQUIRED_PES {1'b1}};
$display("wei_read_addr = ", wei_read_addr);
$display("%h",wei_buf.mem[wei_read_addr]);
$display("act_read_addr = ", act_read_addr);
$display("%h",act_buf.mem[act_read_addr]);
$display(loop_idx);
#(`CORE_CLK);
loop_cnt = loop_cnt + 1;
end
end
end
end
end
end
end
end
#(`CORE_CLK);
#(`CORE_CLK);
#(`CORE_CLK);
#(`CORE_CLK);
#(`CORE_CLK);
$finish;
end
endmodule
