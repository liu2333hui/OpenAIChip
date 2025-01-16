`include "mult.vh"

//Pipelined Strips Multiplier
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
  

localparam INDEX = $clog2(`MAX_PRECISION);
   
   //Pipeline
   reg signed [`MAX_PRECISION*2-1:0]  jia_saved [`MAX_PRECISION-1:0];
   reg signed [`MAX_PRECISION-1:0]  yi_saved [`MAX_PRECISION-1:0];
   reg signed [`MAX_PRECISION-1:0]  yi_orig [`MAX_PRECISION-1:0]; 
   reg signed [`MAX_PRECISION*2-1:0]  zi_saved [`MAX_PRECISION-1:0];
 
   reg [`MAX_PRECISION-1:0] valid_saved;
   reg [`MAX_PRECISION-1:0] ready_saved;

   reg [`MAX_PRECISION-1:0] ready_top;



   /*
   //Parallel to serial
   reg [INDEX-1:0] index;
   reg lsb;
    always@(*) begin
        for (integer i = 0; i < `MAX_PRECISION; i++) begin
             if( index ==  i) begin
                 lsb = yi[i]; 
             end
        end
   end    

   //Dynamically know the max index
   reg signed [INDEX-1:0] max_index;
   always@(*) begin
           if( yi[`MAX_PRECISION-1] == 1   ) begin
              max_index = `MAX_PRECISION-1;   
           end
 
   
       for (integer i = `MAX_PRECISION -2 ; i >= 0; i--) begin
           $display(yi & (1<<i),"\t", |(yi & (1<<i)), "\t1<<i",1<<i, yi,"\t", yi >= (1<<i),"\t", max_index);
           if( |(yi & (1<<i)) == 1   ) begin
              max_index = i;   
           end
 
       end
   end
   */


   // The multiplication is done and assign to zi
   // [0, 0, 1, 1, 0, 0] ==> [0, 0, 1, 0, 
   /*
   always_comb
   begin
      	for (int i = 0; i < `MAX_PRECISION; i++) begin
             if( ready_saved >= (1 << i)) begin
                      ready_top = (1 << i) ;
             end
         end 

   end
   

   always_comb
   begin
    
      	for (int i = 0; i < `MAX_PRECISION; i++) begin
             if( (ready_top & ready_saved) == (1 << i)) begin
                      zi = zi_saved[i];
             end
         end 

   end
 
 */ 
  assign zi = zi_saved[`MAX_PRECISION-1];



   always@(posedge clk_gate or negedge rst_n) begin
       if (~rst_n) begin
           ready <= 0;
           
           valid_saved <= 0;
           ready_saved <= 0;

       end  else begin
          if(valid) begin

              

            jia_saved[0] <= jia; 
            yi_saved[0] <= (yi >> 1); 
            yi_orig[0] <= yi;
            valid_saved[0] <=  valid ; //(yi >> 1) == 0 ? 1'b0 :  valid;

              // Do the stripes operation
             zi_saved[0] <={`MAX_PRECISION*2 {yi[0]}} &{ { `MAX_PRECISION{jia[`MAX_PRECISION-1]}},  jia} ;
        
              // $display("lsb", lsb, max_index);
           ready_saved[0] <= ((yi >> 1) == 0);

                     
          end      
          for (integer i = 1; i < `MAX_PRECISION;i++) begin
               
               //remove one at a time
               if (ready_top[i] == 1)begin
                      ready_saved[i] <= 0;
               end


//               if (valid_saved[i-1] & ~ready_saved[i]) begin
               if (valid_saved[i-1] ) begin
 
                    jia_saved[i] <= jia_saved[i-1]; 
                    yi_saved[i] <= (yi_saved[i-1] >> 1); 
                    yi_orig[i] <= yi_orig[i-1];
                   valid_saved[i] <= valid_saved[i-1];  // (yi_saved[i-1] >> 1 == 0) ? 1'b0:   valid_saved[i-1];

                  if(i == `MAX_PRECISION - 1 ) begin
                  zi_saved[i] <=  -({`MAX_PRECISION*2 {yi_saved[i-1][0]}}&(jia_saved[i-1]<<i))  + zi_saved[i-1]; 
                    end else begin 
                  zi_saved[i] <=({`MAX_PRECISION*2 {yi_saved[i-1][0]}}&(jia_saved[i-1]<<i))  + zi_saved[i-1];
                   end
 
                 ready_saved[i] <= ((yi_saved[i-1] >> 1) == 0);  // (valid_saved[i-1] & ~ready_saved[i-1] &   (yi_saved[i-1] >> 1) == 0);
                

               end

               
                       
          end  
        
            
             $display("jia_saved ", jia_saved);
             $display("yi_orig ", yi_orig);  
             $display("zi_saved ", zi_saved);
             $display("yi_saved ", yi_saved);
             $display("valid_saved %b",valid_saved);
             $display("ready_saved %b",ready_saved);
             $display("ready_top %b",ready_top & ready_saved);
             $display(jia, "\t", yi, "\tzi", zi);
 
             //$display("> 1", ready_saved > 1);
             //$display("> 2", ready_saved > 2);
             //$display("> 4", ready_saved > 4);
             //$display("> 8", ready_saved > 8);
             //$display("> 16", ready_saved > 16);







           




      end




   end


endmodule


