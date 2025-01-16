def gen_elt_unit(hardware_config, meta_config, MACRO_CONFIG):

    f = open(meta_config["dossier"] + "/element_unit.v", "w")
    
    s = "module ELEMENT_UNIT(\n\
            input clk,\n\
            input rst_n,\n\
            input [5:0] output_precision,\n\
            input [5:0] input_precision,\n\
            input out_buf_write_ready,\n\
            output out_buf_write_valid,\n\
            input [`PSUM_BUF_DATA-1:0] out_buf_write_data,\n\
            input [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, \n\
                \n\
            output reg [`MAX_ELEMENT_UNITS*`MAX_OUT_PRECISION-1:0] element_buf_data,\n\
            output reg [5 : 0] element_buf_addr, \n\
            output reg element_buf_data_ready,\n\
                \n\
            input [3:0] element_operation\n\
        );\n"

    #ELEMENT OPERATIONS

    #0 - RELU

    #1 - LUT

    #2 - BN

    #3 - ADD

    #4 - BN RELU

    #5 - ADD RELU

    #6 - ADD BN RELU

    

    s += "endmodule;\n"

    f.write(s)
    f.close()

'''
#Element Unit (RELU, tanh, batch_norm, quantization scaling, etc.)
            #提前scale一下结果
            input quant_scale,
            input [15:0] scaler,
            input [3:0] operation, #RELU = 0, LUT = 1, BN = 2, RELU_BN = 3...
            input  out_buf_write_ready; \n\
            input out_buf_write_valid;\n\
            input [`PARTIAL_SUMS*`PRECISION_PSUM-1:0] out_buf_write_data;\n\
            input [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr; \n
                \n\
            output element_buf_data;\n\
            output element_buf_write_addr;\n\
            output element_buf_data_ready;\n\
            output element_buf_data_valid;\n\
                \n\
            output element_unit_stall;
            input accum_prec,
            input element_prec,
            
                \n\
            #READ_ONLY
            input lut_write_data,
            input lut_write_addr,
            input lut_write_valid,
            input lut_write_ready,
            

            #QUANT_SCALERS
            #RELU_UNITS
            #LUT_UNITS
            #BN_UNITS
            
            #out_buf_write_data --> local_data
            reg [`PARTIAL_SUMS*`PRECISION_PSUM - 1:0] save_data;

            @(posedge clk)
            if(out_buf_write_ready)
            save_data = out_buf_write_data

            #SYSTOLIC LOADING POSSIBILITY
            pingpong = PARTIAL_SUMS / UNITS
                if(UNITS < PARTIAL_SUMS):
                    if(pingpong = 0)
                    local_data = save_data[:]
                    if(pingpong = 1)
                    ...local_data = save_data[:]
                    else
                    local_data = save_data[:]
                else:
                     local_data <= out_buf_write_data;

            @(posedge clk)
            if(out_buf_write_ready)
                local_en = 1
                ...
            else
            ping_pong = ping_pong + 1
            if(ping_pong > RATIO)
            ping_pong = 0
            


            #local_data --> dataflow

            #0. 初始: 先，都一样,UNITS统一
            for i in range(QUANT_SCALERS):
                QUANT_UNIT LIANGHUAq%d %(i)

            for j in range(RELU_UNITS):
                RELU_UNIT RELU%d %(i)

            for k in range(BN_UNITS):
                BN_UNIT BN%d %(i)

            for l in range(LUT_UNITS):
                LUT_UNIT L%d %(i)

            #RELU = 0, LUT = 1, BN = 2, RELU_BN = 3. BN_RELU, 4. LUT_BN, 5. BN_LUT, 
            #本地 -> relu_in
            if(operation == 0):
                relu_in = local_data;
                relu_en = local_ready;
                element_result = relu_out
                ready = relu_ready;

            elif(operation == 1):
                lut_in = local_data
                element_result = lut_out
                ready = lut_ready
                lut_en = local_ready
                
            elif(operation == 2):
                bn_in = local_data
                element_result = bn_out
                ready = bn_ready
                bn_en = local_ready
                
            elif(operation == 3):
                relu_in = local_data
                relu_en = local_ready
                
                bn_in = relu_out
                bn_en = relu_ready
                
                element_result = bn_out
                relu_en = local_ready
                
            elif(operation == 4):

                bn_in = local_data
                bn_en = local_ready
                
                relu_in = bn_out
                relu_en = bn_ready
                
                element_result = relu_out
                bn_en = local_ready                

            #final
            elemtn_buf_data[0] = element_Result >> (ELEMENT_INTERMEDIATE_PREC - MAX_ACTIVATION_PREC);
            


INT25 --> FP25,   25  --> 1.3
INT13 --> FP13,   132 
#etc. 乘0.9 = 230/256
#0.98 = 2007/2048
module QUANT_UNIT(
    input en,
    input clk,
    input jia,
    input yi,
    input shift,
    output zi);
    #MULTIPLIER, 我们要做一个新的Mulilier
    MULT(...)

    zi = (ZI >> shift);
    assign ready = mult_ready;
endmodule

module RELU_UNIT(
    input en,
    input jia,
    input yi,
    output zi,
    output ready);
    assign zi = (jia >= 0) ? jia : yi;
    assign ready = 1;
endmodule

module BN_UNIT(
    input en,
    input a,
    input b,
    input c,
    input d,
    output zi,
    output ready,
    );

    MULT()

    e = (ZI >> shift);

    zi <= e + c;
    assign e_ready;
endmodule

module LUT_UNIT(
    input en,
    input 

    output ready
);

    MULT()

    e = (ZI >> shift);

    zi <= e + c;
    assign e_ready;
endmodule

'''
