######################################################

#Multi-precision support
ACT_SUPPORTED_PRECISION = [8]
ACT_MAX_PRECISION = max(ACT_SUPPORTED_PRECISION)

WEI_SUPPORTED_PRECISION = [8]
WEI_MAX_PRECISION = max(WEI_SUPPORTED_PRECISION)

#sparsity features
# 0 = only one kind of accelerator like SCNN, 1 = support both sparsity and non-sparse modes, some kind of mux to switch between the modes like Codesign V1
SPARSITY_MODES = 0

#1. Encoding , 0 = none, 1 = RLE, 2 = ??
ACT_ENCODING = 0
WEI_ENCODING = 0

# Zero-policies
#2.1 Gating strategy
ACT_ZERO_GATING = False
WEI_ZERO_GATING = False

#2.2 Skipping MAC, 
ACT_ZERO_SKIP_MAC = 1
WEI_ZERO_SKIP_MAC = 1

#2.3 Skipping Buffer , L1 or L2
ACT_ZERO_SKIP_L1 = False
WEI_ZERO_SKIP_L1 = False

#2.4 Skipping DRAM
ACT_ZERO_SKIP_DRAM = True
WEI_ZERO_SKIP_DRAM = True

#3. Indexing, 0 = None/direct index, 1 = stepped index
ACT_INDEXING = 0
WEI_INDEXING = 0
ACT_INDEX_PRECISION = 16
WEI_INDEX_PRECISION = 16

#4. Output related [todos]


#DRAM storage method, 0 = in-order, 1 = by tiling and access time
ACT_DRAM_STORE_ORDER = 0
WEI_DRAM_STORE_ORDER = 0




DRAM_BW = 128 #DRAM read/write data size in bits
L1_BW = 128 #Buffer read/write data size in bits

######################################################


#settings
ACT_PRECISION = 8
WEI_PRECISION = 8

SPARSITY_EN = 1




#neural network workload

INPUT_BATCH = 1
INPUT_X = 8
INPUT_Y = 8
IN_CHANNELS = 1
OUT_CHANNELS = 1
KERNEL_SIZE = [3,3]

######################################################

WORK = "./test"
import os
if(not os.path.exists(WORK)):
    os.mkdir(WORK)
######################################################

import numpy as np

ACT = np.arange(0, INPUT_BATCH*IN_CHANNELS*INPUT_X*INPUT_Y)
ACT = ACT % 11 #reduce all the even ones to 0 for sparsity testing
ACT = ACT.reshape((INPUT_BATCH, IN_CHANNELS, INPUT_X, INPUT_Y))

WEI = np.arange(0, OUT_CHANNELS*IN_CHANNELS*KERNEL_SIZE[0]*KERNEL_SIZE[1])
WEI = WEI % 7 #reduce all the even ones to 0 for sparsity testing
WEI = WEI.reshape((OUT_CHANNELS, IN_CHANNELS, KERNEL_SIZE[0], KERNEL_SIZE[1]))


print(ACT)
print(WEI)
#Inputs: (above)
#Outputs:
#   1. act data for dram
#   2. act sparse index
#   3. wei data for dram (loop if multiple layers)
#   4. wei sparse index (loop if multiple layers)
#   5. Verilog files
#   6. Testbench files


act_data_f = open(WORK + "/act_data.txt", 'w')
wei_data_f = open(WORK + "/wei_data.txt", 'w')
act_sparse_idx_f = open(WORK + "/act_sparse_idx.txt", "w")
wei_sparse_idx_f = open(WORK + "/wei_sparse_idx.txt", "w")


##############################1-2 act data and sparse idx for dram#############################

#In order
if(ACT_DRAM_STORE_ORDER == 0):
    ##
    #1. in-order + no zero skip
    ##
    if(ACT_ZERO_SKIP_DRAM == 0):
        print("act_data")
        ddr_idx = 0
        for b in range(0, INPUT_BATCH):
            for x in range(INPUT_X):
                for y in range(INPUT_Y):
                    for i in range(IN_CHANNELS):
                        ddr_idx += ACT_PRECISION
                        if(ddr_idx >= DRAM_BW):
                            print(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4), end="\n")
                            act_data_f.write(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4)+"\n")
                            ddr_idx = 0
                        else:
                            print(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4),"\t",end="")
                            act_data_f.write(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4))#end="")
                            #act_data_f.write(ACT[b][i][x][y])
                            #print(ACT[b][i][x][y])
    ##
    #2. in-order + zero skip
    ##                            
    else:
        ddr_idx = 0
        #data
        print("act_data (zero skipped)")
        for b in range(0, INPUT_BATCH):
            for x in range(INPUT_X):
                for y in range(INPUT_Y):
                    for i in range(IN_CHANNELS):
                        if(ACT[b][i][x][y] != 0):
                            ddr_idx += ACT_PRECISION
                            if(ddr_idx >= DRAM_BW):
                                print(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4), end="\n")
                                act_data_f.write(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4)+"\n")
                                ddr_idx = 0
                            else:
                                print(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4),"\t",end="")
                                act_data_f.write(hex(ACT[b][i][x][y])[2:].zfill(ACT_PRECISION//4))
                                    
        ###
        #2.1 in-order + zero skip + direct index
        ###
        if(ACT_INDEXING == 0):
            #index
            print("\nact_sparse_idx (direct)")
            ddr_idx = 0
            for b in range(0, INPUT_BATCH):
                for x in range(INPUT_X):
                    for y in range(INPUT_Y):
                        for i in range(IN_CHANNELS):
                            ddr_idx += 1 #or should this be 1 in reality ?[todos]
                            if(ACT[b][i][x][y] != 0):
                                print(1,end="\t")
                                act_sparse_idx_f.write('1')
                            else:
                                print(0,end="\t")
                                act_sparse_idx_f.write('0')

                            if(ddr_idx >= DRAM_BW):
                                act_sparse_idx_f.write("\n")
                                print()
                                ddr_idx = 0

                            
        ###                    
        #2.2 in-order + zero skip + indirect index
        ###                                  
        else:
            #index
            print("\nact_sparse_idx (step)")
            ddr_idx = 0
            zero_len = 0
            start = 0
            for b in range(0, INPUT_BATCH):
                for x in range(INPUT_X):
                    for y in range(INPUT_Y):
                        for i in range(IN_CHANNELS):
                            
                            #print(zero_len)
                            
                            if(ACT[b][i][x][y] != 0 ):
                                ddr_idx += ACT_INDEX_PRECISION #or should this be 1 in reality ?[todos]
                                #print(1,end="\t")
                                if(start == 0):
                                    print(zero_len,end="\t")
                                    act_sparse_idx_f.write(hex(zero_len)[2:].zfill(ACT_INDEX_PRECISION//4))
                                    zero_len = 0
                                    start = 1
                                else:
                                    #if(zero_len != 0):
                                    print(zero_len,end="\t")
                                    act_sparse_idx_f.write(hex(zero_len)[2:].zfill(ACT_INDEX_PRECISION//4))
                                    zero_len = 0
                                    
                            else:
                                zero_len += 1

                            if(ddr_idx >= DRAM_BW):
                                print()
                                act_sparse_idx_f.write("\n")
                                ddr_idx = 0
            
# In tile-order
else:
    pass




##############################3-4 wei data and sparse idx for dram#############################
print()
#In order
if(WEI_DRAM_STORE_ORDER == 0):
    ##
    #1. in-order + no zero skip
    ##
    if(WEI_ZERO_SKIP_DRAM == 0):
        print("wei_data")
        ddr_idx = 0
        for o in range(OUT_CHANNELS):
            for i in range(IN_CHANNELS):
                for kx in range(KERNEL_SIZE[0]):
                    for ky in range(KERNEL_SIZE[1]):             
                        ddr_idx += WEI_PRECISION
                        if(ddr_idx >= DRAM_BW):
                            print(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4), end="\n")
                            wei_data_f.write(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4)+"\n")
                            ddr_idx = 0
                        else:
                            print(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4),"\t",end="")
                            wei_data_f.write(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4))

    ##
    #2. in-order + zero skip
    ##                            
    else:
        print("wei_data (zero skipped)")
        ddr_idx = 0
        for o in range(OUT_CHANNELS):
            for i in range(IN_CHANNELS):
                for kx in range(KERNEL_SIZE[0]):
                    for ky in range(KERNEL_SIZE[1]):
                        if(WEI[o][i][kx][ky] != 0):
                            ddr_idx += 1 #should this be 1 ?
                            if(ddr_idx >= DRAM_BW):
                                print(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4), end="\n")
                                wei_data_f.write(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4)+"\n")
                                ddr_idx = 0
                            else:
                                print(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4),"\t",end="")
                                wei_data_f.write(hex(WEI[o][i][kx][ky])[2:].zfill(WEI_PRECISION//4))
                                    
        ###
        #2.1 in-order + zero skip + direct index
        ###
        if(WEI_INDEXING == 0):
            #index
            print("\nwei_sparse_idx (direct)")
            ddr_idx = 0
            for o in range(OUT_CHANNELS):
                for i in range(IN_CHANNELS):
                    for kx in range(KERNEL_SIZE[0]):
                        for ky in range(KERNEL_SIZE[1]):
                            ddr_idx += 1 #or should this be 1 in reality ?[todos]
                            if(WEI[o][i][kx][ky] != 0):
                                print(1,end="\t")
                                wei_sparse_idx_f.write('1')
                            else:
                                print(0,end="\t")
                                wei_sparse_idx_f.write('0')

                            if(ddr_idx >= DRAM_BW):
                                print()
                                wei_sparse_idx_f.write("\n")
                                ddr_idx = 0

                            
        ###                    
        #2.2 in-order + zero skip + indirect index
        ###                                  
        else:
            #index
            print("\nact_sparse_idx (step)")
            ddr_idx = 0
            zero_len = 0
            start = 0
            for o in range(OUT_CHANNELS):
                for i in range(IN_CHANNELS):
                    for kx in range(KERNEL_SIZE[0]):
                        for ky in range(KERNEL_SIZE[1]):
                            
                            #print(zero_len)
                            
                            if(WEI[o][i][kx][ky] != 0):
                                ddr_idx += WEI_INDEX_PRECISION #or should this be 1 in reality ?[todos]
                                if(start == 0):
                                    print(zero_len,end="\t")
                                    wei_sparse_idx_f.write(hex(zero_len)[2:].zfill(WEI_INDEX_PRECISION//4))
                                    zero_len = 0
                                    start = 1
                                else:
                                    #if(zero_len != 0):
                                    print(zero_len,end="\t")
                                    wei_sparse_idx_f.write(hex(zero_len)[2:].zfill(WEI_INDEX_PRECISION//4))
                                    zero_len = 0
                                    
                            else:
                                zero_len += 1

                            if(ddr_idx >= DRAM_BW):
                                print()
                                wei_sparse_idx_f.write("\n")
                                ddr_idx = 0
            
# In tile-order
else:
    pass


act_data_f.close()
wei_data_f.close()
act_sparse_idx_f.close()
wei_sparse_idx_f.close()




####################################5 quick simulation ######################
OUT = np.arange(0, INPUT_BATCH*OUT_CHANNELS*(INPUT_X-KERNEL_SIZE[0]+1)*(INPUT_Y-KERNEL_SIZE[1]+1))
OUT = OUT.reshape((INPUT_BATCH, OUT_CHANNELS, INPUT_X-KERNEL_SIZE[0]+1, INPUT_Y-KERNEL_SIZE[1]+1))
MACS = 0
for b in range(0, INPUT_BATCH):    
    for o in range(OUT_CHANNELS):
        for i in range(IN_CHANNELS):
            for kx in range(KERNEL_SIZE[0]):
                for ky in range(KERNEL_SIZE[1]):
                    for x in range(INPUT_X-KERNEL_SIZE[0]+1):
                        for y in range(INPUT_Y-KERNEL_SIZE[1]+1):
                            if(ACT_ZERO_SKIP_MAC and WEI_ZERO_SKIP_MAC):
                                #print("here")
                                if( WEI[o][i][kx][ky] != 0 and ACT[b][i][x+kx][y+ky] != 0):
                                    OUT[b][o][x][y] += WEI[o][i][kx][ky]*ACT[b][i][x+kx][y+ky]
                                    MACS += 1
                            elif( (WEI_ZERO_SKIP_MAC)):
                                if(WEI[o][i][kx][ky] != 0):
                                    OUT[b][o][x][y] += WEI[o][i][kx][ky]*ACT[b][i][x+kx][y+ky]
                                    MACS += 1
                            elif( (ACT_ZERO_SKIP_MAC)):
                                if( ACT[b][i][x+kx][y+ky] != 0):
                                    OUT[b][o][x][y] += WEI[o][i][kx][ky]*ACT[b][i][x+kx][y+ky]
                                    MACS += 1

                            else:
                                OUT[b][o][x][y] += WEI[o][i][kx][ky]*ACT[b][i][x+kx][y+ky]
                                MACS += 1
print()
print("MACS = ", MACS)
print(OUT)

##############################5 verilog file#############################

# module top
module top (input core_clk, input ddr_clk, input rst_n, input write_valid, output write_ready, input read_valid, output read_ready);

    DMA dma();

    ACT_BUFFER act_buff();

    WEI_BUFFER wei_buff();

    PE pe();

    #contains the PSUM_BUFFER
    ACC acc();

    SDP sdp();

    
endmodule

# module 1 (ddr from DRAM to Buffer, DMA)

module DMA( input clk, input rst_n, input write_en, input write_addr, input read_en, input read_addr, output read_data, input write_data);

endmodule

# module 3 (Buffer to PE, BUFFER)
module ACT_BUFFER ( input clk, input rst_n, input write_en, input write_addr, input read_en, input read_addr, output read_data, input write_data);

endmodule

module WEI_BUFFER (input clk, input rst_n, input write_en, input write_addr, input read_en, input read_addr, output read_data, input write_data);

endmodule

# module 4 (PE to accumulator, PE, ACC)

# module 5 (accumulator to SDP, SDP)


#########################6 testbench file################################

# DRAM storage



#####################################################################


