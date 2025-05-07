import paddle
from paddle.vision.models import AlexNet
from paddle.vision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize,Grayscale
from PIL import Image

import paddle.nn as nn
from paddle.vision.models import LeNet, alexnet,AlexNet
from paddle.vision.models import vgg16, resnet50, resnet18, resnet34, resnet101, resnet152
def parse_model(model):
    execution_tree = []
    # 递归遍历所有子层
    for name, layer in model.named_children():
        print(name, layer)
        if isinstance(layer, nn.Sequential):
            # 展开Sequential容器
            execution_tree.extend(parse_model(layer))
        elif isinstance(layer, nn.Conv2D):
            params = {
                "in_channels": layer._in_channels,
                "out_channels": layer._out_channels,
                "kernel_size": layer._kernel_size,
                "stride": layer._stride,
                "padding": layer._padding
            }
            execution_tree.append((name,"Conv2D", params))
        elif isinstance(layer, nn.Linear):  # 处理全连接层
            params = {
                	"in_features": layer.weight.shape[1],
				"out_features": layer.weight.shape[0]
			}
            execution_tree.append((name,"Linear", params))
        elif isinstance(layer, nn.MaxPool2D):
            params = {
                "kernel_size": layer.ksize,
                "stride": layer.stride,
                "padding": layer.padding
            }
            execution_tree.append((name,"MaxPool2D", params))
        elif isinstance(layer, nn.AvgPool2D):
            params = {
                "kernel_size": layer.ksize,
                "stride": layer.stride,
                "padding": layer.padding
            }
            execution_tree.append((name,"AvgPool2D", params))
        elif isinstance(layer, nn.BatchNorm2D):
            params = {
                "num_features": layer.weight.shape[0],
                "momentum": layer._momentum,
                "epsilon": layer._epsilon
            }
            execution_tree.append((name,"BatchNorm2D", params))
        elif isinstance(layer, nn.ReLU):
            execution_tree.append((name,"ReLU", {}))
        elif hasattr(layer, "conv"):  # 处理 ResNet 的 Bottleneck 或 BasicBlock
            # 递归解析子模块（例如 Bottleneck 中的 conv1、conv2、conv3）
            execution_tree.extend(parse_model(layer))
        elif hasattr(layer, "_conv"):
            execution_tree.extend(parse_model(layer))
        elif hasattr(layer, "Bottle"):
            execution_tree.extend(parse_model(layer))
        elif isinstance(layer, paddle.nn.Layer) and 'add' in layer._full_name.lower():
            execution_tree.append((name,"Elementwise Add", {}))
    return execution_tree

def load_and_preprocess_images(image_paths, transform):
    """
    加载图片并应用预处理流程。

    参数:
        image_paths (list): 图片路径的列表。
        transform (callable): 预处理流程。

    返回:
        paddle.Tensor: 形状为 [B, 3, 224, 224] 的 Tensor。
    """
    processed_images = []

    for path in image_paths:
        # 加载图片
        img = Image.open(path).convert('RGB')  # 确保图片是 RGB 格式

        # 应用预处理
        img = transform(img)

        # 添加到列表中
        processed_images.append(img)
    # return processed_images
	
    # 将列表堆叠为一个 Tensor，形状为 [B, 3, 224, 224]
    return paddle.stack(processed_images)
	
def inference(input_tensor, model):
	# 定义钩子函数，用于保存中间层的数据
	intermediate_outputs = []
	
	def hook_fn(layer, inp, output):
	    layer_name = layer._full_name  # 获取层的名称
		
	    intermediate_outputs.append((layer_name, layer, inp, output.numpy()))  # 保存输出数据
	
	# 注册钩子
	for name, layer in model.named_sublayers():
	    if isinstance(layer, (nn.AvgPool2D, nn.ReLU,paddle.nn.Conv2D, paddle.nn.MaxPool2D, paddle.nn.Linear)):
	        layer.register_forward_post_hook(hook_fn)
	
	# for name, layer in model.named_sublayers():
	#     print(name)
	# 执行推理
	with paddle.no_grad():  # 禁用梯度计算
	    output = model(input_tensor)  # 前向传播
	
	# 打印中间层的数据
	# execution_tree = [] #sequential for now
	for layer_name, layer, in_data, out_data in intermediate_outputs:
	    print(f"Layer: {layer_name}")
		
	return intermediate_outputs, output
	
#1. 1. images + NN --> intermediate_outputs
# (layer_name, layer, input_vec, output_vec)
def get_intermediate_output(images, model, bw_img=False):
	compose = [
			Resize(256),  # 调整图片大小为 256x256
			CenterCrop(224),  # 中心裁剪为 224x224
			ToTensor(),  # 转换为 Tensor
			Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 归一化
		]
	
	if(bw_img):
		compose.append(Grayscale())
	transform = Compose(compose)
	
	processed_images = load_and_preprocess_images(images, transform)
	intermediate,output = inference(processed_images, model)

	return intermediate,output

def check_labels(output):
	# print(output.size)
	for o in output:
		probabilities = paddle.nn.functional.softmax(o, axis=0)  # 转换为概率分布
		top5_prob, top5_class = paddle.topk(probabilities, k=5)  # 获取概率最高的前 5 个类别
		
		# 加载类别标签
		import requests
		label_url = "https://github.com/PaddlePaddle/PaddleClas/raw/release/2.4/deploy/utils/imagenet1k_label_list.txt"
		labels = requests.get(label_url).text.splitlines()
		
		# 打印最终结果
		print("Top 5 predictions:")
		for i in range(5):
			print(f"  Class: {labels[top5_class[i].item()]}, Probability: {top5_prob[i].item():.4f}")
		
	
if __name__ == "__main__":
	images = ["src/test/resources/gou.jpg","src/test/resources/qiche.jpg",
		"src/test/resources/gou.jpg","src/test/resources/qiche.jpg"]
	model = alexnet(pretrained=True)
	intermediate,output = get_intermediate_output(images, model)
	check_labels(output)
	
	
if __name__ == "__main__2":

	# 加载图片
	image_path = "src/test/resources/gou.jpg"  # 替换为你的图片路径
	image = Image.open(image_path).convert("RGB")  # 确保图片是 RGB 格式

	model = alexnet(pretrained=True)#paddle.vision.models.mobilenet_v2(pretrained=True)
	
	
    # 定义图片预处理流程
	transform = Compose([
        Resize(256),  # 调整图片大小为 256x256
        CenterCrop(224),  # 中心裁剪为 224x224
        ToTensor(),  # 转换为 Tensor
        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 归一化
    ])
	
	# 预处理图片
	input_tensor = transform(image)  # 转换为 Tensor 并预处理
	input_tensor = input_tensor.unsqueeze(0)  # 增加 batch 维度 [1, 3, 224, 224]

	# 定义钩子函数，用于保存中间层的数据
	intermediate_outputs = []
	
	def hook_fn(layer, inp, output):
	    layer_name = layer._full_name  # 获取层的名称
		
	    intermediate_outputs.append((layer_name, layer, inp, output.numpy()))  # 保存输出数据
	
	# 注册钩子
	for name, layer in model.named_sublayers():
	    if isinstance(layer, (nn.AvgPool2D, nn.ReLU,paddle.nn.Conv2D, paddle.nn.MaxPool2D, paddle.nn.Linear)):
	        layer.register_forward_post_hook(hook_fn)
	
	# for name, layer in model.named_sublayers():
	#     print(name)
	# 执行推理
	with paddle.no_grad():  # 禁用梯度计算
	    output = model(input_tensor)  # 前向传播
	
	# 打印中间层的数据
	# execution_tree = [] #sequential for now
	for layer_name, layer, in_data, out_data in intermediate_outputs:
	    print(f"Layer: {layer_name}")
		# config = parse_layer(layer)
		# execution_tree.append(config)
		# print(f"Output Shape: {data.shape}")
	    # print(f"Output Data (first few values): {data.flatten()[:10]}")  # 打印前 10 个值
	    # print("\n" + "-" * 50 + "\n")
	
	# 解析最终输出结果
	probabilities = paddle.nn.functional.softmax(output[0], axis=0)  # 转换为概率分布
	top5_prob, top5_class = paddle.topk(probabilities, k=5)  # 获取概率最高的前 5 个类别
	
	# 加载类别标签
	import requests
	label_url = "https://github.com/PaddlePaddle/PaddleClas/raw/release/2.4/deploy/utils/imagenet1k_label_list.txt"
	labels = requests.get(label_url).text.splitlines()
	
	# 打印最终结果
	print("Top 5 predictions:")
	for i in range(5):
	    print(f"  Class: {labels[top5_class[i].item()]}, Probability: {top5_prob[i].item():.4f}")
	
	

if __name__ == "__main__2":
	models = {
		# "LeNet": LeNet(),
		"AlexNet": AlexNet(),#alexnet(pretrained=True),
		# "VGG16": vgg16(pretrained=True),  # 加载预训练的 VGG16
		# "ResNet18": resnet18(pretrained=True),
		# "ResNet34": resnet34(pretrained=True),
		# "ResNet50": resnet50(pretrained=True),
		# "ResNet101": resnet101(pretrained=True),
		# "ResNet152": resnet152(pretrained=True),
	}

	# 遍历模型并解析执行树
	for name, model in models.items():
		# 加载预训练权重
		# model_state_dict = paddle.load(f"{name.lower()}.pdparams")
		# model.set_state_dict(model_state_dict)

		# 解析模型结构
		execution_tree = parse_model(model)

		# 打印执行树
		print(f"Execution Tree for {name}:")
		for layer in execution_tree:
			print(f"{layer[0]} -  {layer[1]}: {layer[2]}")
		print("\n" + "=" * 60 + "\n")
