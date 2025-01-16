# 导入依赖包
import paddle
from PIL import Image
from paddle.vision.datasets import DatasetFolder
from paddle.vision.transforms import transforms
from paddleslim.auto_compression import AutoCompression
paddle.enable_static()
# 定义DataSet
class ImageNetDataset(DatasetFolder):
    def __init__(self, path, image_size=224):
        super(ImageNetDataset, self).__init__(path)
        normalize = transforms.Normalize(
            mean=[123.675, 116.28, 103.53], std=[58.395, 57.120, 57.375])
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(image_size), transforms.Transpose(),
            normalize
        ])

    def __getitem__(self, idx):
        img_path, _ = self.samples[idx]
        return self.transform(Image.open(img_path).convert('RGB'))

    def __len__(self):
        return len(self.samples)

# 定义DataLoader
train_dataset = ImageNetDataset("./ILSVRC2012/train2/")
image = paddle.static.data(
    name='inputs', shape=[None] + [3, 224, 224], dtype='float32')
train_loader = paddle.io.DataLoader(train_dataset, feed_list=[image], batch_size=1, return_list=False)


# 开始自动压缩
precision = 4
sparsity = 0.5
strategy = 'UnstructurePrune'#"ChannelPrune"

if(strategy == "ChannelPrune"):
    strat = {"prune_ratio": sparsity }
elif(strategy == "UnstructurePrune"):
    strat = {"ratio": sparsity,  'prune_params_type':None,  }
elif(strategy == "ASPPrune"):
    pass


ac = AutoCompression(
    model_dir="./benchmarks/paddle/efficientnetb0",
    model_filename="inference.pdmodel",
    params_filename="inference.pdiparams",
    save_dir="./benchmarks/paddle/efficientnetb0_%s%s_INT%d" % (strategy, str(sparsity), precision),
    #config={"QuantPost": {}, "HyperParameterOptimization": {'ptq_algo': ['avg'], 'max_quant_count': 3}},
    #config={"ChannelPrune ": {}}, #, "Distillation": {}}
    config={"QuantAware": {'onnx_format': True, 'weight_bits': precision, 'activation_bits': precision}, "Distillation": {},
            strategy: strat }, ### 如果您的系统为Windows系统, 请使用当前这一行配置
    train_dataloader=train_loader,
    #eval_dataloader=train_loader)
    #train_config=None,
    )
ac.compress()
