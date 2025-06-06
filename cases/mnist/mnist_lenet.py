from torchvision import transforms, datasets
import numpy as np
from time import time
import os

from mytorch.ops import Max as mymax
from mytorch.tensor import Tensor, no_grad
from mytorch.dataset import MNISTDataset
from mytorch.dataloader import DataLoader, prepare_mnist_data
import mytorch.module as nn
from mytorch.module import Module, Linear, Conv2D, MaxPooling2D
import mytorch.functions as F
from mytorch.functions import relu, softmax
from mytorch.optim import Adam, SGD, Adagrad
from mytorch.loss import CrossEntropyLoss, NLLLoss
from mytorch import cuda
import swanlab

# 初始化 SwanLab
run = swanlab.init(
    project="MNIST-LeNet-1230",
    experiment_name="MNIST-LeNet",
    config={
        "optimizer": "Adam",
        "learning_rate": 0.01,
        "batch_size": 64,
        "num_epochs": 10,
        "device": "cuda" if cuda.is_available() else "cpu",
    },
)

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(root_dir, 'data')

# 加载和准备数据
train_dataset = prepare_mnist_data(root=data_dir, backend='numpy', train=True)
test_dataset = prepare_mnist_data(root=data_dir, backend='numpy', train=False)

train_loader = DataLoader(train_dataset, batch_size=run.config.batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=run.config.batch_size, shuffle=False)

class LeNet(nn.Module):
    def __init__(self):
        super(LeNet, self).__init__()
        # 第一个卷积层: 1个输入通道, 6个输出通道, 5x5的卷积核
        self.conv1 = Conv2D(1, 6, (5, 5))
        # 第一个池化层: 2x2
        self.pool1 = MaxPooling2D(2, 2, 2)
        # 第二个卷积层: 6个输入通道, 16个输出通道, 5x5的卷积核
        self.conv2 = Conv2D(6, 16, (5, 5))
        # 第二个池化层: 2x2
        self.pool2 = MaxPooling2D(2, 2, 2)
        # 三个全连接层
        self.fc1 = Linear(16 * 4 * 4, 120)
        self.fc2 = Linear(120, 84)
        self.fc3 = Linear(84, 10)

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        
        batch_size = x.shape[0]
        x = x.view(batch_size, -1)
        
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x = F.log_softmax(x)
        return x

model = LeNet()
print("Model initialized.")

criterion = NLLLoss()
optimizer = Adam(model.parameters(), lr=run.config.learning_rate) # model.parameters()会返回模型中所有需要优化的参数

def train(epoch):
    start_time = time()
    running_loss = 0.0
    total_batches = len(train_loader)
    print(f"\n【Epoch {epoch + 1}】")
    
    model.train()  # 设置为训练模式
    for batch_idx, (inputs, target) in enumerate(train_loader):
        outputs = model(inputs)
        loss = criterion(outputs, target)
        optimizer.zero_grad()  # 如果不清零，新一轮的梯度会与之前的梯度叠加，导致更新错误
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        
        # 每10个batch更新一次损失
        if batch_idx % 10 == 0:
            avg_loss = running_loss / (batch_idx + 1)
            run.log({
                "main/loss": avg_loss,
            }, step=epoch * total_batches + batch_idx)
            
            # 计算准确率
            predicted = mymax().forward(outputs.data, axis=1)
            predicted = np.round(predicted)
            correct = (predicted == target.array()).sum().item()
            accuracy = 100 * correct / target.array().size
            
            # 打印进度条
            print(f"Batch [{batch_idx + 1}/{total_batches}]  - Loss: [{avg_loss:.4f}]  - Accuracy: [{accuracy:.2f}%]", end="\r")
    
    # 打印epoch总结
    epoch_loss = running_loss / total_batches
    epoch_time = time() - start_time
    print(f"\nTime Used: {epoch_time:.2f} s")

    run.log({
        "train/epoch_loss": epoch_loss,
        "train/epoch_time": epoch_time,
        "main/samples_per_second": len(train_dataset) / epoch_time
    }, step=epoch)

def test(epoch):
    start_time = time()
    correct = 0
    total = 0
    total_loss = 0
    total_batches = len(test_loader)
    
    print(f"\n【Test {epoch + 1}】")
    model.eval()  # 设置为评估模式
    
    with no_grad():
        for batch_idx, (inputs, labels) in enumerate(test_loader):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            predicted = mymax().forward(outputs.data, axis=1)
            predicted = np.round(predicted)

            total_loss += loss.item()
            total += labels.array().size
            correct += (predicted == labels.array()).sum().item()
            
            # 打印进度条
            print(f"Batch [{batch_idx + 1}/{total_batches}]  - Accuracy: [{100 * correct / total:.2f}%]", end="\r")
    
    # 计算最终指标
    accuracy = 100 * correct / total
    avg_loss = total_loss / total_batches
    test_time = time() - start_time
    
    # 记录到SwanLab
    run.log({
        "main/accuracy": accuracy,
        "test/loss": avg_loss,
        "test/time": test_time
    }, step=epoch)
    
    # 打印测试结果总结
    print(f"\nTime Used: {test_time:.2f} s")

if __name__ == '__main__':
    total_params = sum(p.array().size for p in model.parameters())
    print(f"\nModel Summary:")
    print(f"Total Parameters: {total_params:,}")
    print(f"Training Device: {run.config.device}")
    print(f"\nStarting training for {run.config.num_epochs} epochs...")
    
    for epoch in range(run.config.num_epochs):
        train(epoch)
        test(epoch)
        
        # 每个epoch后记录学习率
        swanlab.log({
            "train/learning_rate": optimizer.param_groups[0]["lr"]
        }, step=epoch)