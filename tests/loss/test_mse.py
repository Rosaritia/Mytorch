import numpy as np
import torch

from .loss import MSELoss
from .tensor import Tensor


def test_mse():
    x = np.random.randn(3, 5)
    t = np.random.randn(3, 5)
    mx = Tensor(x, requires_grad=True)
    mt = Tensor(t)

    tx = torch.tensor(x, dtype=torch.float32, requires_grad=True)
    tt = torch.tensor(t, dtype=torch.float32)

    my_loss = MSELoss()
    torch_loss = torch.nn.MSELoss()

    ml = my_loss(mx, mt)
    tl = torch_loss(tx, tt)

    assert np.allclose(ml.item(), tl.item())

    ml.backward()
    tl.backward()

    assert np.allclose(mx.grad, tx.grad)
