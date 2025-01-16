`include "mult.vh"

module generic_mult_tb;

    reg clk;
    reg rst_n;
    reg en; //power gating

    reg [5:0] precision; // 4, 8, 16, 32 
    reg signed [`MAX_PRECISION-1:0] jia;
    reg signed [`MAX_PRECISION-1:0] yi;
    wire signed [`MAX_PRECISION*2 - 1: 0] zi;

    reg valid; //data is valid and ready for processing
    wire ready; //data is ready and multiplied 

    generic_mult mult_u(
       clk,
       rst_n,
   
       en, // clock gating
       
       precision, // only for multi-precision multipliers
       
       jia,
       yi,
       zi,

       valid,
       ready
    ); 


    initial begin
    clk = 0;
    forever begin
    #(`CLK_PERIOD/2); clk = ~clk;
    end
    end

    initial begin
    en = 1;
    precision = 8;
    jia = 0;
    yi = 0;
    valid = 0;
    rst_n = 1;
    #(`CLK_PERIOD);
    rst_n = 0;
    #(`CLK_PERIOD);
    rst_n = 1;
    $display("Reset done");

    //BEGIN TEST
    jia = 8;
    yi = 31;
    valid = 1;
    #(`CLK_PERIOD);//*precision/2);
    $display("Multiplier ", mult_u.jia, mult_u.yi, mult_u.zi, "\t", ready, "\t", valid); 
    //$finish;
    jia = -8;
    yi = 2;
    valid = 1;
    #(`CLK_PERIOD);
    $display("Multiplier ", mult_u.jia, mult_u.yi, mult_u.zi, "\t", ready, "\t", valid);  
    jia = -8;
    yi = 31;
    valid = 1;
    #(`CLK_PERIOD);
     valid = 0;
 
    #(`CLK_PERIOD*10);
    $display("Multiplier ", mult_u.jia, mult_u.yi, mult_u.zi, "\t", ready, "\t", valid);  


    $finish;
    jia = 32;
    yi = 23;
    valid = 1;
    #(`CLK_PERIOD*precision/2);
    $display("Multiplier ", mult_u.jia, mult_u.yi, mult_u.zi, "\t", ready, "\t", valid);  
 
    jia = 8;
    yi = -7;
    valid = 1;
    #(`CLK_PERIOD*precision/2);
    $display("Multiplier ", mult_u.jia, mult_u.yi, mult_u.zi, "\t", ready, "\t", valid);  
 

    $finish; 


    end



endmodule







