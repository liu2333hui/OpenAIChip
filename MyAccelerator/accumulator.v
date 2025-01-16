module ACCUM(
        input clk,
        input rst_n,
        input accum_en,
            
        input [`MAX_STRIDE_LOG-1:0] stride, 
        input [`MAX_KX_LOG-1:0] fkx,
        input [`MAX_KY_LOG-1:0] fky,
        input [`MAX_X_LOG-1:0] x,
        input [`MAX_Y_LOG-1:0] y, 
        input [`MAX_N_LOG-1:0] nc, 
        input [`MAX_I_LOG-1:0] ic, 
        input [`MAX_B_LOG-1:0] batch,
        input [`MAX_PADDING_X_LOG-1:0] padding_x,
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,
            
        input [`PSUM_BUF_DATA - 1:0] zi_buf,
            
        output reg psum_write_en,
        output reg psum_read_en,
        output reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr,
        output reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_write_addr,
        output reg [ `PSUM_BUF_DATA  - 1 :0] psum_write_data,
        input [ `PSUM_BUF_DATA - 1 :0] psum_read_data,
            
            input int_inference,
            input [5:0] wei_precision,
            input [5:0] act_precision,
                
            output reg result_done,
                
            output out_buf_write_ready, 
            input out_buf_write_valid, 
            output reg [`PSUM_BUF_DATA-1:0] out_buf_write_data,
            output reg [`PSUM_BUF_ROWS_LOG2   - 1 :0] out_buf_write_addr, 
                
            output accum_done,
            output reg ACC_stalled 
); 
             
                //LOOP DIFFERENT DATAFLOWS(TODOS) 
wire acc_done;
assign accum_done = acc_done;
reg done_done;
reg accum_en_;
        always@(*) begin
            accum_en_ = accum_en;
        end
reg [5:0] a_ratio;reg [5:0] w_ratio;reg [5:0] TX_lv;reg [5:0] TY_lv;reg [5:0] TKX_lv;reg [5:0] TKY_lv;reg [5:0] TN_lv;reg [5:0] TB_lv;reg [5:0] TI_lv;reg [3:0] TX_shift;reg [3:0] TY_shift;reg [3:0] TKX_shift;reg [3:0] TKY_shift;reg [3:0] TN_shift;reg [3:0] TB_shift;reg [3:0] TI_shift;wire [`MAX_ACC_PRECISION_INT-1:0] zi_buf_0;
assign zi_buf_0 = zi_buf[(0+1)*`MAX_ACC_PRECISION_INT -1 : 0*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] acc_buf_0;
assign acc_buf_0 = psum_read_data[(0+1)*`MAX_ACC_PRECISION_INT -1 : 0*`MAX_ACC_PRECISION_INT];
wire signed [`MAX_ACC_PRECISION_INT-1:0] write_dat_0;
assign write_dat_0 = psum_write_data[(0+1)*`MAX_ACC_PRECISION_INT -1 : 0*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] zi_buf_1;
assign zi_buf_1 = zi_buf[(1+1)*`MAX_ACC_PRECISION_INT -1 : 1*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] acc_buf_1;
assign acc_buf_1 = psum_read_data[(1+1)*`MAX_ACC_PRECISION_INT -1 : 1*`MAX_ACC_PRECISION_INT];
wire signed [`MAX_ACC_PRECISION_INT-1:0] write_dat_1;
assign write_dat_1 = psum_write_data[(1+1)*`MAX_ACC_PRECISION_INT -1 : 1*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] zi_buf_2;
assign zi_buf_2 = zi_buf[(2+1)*`MAX_ACC_PRECISION_INT -1 : 2*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] acc_buf_2;
assign acc_buf_2 = psum_read_data[(2+1)*`MAX_ACC_PRECISION_INT -1 : 2*`MAX_ACC_PRECISION_INT];
wire signed [`MAX_ACC_PRECISION_INT-1:0] write_dat_2;
assign write_dat_2 = psum_write_data[(2+1)*`MAX_ACC_PRECISION_INT -1 : 2*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] zi_buf_3;
assign zi_buf_3 = zi_buf[(3+1)*`MAX_ACC_PRECISION_INT -1 : 3*`MAX_ACC_PRECISION_INT];
wire [`MAX_ACC_PRECISION_INT-1:0] acc_buf_3;
assign acc_buf_3 = psum_read_data[(3+1)*`MAX_ACC_PRECISION_INT -1 : 3*`MAX_ACC_PRECISION_INT];
wire signed [`MAX_ACC_PRECISION_INT-1:0] write_dat_3;
assign write_dat_3 = psum_write_data[(3+1)*`MAX_ACC_PRECISION_INT -1 : 3*`MAX_ACC_PRECISION_INT];
always@(*) begin
if(act_precision == 16 &  wei_precision == 16) begin 
                        w_ratio =1; 
                        a_ratio =1; 
                        TX_lv = 1;
                        TY_lv = 1;
                        TKX_lv = 1;
                        TKY_lv = 1;
                        TN_lv = 1;
                        TB_lv = 1;
                        TI_lv = 1;
                            
                        TX_shift = 0;
                        TY_shift = 0;
                        TKX_shift = 0;
                        TKY_shift = 0;
                        TN_shift = 0;
                        TB_shift = 0;
                        TI_shift = 0;
TN_lv = 1;
TN_shift = 0.0;
end
end


reg [`MAX_KX_LOG-1:0] kkx;
reg [`MAX_KY_LOG-1:0] kky;
reg [`MAX_X_LOG-1:0] xx;
reg [`MAX_Y_LOG-1:0] yy;
reg [`MAX_X_LOG-1:0] xxx;
reg [`MAX_Y_LOG-1:0] yyy;
reg [`MAX_N_LOG-1:0] nn;
reg [`MAX_I_LOG-1:0] ii;
reg [`MAX_N_LOG-1:0] nnn;
reg [`MAX_I_LOG-1:0] iii;
reg [`MAX_B_LOG-1:0] bb;
reg [`MAX_Y_LOG-1:0] yy_0;
reg [`MAX_Y_LOG-1:0] yy_0_chu;
reg [`MAX_Y_LOG-1:0] yy_1;
reg [`MAX_Y_LOG-1:0] yy_1_chu;
always@(*) begin
                              yy_0 = yy;
                          end
always@(*) begin
	if(  (yy_0_chu >= (y - fky + 1) ) | (yy_0_chu >= (y - fky + 1) ) ) 
		yy_1 = 0;
	else  
		yy_1 = yy_0_chu ; 
	end
reg [`MAX_X_LOG-1:0] xx_0;
reg [`MAX_X_LOG-1:0] xx_0_chu;
reg [`MAX_X_LOG-1:0] xx_1;
reg [`MAX_X_LOG-1:0] xx_1_chu;
always@(*) begin
                              xx_0 = xx;
                          end
always@(*) begin
	if(  (xx_0_chu >= (x - fkx + 1) ) | (xx_0_chu >= (x - fkx + 1) ) ) 
		xx_1 = 0;
	else  
		xx_1 = xx_0_chu ; 
	end
reg [`MAX_KX_LOG-1:0] kkx_0;
reg [`MAX_KX_LOG-1:0] kkx_0_chu;
reg [`MAX_KX_LOG-1:0] kkx_1;
reg [`MAX_KX_LOG-1:0] kkx_1_chu;
always@(*) begin
                              kkx_0 = kkx;
                          end
always@(*) begin
	if(  (kkx_0_chu >= fkx ) | (kkx_0_chu >= fkx ) ) 
		kkx_1 = 0;
	else  
		kkx_1 = kkx_0_chu ; 
	end
reg [`MAX_KY_LOG-1:0] kky_0;
reg [`MAX_KY_LOG-1:0] kky_0_chu;
reg [`MAX_KY_LOG-1:0] kky_1;
reg [`MAX_KY_LOG-1:0] kky_1_chu;
always@(*) begin
                              kky_0 = kky;
                          end
always@(*) begin
	if(  (kky_0_chu >= fky ) | (kky_0_chu >= fky ) ) 
		kky_1 = 0;
	else  
		kky_1 = kky_0_chu ; 
	end
reg [`MAX_I_LOG-1:0] ii_0;
reg [`MAX_I_LOG-1:0] ii_0_chu;
reg [`MAX_I_LOG-1:0] ii_1;
reg [`MAX_I_LOG-1:0] ii_1_chu;
always@(*) begin
                              ii_0 = ii;
                          end
always@(*) begin
	if(  (ii_0_chu >= ic ) | (ii_0_chu >= ic ) ) 
		ii_1 = 0;
	else  
		ii_1 = ii_0_chu ; 
	end
reg [`MAX_N_LOG-1:0] nn_0;
reg [`MAX_N_LOG-1:0] nn_0_chu;
reg [`MAX_N_LOG-1:0] nn_1;
reg [`MAX_N_LOG-1:0] nn_1_chu;
always@(*) begin
                              nn_0 = nn;
                          end
always@(*) begin
	if(  (nn_0_chu >= nc ) | (nn_0_chu >= nc ) ) 
		nn_1 = 0;
	else  
		nn_1 = nn_0_chu ; 
	end
reg [`MAX_B_LOG-1:0] bb_0;
reg [`MAX_B_LOG-1:0] bb_0_chu;
reg [`MAX_B_LOG-1:0] bb_1;
reg [`MAX_B_LOG-1:0] bb_1_chu;
always@(*) begin
                              bb_0 = bb;
                          end
always@(*) begin
	if(  (bb_0_chu >= batch ) | (bb_0_chu >= batch ) ) 
		bb_1 = 0;
	else  
		bb_1 = bb_0_chu ; 
	end
always@(*) begin
		yy_0_chu =yy_0+1*stride;
	end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) ))		xx_0_chu = xx_0+1*stride;
	else  
		xx_0_chu = xx_0; 
end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) )&( (xx_0+1*stride >= (x - fkx + 1) ) | (xx_0+1*stride >= (x - fkx + 1) ) ))		kkx_0_chu = kkx_0+1;
	else  
		kkx_0_chu = kkx_0; 
end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) )&( (xx_0+1*stride >= (x - fkx + 1) ) | (xx_0+1*stride >= (x - fkx + 1) ) )&( (kkx_0+1 >= fkx ) | (kkx_0+1 >= fkx ) ))		kky_0_chu = kky_0+1;
	else  
		kky_0_chu = kky_0; 
end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) )&( (xx_0+1*stride >= (x - fkx + 1) ) | (xx_0+1*stride >= (x - fkx + 1) ) )&( (kkx_0+1 >= fkx ) | (kkx_0+1 >= fkx ) )&( (kky_0+1 >= fky ) | (kky_0+1 >= fky ) ))		ii_0_chu = ii_0+4;
	else  
		ii_0_chu = ii_0; 
end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) )&( (xx_0+1*stride >= (x - fkx + 1) ) | (xx_0+1*stride >= (x - fkx + 1) ) )&( (kkx_0+1 >= fkx ) | (kkx_0+1 >= fkx ) )&( (kky_0+1 >= fky ) | (kky_0+1 >= fky ) )&( (ii_0+4 >= ic ) | (ii_0+4 >= ic ) ))		nn_0_chu = nn_0+4;
	else  
		nn_0_chu = nn_0; 
end
always@(*) begin
	if(( (yy_0+1*stride >= (y - fky + 1) ) | (yy_0+1*stride >= (y - fky + 1) ) )&( (xx_0+1*stride >= (x - fkx + 1) ) | (xx_0+1*stride >= (x - fkx + 1) ) )&( (kkx_0+1 >= fkx ) | (kkx_0+1 >= fkx ) )&( (kky_0+1 >= fky ) | (kky_0+1 >= fky ) )&( (ii_0+4 >= ic ) | (ii_0+4 >= ic ) )&( (nn_0+4 >= nc ) | (nn_0+4 >= nc ) ))		bb_0_chu = bb_0+1;
	else  
		bb_0_chu = bb_0; 
end
always@(*) begin
		yy_1_chu =yy_1+1*stride;
	end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) ))		xx_1_chu = xx_1+1*stride;
	else  
		xx_1_chu = xx_1; 
end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) )&( (xx_1+1*stride >= (x - fkx + 1) ) | (xx_1+1*stride >= (x - fkx + 1) ) ))		kkx_1_chu = kkx_1+1;
	else  
		kkx_1_chu = kkx_1; 
end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) )&( (xx_1+1*stride >= (x - fkx + 1) ) | (xx_1+1*stride >= (x - fkx + 1) ) )&( (kkx_1+1 >= fkx ) | (kkx_1+1 >= fkx ) ))		kky_1_chu = kky_1+1;
	else  
		kky_1_chu = kky_1; 
end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) )&( (xx_1+1*stride >= (x - fkx + 1) ) | (xx_1+1*stride >= (x - fkx + 1) ) )&( (kkx_1+1 >= fkx ) | (kkx_1+1 >= fkx ) )&( (kky_1+1 >= fky ) | (kky_1+1 >= fky ) ))		ii_1_chu = ii_1+4;
	else  
		ii_1_chu = ii_1; 
end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) )&( (xx_1+1*stride >= (x - fkx + 1) ) | (xx_1+1*stride >= (x - fkx + 1) ) )&( (kkx_1+1 >= fkx ) | (kkx_1+1 >= fkx ) )&( (kky_1+1 >= fky ) | (kky_1+1 >= fky ) )&( (ii_1+4 >= ic ) | (ii_1+4 >= ic ) ))		nn_1_chu = nn_1+4;
	else  
		nn_1_chu = nn_1; 
end
always@(*) begin
	if(( (yy_1+1*stride >= (y - fky + 1) ) | (yy_1+1*stride >= (y - fky + 1) ) )&( (xx_1+1*stride >= (x - fkx + 1) ) | (xx_1+1*stride >= (x - fkx + 1) ) )&( (kkx_1+1 >= fkx ) | (kkx_1+1 >= fkx ) )&( (kky_1+1 >= fky ) | (kky_1+1 >= fky ) )&( (ii_1+4 >= ic ) | (ii_1+4 >= ic ) )&( (nn_1+4 >= nc ) | (nn_1+4 >= nc ) ))		bb_1_chu = bb_1+1;
	else  
		bb_1_chu = bb_1; 
end
always@(posedge clk or negedge rst_n) begin
                  if(~rst_n) begin
                        kkx = 0;
                        kky = 0;
                        xx = 0;
                        yy = 0;
                        xxx = 0;
                        yyy = 0;
                        nn = 0;
                        ii = 0;
                        nnn = 0;
                        iii = 0;
                        bb = 0;
                   end else begin
                        if(psum_read_en)begin
                                kkx = kkx_1;
                        kky = kky_1;
                        xx = xx_1;
                        yy = yy_1;
                        nn = nn_1;
                        ii = ii_1;
                        bb = bb_1;
          end
                   end
              end
wire start; 
               reg    start_; 
always@(posedge clk) begin
                if(accum_en_)
                start_ <= start;
              end
wire done, ic_done, fkx_done, fky_done;
reg [ `PSUM_BUF_ROWS_LOG2 - 1 : 0] psum_res [0:`PSUM_BUF_ROWS -1];
reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_addr;
reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_raddr_addr;
reg [`PSUM_BUF_ROWS_LOG2 - 1:0] psum_res_raddr;
assign start = (ii == 0 & kkx == 0 & kky == 0);
reg [`MAX_X_LOG-1:0] SUM_xx;
reg [`MAX_Y_LOG-1:0] SUM_yy;
reg [`MAX_KX_LOG-1:0] SUM_kkx;
reg [`MAX_KY_LOG-1:0] SUM_kky;
reg [`MAX_N_LOG-1:0] SUM_nn;
reg [`MAX_I_LOG-1:0] SUM_ii;
reg [`MAX_B_LOG-1:0] SUM_bb;
reg [ `PSUM_BUF_DATA  - 1 :0] zi_buf_p1;reg [ `PSUM_BUF_DATA  - 1 :0] zi_buf_p2;reg psum_read_en_p1;
reg psum_read_en_p2;
reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr_p1;
reg [ `PSUM_BUF_ROWS_LOG2  - 1 :0] psum_read_addr_p2;
reg RAW_stall, RAW_STALL2;
reg result_done_;
always@(posedge clk) begin
                if(~rst_n) begin
                      SUM_xx <= 0;
                      SUM_yy  <= 0;
                      SUM_kkx <= 0;
                      SUM_kky <= 0;
                      SUM_nn  <= 0;
                      SUM_bb  <= 0;
                      SUM_ii  <= 0;
                end else begin 
                if(accum_en_ & ~RAW_stall) begin
                      SUM_xx <= xx;
                      SUM_yy  <= yy;
                      SUM_kkx <= kkx;
                      SUM_kky <= kky;
                      SUM_nn  <= nn;
                      SUM_bb  <= bb;
                      SUM_ii  <= ii;
                end
              end
            end
always@(*) begin
                        RAW_stall = (psum_read_addr == psum_write_addr) &psum_write_en& ~start;
                  end
reg accum_en_next;
always@(posedge clk) begin 
                        accum_en_next <= accum_en_;
                  end
always@(posedge clk or negedge rst_n) begin
                    if(~rst_n) begin 
                           RAW_STALL2 <= 0; 
                    end else begin 
                    if(accum_en_next)
                        RAW_STALL2 <= (psum_read_addr == psum_write_addr) & psum_write_en & ~start;
                    end
                  end
always@(*) begin
                        ACC_stalled <= RAW_stall;
                  end
always@(posedge clk) begin
                    psum_read_addr_p1 <= ((((0*((batch/1)>> TB_shift)+  ((bb/1)>> TB_shift))*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*((( x-fkx+1 +  1 -1 )/1) >> TX_shift)+  ((xx/1)>> TX_shift))*((( x-fkx+1 + 1 -1 )/1) >> TY_shift)+  ((yy/1)>> TY_shift));
                    psum_read_addr_p2 <= psum_read_addr;
                end
always@(*) begin
                    psum_read_addr <= ((((0*((batch/1)>> TB_shift)+  ((bb/1)>> TB_shift))*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*((( x-fkx+1 +  1 -1 )/1) >> TX_shift)+  ((xx/1)>> TX_shift))*((( x-fkx+1 + 1 -1 )/1) >> TY_shift)+  ((yy/1)>> TY_shift));//read_stalled?  psum_read_addr_p2 : ((((0*((batch/1)>> TB_shift)+  ((bb/1)>> TB_shift))*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*((( x-fkx+1 +  1 -1 )/1) >> TX_shift)+  ((xx/1)>> TX_shift))*((( x-fkx+1 + 1 -1 )/1) >> TY_shift)+  ((yy/1)>> TY_shift));
                end
always@(*) begin
                    psum_read_en <= accum_en_ & ~RAW_stall;
                end
always@(posedge clk) begin
                    //if(psum_read_en) begin
                        zi_buf_p1 <= zi_buf;
                        zi_buf_p2 <= zi_buf_p1;
                    //end
                end
reg stalled, read_stalled;
always@(posedge clk) begin
                        stalled <= 0;//RAW_STALL2;
                        read_stalled <= RAW_stall;
                end
reg start__;
always@(posedge clk) begin 
                    start__ <= start_;
                  end
reg result_done__;
always@(posedge clk or negedge rst_n) begin 
                    if(~rst_n) result_done__ <= 0;
                    else result_done__ <= result_done_;
                  end
always@(*) begin 
                if(psum_read_en) begin 
                    if( start_ & ~result_done__ ) begin
                    psum_write_data <= stalled? zi_buf_p2: zi_buf_p1; 
                end else begin
                       psum_write_data[(0+1)*`MAX_ACC_PRECISION-1:(0)*`MAX_ACC_PRECISION] <= (stalled? zi_buf_p2[(0+1)*`MAX_ACC_PRECISION-1:(0)*`MAX_ACC_PRECISION]: zi_buf_p1[(0+1)*`MAX_ACC_PRECISION-1:(0)*`MAX_ACC_PRECISION]) + psum_read_data[(0+1)*`MAX_ACC_PRECISION-1:(0)*`MAX_ACC_PRECISION]; 
psum_write_data[(1+1)*`MAX_ACC_PRECISION-1:(1)*`MAX_ACC_PRECISION] <= (stalled? zi_buf_p2[(1+1)*`MAX_ACC_PRECISION-1:(1)*`MAX_ACC_PRECISION]: zi_buf_p1[(1+1)*`MAX_ACC_PRECISION-1:(1)*`MAX_ACC_PRECISION]) + psum_read_data[(1+1)*`MAX_ACC_PRECISION-1:(1)*`MAX_ACC_PRECISION]; 
psum_write_data[(2+1)*`MAX_ACC_PRECISION-1:(2)*`MAX_ACC_PRECISION] <= (stalled? zi_buf_p2[(2+1)*`MAX_ACC_PRECISION-1:(2)*`MAX_ACC_PRECISION]: zi_buf_p1[(2+1)*`MAX_ACC_PRECISION-1:(2)*`MAX_ACC_PRECISION]) + psum_read_data[(2+1)*`MAX_ACC_PRECISION-1:(2)*`MAX_ACC_PRECISION]; 
psum_write_data[(3+1)*`MAX_ACC_PRECISION-1:(3)*`MAX_ACC_PRECISION] <= (stalled? zi_buf_p2[(3+1)*`MAX_ACC_PRECISION-1:(3)*`MAX_ACC_PRECISION]: zi_buf_p1[(3+1)*`MAX_ACC_PRECISION-1:(3)*`MAX_ACC_PRECISION]) + psum_read_data[(3+1)*`MAX_ACC_PRECISION-1:(3)*`MAX_ACC_PRECISION]; 
 
                end
              end
            end
always@(posedge clk) begin
                    psum_write_en <= psum_read_en;
                  end
always@(posedge clk) begin
                    psum_write_addr <= psum_read_addr;
                  end
assign done = ic_done & fkx_done & fky_done & accum_en;
assign fkx_done =  (fkx < (1>> TKX_shift) )|(kkx+ (1>> TKX_shift) >=  fkx);
assign fky_done =  (fky < (1>> TKY_shift) )|(kky+ (1>> TKY_shift) >=  fky);
assign ic_done = (ic < (4>> TI_shift) )| (iii+ii + (4>> TI_shift)  >=  ic  );
wire nc_done, b_done, x_done, y_done;
assign nc_done =  (nc < (4>> TN_shift) )| (nnn+nn + (4>> TN_shift)  >= nc  );
assign b_done =  (bb < (1>> TB_shift) )| (bb + (1>> TB_shift)  >= nc  );
assign x_done =  (x < (1>> TX_shift) )| (xxx+xx + (1>> TX_shift)  >= x -fkx+1 );
assign y_done =  (y < (1>> TY_shift) )| (yyy+yy + (1>> TY_shift)  >= y -fky+1 );
assign acc_done = fkx_done&  fky_done&ic_done&nc_done&b_done&x_done&y_done& accum_en;
always@(posedge clk or negedge rst_n) begin
            if(~rst_n) begin 
                  result_done_ <= 0;  
            end else begin
                if(acc_done) begin
                   result_done_ <=  acc_done ;   
                end
            end
              end
always@(posedge clk) begin
                result_done <= result_done_;//result_done_ & ~start;
            end
reg first = 0;
assign out_buf_write_ready = start & first & ~out_buf_write_valid;
always@(posedge clk) begin
                if(start & first) begin
                   out_buf_write_data = psum_read_data; 
                   //out_buf_write_ready = 1;
                end
              end
always@(posedge clk or negedge rst_n) begin
               if(~rst_n) begin
                    out_buf_write_addr = 0;
                end else begin
                if(out_buf_write_valid) begin;
                    out_buf_write_addr = out_buf_write_addr + 1;
                    //out_buf_write_ready = 0;
                end
                end
              end
always@(posedge clk)begin
                if(done) begin
                    first = 1;
                end 
                end
always@(posedge clk) begin
                    done_done <= done;
            end
reg done_done_done;always@(posedge clk) begin
                    done_done_done = done_done;
            end
always@(negedge clk) begin
                if(done_done) begin
            $display("PSUM_DONE");
                //, "t%h",zi_buf + psum_read_data, "	%h",zi_buf, psum_write_data, "	%h",psum_read_data);  
                    //  ;
$display("	%d", write_dat_0,"	%d", write_dat_1,"	%d", write_dat_2,"	%d", write_dat_3);
                end
              end
            
        endmodule
