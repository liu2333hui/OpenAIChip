module PE_ARRAY(
            input clk,
            input rst_n,
            input [16-1:0] en,
            input int_inference,
            input [5:0] wei_precision,
            input [5:0] act_precision,
            
            input [5:0] wei_mantissa,
            input [5:0] act_mantissa,
            input [5:0] wei_exponent,
            input [5:0] act_exponent,
            input [5:0] wei_regime,
            input [5:0] act_regime,
input  [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,
              input  [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,
              output [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi,
input [16-1:0] valid,
            output [16-1:0] ready,
            output [16-1:0] last,
            output [16-1:0] start,
            
            input pe_all_ready
        );
wire [`MAX_PSUM_PRECISION_INT*`REQUIRED_PES-1:0] zi_int;
wire [`MAX_PSUM_PRECISION_FP*`REQUIRED_PES-1:0] zi_fp;
wire [16-1:0] ready_int;
wire [16-1:0] ready_fp;
wire [16-1:0] last_int;
wire [16-1:0] last_fp;
wire [16-1:0] start_int;
wire [16-1:0] start_fp;
//Binding for input PES
wire [`REQUIRED_PES-1:0] zero_gate;
wire [`REQUIRED_PES-1:0] zero_gate_int;
wire [`REQUIRED_PES-1:0] zero_gate_fp;

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_0 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_0 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_0 ;
assign yi_0 = yi[`MAX_ACT_PRECISION_INT*(0+1) -1:`MAX_ACT_PRECISION_INT*0];
                    assign jia_0 =jia[`MAX_WEI_PRECISION_INT*(0+1) -1:`MAX_WEI_PRECISION_INT*0];
                    assign zi_0 =zi_int[`MAX_PSUM_PRECISION_INT*(0+1) -1:`MAX_PSUM_PRECISION_INT*0];
                    //wire zero_gate_int0;
assign zero_gate_int[0] = 1'b0;
MULT_INT mult_0 (.clk(clk),.rst_n(rst_n),
                        .en(en[0] & int_inference   & ~zero_gate_int[0]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_0),.yi(yi_0),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(0+1) -1:`MAX_PSUM_PRECISION_INT*0]),
                        .valid(valid[0]),.ready(ready_int[0]),.last(last_int[0]), .start(start_int[0]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_1 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_1 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_1 ;
assign yi_1 = yi[`MAX_ACT_PRECISION_INT*(1+1) -1:`MAX_ACT_PRECISION_INT*1];
                    assign jia_1 =jia[`MAX_WEI_PRECISION_INT*(1+1) -1:`MAX_WEI_PRECISION_INT*1];
                    assign zi_1 =zi_int[`MAX_PSUM_PRECISION_INT*(1+1) -1:`MAX_PSUM_PRECISION_INT*1];
                    //wire zero_gate_int1;
assign zero_gate_int[1] = 1'b0;
MULT_INT mult_1 (.clk(clk),.rst_n(rst_n),
                        .en(en[1] & int_inference   & ~zero_gate_int[1]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_1),.yi(yi_1),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(1+1) -1:`MAX_PSUM_PRECISION_INT*1]),
                        .valid(valid[1]),.ready(ready_int[1]),.last(last_int[1]), .start(start_int[1]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_2 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_2 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_2 ;
assign yi_2 = yi[`MAX_ACT_PRECISION_INT*(2+1) -1:`MAX_ACT_PRECISION_INT*2];
                    assign jia_2 =jia[`MAX_WEI_PRECISION_INT*(2+1) -1:`MAX_WEI_PRECISION_INT*2];
                    assign zi_2 =zi_int[`MAX_PSUM_PRECISION_INT*(2+1) -1:`MAX_PSUM_PRECISION_INT*2];
                    //wire zero_gate_int2;
assign zero_gate_int[2] = 1'b0;
MULT_INT mult_2 (.clk(clk),.rst_n(rst_n),
                        .en(en[2] & int_inference   & ~zero_gate_int[2]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_2),.yi(yi_2),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(2+1) -1:`MAX_PSUM_PRECISION_INT*2]),
                        .valid(valid[2]),.ready(ready_int[2]),.last(last_int[2]), .start(start_int[2]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_3 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_3 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_3 ;
assign yi_3 = yi[`MAX_ACT_PRECISION_INT*(3+1) -1:`MAX_ACT_PRECISION_INT*3];
                    assign jia_3 =jia[`MAX_WEI_PRECISION_INT*(3+1) -1:`MAX_WEI_PRECISION_INT*3];
                    assign zi_3 =zi_int[`MAX_PSUM_PRECISION_INT*(3+1) -1:`MAX_PSUM_PRECISION_INT*3];
                    //wire zero_gate_int3;
assign zero_gate_int[3] = 1'b0;
MULT_INT mult_3 (.clk(clk),.rst_n(rst_n),
                        .en(en[3] & int_inference   & ~zero_gate_int[3]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_3),.yi(yi_3),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(3+1) -1:`MAX_PSUM_PRECISION_INT*3]),
                        .valid(valid[3]),.ready(ready_int[3]),.last(last_int[3]), .start(start_int[3]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_4 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_4 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_4 ;
assign yi_4 = yi[`MAX_ACT_PRECISION_INT*(4+1) -1:`MAX_ACT_PRECISION_INT*4];
                    assign jia_4 =jia[`MAX_WEI_PRECISION_INT*(4+1) -1:`MAX_WEI_PRECISION_INT*4];
                    assign zi_4 =zi_int[`MAX_PSUM_PRECISION_INT*(4+1) -1:`MAX_PSUM_PRECISION_INT*4];
                    //wire zero_gate_int4;
assign zero_gate_int[4] = 1'b0;
MULT_INT mult_4 (.clk(clk),.rst_n(rst_n),
                        .en(en[4] & int_inference   & ~zero_gate_int[4]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_4),.yi(yi_4),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(4+1) -1:`MAX_PSUM_PRECISION_INT*4]),
                        .valid(valid[4]),.ready(ready_int[4]),.last(last_int[4]), .start(start_int[4]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_5 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_5 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_5 ;
assign yi_5 = yi[`MAX_ACT_PRECISION_INT*(5+1) -1:`MAX_ACT_PRECISION_INT*5];
                    assign jia_5 =jia[`MAX_WEI_PRECISION_INT*(5+1) -1:`MAX_WEI_PRECISION_INT*5];
                    assign zi_5 =zi_int[`MAX_PSUM_PRECISION_INT*(5+1) -1:`MAX_PSUM_PRECISION_INT*5];
                    //wire zero_gate_int5;
assign zero_gate_int[5] = 1'b0;
MULT_INT mult_5 (.clk(clk),.rst_n(rst_n),
                        .en(en[5] & int_inference   & ~zero_gate_int[5]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_5),.yi(yi_5),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(5+1) -1:`MAX_PSUM_PRECISION_INT*5]),
                        .valid(valid[5]),.ready(ready_int[5]),.last(last_int[5]), .start(start_int[5]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_6 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_6 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_6 ;
assign yi_6 = yi[`MAX_ACT_PRECISION_INT*(6+1) -1:`MAX_ACT_PRECISION_INT*6];
                    assign jia_6 =jia[`MAX_WEI_PRECISION_INT*(6+1) -1:`MAX_WEI_PRECISION_INT*6];
                    assign zi_6 =zi_int[`MAX_PSUM_PRECISION_INT*(6+1) -1:`MAX_PSUM_PRECISION_INT*6];
                    //wire zero_gate_int6;
assign zero_gate_int[6] = 1'b0;
MULT_INT mult_6 (.clk(clk),.rst_n(rst_n),
                        .en(en[6] & int_inference   & ~zero_gate_int[6]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_6),.yi(yi_6),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(6+1) -1:`MAX_PSUM_PRECISION_INT*6]),
                        .valid(valid[6]),.ready(ready_int[6]),.last(last_int[6]), .start(start_int[6]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_7 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_7 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_7 ;
assign yi_7 = yi[`MAX_ACT_PRECISION_INT*(7+1) -1:`MAX_ACT_PRECISION_INT*7];
                    assign jia_7 =jia[`MAX_WEI_PRECISION_INT*(7+1) -1:`MAX_WEI_PRECISION_INT*7];
                    assign zi_7 =zi_int[`MAX_PSUM_PRECISION_INT*(7+1) -1:`MAX_PSUM_PRECISION_INT*7];
                    //wire zero_gate_int7;
assign zero_gate_int[7] = 1'b0;
MULT_INT mult_7 (.clk(clk),.rst_n(rst_n),
                        .en(en[7] & int_inference   & ~zero_gate_int[7]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_7),.yi(yi_7),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(7+1) -1:`MAX_PSUM_PRECISION_INT*7]),
                        .valid(valid[7]),.ready(ready_int[7]),.last(last_int[7]), .start(start_int[7]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_8 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_8 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_8 ;
assign yi_8 = yi[`MAX_ACT_PRECISION_INT*(8+1) -1:`MAX_ACT_PRECISION_INT*8];
                    assign jia_8 =jia[`MAX_WEI_PRECISION_INT*(8+1) -1:`MAX_WEI_PRECISION_INT*8];
                    assign zi_8 =zi_int[`MAX_PSUM_PRECISION_INT*(8+1) -1:`MAX_PSUM_PRECISION_INT*8];
                    //wire zero_gate_int8;
assign zero_gate_int[8] = 1'b0;
MULT_INT mult_8 (.clk(clk),.rst_n(rst_n),
                        .en(en[8] & int_inference   & ~zero_gate_int[8]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_8),.yi(yi_8),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(8+1) -1:`MAX_PSUM_PRECISION_INT*8]),
                        .valid(valid[8]),.ready(ready_int[8]),.last(last_int[8]), .start(start_int[8]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_9 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_9 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_9 ;
assign yi_9 = yi[`MAX_ACT_PRECISION_INT*(9+1) -1:`MAX_ACT_PRECISION_INT*9];
                    assign jia_9 =jia[`MAX_WEI_PRECISION_INT*(9+1) -1:`MAX_WEI_PRECISION_INT*9];
                    assign zi_9 =zi_int[`MAX_PSUM_PRECISION_INT*(9+1) -1:`MAX_PSUM_PRECISION_INT*9];
                    //wire zero_gate_int9;
assign zero_gate_int[9] = 1'b0;
MULT_INT mult_9 (.clk(clk),.rst_n(rst_n),
                        .en(en[9] & int_inference   & ~zero_gate_int[9]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_9),.yi(yi_9),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(9+1) -1:`MAX_PSUM_PRECISION_INT*9]),
                        .valid(valid[9]),.ready(ready_int[9]),.last(last_int[9]), .start(start_int[9]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_10 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_10 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_10 ;
assign yi_10 = yi[`MAX_ACT_PRECISION_INT*(10+1) -1:`MAX_ACT_PRECISION_INT*10];
                    assign jia_10 =jia[`MAX_WEI_PRECISION_INT*(10+1) -1:`MAX_WEI_PRECISION_INT*10];
                    assign zi_10 =zi_int[`MAX_PSUM_PRECISION_INT*(10+1) -1:`MAX_PSUM_PRECISION_INT*10];
                    //wire zero_gate_int10;
assign zero_gate_int[10] = 1'b0;
MULT_INT mult_10 (.clk(clk),.rst_n(rst_n),
                        .en(en[10] & int_inference   & ~zero_gate_int[10]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_10),.yi(yi_10),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(10+1) -1:`MAX_PSUM_PRECISION_INT*10]),
                        .valid(valid[10]),.ready(ready_int[10]),.last(last_int[10]), .start(start_int[10]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_11 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_11 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_11 ;
assign yi_11 = yi[`MAX_ACT_PRECISION_INT*(11+1) -1:`MAX_ACT_PRECISION_INT*11];
                    assign jia_11 =jia[`MAX_WEI_PRECISION_INT*(11+1) -1:`MAX_WEI_PRECISION_INT*11];
                    assign zi_11 =zi_int[`MAX_PSUM_PRECISION_INT*(11+1) -1:`MAX_PSUM_PRECISION_INT*11];
                    //wire zero_gate_int11;
assign zero_gate_int[11] = 1'b0;
MULT_INT mult_11 (.clk(clk),.rst_n(rst_n),
                        .en(en[11] & int_inference   & ~zero_gate_int[11]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_11),.yi(yi_11),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(11+1) -1:`MAX_PSUM_PRECISION_INT*11]),
                        .valid(valid[11]),.ready(ready_int[11]),.last(last_int[11]), .start(start_int[11]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_12 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_12 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_12 ;
assign yi_12 = yi[`MAX_ACT_PRECISION_INT*(12+1) -1:`MAX_ACT_PRECISION_INT*12];
                    assign jia_12 =jia[`MAX_WEI_PRECISION_INT*(12+1) -1:`MAX_WEI_PRECISION_INT*12];
                    assign zi_12 =zi_int[`MAX_PSUM_PRECISION_INT*(12+1) -1:`MAX_PSUM_PRECISION_INT*12];
                    //wire zero_gate_int12;
assign zero_gate_int[12] = 1'b0;
MULT_INT mult_12 (.clk(clk),.rst_n(rst_n),
                        .en(en[12] & int_inference   & ~zero_gate_int[12]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_12),.yi(yi_12),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(12+1) -1:`MAX_PSUM_PRECISION_INT*12]),
                        .valid(valid[12]),.ready(ready_int[12]),.last(last_int[12]), .start(start_int[12]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_13 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_13 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_13 ;
assign yi_13 = yi[`MAX_ACT_PRECISION_INT*(13+1) -1:`MAX_ACT_PRECISION_INT*13];
                    assign jia_13 =jia[`MAX_WEI_PRECISION_INT*(13+1) -1:`MAX_WEI_PRECISION_INT*13];
                    assign zi_13 =zi_int[`MAX_PSUM_PRECISION_INT*(13+1) -1:`MAX_PSUM_PRECISION_INT*13];
                    //wire zero_gate_int13;
assign zero_gate_int[13] = 1'b0;
MULT_INT mult_13 (.clk(clk),.rst_n(rst_n),
                        .en(en[13] & int_inference   & ~zero_gate_int[13]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_13),.yi(yi_13),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(13+1) -1:`MAX_PSUM_PRECISION_INT*13]),
                        .valid(valid[13]),.ready(ready_int[13]),.last(last_int[13]), .start(start_int[13]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_14 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_14 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_14 ;
assign yi_14 = yi[`MAX_ACT_PRECISION_INT*(14+1) -1:`MAX_ACT_PRECISION_INT*14];
                    assign jia_14 =jia[`MAX_WEI_PRECISION_INT*(14+1) -1:`MAX_WEI_PRECISION_INT*14];
                    assign zi_14 =zi_int[`MAX_PSUM_PRECISION_INT*(14+1) -1:`MAX_PSUM_PRECISION_INT*14];
                    //wire zero_gate_int14;
assign zero_gate_int[14] = 1'b0;
MULT_INT mult_14 (.clk(clk),.rst_n(rst_n),
                        .en(en[14] & int_inference   & ~zero_gate_int[14]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_14),.yi(yi_14),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(14+1) -1:`MAX_PSUM_PRECISION_INT*14]),
                        .valid(valid[14]),.ready(ready_int[14]),.last(last_int[14]), .start(start_int[14]),
                        .pe_all_ready(pe_all_ready));

                wire [`MAX_PSUM_PRECISION_INT-1:0] zi_15 ;
                wire [`MAX_ACT_PRECISION_INT-1:0]  yi_15 ;
                wire [`MAX_WEI_PRECISION_INT-1:0]  jia_15 ;
assign yi_15 = yi[`MAX_ACT_PRECISION_INT*(15+1) -1:`MAX_ACT_PRECISION_INT*15];
                    assign jia_15 =jia[`MAX_WEI_PRECISION_INT*(15+1) -1:`MAX_WEI_PRECISION_INT*15];
                    assign zi_15 =zi_int[`MAX_PSUM_PRECISION_INT*(15+1) -1:`MAX_PSUM_PRECISION_INT*15];
                    //wire zero_gate_int15;
assign zero_gate_int[15] = 1'b0;
MULT_INT mult_15 (.clk(clk),.rst_n(rst_n),
                        .en(en[15] & int_inference   & ~zero_gate_int[15]),
                        .wei_precision(wei_precision),.act_precision(act_precision),
                        .jia(jia_15),.yi(yi_15),.zi(zi_int[`MAX_PSUM_PRECISION_INT*(15+1) -1:`MAX_PSUM_PRECISION_INT*15]),
                        .valid(valid[15]),.ready(ready_int[15]),.last(last_int[15]), .start(start_int[15]),
                        .pe_all_ready(pe_all_ready));
//Binding for output zi + ready
assign zi[`MAX_PSUM_PRECISION_INT*(0+1) -1:`MAX_PSUM_PRECISION_INT*0] =  zero_gate_int[0] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(0+1) -1:`MAX_PSUM_PRECISION_INT*0] ;  
assign ready[0] = zero_gate[0]? 1: ready_int[0];
assign last[0] =  zero_gate[0]? 1:last_int[0];
assign start[0] =  start_int[0];
assign zero_gate[0] = zero_gate_int[0];
assign zi[`MAX_PSUM_PRECISION_INT*(1+1) -1:`MAX_PSUM_PRECISION_INT*1] =  zero_gate_int[1] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(1+1) -1:`MAX_PSUM_PRECISION_INT*1] ;  
assign ready[1] = zero_gate[1]? 1: ready_int[1];
assign last[1] =  zero_gate[1]? 1:last_int[1];
assign start[1] =  start_int[1];
assign zero_gate[1] = zero_gate_int[1];
assign zi[`MAX_PSUM_PRECISION_INT*(2+1) -1:`MAX_PSUM_PRECISION_INT*2] =  zero_gate_int[2] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(2+1) -1:`MAX_PSUM_PRECISION_INT*2] ;  
assign ready[2] = zero_gate[2]? 1: ready_int[2];
assign last[2] =  zero_gate[2]? 1:last_int[2];
assign start[2] =  start_int[2];
assign zero_gate[2] = zero_gate_int[2];
assign zi[`MAX_PSUM_PRECISION_INT*(3+1) -1:`MAX_PSUM_PRECISION_INT*3] =  zero_gate_int[3] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(3+1) -1:`MAX_PSUM_PRECISION_INT*3] ;  
assign ready[3] = zero_gate[3]? 1: ready_int[3];
assign last[3] =  zero_gate[3]? 1:last_int[3];
assign start[3] =  start_int[3];
assign zero_gate[3] = zero_gate_int[3];
assign zi[`MAX_PSUM_PRECISION_INT*(4+1) -1:`MAX_PSUM_PRECISION_INT*4] =  zero_gate_int[4] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(4+1) -1:`MAX_PSUM_PRECISION_INT*4] ;  
assign ready[4] = zero_gate[4]? 1: ready_int[4];
assign last[4] =  zero_gate[4]? 1:last_int[4];
assign start[4] =  start_int[4];
assign zero_gate[4] = zero_gate_int[4];
assign zi[`MAX_PSUM_PRECISION_INT*(5+1) -1:`MAX_PSUM_PRECISION_INT*5] =  zero_gate_int[5] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(5+1) -1:`MAX_PSUM_PRECISION_INT*5] ;  
assign ready[5] = zero_gate[5]? 1: ready_int[5];
assign last[5] =  zero_gate[5]? 1:last_int[5];
assign start[5] =  start_int[5];
assign zero_gate[5] = zero_gate_int[5];
assign zi[`MAX_PSUM_PRECISION_INT*(6+1) -1:`MAX_PSUM_PRECISION_INT*6] =  zero_gate_int[6] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(6+1) -1:`MAX_PSUM_PRECISION_INT*6] ;  
assign ready[6] = zero_gate[6]? 1: ready_int[6];
assign last[6] =  zero_gate[6]? 1:last_int[6];
assign start[6] =  start_int[6];
assign zero_gate[6] = zero_gate_int[6];
assign zi[`MAX_PSUM_PRECISION_INT*(7+1) -1:`MAX_PSUM_PRECISION_INT*7] =  zero_gate_int[7] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(7+1) -1:`MAX_PSUM_PRECISION_INT*7] ;  
assign ready[7] = zero_gate[7]? 1: ready_int[7];
assign last[7] =  zero_gate[7]? 1:last_int[7];
assign start[7] =  start_int[7];
assign zero_gate[7] = zero_gate_int[7];
assign zi[`MAX_PSUM_PRECISION_INT*(8+1) -1:`MAX_PSUM_PRECISION_INT*8] =  zero_gate_int[8] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(8+1) -1:`MAX_PSUM_PRECISION_INT*8] ;  
assign ready[8] = zero_gate[8]? 1: ready_int[8];
assign last[8] =  zero_gate[8]? 1:last_int[8];
assign start[8] =  start_int[8];
assign zero_gate[8] = zero_gate_int[8];
assign zi[`MAX_PSUM_PRECISION_INT*(9+1) -1:`MAX_PSUM_PRECISION_INT*9] =  zero_gate_int[9] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(9+1) -1:`MAX_PSUM_PRECISION_INT*9] ;  
assign ready[9] = zero_gate[9]? 1: ready_int[9];
assign last[9] =  zero_gate[9]? 1:last_int[9];
assign start[9] =  start_int[9];
assign zero_gate[9] = zero_gate_int[9];
assign zi[`MAX_PSUM_PRECISION_INT*(10+1) -1:`MAX_PSUM_PRECISION_INT*10] =  zero_gate_int[10] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(10+1) -1:`MAX_PSUM_PRECISION_INT*10] ;  
assign ready[10] = zero_gate[10]? 1: ready_int[10];
assign last[10] =  zero_gate[10]? 1:last_int[10];
assign start[10] =  start_int[10];
assign zero_gate[10] = zero_gate_int[10];
assign zi[`MAX_PSUM_PRECISION_INT*(11+1) -1:`MAX_PSUM_PRECISION_INT*11] =  zero_gate_int[11] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(11+1) -1:`MAX_PSUM_PRECISION_INT*11] ;  
assign ready[11] = zero_gate[11]? 1: ready_int[11];
assign last[11] =  zero_gate[11]? 1:last_int[11];
assign start[11] =  start_int[11];
assign zero_gate[11] = zero_gate_int[11];
assign zi[`MAX_PSUM_PRECISION_INT*(12+1) -1:`MAX_PSUM_PRECISION_INT*12] =  zero_gate_int[12] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(12+1) -1:`MAX_PSUM_PRECISION_INT*12] ;  
assign ready[12] = zero_gate[12]? 1: ready_int[12];
assign last[12] =  zero_gate[12]? 1:last_int[12];
assign start[12] =  start_int[12];
assign zero_gate[12] = zero_gate_int[12];
assign zi[`MAX_PSUM_PRECISION_INT*(13+1) -1:`MAX_PSUM_PRECISION_INT*13] =  zero_gate_int[13] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(13+1) -1:`MAX_PSUM_PRECISION_INT*13] ;  
assign ready[13] = zero_gate[13]? 1: ready_int[13];
assign last[13] =  zero_gate[13]? 1:last_int[13];
assign start[13] =  start_int[13];
assign zero_gate[13] = zero_gate_int[13];
assign zi[`MAX_PSUM_PRECISION_INT*(14+1) -1:`MAX_PSUM_PRECISION_INT*14] =  zero_gate_int[14] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(14+1) -1:`MAX_PSUM_PRECISION_INT*14] ;  
assign ready[14] = zero_gate[14]? 1: ready_int[14];
assign last[14] =  zero_gate[14]? 1:last_int[14];
assign start[14] =  start_int[14];
assign zero_gate[14] = zero_gate_int[14];
assign zi[`MAX_PSUM_PRECISION_INT*(15+1) -1:`MAX_PSUM_PRECISION_INT*15] =  zero_gate_int[15] ? 0  :  zi_int[`MAX_PSUM_PRECISION_INT*(15+1) -1:`MAX_PSUM_PRECISION_INT*15] ;  
assign ready[15] = zero_gate[15]? 1: ready_int[15];
assign last[15] =  zero_gate[15]? 1:last_int[15];
assign start[15] =  start_int[15];
assign zero_gate[15] = zero_gate_int[15];
endmodule
