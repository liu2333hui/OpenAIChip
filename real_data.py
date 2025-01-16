import numpy as np
def get_data(BASE, NETWORK):
    #####Actual data
    weight = np.load(BASE+"/"+NETWORK+".npy")
    act = np.load(BASE+"/"+NETWORK+"_act.npy")
    print(weight.shape)
    print(act.shape) 
    
    IN_CHANNELS  = 8#weight.shape[1]
    OUT_CHANNELS = 6#weight.shape[0]
    KX = 2#weight.shape[2]
    KY = 2#weight.shape[3]
    INPUT_X = 4#act.shape[2]
    INPUT_Y = 4#act.shape[3]
    INPUT_BATCH = act.shape[0]
    STRIDE = 1
    PADDING = 0

    #exit(0) 
    return IN_CHANNELS, OUT_CHANNELS, KX, KY, INPUT_X, INPUT_Y, INPUT_BATCH, STRIDE, PADDING, weight, act
