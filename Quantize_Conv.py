#GENERATES A CONVOLUTION LAYER AND QUANTIZES IT

import paddle

from paddle.io import Dataset
import numpy as np
from paddle.static import InputSpec
from paddle.jit import to_static

from paddleslim.auto_compression import AutoCompression
#A FUSION SUPPORTING LAYER
#CONV
#CONV+ACTIVATION/BN
#CONV+ACTIVATION/BN+POOL
#CONV+POOL
#ACTIVATION
#POOL
class ConvFuseOp(paddle.nn.Layer):

    def forward(self, x):

        if(self.CONV):
            x = self.conv(x)

        if(self.BATCH_NORM):
            x = self.bn(x)

        if(self.ACTIVATION):
            x = self.act(x)

        if(self.POOLING):
            x = self.pool(x)
        
        return x
    
    def __init__(self, CONV, IN_CHANNELS, OUT_CHANNELS,KERNEL_SIZE,
                 STRIDE,PADDING, DILATION, GROUPS, BIAS,

                 ACTIVATION, 

                 BATCH_NORM, 

                 POOLING, POOL_SIZE, POOL_STRIDE = 1, POOL_PAD= 0):
        super(ConvFuseOp, self).__init__()

        self.CONV = (CONV != None)
        
        self.conv = paddle.nn.Conv2D(IN_CHANNELS, OUT_CHANNELS,
                                     KERNEL_SIZE, STRIDE, PADDING, DILATION,
                                     GROUPS,
                                     bias_attr=BIAS)#todos
        self.POOLING = (POOLING != None and POOLING != False)


        self.ACTIVATION = (ACTIVATION != None and ACTIVATION != False)

        self.BATCH_NORM = (BATCH_NORM != None and BATCH_NORM != False)

        if(self.BATCH_NORM):
            self.bn = paddle.nn.BatchNorm(OUT_CHANNELS)
        else:
            print("skipping batch norm")

        if(ACTIVATION == "relu"):
            self.act = paddle.nn.ReLU()
        elif(ACTIVATION == "relu6"):
            self.act = paddle.nn.ReLU6()
        elif(ACTIVATION == "swish"):
            self.act = paddle.nn.Swish()
        elif(ACTIVATION == "tanh"):
            self.act = paddle.nn.Tanh()
        elif(ACTIVATION == "sigmoid"):
            self.act = paddle.nn.sigmoid()
        else:
            print("skipping activation")


        if(POOLING == "max"):
            self.pool = paddle.nn.MaxPool2D(POOL_SIZE, POOL_STRIDE, POOL_PAD)
        elif(POOLING == "avg"):
            self.pool = paddle.nn.AvgPool2D(POOL_SIZE, POOL_STRIDE,POOL_PAD)
        else:
            print("Skipping Pooling")




def JIA_QUANTIZE(
        config
    ):

    IN_CHANNELS = config["IN_CHANNELS"]
    OUT_CHANNELS=config["OUT_CHANNELS"] 
    KERNEL_SIZE=config["KERNEL_SIZE"]
    STRIDE=config["STRIDE"] 
    
    PADDING=config["PADDING"]
    DILATION=config["DILATION"]
    GROUPS=config["GROUPS"]

    POOL_SIZE=config["POOL_SIZE"]
    POOL_STRIDE=config["POOL_STRIDE"] 
    POOL_PAD=config["POOL_PAD"] 

    CONV=config["CONV"] 
    ACTIVATION=config["ACTIVATION"] 
    POOLING=config["POOLING"]
    BATCH_NORM=config["BATCH_NORM"]
    
    INPUT_BATCH=config["INPUT_BATCH"] 
    INPUT_CHANNELS=config["INPUT_CHANNELS"]
    INPUT_X=config["INPUT_X"] 
    INPUT_Y=config["INPUT_Y"] 

    activation_precision=config["activation_precision"]
    weight_precision=config["weight_precision"]
    
    sparsity=config["sparsity"] 
    strategy=config["strategy"] 

    benchmark=config["benchmark"]
    
    
    #benchmark = "./benchmarks/paddle/ConvFuseOp"
    features = []
    if(CONV):
        benchmark += "."+ "_".join([str(s) for s in [OUT_CHANNELS, IN_CHANNELS, KERNEL_SIZE[0],
                                                     KERNEL_SIZE[1], STRIDE[0], STRIDE[1], PADDING[0], PADDING[1],
                         DILATION, GROUPS, BIAS]])

    if(BATCH_NORM):
        benchmark += ".BN"
        
    if(ACTIVATION):
        benchmark += "."+ ACTIVATION

    if(POOLING):
        benchmark += "." + "_".join([str(s) for s in [POOL_SIZE[0], POOL_SIZE[1], POOL_STRIDE[0], POOL_STRIDE[1], POOL_PAD[0],POOL_PAD[1]]])


    network = ConvFuseOp(CONV, IN_CHANNELS, OUT_CHANNELS,KERNEL_SIZE,
                     STRIDE,PADDING, DILATION, GROUPS, BIAS,

                     ACTIVATION, 

                     BATCH_NORM, 

                     POOLING, POOL_SIZE, POOL_STRIDE, POOL_PAD)
    paddle.summary(network, (1, IN_CHANNELS, 128, 128))

    fake_vector = paddle.to_tensor(np.zeros((1, IN_CHANNELS, INPUT_X, INPUT_Y)), dtype="float32")
    fake_act = network(fake_vector)


    save_net = to_static(network, input_spec=[InputSpec(shape=[None, IN_CHANNELS, INPUT_X, INPUT_Y], name='inputs')])
    import os
    if (not os.path.isdir(benchmark)):
        os.mkdir(benchmark)
        
    paddle.jit.save(save_net, benchmark+"/inference")
    #paddle.save(paddle.Model(network), benchmark)
    ##########################################################


    # define a random dataset
    class RandomDataset(Dataset):
        def __init__(self, num_samples, in_shape, out_shape):
            self.num_samples = num_samples
            self.in_shape = in_shape
            self.out_shape = out_shape

        def __getitem__(self, idx):
            image = np.random.random(self.in_shape[1:]).astype('float32') 
            label = np.random.random(self.out_shape[1:]).astype('float32') #np.random.randint(0, 9, (1, )).astype('int64')
            return image#, label

        def __len__(self):
            return self.num_samples

        
    #Some fake training data
    # 定义DataLoader
    paddle.enable_static()
    #print(fake_vector.shape, fake_act.shape)
    train_dataset = RandomDataset(100, in_shape = fake_vector.shape, out_shape =  fake_act.shape)
    image = paddle.static.data(
        name='inputs', shape=[None, INPUT_CHANNELS, INPUT_X, INPUT_Y],
        dtype='float32')
    train_loader = paddle.io.DataLoader(train_dataset, feed_list=[image], batch_size=INPUT_BATCH, return_list=False)

    #train_dataset[0]
    ##########################################################


    # 开始自动压缩

    if(strategy == "ChannelPrune"):
        strat = {"prune_ratio": sparsity }
    elif(strategy == "UnstructurePrune"):
        strat = {"ratio": sparsity,  'prune_params_type':None,  }
    elif(strategy == "ASPPrune"):
        pass


    ac = AutoCompression(
        model_dir=benchmark,
        model_filename="inference.pdmodel",
        params_filename="inference.pdiparams",
        save_dir=benchmark+"/%s%s_INT%d_%d" % (strategy, str(sparsity), activation_precision, weight_precision),#precision),
        #config={"QuantPost": {}, "HyperParameterOptimization": {'ptq_algo': ['avg'], 'max_quant_count': 3}},
        #config={"ChannelPrune ": {}}, #, "Distillation": {}}
        config={"QuantAware": {'onnx_format': True, 'weight_bits': weight_precision, 'activation_bits': activation_precision,
                               'quantize_op_types': ['conv2d', 'depthwise_conv2d', 'conv2d_transpose',
                                                     'elementwise_add',
                                                    'batch_norm',                        
                                                     'mul', 'matmul', 'matmul_v2']

                               }, "Distillation": {},
                strategy: strat }, ### 如果您的系统为Windows系统, 请使用当前这一行配置
        train_dataloader=train_loader,
        #eval_dataloader=train_loader)
        #train_config=None,
        )
    ac.compress()


if __name__ == "__main__":


    ####################################################################
    # Software  (CHANGEME)
    ####################################################################
    #WEIGHT
    IN_CHANNELS = 1
    OUT_CHANNELS = 1
    KERNEL_SIZE = [3,3]
    STRIDE = [1,1]
    PADDING = [0,0]
    DILATION = 1 #todos
    GROUPS = 1 #todos
    BIAS = True

    POOL_SIZE = [2,2]
    POOL_STRIDE = 1
    POOL_PAD = [0,0]

    #optional
    CONV = True
    ACTIVATION = False#"relu" #"relu"
    POOLING = False #"avg", "max"
    BATCH_NORM = False #False True

    #INPUT
    INPUT_BATCH = 1
    INPUT_CHANNELS = IN_CHANNELS
    INPUT_X = 6
    INPUT_Y = 6

    #Sparsity and Pruning and Quantization
    #precision = 8
    weight_precision = 8
    activation_precision = 8
    sparsity = 0.5
    strategy = 'UnstructurePrune'#"ChannelPrune"

    ##Save name
    benchmark = "./benchmarks/paddle/ConvFuseOp"

    config = {
        "IN_CHANNELS": IN_CHANNELS,
        "OUT_CHANNELS": OUT_CHANNELS,
        "KERNEL_SIZE": KERNEL_SIZE,
        "STRIDE": STRIDE,

        "BIAS": BIAS,
        
        "PADDING": PADDING,
        "DILATION":DILATION,
        "GROUPS":GROUPS,

        "POOL_SIZE":POOL_SIZE,
        "POOL_STRIDE": POOL_STRIDE,
        "POOL_PAD": POOL_PAD,

        "CONV": CONV,
        "ACTIVATION": ACTIVATION,
        "POOLING": POOLING,
        "BATCH_NORM": BATCH_NORM,

        "INPUT_BATCH": INPUT_BATCH,
        "INPUT_CHANNELS": INPUT_CHANNELS,
        "INPUT_X": INPUT_X,
        "INPUT_Y": INPUT_Y,

        #"precision": precision,

        "activation_precision": activation_precision,
        "weight_precision": weight_precision,
        
        "sparsity": sparsity,
        "strategy": strategy,

        "benchmark": benchmark

        }

    #############################################################


    JIA_QUANTIZE(
        config
    )
