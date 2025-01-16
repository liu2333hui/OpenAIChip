module INTER_PE(
input clk,
        input rst_n,
        input [`WEI_BUF_DATA-1:0] jia_buf,
output reg [`MAX_WEI_PRECISION*`REQUIRED_PES-1:0] jia,
input [`ACT_BUF_DATA-1:0] yi_buf,
output reg [`MAX_ACT_PRECISION*`REQUIRED_PES-1:0] yi,

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
            
        input [`MAX_KX_LOG-1:0] kkx,
        input [`MAX_KY_LOG-1:0] kky,
        input [`MAX_X_LOG-1:0] xx,
        input [`MAX_Y_LOG-1:0] yy, 
        input [`MAX_X_LOG-1:0] xxx,
        input [`MAX_Y_LOG-1:0] yyy, 
        input [`MAX_N_LOG-1:0] nn, 
        input [`MAX_I_LOG-1:0] ii, 
        input [`MAX_N_LOG-1:0] nnn, 
        input [`MAX_I_LOG-1:0] iii, 
        input [`MAX_B_LOG-1:0] bb,
            
            input int_inference,
            input [5:0] wei_precision,
            input [5:0] act_precision, 
input wei_sys_en,
          input act_sys_en,
input [5:0] jia_sys_jie, 
          input [5:0] yi_sys_jie, 
output sparse_stall, 
input mac_en, 
output tile_done_flag, 
input mult_done,
          input pre_mult_done
);
    //dataflow1


reg [`WEI_BUF_DATA*1-1:0] jia_buf_loaded;
always@(posedge clk) begin
jia_buf_loaded <= jia_buf;
end
reg [16*`MAX_WEI_PRECISION_INT -1:0] jia_buffered;
reg [16*`MAX_ACT_PRECISION_INT -1:0] yi_buffered;
reg [16 -1:0] jia_sparse_map_buffered;
reg [16 -1:0] yi_sparse_map_buffered;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_0;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_0;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_1;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_1;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_2;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_2;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_3;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_3;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_4;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_4;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_5;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_5;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_6;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_6;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_7;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_7;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_8;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_8;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_9;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_9;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_10;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_10;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_11;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_11;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_12;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_12;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_13;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_13;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_14;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_14;
reg [`MAX_WEI_PRECISION-1:0] jia_buffered_15;
reg [`MAX_ACT_PRECISION-1:0] yi_buffered_15;
always@(*) begin 
if(act_precision == 16 &  wei_precision == 16) begin 
//1 , 1
    jia_buffered[(( 16-1 - 0)+1)*16-1:(( 16-1 - 0))*16] =                                                         jia_buf_loaded[(((((0*4+  0)*4+  0)*1+  0)*1+  0)+1)*16-1:(((((0*4+  0)*4+  0)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 0)+1)*16-1:(( 16-1 - 0))*16] =                                                         yi_buf[(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_15 = jia_buffered[(( 16-1 - 0)+1)*16-1:(( 16-1 - 0))*16];
   yi_buffered_15 = yi_buffered[(( 16-1 - 0)+1)*16-1:(( 16-1 - 0))*16];
    jia_buffered[(( 16-1 - 1)+1)*16-1:(( 16-1 - 1))*16] =                                                         jia_buf_loaded[(((((0*4+  1)*4+  0)*1+  0)*1+  0)+1)*16-1:(((((0*4+  1)*4+  0)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 1)+1)*16-1:(( 16-1 - 1))*16] =                                                         yi_buf[(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_14 = jia_buffered[(( 16-1 - 1)+1)*16-1:(( 16-1 - 1))*16];
   yi_buffered_14 = yi_buffered[(( 16-1 - 1)+1)*16-1:(( 16-1 - 1))*16];
    jia_buffered[(( 16-1 - 2)+1)*16-1:(( 16-1 - 2))*16] =                                                         jia_buf_loaded[(((((0*4+  2)*4+  0)*1+  0)*1+  0)+1)*16-1:(((((0*4+  2)*4+  0)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 2)+1)*16-1:(( 16-1 - 2))*16] =                                                         yi_buf[(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_13 = jia_buffered[(( 16-1 - 2)+1)*16-1:(( 16-1 - 2))*16];
   yi_buffered_13 = yi_buffered[(( 16-1 - 2)+1)*16-1:(( 16-1 - 2))*16];
    jia_buffered[(( 16-1 - 3)+1)*16-1:(( 16-1 - 3))*16] =                                                         jia_buf_loaded[(((((0*4+  3)*4+  0)*1+  0)*1+  0)+1)*16-1:(((((0*4+  3)*4+  0)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 3)+1)*16-1:(( 16-1 - 3))*16] =                                                         yi_buf[(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_12 = jia_buffered[(( 16-1 - 3)+1)*16-1:(( 16-1 - 3))*16];
   yi_buffered_12 = yi_buffered[(( 16-1 - 3)+1)*16-1:(( 16-1 - 3))*16];
    jia_buffered[(( 16-1 - 4)+1)*16-1:(( 16-1 - 4))*16] =                                                         jia_buf_loaded[(((((0*4+  0)*4+  1)*1+  0)*1+  0)+1)*16-1:(((((0*4+  0)*4+  1)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 4)+1)*16-1:(( 16-1 - 4))*16] =                                                         yi_buf[(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_11 = jia_buffered[(( 16-1 - 4)+1)*16-1:(( 16-1 - 4))*16];
   yi_buffered_11 = yi_buffered[(( 16-1 - 4)+1)*16-1:(( 16-1 - 4))*16];
    jia_buffered[(( 16-1 - 5)+1)*16-1:(( 16-1 - 5))*16] =                                                         jia_buf_loaded[(((((0*4+  1)*4+  1)*1+  0)*1+  0)+1)*16-1:(((((0*4+  1)*4+  1)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 5)+1)*16-1:(( 16-1 - 5))*16] =                                                         yi_buf[(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_10 = jia_buffered[(( 16-1 - 5)+1)*16-1:(( 16-1 - 5))*16];
   yi_buffered_10 = yi_buffered[(( 16-1 - 5)+1)*16-1:(( 16-1 - 5))*16];
    jia_buffered[(( 16-1 - 6)+1)*16-1:(( 16-1 - 6))*16] =                                                         jia_buf_loaded[(((((0*4+  2)*4+  1)*1+  0)*1+  0)+1)*16-1:(((((0*4+  2)*4+  1)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 6)+1)*16-1:(( 16-1 - 6))*16] =                                                         yi_buf[(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_9 = jia_buffered[(( 16-1 - 6)+1)*16-1:(( 16-1 - 6))*16];
   yi_buffered_9 = yi_buffered[(( 16-1 - 6)+1)*16-1:(( 16-1 - 6))*16];
    jia_buffered[(( 16-1 - 7)+1)*16-1:(( 16-1 - 7))*16] =                                                         jia_buf_loaded[(((((0*4+  3)*4+  1)*1+  0)*1+  0)+1)*16-1:(((((0*4+  3)*4+  1)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 7)+1)*16-1:(( 16-1 - 7))*16] =                                                         yi_buf[(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_8 = jia_buffered[(( 16-1 - 7)+1)*16-1:(( 16-1 - 7))*16];
   yi_buffered_8 = yi_buffered[(( 16-1 - 7)+1)*16-1:(( 16-1 - 7))*16];
    jia_buffered[(( 16-1 - 8)+1)*16-1:(( 16-1 - 8))*16] =                                                         jia_buf_loaded[(((((0*4+  0)*4+  2)*1+  0)*1+  0)+1)*16-1:(((((0*4+  0)*4+  2)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 8)+1)*16-1:(( 16-1 - 8))*16] =                                                         yi_buf[(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_7 = jia_buffered[(( 16-1 - 8)+1)*16-1:(( 16-1 - 8))*16];
   yi_buffered_7 = yi_buffered[(( 16-1 - 8)+1)*16-1:(( 16-1 - 8))*16];
    jia_buffered[(( 16-1 - 9)+1)*16-1:(( 16-1 - 9))*16] =                                                         jia_buf_loaded[(((((0*4+  1)*4+  2)*1+  0)*1+  0)+1)*16-1:(((((0*4+  1)*4+  2)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 9)+1)*16-1:(( 16-1 - 9))*16] =                                                         yi_buf[(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_6 = jia_buffered[(( 16-1 - 9)+1)*16-1:(( 16-1 - 9))*16];
   yi_buffered_6 = yi_buffered[(( 16-1 - 9)+1)*16-1:(( 16-1 - 9))*16];
    jia_buffered[(( 16-1 - 10)+1)*16-1:(( 16-1 - 10))*16] =                                                         jia_buf_loaded[(((((0*4+  2)*4+  2)*1+  0)*1+  0)+1)*16-1:(((((0*4+  2)*4+  2)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 10)+1)*16-1:(( 16-1 - 10))*16] =                                                         yi_buf[(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_5 = jia_buffered[(( 16-1 - 10)+1)*16-1:(( 16-1 - 10))*16];
   yi_buffered_5 = yi_buffered[(( 16-1 - 10)+1)*16-1:(( 16-1 - 10))*16];
    jia_buffered[(( 16-1 - 11)+1)*16-1:(( 16-1 - 11))*16] =                                                         jia_buf_loaded[(((((0*4+  3)*4+  2)*1+  0)*1+  0)+1)*16-1:(((((0*4+  3)*4+  2)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 11)+1)*16-1:(( 16-1 - 11))*16] =                                                         yi_buf[(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_4 = jia_buffered[(( 16-1 - 11)+1)*16-1:(( 16-1 - 11))*16];
   yi_buffered_4 = yi_buffered[(( 16-1 - 11)+1)*16-1:(( 16-1 - 11))*16];
    jia_buffered[(( 16-1 - 12)+1)*16-1:(( 16-1 - 12))*16] =                                                         jia_buf_loaded[(((((0*4+  0)*4+  3)*1+  0)*1+  0)+1)*16-1:(((((0*4+  0)*4+  3)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 12)+1)*16-1:(( 16-1 - 12))*16] =                                                         yi_buf[(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  0)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_3 = jia_buffered[(( 16-1 - 12)+1)*16-1:(( 16-1 - 12))*16];
   yi_buffered_3 = yi_buffered[(( 16-1 - 12)+1)*16-1:(( 16-1 - 12))*16];
    jia_buffered[(( 16-1 - 13)+1)*16-1:(( 16-1 - 13))*16] =                                                         jia_buf_loaded[(((((0*4+  1)*4+  3)*1+  0)*1+  0)+1)*16-1:(((((0*4+  1)*4+  3)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 13)+1)*16-1:(( 16-1 - 13))*16] =                                                         yi_buf[(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  1)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_2 = jia_buffered[(( 16-1 - 13)+1)*16-1:(( 16-1 - 13))*16];
   yi_buffered_2 = yi_buffered[(( 16-1 - 13)+1)*16-1:(( 16-1 - 13))*16];
    jia_buffered[(( 16-1 - 14)+1)*16-1:(( 16-1 - 14))*16] =                                                         jia_buf_loaded[(((((0*4+  2)*4+  3)*1+  0)*1+  0)+1)*16-1:(((((0*4+  2)*4+  3)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 14)+1)*16-1:(( 16-1 - 14))*16] =                                                         yi_buf[(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  2)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_1 = jia_buffered[(( 16-1 - 14)+1)*16-1:(( 16-1 - 14))*16];
   yi_buffered_1 = yi_buffered[(( 16-1 - 14)+1)*16-1:(( 16-1 - 14))*16];
    jia_buffered[(( 16-1 - 15)+1)*16-1:(( 16-1 - 15))*16] =                                                         jia_buf_loaded[(((((0*4+  3)*4+  3)*1+  0)*1+  0)+1)*16-1:(((((0*4+  3)*4+  3)*1+  0)*1+  0))*16];
    yi_buffered[(( 16-1 - 15)+1)*16-1:(( 16-1 - 15))*16] =                                                         yi_buf[(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0)+1)*16-1:(((((0*1+  0)*4+  3)*(1+1-1)+  0+0)*(1+1-1)+  0+0))*16];
   jia_buffered_0 = jia_buffered[(( 16-1 - 15)+1)*16-1:(( 16-1 - 15))*16];
   yi_buffered_0 = yi_buffered[(( 16-1 - 15)+1)*16-1:(( 16-1 - 15))*16];
    end
end
always@(*) begin
                            jia = jia_buffered;
                            yi = yi_buffered;
                    end
assign sparse_stall = 0;
endmodule

