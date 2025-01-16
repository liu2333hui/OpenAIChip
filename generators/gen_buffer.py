
#Buffer's require negedge reversed to work
def create_buffer(buf_rows_name, buf_data_name, module_name, read_delay = 0,edge="posedge"):

    
    s = "module "+module_name+"(\n\
            input read_clk,\n\
            input write_clk,\n\
            input read_en,\n\
            input rst_n, \n\
            input [`"+buf_rows_name+"_LOG2" + " - 1 : 0] read_addr,\n\
            output reg [`"+buf_data_name+" - 1 : 0] read_data,\n\
            input write_en,\n\
            input [`"+buf_rows_name+"_LOG2" + " - 1 : 0] write_addr,\n\
            input [`"+buf_data_name+" - 1 : 0] write_data);\n\
            reg [`"+buf_data_name+" - 1 : 0] mem [0 : `"+buf_rows_name+" -1];\n\
            always@("+edge+" read_clk or negedge rst_n) begin\n\
                if(~rst_n) begin\n\
                    read_data <= 0; \n\
                end else begin\n\
               if(read_en) begin\n\
                   read_data <= #("+str(read_delay)+") mem[read_addr]; \n\
               end else begin\n\
                   read_data <= read_data; \n\
               end\n\
               end\n\
            end\n\
            \n\
            always@("+edge+" write_clk) begin\n\
                if(write_en) begin\n\
                    mem[write_addr] <= write_data;\n\
                end else begin\n\
                    //wu \n\
                end\n\
            end\n\
            \n\
            endmodule\n"

    
    return s

import numpy as np
def create_buffer_banks(buf_rows_name, buf_data_name, module_name, hardware_config, macro_cfg, read_delay = 0, edge = "posedge"):

    #
    macro_cfg = macro_cfg
    hardware_config = hardware_config

    #2prf (i.e. optim?) (Todos)
    X_UNIT = hardware_config.get("SRAMS",{}).get("L1_SRAM_UNITS", [512, 8])[0][1] 
    Y_UNIT = hardware_config.get("SRAMS",{}).get("L1_SRAM_UNITS", [512, 8])[0][0]
    Y_UNIT_LOG = int(np.log2(Y_UNIT))

    #X_BANKS
    ROW_DATA = macro_cfg[buf_data_name]
    X_BANKS = ROW_DATA // X_UNIT
        
    #Y_BANKS
    GAO_DATA = macro_cfg[buf_rows_name]
    Y_BANKS = GAO_DATA // Y_UNIT
    
    s = "module "+module_name+"(\n\
            input read_clk,\n\
            input write_clk,\n\
            input read_en,\n\
            input rst_n, \n\
            input [`"+buf_rows_name+"_LOG2" + " - 1 : 0] read_addr,\n\
            output reg [`"+buf_data_name+" - 1 : 0] read_data,\n\
            input write_en,\n\
            input [`"+buf_rows_name+"_LOG2" + " - 1 : 0] write_addr,\n\
            input [`"+buf_data_name+" - 1 : 0] write_data);\n\
            //reg [`"+buf_data_name+" - 1 : 0] mem [0 : `"+buf_rows_name+" -1];\n\
            \n"

    
    for x in range(X_BANKS):
        for y in range(Y_BANKS):
            s += "\n"
            idx = x + y*X_BANKS
            s += "wire [%d-1:0] read_data_%d_%d;\n" %(X_UNIT,y,x)
            s += "wire [%d-1:0] read_addr_%d_%d;\n" %(Y_UNIT_LOG,y,x)
            s += "wire [%d-1:0] write_data_%d_%d;\n" %(X_UNIT,y,x)
            s += "wire [%d-1:0] write_addr_%d_%d;\n" %(Y_UNIT_LOG,y,x)
            s += "wire read_en_%d_%d;\n"  %(y,x)
            s += "wire write_en_%d_%d;\n" %(y,x)


            s += "assign read_addr_%d_%d = read_addr[%d-1:0];\n" %(y,x, Y_UNIT_LOG)

            s += "assign write_addr_%d_%d = write_addr[%d-1:0];\n" %(y,x, Y_UNIT_LOG)

            s += "assign write_data_%d_%d = write_data[(%d+1)*%d-1:%d*%d];\n" %(y,x,   x,X_UNIT, x,X_UNIT)

            s += "assign read_en_%d_%d =  (read_addr[`"%(y,x)+buf_rows_name+"_LOG2" + " - 1 : %d ]  ==%d)? read_en: 0;\n" % (       Y_UNIT_LOG,       y)
            s += "assign write_en_%d_%d = (write_addr[`"%(y,x)+buf_rows_name+"_LOG2" + " - 1 : %d ] ==%d)? write_en:0;\n"  %(  Y_UNIT_LOG,    y)


    for x in range(X_BANKS):
        for y in range(Y_BANKS):
            s += "L1_SRAM_%d_%d sram_%d_%d(" %(Y_UNIT,X_UNIT,y,x)            
            s += ".read_clk(read_clk),\n"
            s += ".write_clk(write_clk),\n"
            s += ".read_en(read_en_%d_%d),\n" %(y,x)     
            s += ".rst_n(rst_n), \n" 
            s += ".read_addr(read_addr_%d_%d), \n"  %(y,x)
            s += ".read_data(read_data_%d_%d), \n"  %(y,x)
            s += ".write_en(write_en_%d_%d), \n" %(y,x)
            s += ".write_addr(write_addr_%d_%d),\n"%(y,x)
            s += ".write_data(write_data_%d_%d));\n"%(y,x)

    s += "reg [`"+buf_rows_name+"_LOG2" + " - 1 : 0]  read_addr_save;\n"

    s += "always@(posedge read_clk) begin\n\
        if(read_en) read_addr_save <= read_addr;\n\
          end\n"


    s += "always@(*) begin\n"
    for y in range(Y_BANKS):
         s += "if(read_addr_save[`"+buf_rows_name+"_LOG2" + " - 1 : %d ] == %d) begin\n" %(Y_UNIT_LOG,y)
         s += ""
         for x in range(X_BANKS):
             idx = "(%d+1)*%d-1:%d*%d" %(x, X_UNIT, x, X_UNIT)
             s += "read_data[%s] = read_data_%d_%d;\n" %(idx, y, x)
         s += "end\n"

    s += "end\n"
    
    s += "\n\
            endmodule\n"



    return s


def create_wei_buffer(hardware_config, meta_config, macro_cfg):


    #多少个存的...
    ACTUAL_BANKS = 1

    #1.L2_L1 WINDOW, BANKS itself, SPARSE_WINDOW, SYSTOLIC does not affect banking directly
    WEI_L2_L1_BW_RATIO = hardware_config["WEI_L2_L1_BW_RATIO"]
    TILE_BANKS = hardware_config["WEI_BANKS"]
    SPARSE_WINDOWS = macro_cfg.get("WEI_WINDOW", 1)


    READ_PORTS = SPARSE_WINDOWS
    WRITE_PORTS = WEI_L2_L1_BW_RATIO

    ACTUAL_BANKS = max(READ_PORTS, WRITE_PORTS) * TILE_BANKS

    read_delay = hardware_config["WEI_L1_READ_DELAY"]

    ROW_BANKS = 1 #(TODOS if there are constraints here)
    

    #IMPLEMENTATION : (TODOS) SRAM COPMILE
    #To take into account of constraints
    
    
    
    #IMPLEMENTATION : REGISTERS
    
    s = "module WEI_BUF (\n\
            input read_clk,\n\
            input write_clk,\n\
            input read_en,\n\
            input rst_n, \n\
            input [`WEI_BUF_ROWS_LOG2  - 1 : 0] read_addr,\n\
            output reg [`WEI_BUF_DATA*"+str(READ_PORTS)+"*"+str(TILE_BANKS)+" - 1 : 0] read_data,\n\
            input write_en,\n\
            input [`WEI_BUF_ROWS_LOG2  - 1 : 0] write_addr,\n\
            input [`WEI_BUF_DATA*"+str(WRITE_PORTS)+"*"+str(TILE_BANKS)+" - 1 : 0] write_data);\n\
                \n"
    for row in range(ROW_BANKS):
        for bank in range(ACTUAL_BANKS):
            idx = str(bank)+"_r"+str(row)
            s += "reg [`WEI_BUF_DATA - 1 : 0] mem_"+idx+" [0 : `"+buf_rows_name+" -1];\n"
            s += "wire [`WEI_BUF_ROWS_LOG2  - 1 : 0] write_addr_"+idx + ';\n'
            s += "wire [`WEI_BUF_ROWS_LOG2  - 1 : 0] read_addr_"+idx + ';\n'

            s += "assign write_addr_"+idx + ' = ;\n'
            s += "assign read_addr_"+idx + '  = ;\n'


            
    for row in range(ROW_BANKS):
        for bank in range(WRITE_PORTS*TILE_BANKS):
            pass
            
    for row in range(ROW_BANKS):
        for bank in range(WRITE_PORTS*TILE_BANKS):            
            s += "reg [`WEI_BUF_ROWS_LOG2  - 1 : 0] read_addr_"+idx + ';\n'


            s += "always@(*) begin\n\
                      read_addr_"+idx + " =  read_addr ;  \n\
                  end\n"

            
            s += "always@("+edge+" read_clk or negedge rst_n) begin\n\
                        if(~rst_n) begin\n\
                            read_data <= 0; \n\
                        end else begin\n\
                       if(read_en) begin\n\
                           read_data <= #("+str(read_delay)+") mem[read_addr]; \n\
                       end else begin\n\
                           read_data <= read_data; \n\
                       end\n\
                       end\n\
                    end\n"
            
            s += "always@("+edge+" write_clk) begin\n\
                        if(write_en) begin\n\
                            mem[write_addr] <= write_data;\n\
                        end else begin\n\
                            //wu \n\
                        end\n\
                    end\n\
                    \n"

    

    s += "\n\
            endmodule\n"
    return s



#assume delays are one for this buffer's read
def gen_buffers(hardware_config, meta_config, macro_cfg):
    print("\n// GEN_BUFFERS VERILO\n")
    f = open(meta_config["dossier"]+"/buffers.v", "w")

    s = ""


    #print(hardware_config.get("SRAMS", {}).get("L1_SRAM", None))
    #exit(0)
    if(hardware_config.get("SRAMS", {}).get("L1_SRAM", None) == None):
        #exit(0)
    
        #s = create_wei_buffer(hardware_config, meta_config, macro_cfg)
        
        s = create_buffer("WEI_BUF_ROWS", "WEI_BUF_DATA", "WEI_BUF", edge="negedge")
        s += create_buffer("ACT_BUF_ROWS", "ACT_BUF_DATA", "ACT_BUF", edge="negedge") #negedge for now
        s += create_buffer("PSUM_BUF_ROWS", "PSUM_BUF_DATA", "PSUM_BUF", edge="negedge")

        #IF SPARSE_MAP
        if("ACT_SPARSITY_MAP_BUF_DATA" in macro_cfg and macro_cfg["ACT_SPARSITY_MAP_BUF_DATA"] > 0):
            s += create_buffer("ACT_BUF_ROWS", "ACT_SPARSITY_MAP_BUF_DATA", "ACT_SPARSITY_MAP_BUF", edge="negedge")

        if("WEI_SPARSITY_MAP_BUF_DATA" in macro_cfg and macro_cfg["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
            s += create_buffer("WEI_BUF_ROWS", "WEI_SPARSITY_MAP_BUF_DATA", "WEI_SPARSITY_MAP_BUF", edge="negedge")
    else:
        s = create_buffer_banks("WEI_BUF_ROWS", "WEI_BUF_DATA", "WEI_BUF", hardware_config=hardware_config, macro_cfg=macro_cfg,edge="negedge")
        s += create_buffer_banks("ACT_BUF_ROWS", "ACT_BUF_DATA", "ACT_BUF", hardware_config=hardware_config, macro_cfg=macro_cfg,edge="negedge") #negedge for now
        s += create_buffer_banks("PSUM_BUF_ROWS", "PSUM_BUF_DATA", "PSUM_BUF", hardware_config=hardware_config, macro_cfg=macro_cfg,edge="negedge")

        #IF SPARSE_MAP
        if("ACT_SPARSITY_MAP_BUF_DATA" in macro_cfg and macro_cfg["ACT_SPARSITY_MAP_BUF_DATA"] > 0):
            s += create_buffer_banks("ACT_BUF_ROWS", "ACT_SPARSITY_MAP_BUF_DATA", "ACT_SPARSITY_MAP_BUF", hardware_config=hardware_config, macro_cfg=macro_cfg,edge="negedge")

        if("WEI_SPARSITY_MAP_BUF_DATA" in macro_cfg and macro_cfg["WEI_SPARSITY_MAP_BUF_DATA"] > 0):
            s += create_buffer_banks("WEI_BUF_ROWS", "WEI_SPARSITY_MAP_BUF_DATA", "WEI_SPARSITY_MAP_BUF", hardware_config=hardware_config, macro_cfg=macro_cfg,edge="negedge")
        
    f.write(s)
    f.close()

    print("\n// GEN_BUFFERS VERILOG - DONE\n")



