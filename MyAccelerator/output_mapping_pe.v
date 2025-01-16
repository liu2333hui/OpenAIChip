module OUTPUT_MAPPING_PE(
        input clk,
           input rst_n, 
input signed [`MAX_PSUM_PRECISION*`REQUIRED_PES - 1:0] zi,
output   reg  signed [`PSUM_BUF_DATA - 1:0] zi_buf,
            
        input [`MAX_STRIDE_LOG-1:0] stride, 
        input [`MAX_KX_LOG-1:0] kx,
        input [`MAX_KY_LOG-1:0] ky,
        input [`MAX_X_LOG-1:0] x,
        input [`MAX_Y_LOG-1:0] y, 
        input [`MAX_N_LOG-1:0] nc, 
        input [`MAX_I_LOG-1:0] ic, 
        input [`MAX_B_LOG-1:0] batch,
        input [`MAX_PADDING_X_LOG-1:0] padding_x,
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,
        input [3:0] OP_TYPE,
        input [3:0] SYSTOLIC_OP,
        
            input int_inference,
            input [5:0] wei_precision,
            input [5:0] act_precision,
                
        input mult_done, 
        input tile_done, 
        output reg add_tree_ready 
            );    //dataflow1
always@(*) begin
add_tree_ready = mult_done;


if(act_precision == 16 &  wei_precision == 16) begin 
//1 , 1
zi_buf[(0)*(41)+16+16-1:(0)*(41)] = zi[(0+1)*(16+16)-1:(0)*(16+16)]+zi[(1+1)*(16+16)-1:(1)*(16+16)]+zi[(2+1)*(16+16)-1:(2)*(16+16)]+zi[(3+1)*(16+16)-1:(3)*(16+16)];
zi_buf[(0+1)*(41)-1:(0)*(41)+16+16] =                                                     {(41-16-16){zi_buf[(0)*(41)+16+16-1]}};
zi_buf[(1)*(41)+16+16-1:(1)*(41)] = zi[(4+1)*(16+16)-1:(4)*(16+16)]+zi[(5+1)*(16+16)-1:(5)*(16+16)]+zi[(6+1)*(16+16)-1:(6)*(16+16)]+zi[(7+1)*(16+16)-1:(7)*(16+16)];
zi_buf[(1+1)*(41)-1:(1)*(41)+16+16] =                                                     {(41-16-16){zi_buf[(1)*(41)+16+16-1]}};
zi_buf[(2)*(41)+16+16-1:(2)*(41)] = zi[(8+1)*(16+16)-1:(8)*(16+16)]+zi[(9+1)*(16+16)-1:(9)*(16+16)]+zi[(10+1)*(16+16)-1:(10)*(16+16)]+zi[(11+1)*(16+16)-1:(11)*(16+16)];
zi_buf[(2+1)*(41)-1:(2)*(41)+16+16] =                                                     {(41-16-16){zi_buf[(2)*(41)+16+16-1]}};
zi_buf[(3)*(41)+16+16-1:(3)*(41)] = zi[(12+1)*(16+16)-1:(12)*(16+16)]+zi[(13+1)*(16+16)-1:(13)*(16+16)]+zi[(14+1)*(16+16)-1:(14)*(16+16)]+zi[(15+1)*(16+16)-1:(15)*(16+16)];
zi_buf[(3+1)*(41)-1:(3)*(41)+16+16] =                                                     {(41-16-16){zi_buf[(3)*(41)+16+16-1]}};
    end
else begin
zi_buf = 0;
end
end
endmodule

