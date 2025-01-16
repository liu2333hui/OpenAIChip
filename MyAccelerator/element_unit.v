module ELEMENT_UNIT(
            input clk,
            input rst_n,
            input [5:0] output_precision,
            input [5:0] input_precision,
            input out_buf_write_ready,
            output out_buf_write_valid,
            input [`PSUM_BUF_DATA-1:0] out_buf_write_data,
            input [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, 
                
            output reg [`MAX_ELEMENT_UNITS*`MAX_OUT_PRECISION-1:0] element_buf_data,
            output reg [5 : 0] element_buf_addr, 
            output reg element_buf_data_ready,
                
            input [3:0] element_operation
        );
endmodule;
