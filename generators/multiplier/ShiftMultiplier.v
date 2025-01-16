// https://blog.csdn.net/jiang1960034308/article/details/118078073
module mult_int_tree(
   partial,
   out_sum
);

    parameter DATA_WIDTH = 16;
    parameter LENGTH = 8; 

    input signed [DATA_WIDTH - 1:0]  partial [LENGTH-1:0];
    output signed  [DATA_WIDTH - 1:0]  out_sum;

    generate
      if(LENGTH == 1) begin
       assign out_sum = partial[0];
    end  else begin
        wire signed [DATA_WIDTH - 1:0] sum_jia;
        wire signed [DATA_WIDTH - 1:0] sum_yi;
     wire signed [DATA_WIDTH - 1:0]  partial_jia [LENGTH/2-1:0];
     wire signed [DATA_WIDTH - 1:0]  partial_yi [LENGTH/2-1:0];
             genvar i; 
            for ( i = 0; i < LENGTH / 2; i += 1) begin
                assign                 partial_jia[i] = partial[i];
                assign  partial_yi[i] = partial[i + LENGTH / 2]; 
            end




        mult_int_tree  #(.DATA_WIDTH(DATA_WIDTH),.LENGTH( LENGTH / 2)) yin(
            partial_jia   , 
            sum_jia
        );

      mult_int_tree  #(.DATA_WIDTH(DATA_WIDTH),.LENGTH( LENGTH / 2)) yang(
   
            partial_yi         , 
            sum_yi
        );

        assign out_sum = sum_jia + sum_yi;

     end

     

   endgenerate 


endmodule




// ShiftMultiplier 
// 1 cycle to complete
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

   wire [`MAX_PRECISION*2-1:0]  sign_yi = {    { `MAX_PRECISION{   yi[`MAX_PRECISION-1] }} , yi};
   
   wire signed [`MAX_PRECISION*2 - 1: 0] partials [`MAX_PRECISION-1:0];
   generate
      genvar i;
      for ( i = 0; i < `MAX_PRECISION-1; i+=1) begin
       assign     partials[i]= (jia[i]) ? (sign_yi << i) : 1'b0; 
      end
       assign partials[`MAX_PRECISION-1] = (jia[`MAX_PRECISION-1]) ? -(sign_yi << (`MAX_PRECISION-1)) : 1'b0;
   endgenerate

   wire [`MAX_PRECISION*2-1:0] sum;
   mult_int_tree #(.DATA_WIDTH(`MAX_PRECISION*2), .LENGTH(`MAX_PRECISION)) add_u (partials, sum);

   always@(posedge clk_gate or negedge rst_n) begin
       if (~rst_n) begin
           ready <= 0;
           zi <= 0;
       end  else begin
          if(valid) begin
 
           // $display(partials); 
           zi <= sum; // Most simple implementation, but most costly in PPA
 
           ready <= 1;
          end else  begin
           zi <= zi;
           ready <= 0; 
          end 
       end

   end


endmodule


