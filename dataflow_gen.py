def dataflow_gen(hardware_config, software_config, activation, weight):
    TX=hardware_config["TX"]
    TY=hardware_config["TY"]
    TB=hardware_config["TB"]
    TN=hardware_config["TN"]
    TI=hardware_config["TI"]
    TKX=hardware_config["TKX"]
    TKY=hardware_config["TKY"]
    TNN=hardware_config["TNN"]
    TII=hardware_config["TII"]
    TXX=hardware_config["TXX"]
    TYY=hardware_config["TYY"]
    WEIGHT_SCRATCHPAD=hardware_config["WEIGHT_SCRATCHPAD"]
    ACT_SCRATCHPAD=hardware_config["ACT_SCRATCHPAD"]
    INTER_PE=hardware_config["INTER_PE"]
    ALLOW_DIAGONAL=hardware_config["ALLOW_DIAGONAL"]
    WEI_BROADCAST=hardware_config["WEI_BROADCAST"]
    ACT_BROADCAST=hardware_config["ACT_BROADCAST"]
    WEIGHT_BUFFER=hardware_config["WEIGHT_BUFFER"]
    WEIGHT_BANKS=hardware_config["WEIGHT_BANKS"]
    ACT_BUFFER=hardware_config["ACT_BUFFER"]
    ACT_BANKS=hardware_config["ACT_BANKS"]
    OUTPUT_BANKS=hardware_config["OUTPUT_BANKS"]
    OUTPUT_BUFFER=hardware_config["OUTPUT_BUFFER"]
    GLOBAL_SRAM=hardware_config["GLOBAL_SRAM"]
    L2_DATA_FORMAT=hardware_config["L2_DATA_FORMAT"]
    L2_WIDTH=hardware_config["L2_WIDTH"]
    L2_ROWS=hardware_config["L2_ROWS"]
    L2_BANKS=hardware_config["L2_BANKS"]
    DDR_WIDTH=hardware_config["DDR_WIDTH"]
    BURST=hardware_config["BURST"]
    DDR_ACT_FORMAT=hardware_config["DDR_ACT_FORMAT"]
    DDR_WEI_FORMAT=hardware_config["DDR_WEI_FORMAT"]
    SUPPORTED_PRECISIONS=hardware_config["SUPPORTED_PRECISIONS"]
    MAX_PRECISIONS=hardware_config["MAX_PRECISIONS"]
    IN_CHANNELS=software_config["IN_CHANNELS"]
    OUT_CHANNELS=software_config["OUT_CHANNELS"]
    KERNEL_SIZE=software_config["KERNEL_SIZE"]
    STRIDE=software_config["STRIDE"]
    PADDING=software_config["PADDING"]
    DILATION=software_config["DILATION"]
    GROUPS=software_config["GROUPS"]
    POOL_SIZE=software_config["POOL_SIZE"]
    POOL_STRIDE=software_config["POOL_STRIDE"]
    POOL_PAD=software_config["POOL_PAD"]
    CONV=software_config["CONV"]
    ACTIVATION=software_config["ACTIVATION"]
    POOLING=software_config["POOLING"]
    BATCH_NORM=software_config["BATCH_NORM"]
    INPUT_BATCH=software_config["INPUT_BATCH"]
    INPUT_CHANNELS=software_config["INPUT_CHANNELS"]
    INPUT_X=software_config["INPUT_X"]
    INPUT_Y=software_config["INPUT_Y"]
    activation_precision=software_config["activation_precision"]
    weight_precision=software_config["weight_precision"]
    sparsity=software_config["sparsity"]
    strategy=software_config["strategy"]
    benchmark=software_config["benchmark"]
    wei_data_f = open('./benchmarks/paddle/ConvFuseOp.1_1_3_3_1_1_0_0_1_1_True/UnstructurePrune0.5_INT8_8/weights.txt',"w")
    act_data_f = open('./benchmarks/paddle/ConvFuseOp.1_1_3_3_1_1_0_0_1_1_True/UnstructurePrune0.5_INT8_8/activation.txt',"w")
    cycle = 0
    act_ddr_idx = 0
    wei_ddr_idx = 0
    for bb in range(0, INPUT_BATCH , TB):
        for xxx in range(0, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ), TXX):
            for kky in range(0, KERNEL_SIZE[1], TKY):
                for yyy in range(0, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ), TYY):
                    for yy in range(yyy, min(yyy+TYY, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  )), TY):
                        for xx in range(xxx, min(xxx+TXX, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )), TX):
                            for iii in range(0, INPUT_CHANNELS , TII):
                                for ii in range(iii, min(iii+TII, INPUT_CHANNELS), TI):
                                    for kkx in range(0, KERNEL_SIZE[0], TKX):
                                        for nnn in range(0, OUT_CHANNELS, TNN):
                                            for nn in range(nnn, min(nnn+TNN, OUT_CHANNELS), TN):
                                                    print('@CYCLE = ', cycle)
                                                    pe_no = 0
                                                    cycle += 1
                                                    #ACT_ATOMIC = set()
                                                    for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):
                                                        for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):
                                                            for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                                                                for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                                                                    for i in range(ii, min(ii+TI, IN_CHANNELS)):
                                                                        for n in range(nn, min(nn+TN, OUT_CHANNELS)):
                                                                            for b in range(bb, min(bb + INPUT_BATCH, TB)):
                                                                                #print('  ACT', pe_no, '	B', b, '	I', i, '	IX', x+kx, '	IY', y+ky, '	TN', n , activation[b][i][x+kx][y+ky]) #b, i, x + kx, y + ky)
                                                                                pe_no += 1
                                                    pe_no = 0
                                                    for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):
                                                        for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):
                                                            for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                                                                for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                                                                    for i in range(ii, min(ii+TI, IN_CHANNELS)):
                                                                        for n in range(nn, min(nn+TN, OUT_CHANNELS)):
                                                                            for b in range(bb, min(bb + INPUT_BATCH, TB)):
                                                                                #print('  Wei', pe_no, '	N', n, '	I', i, '	KX', kx, '	KY', ky, weight[n][i][kx][ky])
                                                                                pe_no += 1
    for kky in range(0, KERNEL_SIZE[1], TKY):
        for iii in range(0, INPUT_CHANNELS , TII):
            for ii in range(iii, min(iii+TII, INPUT_CHANNELS), TI):
                for kkx in range(0, KERNEL_SIZE[0], TKX):
                    for nnn in range(0, OUT_CHANNELS, TNN):
                        for nn in range(nnn, min(nnn+TNN, OUT_CHANNELS), TN):

                                for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                                    for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                                        for i in range(ii, min(ii+TI, IN_CHANNELS)):
                                            for n in range(nn, min(nn+TN, OUT_CHANNELS)):
                                                wei_ddr_idx += weight_precision
                                                if(wei_ddr_idx >= DDR_WIDTH):
                                                    wei_data_f.write(hex(weight[n][i][kx][ky])[2:].zfill(weight_precision//4)+'')
                                                    wei_ddr_idx = 0
                                                else:
                                                    wei_data_f.write(hex(weight[n][i][kx][ky])[2:].zfill(weight_precision//4))
                                #wei_data_f.write(str(cycle)+'\n')
    for bb in range(0, INPUT_BATCH , TB):
        for xxx in range(0, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ), TXX):
            for kky in range(0, KERNEL_SIZE[1], TKY):
                for yyy in range(0, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ), TYY):
                    for yy in range(yyy, min(yyy+TYY, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  )), TY):
                        for xx in range(xxx, min(xxx+TXX, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )), TX):
                            for iii in range(0, INPUT_CHANNELS , TII):
                                for ii in range(iii, min(iii+TII, INPUT_CHANNELS), TI):
                                    for kkx in range(0, KERNEL_SIZE[0], TKX):

                                            #act_data_f.write(str(kkx)+'	'+ str(kky)+'	'+ str(xx+TX)+'	'+str(yy+TY)+'\n')
                                            if((kkx < TX and kky < TY) or ( kkx >= (KERNEL_SIZE[0]-TX) and kky >= (KERNEL_SIZE[1]-TY) and yy+TY >= ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ) and (xx+TX >= ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0])  ))                    or (kky >= TY and   yy+TY >= ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ) and (xx+TX < ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0])  )))                    or (kkx >= TX and   yy+TY < ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1] ) and (xx+TX >= ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ))                    ):
                                                for x in range(xx, min(xx+TX, (INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  )):
                                                    for y in range(yy, min(yy+TY, (INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1)//STRIDE[1])):
                                                        for kx in range(kkx, min(kkx + TKX, KERNEL_SIZE[0])):
                                                            for ky in range(kky, min(kky + TKY, KERNEL_SIZE[1])):
                                                                for i in range(ii, min(ii+TI, IN_CHANNELS)):
                                                                    for b in range(bb, min(bb + INPUT_BATCH, TB)):
                                                                        act_ddr_idx += activation_precision
                                                                        if(act_ddr_idx >= DDR_WIDTH):
                                                                            act_data_f.write(hex(activation[b][i][x+kx][y+ky])[2:].zfill(activation_precision//4)+'')
                                                                            act_ddr_idx = 0
                                                                        else:
                                                                            act_data_f.write(hex(activation[b][i][x+kx][y+ky])[2:].zfill(activation_precision//4))
                                                act_data_f.write('\n')
