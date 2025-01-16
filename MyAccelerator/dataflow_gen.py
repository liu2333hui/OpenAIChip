def dataflow_gen(hardware_config, runtime_config, activation, weight):
    SUPPORTED_WEI_DTYPES=hardware_config["SUPPORTED_WEI_DTYPES"]
    SUPPORTED_ACT_DTYPES=hardware_config["SUPPORTED_ACT_DTYPES"]
    ACT_ZERO_GATING=hardware_config["ACT_ZERO_GATING"]
    WEI_ZERO_GATING=hardware_config["WEI_ZERO_GATING"]
    MULT_TYPE_INT=hardware_config["MULT_TYPE_INT"]
    MULT_TYPE_FP=hardware_config["MULT_TYPE_FP"]
    TILINGS=hardware_config["TILINGS"]
    multicast=hardware_config["multicast"]
    WEI_BUFFER=hardware_config["WEI_BUFFER"]
    WEI_BANKS=hardware_config["WEI_BANKS"]
    ACT_BUFFER=hardware_config["ACT_BUFFER"]
    ACT_BANKS=hardware_config["ACT_BANKS"]
    PSUM_BUFFER=hardware_config["PSUM_BUFFER"]
    PSUM_BANKS=hardware_config["PSUM_BANKS"]
    MAX_STRIDE=hardware_config["MAX_STRIDE"]
    MAX_KX=hardware_config["MAX_KX"]
    MAX_KY=hardware_config["MAX_KY"]
    MAX_X=hardware_config["MAX_X"]
    MAX_Y=hardware_config["MAX_Y"]
    MAX_N=hardware_config["MAX_N"]
    MAX_I=hardware_config["MAX_I"]
    MAX_B=hardware_config["MAX_B"]
    MAX_PADDING_X=hardware_config["MAX_PADDING_X"]
    MAX_PADDING_Y=hardware_config["MAX_PADDING_Y"]
    DDR_WIDTH=hardware_config["DDR_WIDTH"]
    DDR_CLK=runtime_config["DDR_CLK"]
    CORE_CLK=runtime_config["CORE_CLK"]
    Operation=runtime_config["Operation"]
    Operation_Params=runtime_config["Operation_Params"]
    WEIGHTS=runtime_config["WEIGHTS"]
    INPUTS=runtime_config["INPUTS"]
    WEI_PREC=runtime_config["WEI_PREC"]
    ACT_PREC=runtime_config["ACT_PREC"]
    BURST=runtime_config["BURST"]
    DRAM_DELAY=runtime_config["DRAM_DELAY"]
    FIRST_LAYER=runtime_config["FIRST_LAYER"]
    wei_data_f = open('MyAccelerator/tc1/weights.txt',"w")
    act_data_f = open('MyAccelerator/tc1/activation.txt',"w")
    cycle = 0
    act_ddr_idx = 0
    wei_ddr_idx = 0
    for bb in range(0, INPUT_BATCH , TB):
        for nnn in range(0, OUT_CHANNELS, TNN):
            for iii in range(0, INPUT_CHANNELS , TII):
                for xxx in range(0, ((INPUT_X + PADDING[0]*2 - KERNEL_SIZE[0] + 1) // STRIDE[0]  ), TXX):
                    for yyy in range(0, ((INPUT_Y + PADDING[1]*2 - KERNEL_SIZE[1] + 1) // STRIDE[1]  ), TYY):
