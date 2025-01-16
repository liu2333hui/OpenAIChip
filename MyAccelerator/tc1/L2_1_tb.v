module L2_level_tb();

            reg ddr_clk;
            reg core_clk;
            reg rst_n;
                
            wire wei_buf_read_ready; 
            reg  wei_buf_read_valid; 
            reg [`WEI_BUF_DATA*1-1:0] wei_buf_read_data;
            wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_buf_read_addr; 
                
            wire act_buf_read_ready; 
            reg  act_buf_read_valid; 
            reg [`ACT_BUF_DATA - 1:0] act_buf_read_data;
            wire [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_buf_read_addr; 
                
            reg [`MAX_PADDING_X_LOG-1:0] padding_x;
            reg [`MAX_PADDING_Y_LOG-1:0] padding_y;
            reg [`MAX_STRIDE_LOG-1:0] stride;
            reg [`MAX_KX_LOG-1:0] fkx;
            reg [`MAX_KY_LOG-1:0] fky;
            reg  [`MAX_X_LOG-1:0] x;
            reg  [`MAX_Y_LOG-1:0] y;
            reg  [`MAX_N_LOG-1:0] nc;
            reg  [`MAX_I_LOG-1:0] ic;
            reg  [`MAX_B_LOG-1:0] batch;
                
            reg int_inference;
            reg [5:0] wei_precision;
            reg [5:0] act_precision;
            reg [5:0] wei_mantissa;
            reg [5:0] act_mantissa;
            reg [5:0] wei_exponent;
            reg [5:0] act_exponent;
            reg [5:0] wei_regime;
            reg [5:0] act_regime;
                
            wire  out_buf_write_ready; 
            reg out_buf_write_valid;
            wire [`PSUM_BUF_DATA-1:0] out_buf_write_data;
            wire [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr; 
reg addr_cnt_en;
wire operation_done;
reg [`WEI_BUF_DATA*1  - 1: 0] L2_WEI [0:`L2_WEI_BUF_ROWS];
reg [`ACT_BUF_DATA*1  - 1: 0] L2_ACT [0:`L2_ACT_BUF_ROWS];
wire [`WEI_BUF_DATA  - 1: 0] wei0;
assign wei0 = L2_WEI[0];
wire [`WEI_BUF_DATA  - 1: 0] wei1;
assign wei1 = L2_WEI[1];
wire [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_addr;
assign wei_L2_buf_addr = wei_buf_read_addr;
always@(negedge core_clk) begin 
               if(wei_buf_read_ready)begin
                    wei_buf_read_data <=  L2_WEI[wei_L2_buf_addr]; 
                    wei_buf_read_valid <= #(0) 1;
               end 
               else begin
                    wei_buf_read_valid <= 0;
               end
          end
always@(negedge core_clk) begin 
               if(act_buf_read_ready)begin
                    act_buf_read_data <= #(0) L2_ACT[act_buf_read_addr]; 
                    act_buf_read_valid = #(0) 1;
               end 
               else begin
                    act_buf_read_valid = 0;
               end
          end
wire [`WEI_BUF_DATA-1:0] jia_buf;
wire [`ACT_BUF_DATA-1:0] yi_buf;
wire wei_L1_write_en;
wire wei_L1_read_en;
wire [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_read_addr;
wire  [`WEI_BUF_ROWS_LOG2  - 1 :0] wei_L1_write_addr;
wire [`WEI_BUF_DATA  - 1 :0] wei_L1_write_data;
wire act_L1_write_en;
wire act_L1_read_en;
wire [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_read_addr;
wire  [`ACT_BUF_ROWS_LOG2  - 1 :0] act_L1_write_addr;
wire [`ACT_BUF_DATA  - 1 :0] act_L1_write_data;
wire psum_write_en;
wire psum_read_en;
wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr;
wire [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr;
wire [ `PSUM_BUF_DATA  - 1 :0] psum_write_data;
wire [ `PSUM_BUF_DATA - 1 :0] psum_read_data;
WEI_BUF wei_buf(
            .rst_n(rst_n),
            .read_clk(core_clk),
            .write_clk(core_clk),
            .read_en(wei_L1_read_en),
            .read_addr(wei_L1_read_addr),
            .read_data(jia_buf),
            .write_en(wei_L1_write_en),
            .write_addr(wei_L1_write_addr),
            .write_data(wei_L1_write_data)
        );
ACT_BUF act_buf(
            .rst_n(rst_n),
            .read_clk(core_clk),
            .write_clk(core_clk),
            .read_en(act_L1_read_en),
            .read_addr(act_L1_read_addr),
            .read_data(yi_buf),
            .write_en(act_L1_write_en),
            .write_addr(act_L1_write_addr),
            .write_data(act_L1_write_data)
        );
PSUM_BUF psum_buf(
            .rst_n(rst_n),
            .read_clk(~core_clk),
            .write_clk(~core_clk),
            .read_en(psum_read_en),
            .read_addr(psum_read_addr),
            .read_data(psum_read_data),
            .write_en(psum_write_en),
            .write_addr(psum_write_addr),
            .write_data(psum_write_data)
);
DLA_CORE dla_core( 
            .ddr_clk(ddr_clk),
            .core_clk(core_clk),
            .rst_n(rst_n),
                
            .addr_cnt_en(addr_cnt_en),
            .result_done(operation_done),
                
            .wei_buf_read_ready(wei_buf_read_ready), 
            .  wei_buf_read_valid(wei_buf_read_valid), 
            . wei_buf_read_data(wei_buf_read_data),
            .wei_buf_read_addr(wei_buf_read_addr), 
                
            . act_buf_read_ready(act_buf_read_ready), 
            .  act_buf_read_valid(act_buf_read_valid), 
            .act_buf_read_data(act_buf_read_data),
            .act_buf_read_addr(act_buf_read_addr), 
                
            .padding_x(padding_x),
            .padding_y(padding_y),
            .stride(stride),
            .fkx(fkx),
            .fky(fky),
            .x(x),
            .y(y),
            .nc(nc),
            .ic(ic),
            .batch(batch),
                
            .int_inference(int_inference),
            .wei_precision(wei_precision),
            .act_precision(act_precision),
            .wei_mantissa(wei_mantissa),
            .act_mantissa(act_mantissa),
            .wei_exponent(wei_exponent),
            .act_exponent(act_exponent),
            .wei_regime(wei_regime),
            .act_regime(act_regime),
                
            .out_buf_write_ready(out_buf_write_ready), 
            .out_buf_write_valid(out_buf_write_valid), 
            .out_buf_write_data(out_buf_write_data),
            .out_buf_write_addr(out_buf_write_addr) ,
.jia_buf(jia_buf),
            .wei_L1_read_en(wei_L1_read_en),
            .wei_L1_read_addr(wei_L1_read_addr),
            .wei_L1_write_en(wei_L1_write_en),
            .wei_L1_write_addr(wei_L1_write_addr),
            .wei_L1_write_data(wei_L1_write_data),
            .act_L1_read_en(act_L1_read_en),
            .act_L1_read_addr(act_L1_read_addr),
            .yi_buf(yi_buf),
            .act_L1_write_en(act_L1_write_en),
            .act_L1_write_addr(act_L1_write_addr),
            .act_L1_write_data(act_L1_write_data),
            .psum_read_en(psum_read_en),
            .psum_read_addr(psum_read_addr),
            .psum_read_data(psum_read_data),
            .psum_write_en(psum_write_en),
            .psum_write_addr(psum_write_addr),
            .psum_write_data(psum_write_data)
);
initial begin
$readmemh("MyAccelerator/tc1/weights.txt", L2_WEI);
$readmemh("MyAccelerator/tc1/activation.txt", L2_ACT);
end
`define CORE_CLK 10
`define DDR_CLK 40
initial begin
    core_clk = 1'b1;
    forever begin
        #(`CORE_CLK/2); core_clk = ~core_clk;
    end
    end
initial begin
    ddr_clk = 1'b1;
    forever begin
    #(`DDR_CLK/2); ddr_clk = ~ddr_clk;
    end
    end
initial begin
$dumpfile("MyAccelerator/tc1/l2_tc.vcd");
$dumpvars(0, L2_level_tb);
end;
initial begin
                #(`CORE_CLK*262144.0);
                $finish;
          end
initial begin
        rst_n = 0;
        addr_cnt_en = 0;
            
        #(`CORE_CLK*2);
        rst_n = 1;
            
            
        #(`CORE_CLK*0);
            
        wei_precision = 16;
        act_precision = 16;
        int_inference = 1;
            
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
            
        addr_cnt_en = 1;
            
        @(posedge operation_done)
        #(2*`CORE_CLK);
        $finish;
          end
endmodule