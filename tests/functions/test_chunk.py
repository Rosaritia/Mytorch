import numpy as np
import torch

import .functions as F
from .tensor import Tensor


def test_simple_chunk():
    x = np.arange(12).astype(np.float32)

    mx = Tensor(x, requires_grad=True)

    tx = torch.tensor(x, requires_grad=True)

    my = F.chunk(mx, 2)
    ty = torch.chunk(tx, 2)

    # 这里返回的是元组
    assert isinstance(my, tuple)

    assert np.allclose(my[0].data, ty[0].data)
    assert np.allclose(my[-1].data, ty[-1].data)

    ty0 = ty[0] * 2
    ty1 = ty[1] * 3

    my0 = my[0] * 2
    my1 = my[1] * 3

    (my0 + my1).sum().backward()
    (ty0 + ty1).sum().backward()

    assert np.allclose(mx.grad, tx.grad)


def test_chunk():
    x = np.arange(11).astype(np.float32)

    mx = Tensor(x, requires_grad=True)

    tx = torch.tensor(x, requires_grad=True)

    my = F.chunk(mx, 6)
    ty = torch.chunk(tx, 6)

    # 这里返回的是元组
    assert isinstance(my, tuple)

    assert np.allclose(my[0].data, ty[0].data)
    assert np.allclose(my[-1].data, ty[-1].data)

    (my[0]).sum().backward()
    (ty[0]).sum().backward()

    print(mx.grad)

    assert np.allclose(mx.grad, tx.grad)
