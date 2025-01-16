module ADDR_CNT(
            input clk,
            input rst_n,
                
            input addr_cnt_en,
            output reg operation_done,
                
        input [`MAX_PADDING_X_LOG-1:0] padding_x,
        input [`MAX_PADDING_Y_LOG-1:0] padding_y,
            input [`MAX_STRIDE_LOG-1:0] stride,
            input [`MAX_KX_LOG-1:0] fkx,
            input [`MAX_KY_LOG-1:0] fky,
            input  [`MAX_X_LOG-1:0] x,
            input  [`MAX_Y_LOG-1:0] y,
            input  [`MAX_N_LOG-1:0] nc,
            input  [`MAX_I_LOG-1:0] ic,
            input  [`MAX_B_LOG-1:0] batch,
            input [5:0] wei_precision,
            input [5:0] act_precision,
                
            output reg wei_L2_buf_read_ready, 
            input  wei_L2_buf_read_valid, 
            output reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_read_addr, 
            input  [`WEI_BUF_DATA*1-1 :0] wei_L2_buf_read_data, 
                
            output reg act_L2_buf_read_ready, 
            input  act_L2_buf_read_valid, 
            output reg [`L2_ACT_BUF_ROWS_LOG2   - 1 :0] act_L2_buf_read_addr, 
            input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, 
                
            output reg act_L1_buf_write_en,
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_write_addr, 
            output  [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, 
                
            output  reg wei_L1_buf_write_en,
            output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr, 
            output  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, 
                
            output reg act_L1_buf_read_en,
            output reg [`ACT_BUF_ROWS_LOG2   - 1 :0] act_L1_buf_read_addr, 
                
            output reg  wei_L1_buf_read_en,
            output reg [`WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_read_addr, 
                
            output reg mac_en,
            
        output reg [`MAX_KX_LOG-1:0] kkx,
        output reg [`MAX_KY_LOG-1:0] kky,
        output reg [`MAX_X_LOG-1:0] xx,
        output reg [`MAX_Y_LOG-1:0] yy, 
        output reg [`MAX_X_LOG-1:0] xxx,
        output reg[`MAX_Y_LOG-1:0] yyy, 
        output  reg[`MAX_N_LOG-1:0] nn, 
        output reg[`MAX_I_LOG-1:0] ii, 
        output reg[`MAX_N_LOG-1:0] nnn, 
        output reg[`MAX_I_LOG-1:0] iii, 
        output reg[`MAX_B_LOG-1:0] bb,
            
        output reg [`MAX_KX_LOG-1:0] ACC_kkx,
        output reg [`MAX_KY_LOG-1:0] ACC_kky,
        output reg [`MAX_X_LOG-1:0] ACC_xx,
        output reg [`MAX_Y_LOG-1:0] ACC_yy, 
        output reg [`MAX_X_LOG-1:0] ACC_xxx,
        output reg[`MAX_Y_LOG-1:0] ACC_yyy, 
        output reg [`MAX_N_LOG-1:0] ACC_nn, 
        output reg[`MAX_I_LOG-1:0] ACC_ii, 
        output reg[`MAX_N_LOG-1:0] ACC_nnn, 
        output reg[`MAX_I_LOG-1:0] ACC_iii, 
        output reg[`MAX_B_LOG-1:0] ACC_bb,
            
        input accum_done,
            
        input pe_array_start,
        input pe_array_ready,
        input pe_array_last,
            
        input ACC_stalled,
            
        output [5:0] jia_sys_jie, 
        output [5:0] yi_sys_jie, 
            
        output reg ACCUM_stall,
            
        input inter_pe_sparse_stall
        );
reg wei_done, act_done;
reg [5:0] a_ratio;reg [5:0] w_ratio;reg [5:0] TX_lv;reg [5:0] TY_lv;reg [5:0] TKX_lv;reg [5:0] TKY_lv;reg [5:0] TN_lv;reg [5:0] TB_lv;reg [5:0] TI_lv;reg [3:0] TX_shift;reg [3:0] TY_shift;reg [3:0] TKX_shift;reg [3:0] TKY_shift;reg [3:0] TN_shift;reg [3:0] TB_shift;reg [3:0] TI_shift;always@(*) begin
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
wire wei_L1_yi_addr;
wire act_L1_yi_addr;
assign wei_L1_yi_addr = 1;
assign act_L1_yi_addr = 1;
reg [1:0] systolic_wei_load;
reg [1:0] systolic_wei_load_nxt;
always@(posedge clk or negedge rst_n) begin
                    if(~rst_n) systolic_wei_load <= 0;
                    else systolic_wei_load <= 0;
                end
always@(posedge clk or negedge rst_n) begin 
                    if (~rst_n) systolic_wei_load_nxt <= 0;
                    else systolic_wei_load_nxt <= systolic_wei_load;
              end
reg initial_mac = 0;
reg wei_initial_L1_read = 0;
reg wei_initial_L1_write = 0;
reg wei_initial_L2_read = 0;
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) wei_initial_L2_read <= 0;
                else begin
                    if(wei_initial_L2_read == 0) wei_initial_L2_read <= addr_cnt_en;
                end
            end
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) wei_initial_L1_write <= 0;
                else begin
                    if(wei_initial_L1_write == 0) wei_initial_L1_write <= wei_L2_buf_read_valid;
                end
            end
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) wei_initial_L1_read <= 0;
                else begin
                    if(wei_initial_L1_read == 0) wei_initial_L1_read <= wei_initial_L1_write;
                end
            end
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) begin
                    initial_mac <= 0;
                end else begin
                    if(initial_mac == 0) begin
                        initial_mac <= wei_initial_L1_read;
                    end
                    end
              end
wire [5:0] L2_L1_wei_jie;
reg [1:0] wei_jie;
reg L2_READ_wei_stall, L1_WRITE_wei_stall, L1_READ_wei_stall, MAC_stall;
reg stall_from_mac;
              always@(*) begin
                  stall_from_mac =    initial_mac& (inter_pe_sparse_stall | ~pe_array_last)  & ~accum_done;
                  L2_READ_wei_stall = (stall_from_mac | L2_L1_wei_jie > 0 | systolic_wei_load > 0 ) & ~accum_done ;
                  L1_WRITE_wei_stall = (stall_from_mac | systolic_wei_load_nxt > 0)& ~accum_done;
                  L1_READ_wei_stall = stall_from_mac & ~accum_done;
                  MAC_stall       = (systolic_wei_load_nxt > 0 | wei_jie > 0);
              end
always@(posedge clk) begin
                ACCUM_stall <= ~mac_en;
              end
reg wei_L1_buf_read_en_pre;
reg wei_L1_buf_read_en_val;
always@(*) begin
                wei_L2_buf_read_ready = wei_initial_L2_read & (~L2_READ_wei_stall | systolic_wei_load > 0 | systolic_wei_load_nxt>0) & ~wei_done;
                wei_L1_buf_write_en   = wei_initial_L1_write& (~L1_WRITE_wei_stall| systolic_wei_load_nxt>0) & ~wei_done;
                    
                wei_L1_buf_read_en_pre    = wei_L1_yi_addr& wei_initial_L1_read& ~L1_READ_wei_stall;
                wei_L1_buf_read_en        = wei_L1_buf_read_en_val;
                mac_en = initial_mac & ~MAC_stall ;
            end
reg L2_READ_act_stall, L1_WRITE_act_stall, L1_READ_act_stall;
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
                        kkx <= 0;
                        kky <= 0;
                        xx <= 0;
                        yy <= 0;
                        xxx <= 0;
                        yyy <= 0;
                        nn <= 0;
                        ii <= 0;
                        nnn <= 0;
                        iii <= 0;
                        bb <= 0;
                   end else begin
                        if(wei_initial_L1_write& ~L1_WRITE_act_stall)begin
                                kkx <= kkx_1;
                        kky <= kky_1;
                        xx <= xx_1;
                        yy <= yy_1;
                        nn <= nn_1;
                        ii <= ii_1;
                        bb <= bb_1;
          end
                   end
              end
reg [31:0] wei_L2_buf_tiled_addr;
reg [31:0] wei_L1_buf_read_tiled_addr;
reg [31:0] wei_L1_buf_write_tiled_addr;
always@(*) begin
                wei_L2_buf_tiled_addr =((((0*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*(((ic+4-1)/4)>> TI_shift)+  ((ii/4)>> TI_shift))*(((fky+1-1)/1)>> TKY_shift)+  ((kky/1)>> TKY_shift))*(((fkx+1-1)/1)>> TKX_shift)+  ((kkx/1)>> TKX_shift));
              end
reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L2_buf_read_addr_pre;
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) begin 
                    wei_L2_buf_read_addr_pre <= 0;
                    wei_L1_buf_write_tiled_addr <= 0;
                end else begin
                    if(wei_initial_L2_read & ~L2_READ_wei_stall) begin
                      wei_L2_buf_read_addr_pre <= wei_L2_buf_read_addr_pre + 1;
                      wei_L1_buf_write_tiled_addr <= wei_L2_buf_tiled_addr;
                    end
                end
              end
always@(*) begin
                wei_L2_buf_read_addr = (systolic_wei_load > 0) ? (wei_L2_buf_read_addr_pre-1)*1 + systolic_wei_load : wei_L2_buf_read_addr_pre*1;
              end
reg [`L2_WEI_BUF_ROWS_LOG2   - 1 :0] wei_L1_buf_write_addr_pre;
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) begin
                    wei_L1_buf_write_addr_pre <= 0;
                    wei_L1_buf_read_tiled_addr <= 0;
                end else begin
                    if(wei_initial_L1_write& ~L1_WRITE_wei_stall) begin
                        wei_L1_buf_read_tiled_addr <= wei_L1_buf_write_tiled_addr;
                        wei_L1_buf_write_addr_pre <= wei_L1_buf_write_addr_pre + 1;
                    end
                end
              end
always@(*) begin
                    //wei_L1_buf_write_addr = wei_L1_buf_write_addr_pre*1 + systolic_wei_load_nxt;
                    wei_L1_buf_write_addr = (systolic_wei_load_nxt > 0) ? (wei_L1_buf_write_addr_pre-1)*1 + systolic_wei_load_nxt :                                         wei_L1_buf_write_addr_pre*1;
              end
reg [31:0] wei_L1_buf_read_addr_pre;
reg [31:0] wei_L1_buf_read_addr_val;
always@(posedge clk) begin
                if(~rst_n) wei_L1_buf_read_addr_pre <= 0;
                else begin
                    if(wei_L1_buf_read_en) wei_L1_buf_read_addr_pre <= ((((0*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*(((ic+4-1)/4)>> TI_shift)+  ((ii/4)>> TI_shift))*(((fky+1-1)/1)>> TKY_shift)+  ((kky/1)>> TKY_shift))*(((fkx+1-1)/1)>> TKX_shift)+  ((kkx/1)>> TKX_shift));
                end
              end
always@(*) begin
                //wei_L1_buf_read_addr_pre <= ((((0*(((nc+4-1)/4)>> TN_shift)+  ((nn/4)>> TN_shift))*(((ic+4-1)/4)>> TI_shift)+  ((ii/4)>> TI_shift))*(((fky+1-1)/1)>> TKY_shift)+  ((kky/1)>> TKY_shift))*(((fkx+1-1)/1)>> TKX_shift)+  ((kkx/1)>> TKX_shift));//wei_L1_buf_read_tiled_addr;
                wei_L1_buf_read_addr <= wei_L1_buf_read_addr_val ;
              end
reg stall_from_wei_sys_load;
always@(*) begin
                stall_from_wei_sys_load = 0;
                wei_L1_buf_read_en_val = wei_L1_buf_read_en_pre;
                wei_L1_buf_read_addr_val = wei_L1_buf_read_addr_pre;
                wei_jie = 0;
                end
assign jia_sys_jie = wei_jie;
always@(*) begin
                  L2_READ_act_stall = stall_from_mac;
                  L1_WRITE_act_stall = stall_from_mac;
                  L1_READ_act_stall = stall_from_mac;
              end
always@(*) begin
                act_L2_buf_read_ready = wei_initial_L2_read  & ~L2_READ_act_stall & ~act_done;
                act_L1_buf_write_en   = wei_initial_L1_write & ~L1_WRITE_act_stall & ~act_done ;
                act_L1_buf_read_en    = act_L1_yi_addr&  wei_initial_L1_read  & ~L1_READ_act_stall   ;
            end
reg [`MAX_X_LOG-1:0] ACT_L1_WRITE_xx;
reg [`MAX_Y_LOG-1:0] ACT_L1_WRITE_yy;
reg [`MAX_KX_LOG-1:0] ACT_L1_WRITE_kkx;
reg [`MAX_KY_LOG-1:0] ACT_L1_WRITE_kky;
reg [`MAX_N_LOG-1:0] ACT_L1_WRITE_nn;
reg [`MAX_I_LOG-1:0] ACT_L1_WRITE_ii;
reg [`MAX_B_LOG-1:0] ACT_L1_WRITE_bb;
reg [`MAX_X_LOG-1:0] ACT_L1_READ_xx;
reg [`MAX_Y_LOG-1:0] ACT_L1_READ_yy;
reg [`MAX_KX_LOG-1:0] ACT_L1_READ_kkx;
reg [`MAX_KY_LOG-1:0] ACT_L1_READ_kky;
reg [`MAX_N_LOG-1:0] ACT_L1_READ_nn;
reg [`MAX_I_LOG-1:0] ACT_L1_READ_ii;
reg [`MAX_B_LOG-1:0] ACT_L1_READ_bb;
always@(posedge clk or negedge rst_n) begin
                    if(~rst_n) begin 
                        act_L2_buf_read_addr <= 0;
                    end else begin
                        if(wei_initial_L2_read & ~L2_READ_act_stall) begin
                          act_L2_buf_read_addr <= act_L2_buf_read_addr + 1;
                          ACT_L1_WRITE_xx <= xx;
                          ACT_L1_WRITE_yy  <= yy;
                          ACT_L1_WRITE_kkx <= kkx;
                          ACT_L1_WRITE_kky <= kky;
                          ACT_L1_WRITE_nn  <= nn;
                          ACT_L1_WRITE_bb  <= bb;
                          ACT_L1_WRITE_ii  <= ii;
                        end
                    end
                  end
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) begin
                    act_L1_buf_write_addr <= 0;
                end else begin
                    if(wei_initial_L1_write& ~L1_WRITE_act_stall) begin
                        act_L1_buf_write_addr <= act_L1_buf_write_addr + 1;
                          ACT_L1_READ_xx <= ACT_L1_WRITE_xx;
                          ACT_L1_READ_yy  <= ACT_L1_WRITE_yy;
                          ACT_L1_READ_kkx <= ACT_L1_WRITE_kkx;
                          ACT_L1_READ_kky <= ACT_L1_WRITE_kky;
                          ACT_L1_READ_nn  <= ACT_L1_WRITE_nn;
                    end
                end
              end
wire [31:0] index_table_addr;
reg [31:0] loop_idx;
reg cond1, cond2, cond3, cond4;
reg reuse;
assign index_table_addr  = (bb)*ic*(x)*(y) + (ii)*(y)*(x)+(kkx+xx)*(y) + (kky+yy);
always@(*) begin 
                       cond1 <= 1&( (kky >= 1>> TY_shift)   &  (yy +1>> TY_shift< ((y + padding_y*2 - fky + 1) / stride  ) ));
                       cond2 <= 1&( (kkx >= 1>> TX_shift)   &  (xx +1>> TX_shift< ((x + padding_x*2 - fkx + 1) / stride  ) ));
                       cond3 <= (& ((( (kkx >= 1>> TX_shift)   &  (xx +1>> TX_shift< ((x + padding_x*2 - fkx + 1) / stride  ) ))) | (( (kky >= 1>> TY_shift)   &  (yy +1>> TY_shift< ((y + padding_y*2 - fky + 1) / stride  ) ))))   );
                       cond4 <= nn>0;
                       reuse <= cond1 | cond2 | cond3 | cond4;
                  end
wire index_table_read_en;
wire index_table_write_en;
assign index_table_read_en = wei_initial_L1_write & ~L1_WRITE_act_stall & reuse ;
assign index_table_write_en = wei_initial_L1_write & ~L1_WRITE_act_stall & ~reuse ;
reg [31:0] index_table_read_data;
ADDR_TABLE addr_table (
                .clk(clk),
                .index_table_read_data(index_table_read_data),
                .index_table_write_data(loop_idx),
                .index_table_read_en(index_table_read_en),
                .index_table_write_en(index_table_write_en),
                .index_table_read_addr(index_table_addr[10-1:0]),
                .index_table_write_addr(index_table_addr[10-1:0])
    );
reg reuse_save;
always@(*) begin
                    act_L1_buf_read_addr = reuse_save?index_table_read_data: loop_idx-1;
                   end
always@(posedge clk or negedge rst_n) begin
              if(~rst_n) begin
                    loop_idx <= 0;
                    reuse_save <= 0;
              end else begin
                if(wei_initial_L1_write& ~L1_WRITE_act_stall) begin 
                    if (reuse) begin
                        reuse_save<=1;
                        //act_L1_buf_read_addr <= index_table[index_table_addr[10-1:0]] ;
                    end else begin
                        reuse_save<=0;
                        //index_table[index_table_addr[10-1:0]] <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];//act_L1_buf_write_addr;
                        //act_L1_buf_read_addr <= loop_idx[ `ACT_BUF_ROWS_LOG2  - 1 :0];
                        loop_idx <= loop_idx+1;
                    end
                end
              end
            end
assign fkx_done =  (fkx < (1>> TKX_shift) )|(kkx+ (1>> TKX_shift) >= fkx);
assign fky_done =  (fky < (1>> TKY_shift) )|(kky+ (1>> TKY_shift) >= fky);
assign ic_done = (ic < (4>> TI_shift) )| (iii+ii + (4>> TI_shift)  >= ic  );
assign nc_done =  (nc < (4>> TN_shift) )| (nnn+nn + (4>> TN_shift)  >= nc  );
assign b_done =  (bb < (1>> TN_shift) )| (bb + (1>> TB_shift)  >= nc  );
assign x_done =  (x < (1>> TN_shift) )| (xxx+xx + (1>> TX_shift)  >= x -fkx+1 );
assign y_done =  (y < (1>> TN_shift) )| (yyy+yy + (1>> TY_shift)  >= y -fky+1 );
always@(*) begin
operation_done = (fkx_done) & (fky_done) & (ic_done) & (nc_done) & (x_done) & (y_done) & (b_done);
end
wire [31:0] X_VOL = (1>> TX_shift)<=fkx ?  x : ((x+(1>> TX_shift)-1)/(1>> TX_shift))*fkx;
wire [31:0] Y_VOL = (1>> TY_shift)<=fky ?  y : ((y+(1>> TY_shift)-1)/(1>> TY_shift))*fky;
wire [31:0] ACT_VOL =X_VOL*Y_VOL*((ic+4-1)/4); //(x)*(y)*((ic+4-1)/4);
//(((x+(1>> TX_shift)-1)/(1>> TX_shift))*((y+(1>> TY_shift)-1)/(1>> TY_shift))*((ic+4-1)/4));
always@(posedge clk or negedge rst_n) begin
                    if(~rst_n) begin
                        act_done <= 0;
                    end else begin 
                      if(act_L2_buf_read_addr > ACT_VOL)begin
                        act_done <= 1;
                    end
                    end
                end
wire [31:0] WEI_VOL = ((fkx+1-1)/1)*((fky+1-1)/1)*((ic+4-1)/4)*((nc+4-1)/4);;
always@(posedge clk or negedge rst_n) begin
                    if(~rst_n) begin
                        wei_done <= 0;
                    end else begin 
                      if(wei_L2_buf_read_addr_pre > WEI_VOL)begin
                        wei_done <= 1;
                    end
                    end
                end
L2_interconnect_L1 L2lianjieL1(
             .clk(clk),
             .rst_n(rst_n),
            .act_L1_buf_write_data(act_L1_buf_write_data), 
                 .wei_L1_buf_write_data(wei_L1_buf_write_data), 
                .act_L2_buf_read_data(act_L2_buf_read_data), 
             .wei_L2_buf_read_data(wei_L2_buf_read_data) ,
                 
            .L2_L1_wei_jie(L2_L1_wei_jie),
            .wei_L2_buf_read_valid(wei_L2_buf_read_valid),
            .wei_L1_buf_write_en(wei_L1_buf_write_en)
	);
endmodule
module L2_interconnect_L1(
             input clk,
              input rst_n,
            output reg [`ACT_BUF_DATA - 1:0] act_L1_buf_write_data, 
                 output reg  [`WEI_BUF_DATA -1 :0] wei_L1_buf_write_data, 
                input  [`ACT_BUF_DATA -1 :0] act_L2_buf_read_data, 
             input  [`WEI_BUF_DATA*1 -1 :0] wei_L2_buf_read_data, 
                 
            output reg [5:0] L2_L1_wei_jie,
            input wei_L2_buf_read_valid,
            input wei_L1_buf_write_en
	);
             always@(posedge clk) begin
                act_L1_buf_write_data <= act_L2_buf_read_data;
              end

 		
        //always@(posedge clk) begin
         //       wei_L1_buf_write_data <= wei_L2_buf_read_data;
         //     end
	
always@(posedge clk or negedge rst_n) begin
                if(~rst_n) begin
                    L2_L1_wei_jie <= 0; 
                end else begin 
                        if(L2_L1_wei_jie == 0 & wei_L2_buf_read_valid) begin 
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % 1; 
                        end else if(wei_L1_buf_write_en) begin 
                                L2_L1_wei_jie <= (L2_L1_wei_jie+1) % 1; 
                        end 
                end 
              end
always@(posedge clk) begin
if(L2_L1_wei_jie == 0 & ( wei_L1_buf_write_en | wei_L2_buf_read_valid ) ) begin
                      wei_L1_buf_write_data <= wei_L2_buf_read_data[`WEI_BUF_DATA*1-1:`WEI_BUF_DATA*0];
                  end
end
endmodule
module ADDR_TABLE(
            input clk,
            output reg [31:0] index_table_read_data,
            input [31:0] index_table_write_data,
            input  index_table_read_en,
            input index_table_write_en,
            input [10-1:0] index_table_read_addr,
	    input [10-1:0] index_table_write_addr
);
    reg [ `ACT_BUF_ROWS_LOG2  - 1 :0] index_table [0:1024];
                always@(posedge clk) begin
                    if(index_table_read_en)
                        index_table_read_data = index_table[index_table_read_addr]  ;
                end
                 
                always@(posedge clk) begin
                    if(index_table_write_en)
                        index_table[index_table_write_addr] = index_table_write_data ;
                end
            endmodule
