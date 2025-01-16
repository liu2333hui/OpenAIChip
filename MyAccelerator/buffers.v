module WEI_BUF(
            input read_clk,
            input write_clk,
            input read_en,
            input rst_n, 
            input [`WEI_BUF_ROWS_LOG2 - 1 : 0] read_addr,
            output reg [`WEI_BUF_DATA - 1 : 0] read_data,
            input write_en,
            input [`WEI_BUF_ROWS_LOG2 - 1 : 0] write_addr,
            input [`WEI_BUF_DATA - 1 : 0] write_data);
            reg [`WEI_BUF_DATA - 1 : 0] mem [0 : `WEI_BUF_ROWS -1];
            always@(negedge read_clk or negedge rst_n) begin
                if(~rst_n) begin
                    read_data <= 0; 
                end else begin
               if(read_en) begin
                   read_data <= #(0) mem[read_addr]; 
               end else begin
                   read_data <= read_data; 
               end
               end
            end
            
            always@(negedge write_clk) begin
                if(write_en) begin
                    mem[write_addr] <= write_data;
                end else begin
                    //wu 
                end
            end
            
            endmodule
module ACT_BUF(
            input read_clk,
            input write_clk,
            input read_en,
            input rst_n, 
            input [`ACT_BUF_ROWS_LOG2 - 1 : 0] read_addr,
            output reg [`ACT_BUF_DATA - 1 : 0] read_data,
            input write_en,
            input [`ACT_BUF_ROWS_LOG2 - 1 : 0] write_addr,
            input [`ACT_BUF_DATA - 1 : 0] write_data);
            reg [`ACT_BUF_DATA - 1 : 0] mem [0 : `ACT_BUF_ROWS -1];
            always@(negedge read_clk or negedge rst_n) begin
                if(~rst_n) begin
                    read_data <= 0; 
                end else begin
               if(read_en) begin
                   read_data <= #(0) mem[read_addr]; 
               end else begin
                   read_data <= read_data; 
               end
               end
            end
            
            always@(negedge write_clk) begin
                if(write_en) begin
                    mem[write_addr] <= write_data;
                end else begin
                    //wu 
                end
            end
            
            endmodule
module PSUM_BUF(
            input read_clk,
            input write_clk,
            input read_en,
            input rst_n, 
            input [`PSUM_BUF_ROWS_LOG2 - 1 : 0] read_addr,
            output reg [`PSUM_BUF_DATA - 1 : 0] read_data,
            input write_en,
            input [`PSUM_BUF_ROWS_LOG2 - 1 : 0] write_addr,
            input [`PSUM_BUF_DATA - 1 : 0] write_data);
            reg [`PSUM_BUF_DATA - 1 : 0] mem [0 : `PSUM_BUF_ROWS -1];
            always@(negedge read_clk or negedge rst_n) begin
                if(~rst_n) begin
                    read_data <= 0; 
                end else begin
               if(read_en) begin
                   read_data <= #(0) mem[read_addr]; 
               end else begin
                   read_data <= read_data; 
               end
               end
            end
            
            always@(negedge write_clk) begin
                if(write_en) begin
                    mem[write_addr] <= write_data;
                end else begin
                    //wu 
                end
            end
            
            endmodule
