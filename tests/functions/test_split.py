import numpy as np
import torch

import .functions as F
from .tensor import Tensor


def test_simple_split():
    x = np.arange(6).reshape((2, 3)).astype(np.float32)
    # x = array([[0., 1., 2.],
    #           [3., 4., 5.]], dtype=float32)

    mx = Tensor(x, requires_grad=True)

    tx = torch.tensor(x, requires_grad=True)

    my = F.split(mx)
    ty = torch.split(tx, 1)

    # 这里返回的是元组
    assert isinstance(my, tuple)

    assert np.allclose(my[0].data, ty[0].data)

    (my[0] + my[1]).sum().backward()
    (ty[0] + ty[1]).sum().backward()

    assert np.allclose(mx.grad, tx.grad)


def test_split():
    x = np.arange(6).reshape((2, 3)).astype(np.float32)
    # x = array([[0., 1., 2.],
    #           [3., 4., 5.]], dtype=float32)

    mx = Tensor(x, requires_grad=True)

    tx = torch.tensor(x, requires_grad=True)

    my = F.split(mx)
    ty = torch.split(tx, 1)

    # 这里返回的是元组
    assert isinstance(my, tuple)

    assert np.allclose(my[0].data, ty[0].data)

    (my[0]).sum().backward()
    (ty[0]).sum().backward()

    print(mx.grad)
    print(tx.grad)

    assert np.allclose(mx.grad, tx.grad)


def test_single_split():
    x = np.arange(3).reshape((1, 3)).astype(np.float32)
    # x = array([[0., 1., 2.],
    #           [3., 4., 5.]], dtype=float32)

    mx = Tensor(x, requires_grad=True)

    tx = torch.tensor(x, requires_grad=True)

    my = F.split(mx, axis=0)
    ty = torch.split(tx, 3)

    # 这里返回的是元组
    assert isinstance(my, tuple)

    assert np.allclose(my[0].data, ty[0].data)

    (my[0]).sum().backward()
    (ty[0]).sum().backward()


    assert np.allclose(mx.grad, tx.grad)
