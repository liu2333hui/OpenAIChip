module MULT_INT(
                input clk,
                input rst_n,
                input en, //power gating
                            
                input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more
                input [5:0] act_precision, // 4, 8, 16, 32 
                    input signed [`MAX_WEI_PRECISION_INT-1:0] jia,
                    input signed [`MAX_ACT_PRECISION_INT-1:0] yi,
                    output reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] zi,
                            
                input valid,//data is valid and ready for processing
                output reg ready, // data is ready and multiplied , because at most 16/2 cycles
                            
                output reg last, 
                output reg start, 
                            
                input pe_all_ready
        );
reg [2:0] state;
`define TING 0
`define GONG 1
reg [5:0] qi;
reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] cheng;
reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] cheng2;
reg double_buffer_id;
//Precision is un-used
                   reg  clk_gate;
                always@(*) begin
                        clk_gate = en & clk;
                   end
reg valid_;
always@(*) begin
                valid_ <= valid;
              end
wire signed[`MAX_ACT_PRECISION_INT-1:0] shu = yi;
wire signed[`MAX_WEI_PRECISION_INT-1:0] yin = jia;
wire [5:0] zhou = wei_precision+1;
wire [5:0] stripe_zhou = wei_precision+1;
wire [5:0] stripe_zhou_ = wei_precision+1;
reg  signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_yin;
reg  signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_shu;
always@(*) begin
                  last <= (1+1>=zhou)? 1 : ~(qi==0)&((stripe_zhou_<=2)?  stripe_zhou<=2? 1 :  ~ready  :  (((1>=zhou)?  1 : (qi+2*1 >= zhou) | qi + 2*1 >= stripe_zhou_)) & ~pe_all_ready);
                  ready <=  (qi + 1 >= zhou | ((stripe_zhou_ <=2)?  qi + 1 >= stripe_zhou_ : qi + 1 >= stripe_zhou_)) & (state == `GONG);
    zi <= cheng;
    start <= (qi == 0 );//| qi + 1 >= zhou );
              end
reg init;
always@(posedge clk_gate or negedge rst_n) begin
                       if (~rst_n) begin
                           state <= `TING;
                           qi <= 0;
                           double_buffer_id <= 0;
                       end  else begin
                           if(state == `TING) begin 
                                if(valid_) begin 
                                    if(qi + 1 == zhou | qi + 1 >= stripe_zhou) begin 
                                        state <=  `GONG;
                                        shift_yin <= (yin >> 1);
                                        shift_shu <= (shu << 1);
                                        cheng <= yin[1-1:0] * shu ;
                                    end else begin 
                                        cheng <= yin[1-1:0] * shu ;
                                        shift_yin <= (yin >> 1);
                                        shift_shu <= (shu << 1);
                                        qi <= qi + 1;
                                        state <= `GONG;
                                    end
                                end
                            end else if(state == `GONG) begin
                                //$display(888,(qi + 1 == zhou) | (qi + 1 >= stripe_zhou_));
                                //if(  (qi == zhou)  |    (qi >= stripe_zhou_)  )begin
                                    if(pe_all_ready) begin
                                        //$display(233);
                                        cheng <= yin[1-1:0] * shu ;
                                        shift_yin <= (yin >> 1);
                                        shift_shu <= (shu << 1);
                                        qi <= 0 + 1;
                                    //end else begin
                                        //qi <= 0;
                                       // state <= `TING;
                                        //shift_yin <= (yin >> 1);
                                        //shift_shu <= (shu << 1);
                                    //end
                                end else begin 
                                    if(qi == 0) begin
                                       //$display(666);
                                        cheng <= yin[1-1:0] * shu ;
                                        shift_yin <= yin >> 1;
                                        shift_shu <= shu << 1;
                                        qi <= 0 + 1;
                                    end else if((qi + 1 == zhou-1)) begin
                   cheng <= -shift_yin[1-1:0]*shift_shu + cheng ;
                                        shift_yin <= shift_yin >> 1;
                                        shift_shu <= shift_shu << 1;
                                        qi <= qi + 1;
                                    end else begin
                                    //$display(555);
                                        cheng <= shift_yin[1-1:0]*shift_shu + cheng ;
                                        shift_yin <= shift_yin >> 1;
                                        shift_shu <= shift_shu << 1;
                                        qi <= qi + 1;
                                    end
                                end
                            end
                        end
                    end
endmodule
