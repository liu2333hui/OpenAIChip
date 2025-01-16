module L1_level_tb();
reg ddr_clk;
reg core_clk;
reg rst_n;
wire [`WEI_BUF_DATA-1:0] jia_buf;
wire [`ACT_BUF_DATA-1:0] yi_buf;
wire [`MAX_PSUM_PRECISION*`REQUIRED_PES-1:0] zi;
wire [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia;
wire [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi;
wire [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi_buf;
reg [3:0] padding;
reg [`MAX_STRIDE_LOG-1:0] stride;
reg [`MAX_KX_LOG-1:0] fkx;
reg [`MAX_KY_LOG-1:0] fky;
reg [`MAX_X_LOG-1:0] x;
reg [`MAX_Y_LOG-1:0] y;
reg [`MAX_N_LOG-1:0] nc;
reg [`MAX_I_LOG-1:0] ic;
reg [`MAX_B_LOG-1:0] batch;
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

reg [15:0] cha_y;
reg [15:0] cha_x;

reg [`REQUIRED_PES - 1:0] pe_valid;
wire [`REQUIRED_PES - 1:0] pe_ready;
reg wei_write_en;
reg wei_read_en;
reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_read_addr;
reg  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_write_addr;
reg [`WEI_BUF_DATA  - 1 :0] wei_write_data;
WEI_BUF wei_buf(
            .read_clk(core_clk),
            .write_clk(ddr_clk),
            .read_en(write_read_en),
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
            .read_clk(core_clk),
            .write_clk(ddr_clk),
            .read_en(act_read_en),
            .read_addr(act_read_addr),
            .read_data(yi_buf),
            .write_en(act_write_en),
            .write_addr(act_write_addr),
            .write_data(act_write_data)
        );
initial begin
$readmemh("weights.txt", wei_buf.mem);
$readmemh("activation.txt", act_buf.mem);
end
`define CORE_CLK 40
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
cha_y = 0;
$dumpfile("tc.vcd");
$dumpvars(0, L1_level_tb);
rst_n = 0;
#(`CORE_CLK*2);
rst_n = 1;
wei_precision = 8;
act_precision = 8;
stride = 1;
fkx = 3;
fky = 3;
x = 6;
y = 6;
ic = 3;
nc = 1;
batch = 1;
padding_x = 0;
padding_y = 0;
$display("	nn	ii	xx	yy	kkx	kky	bb");
    for (integer bb = 0; bb < batch; bb += 1)begin
        for(integer nn = 0; nn < nc; nn += 16)begin
for(integer xx = 0; xx < ((x + padding_x*2 - fkx + 1) / stride  ); xx += 2)begin
                for(integer yy = 0; yy < ((y + padding_y*2 - fky + 1) / stride  ); yy += 2)begin

                
                    for (integer kkx = 0; kkx < fkx; kkx += 1)begin
                        for (integer kky = 0; kky < fky; kky += 1)begin
                            for(integer ii = 0; ii < ic; ii += 3)begin
if(nn >= nc) begin
end
else if(ii >= ic) begin
end
else if(xx >= ((x + padding_x*2 - fkx + 1) / stride  )) begin
end
else if(yy >= ((y + padding_y*2 - fky + 1) / stride  )) begin
end
else begin



	  if(yy > 0)begin
	          if(kky == 0) begin
                    	cha_y = (fkx*fky - 2); //-TX
	           end                   
      else cha_y = (1 + kkx*1);
                  end else begin
	         cha_y = 0;
                 end
                  //   cha_y = ((yy > 0) & (kky == 0)) ? (fkx*fky - 2): 0;

	if(xx > 0 ) begin
                       if(kkx == 0) begin
                               if(kky == 0) begin
	           	    cha_x =  (fkx*y +  fkx*((y + padding_y*2 - fky + 1) / stride  )/2   -  2*y    ); //TODOS
		end else begin
		    cha_x =  (fkx*y +  fkx*((y + padding_y*2 - fky + 1) / stride  )/2  + yy/2*2   -  2*y    ); //TODOS
		end
                        end else begin
		if(kky == 0) begin
		    cha_x = fkx*((y + padding_y*2 - fky + 1) / stride  )/2  ; //-TY
                                end else begin
		    cha_x = fkx*((y + padding_y*2 - fky + 1) / stride  )/2  + yy/2*2; //-TY
                                 end
                         end
                end else begin
	      cha_x = 0;
                end

$display(nn, ii, xx, yy, kkx, kky, bb);
$display((((((((0*batch/1+  bb/1)*nc/16+  nn/16)*((x + padding_x*2 - fkx + 1) / stride  )/2+  xx/2)*((y + padding_y*2 - fky + 1) / stride  )/2+  yy/2)*fkx/1+  kkx/1)*fky/1+  kky/1)*ic/3+  ii/3)
	- 0 );
$display(((((0*nc/16+  nn/16)*fkx/1+  kkx/1)*fky/1+  kky/1)*ic/3+  ii/3));
$display(((((((0*batch/1+  bb/1)*((x + padding_x*2 - fkx + 1) / stride  )/2+  xx/2)*((y + padding_y*2 - fky + 1) / stride  )/2+  yy/2)*fkx/1+  kkx/1)*fky/1+  kky/1)*ic/3+  ii/3)
	- cha_y - cha_x );

//$display("%h",act_buf.mem[((((((0*batch/1+  bb/1)*((x + padding_x*2 - fkx + 1) / stride  )/2+  xx/2)*((y + padding_y*2 - fky + 1) / stride  )/2+  yy/2)*fkx/1+  kkx/1)*fky/1+  kky/1)*ic/3+  ii/3)
	//-cha_y ]);
//$display("%h",wei_buf.mem[((((0*nc/16+  nn/16)*fkx/1+  kkx/1)*fky/1+  kky/1)*ic/3+  ii/3)]);
end
end
end
end
end
end
end
end
$finish;
end
endmodule
