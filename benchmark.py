import paddle
from paddle.inference import create_predictor

class LayerTao:
    def __init__(self):
        self.type = []
        self.shape = []
        self.weights = []

    def functional_forward(self, activations):
        return

    def tiling_forward(self, tiling, activations):
        return 

#Generic Benchmark
#Contains multiple Layer Taos
class BenchmarkTao:

    def __init__(self):
        self.layers = []
        

#We assume all inputs to the Tao are quantized-ready models
#From quantized models, we load the model and its params
def load_paddle(path, inference):
    print(path+"/"+inference)
    #loaded = paddle.jit.load(path+"/"+inference)
    loaded = paddle.load(path+"/"+inference)
    #config = paddle.inference.Config(path+"/"+inference+".pdmodel", path+"/"+inference+".pdiparams")
    #predictor = create_predictor(config)
    #print(config)
    #print(loaded)
    #print(loaded.keys())
    #return predictor, config
    return loaded
if __name__ == "__main__":
    
    p = load_paddle(path="./benchmarks/paddle/ResNet50_vd_QAT",
                inference="inference")
    print(p)

    print(p.keys())
