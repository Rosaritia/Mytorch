import numpy as np

import .module as nn
from .tensor import Tensor


def test_simple_embedding():
    n, d = 4, 3

    embed = nn.Embedding(n, d)

    x = 2
    mx = Tensor(x)
    my = embed(mx)

    my.sum().backward()

    assert np.allclose(embed.weight.grad, np.array([[0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 0]]))


def test_from_pretrained():
    weight = Tensor.uniform(4, 3)

    embed = nn.Embedding.from_pretrained(weight, freeze=False)

    x = [0, 2]
    mx = Tensor(x, requires_grad=True)
    my = embed(mx)

    my.sum().backward()

    assert np.allclose(embed.weight.grad, np.array([[1, 1, 1], [0, 0, 0], [1, 1, 1], [0, 0, 0]]))

    embed = nn.Embedding.from_pretrained(weight)
    my = embed(mx)
    my.sum().backward()
    # 没有梯度
    assert np.allclose(embed.weight.grad, np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]))
