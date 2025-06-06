# MyTorch

自制深度学习框架 MyTorch，并支持 CPU 和 CUDA 加速，包含了使用不同网络结构对MNIST数据集进行分类的实验代码。

## 安装

安装依赖：
```bash
python setup.py install
```

swanlab：
看这个链接的1、2步：https://docs.swanlab.cn/guide_cloud/general/quick-start.htm

其他：
```bash
conda install xxx
```


## 使用方法（MNIST 数字分类，LeNet实现）
```bash
cd cases/mnist
```

1. MyTorch,CPU
```bash
python mnist_lenet.py
```

2. MyTorch,GPU
```bash
python mnist_lenet_cupy.py
```

3. PyTorch, GPU
```bash
python mnist_lenet_torch.py
```

4. MyTorch,GPU,WEB
**傻瓜式网络训练**
![alt text](image.png)
```bash
cd cases/web
python mnist_lenet_web.py
```
然后打开http://127.0.0.1:5000/，点击“开始训练”按钮，即可开始训练。




