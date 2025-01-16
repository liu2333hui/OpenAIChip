
//Basic multiplier 
module generic_mult(
    input clk,
    input rst_n,
    input en, //power gating

    input [5:0] precision, // 4, 8, 16, 32 
    input signed [`MAX_PRECISION-1:0] jia,
    input signed [`MAX_PRECISION-1:0] yi,
    output reg signed [`MAX_PRECISION*2 - 1: 0] zi,

    input valid,//data is valid and ready for processing
    output reg ready // data is ready and multiplied , because at most 16/2 cycles
    );

   //Precision is un-used   
   wire clk_gate;
   assign clk_gate = en & clk;
  
   always@(posedge clk_gate or negedge rst_n) begin
       if (~rst_n) begin
           ready <= 0;
           zi <= 0;
       end  else begin
          if(valid) begin
           zi <= jia * yi; // Most simple implementation, but most costly in PPA
           ready <= 1;
          end else  begin
           zi <= zi;
           ready <= 0; 
          end 
       end

   end


endmodule


