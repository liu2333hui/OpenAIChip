import numpy as np
import wincnn
def dataflow_gen_tc(hardware_config, runtime_config):
    SUPPORTED_WEI_DTYPES=hardware_config["SUPPORTED_WEI_DTYPES"]
    SUPPORTED_ACT_DTYPES=hardware_config["SUPPORTED_ACT_DTYPES"]
    SUPPORTED_OUT_DTYPES=hardware_config["SUPPORTED_OUT_DTYPES"]
    ACT_ZERO_GATING=hardware_config["ACT_ZERO_GATING"]
    WEI_ZERO_GATING=hardware_config["WEI_ZERO_GATING"]
    MULT_TYPE_INT=hardware_config["MULT_TYPE_INT"]
    MULT_TYPE_FP=hardware_config["MULT_TYPE_FP"]
    MULT_TYPE_INT_META=hardware_config["MULT_TYPE_INT_META"]
    REMOVE_DUPLICATE_ROWS=hardware_config["REMOVE_DUPLICATE_ROWS"]
    UNIFIED_ACC_COUNTER=hardware_config["UNIFIED_ACC_COUNTER"]
    COUNTER=hardware_config["COUNTER"]
    VECTOR_UNIT=hardware_config["VECTOR_UNIT"]
    ELEMENT_UNIT=hardware_config["ELEMENT_UNIT"]
    RESCALE_UNIT=hardware_config["RESCALE_UNIT"]
    ACCUMULATOR=hardware_config["ACCUMULATOR"]
    multicast=hardware_config["multicast"]
    WEI_BUFFER=hardware_config["WEI_BUFFER"]
    WEI_BANKS=hardware_config["WEI_BANKS"]
    WEI_L1_READ_DELAY=hardware_config["WEI_L1_READ_DELAY"]
    WEI_BUFFER_ON_MAX_LAYER=hardware_config["WEI_BUFFER_ON_MAX_LAYER"]
    ACT_BUFFER=hardware_config["ACT_BUFFER"]
    ACT_BANKS=hardware_config["ACT_BANKS"]
    ACT_L1_READ_DELAY=hardware_config["ACT_L1_READ_DELAY"]
    PSUM_BUFFER=hardware_config["PSUM_BUFFER"]
    PSUM_BANKS=hardware_config["PSUM_BANKS"]
    PSUM_BUFFER_ON_MAX_LAYER=hardware_config["PSUM_BUFFER_ON_MAX_LAYER"]
    WEI_L2_READ_DELAY=hardware_config["WEI_L2_READ_DELAY"]
    ACT_L2_READ_DELAY=hardware_config["ACT_L2_READ_DELAY"]
    WEI_PREFETCH=hardware_config["WEI_PREFETCH"]
    ACT_PREFETCH=hardware_config["ACT_PREFETCH"]
    WEI_L2_L1_BW_RATIO=hardware_config["WEI_L2_L1_BW_RATIO"]
    ACT_L2_L1_BW_RATIO=hardware_config["ACT_L2_L1_BW_RATIO"]
    L2_WEI_BUFFER_SIZE=hardware_config["L2_WEI_BUFFER_SIZE"]
    L2_ACT_BUFFER_SIZE=hardware_config["L2_ACT_BUFFER_SIZE"]
    ALIGNED_L1_DATA=hardware_config["ALIGNED_L1_DATA"]
    GEN_CONSTRAINTS=hardware_config["GEN_CONSTRAINTS"]
    DDR_WIDTH=hardware_config["DDR_WIDTH"]
    DDR_MAX_BURST=hardware_config["DDR_MAX_BURST"]
    SRAMS=hardware_config["SRAMS"]
    SRAM_CONSTRAINTS=hardware_config["SRAM_CONSTRAINTS"]
    SRAM_COMPILER_CONFIG=hardware_config["SRAM_COMPILER_CONFIG"]
    DDR_CLK=runtime_config["DDR_CLK"]
    CORE_CLK=runtime_config["CORE_CLK"]
    Operation=runtime_config["Operation"]
    Operation_Params=runtime_config["Operation_Params"]
    WEIGHTS=runtime_config["WEIGHTS"]
    INPUTS=runtime_config["INPUTS"]
    WEI_PREC=runtime_config["WEI_PREC"]
    ACT_PREC=runtime_config["ACT_PREC"]
    OUT_SCALE=runtime_config["OUT_SCALE"]
    OUT_PREC=runtime_config["OUT_PREC"]
    BURST=runtime_config["BURST"]
    DRAM_DELAY=runtime_config["DRAM_DELAY"]
    FIRST_LAYER=runtime_config["FIRST_LAYER"]
    SPARSITY_EN=runtime_config["SPARSITY_EN"]
    KX=runtime_config["Operation_Params"]["KX"]
    KY=runtime_config["Operation_Params"]["KY"]
    X=runtime_config["Operation_Params"]["X"]
    Y=runtime_config["Operation_Params"]["Y"]
    I=runtime_config["Operation_Params"]["I"]
    N=runtime_config["Operation_Params"]["N"]
    B=runtime_config["Operation_Params"]["B"]
    STRIDE=runtime_config["Operation_Params"]["STRIDE"]
    PADDING=runtime_config["Operation_Params"]["PADDING"]
    ID="0"
    DATAFLOW="DIRECT"
    TX=1
    TY=1
    TKX=1
    TKY=1
    TI=4
    TN=4
    TB=1
    TXX=-1
    TYY=-1
    TII=-1
    TNN=-1
    LOOP="['B', 'N', 'I', 'KY', 'KX', 'X', 'Y']"
    WINO_TX="2"
    WINO_TY="2"
    WINO_PRE_WEIGHT="False"
    SYSTOLIC="{'WEIGHT_LOAD': {'TKX': -1, 'TKY': -1, 'TN': -1, 'TI': -1}, 'ACT_LOAD': {'TKX': -1, 'TKY': -1, 'TX': -1, 'TY': -1, 'TI': -1, 'TB': -1}, 'PSUM_OFFLOAD': {'TX': -1, 'TY': -1, 'TN': -1}, 'WEIGHT_CAST': {'TX': -1, 'TY': -1, 'TB': -1}, 'ACT_CAST': {'TN': -1, 'TKX': -1, 'TKY': -1}, 'PSUM_CAST': {'TB': -1, 'TKX': -1, 'TKY': -1}, 'ACT_X_INTER': 'NONE', 'ACT_Y_INTER': 'NONE'}"
    PE_BUF="NONE"
    REMOVE_DUPLICATE_ROWS="True"
    SPARSITY="{'WEI_ENCODING': 'SPARSE_MAP', 'ACT_ENCODING': 'SPARSE_MAP', 'WEI_WINDOW': 4, 'ACT_WINDOW': 4, 'WINDOW_MULTICAST': True, 'LOAD_BALANCE': None, 'WINDOW_GROUP': ['TX'], 'SPARSE_TILING': {'TX': 1, 'TY': 1, 'TN': 2, 'TB': 1, 'TKX': 1, 'TKY': 1, 'TI': 2}, 'GROUPING_POLICY': 'STRUCTURED', 'VALUE_SPARSITY': 'ACT', 'WEI_COMPRESSION': False, 'ACT_COMPRESSION': False, 'PSUM_COMPRESSION': False, 'ADDRESS_GEN': 'ADDERS'}"
    weight_precision = 16
    act_precision = 16
    psum_precision = 32
    wei_data_f = open('MyAccelerator/tc1/weights.txt',"w")
    act_data_f = open('MyAccelerator/tc1/activation.txt',"w")
    WEI_LINE = 1
    ACT_LINE = 1
    cycle = 0
    act_ddr_idx = 0
    wei_ddr_idx = 0
    kkx = 0
    kky = 0
    WEI_LINE *= weight_precision*TI*TN*TKX*TKY
    WEI_LINE *= 1
    wei_ddr_idx = 0
    for nn in range(0, N, TN):
        for ii in range(0, I , TI):
            for kky in range(0, KY, TKY):
                for kkx in range(0, KX, TKX):
                    wei_dim = np.zeros(TI*TN*TKX*TKY).astype('int')
                    for i in range(ii, min(ii+TI, I)):
                        for n in range(nn, min(nn+TN, N)):
                            for kx in range(kkx, min(kkx + TKX, KX)):
                                for ky in range(kky, min(kky + TKY, KY)):
                                    wei_dim[((((0*TI+  (i-ii))*TN+  (n-nn))*TKX+  (kx-kkx))*TKY+  (ky-kky))] = WEIGHTS[n][i][kx][ky]
                    for wei in wei_dim:
                        wei_ddr_idx += weight_precision
                        if(wei < 0 ):
                            wei = wei + (1<<weight_precision) 
                        wei_data_f.write(hex(wei)[2:].zfill(weight_precision//4))
                        if(wei_ddr_idx >= WEI_LINE):
                            wei_data_f.write('\n')
                            wei_ddr_idx = 0
                        else:
                            pass
    ACT_LINE *= act_precision*TB*TI*(TX+TKX-1)*(TY+TKY-1)
    act_ddr_idx = 0
    kkx = 0
    kky = 0
    act_ddr_idx = 0
    visited = [False]*(X*Y*I)
    for bb in range(0, B , TB):
        for ii in range(0, I , TI):
            for kky in range(0, KY, TKY):
                for kkx in range(0, KX, TKX):
                    for xx in range(0, ((X + PADDING*2 - KX + 1) // STRIDE  ), TX):
                        for yy in range(0, ((Y + PADDING*2 - KY + 1) // STRIDE  ), TY):
                            kx = kkx
                            ky = kky
                            act_dim = np.zeros(TB*TI*(TX+TKX-1)*(TY+TKY-1)).astype('int')
                            if(visited[ii*X*Y+(xx+kkx)*Y + (yy+kky)]):
                                continue
                            for b in range(bb, min(bb +TB, B)):
                                for i in range(ii, min(ii+TI, I)):
                                    for x in range(xx, min(xx+TX+TKX-1, (X+PADDING*2)//STRIDE)):
                                        for y in range(yy, min(yy+TY+TKY-1, (Y+PADDING*2)//STRIDE)):
                                            if((x+kx) >= X or (y+ky) >= Y):
                                                continue
                                            tempus = INPUTS[b][i][x+kx][y+ky]
                                            act_dim[((((0*TB+  (b-bb))*TI+  (i-ii))*(TX+TKX-1)+  (x-xx))*(TY+TKY-1)+  (y-yy))] = INPUTS[b][i][x+kx][y+ky]
                            for act in act_dim:
                                act_ddr_idx += act_precision
                                if(act < 0 ):
                                    act = act + (1<<act_precision) 
                                act_data_f.write(hex(act)[2:].zfill(act_precision//4))
                                if(act_ddr_idx >= ACT_LINE):
                                    act_data_f.write('\n')
                                    act_ddr_idx = 0
                                else:
                                    pass
                            visited[ii*X*Y + (xx+kx)*Y + (yy+ky)] = True
    while(act_ddr_idx < ACT_LINE):
        act_data_f.write(hex(0)[2:].zfill(act_precision//4))
        act_ddr_idx += act_precision
    while(wei_ddr_idx < WEI_LINE):
        wei_data_f.write(hex(0)[2:].zfill(weight_precision//4))
        wei_ddr_idx += weight_precision
    act_data_f.close()
    wei_data_f.close()
