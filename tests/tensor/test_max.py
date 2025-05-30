from .tensor import Tensor
import numpy as np
import torch


def test_simple_max():
    x = Tensor([1, 2, 3, 6, 7, 9, 2], requires_grad=True)
    z = x.max()

    assert z.data == [9]
    z.backward()

    assert x.grad.tolist() == [0, 0, 0, 0, 0, 1, 0]


def test_simple_max2():
    x = Tensor([1, 2, 3, 9, 7, 9, 2], requires_grad=True)
    z = x.max()

    assert z.data == [9]  # 最大值还是9
    z.backward()

    # 但是有两个最大值，所以梯度被均分了
    assert x.grad.tolist() == [0, 0, 0, 0.5, 0, 0.5, 0]


def test_matrix_max():
    a = np.array([[1., 1., 8., 9., 1.],
                  [4., 5., 9., 9., 8.],
                  [8., 6., 9., 7., 9.],
                  [8., 6., 1., 9., 8.]])

    x = Tensor(a, requires_grad=True)
    z = x.max()

    assert z.data == [9]  # 最大值是9
    z.backward()

    # 总共有6个9
    np.testing.assert_array_almost_equal(x.grad, [[0, 0, 0, 1 / 6, 0],
                                                       [0, 0, 1 / 6, 1 / 6, 0],
                                                       [0, 0, 1 / 6, 0, 1 / 6],
                                                       [0, 0, 0, 1 / 6, 0]])


def test_matrix_max2():
    a = np.array([[1., 1., 8., 9., 1.],
                  [4., 5., 9., 9., 8.],
                  [8., 6., 9., 7., 9.],
                  [8., 6., 1., 9., 8.]])

    x = Tensor(a, requires_grad=True)
    z = x.max(0)  # [8, 6, 9, 9, 9]

    assert z.data.tolist() == [8, 6, 9, 9, 9]
    z.backward(np.array([1, 1, 1, 1, 1]))

    grad = [[0., 0., 0., 1 / 3, 0.],
            [0., 0., 0.5, 1 / 3, 0.],
            [0.5, 0.5, 0.5, 0, 1],
            [0.5, 0.5, 0., 1 / 3, 0.]]

    np.testing.assert_array_almost_equal(x.grad, np.array(grad))


def test_matrix_with_axis():
    a = np.arange(24).reshape(2, 3, 4)

    mx = Tensor(a, requires_grad=True)
    #    Tensor([[[ 0  1  2  3]
    #             [ 4  5  6  7]
    #             [ 8  9 10 11]]
    #
    #            [[12 13 14 15]
    #             [16 17 18 19]
    #             [20 21 22 23]]]

    my = mx.max(1)  # [8, 6, 9, 9, 9]

    tx = torch.tensor(a, dtype=torch.float32, requires_grad=True)
    ty = tx.max(1)

    assert np.allclose(my.data, ty.values.data)

    my.sum().backward()
    ty.values.sum().backward()

    np.testing.assert_array_almost_equal(tx.grad, mx.grad)


def test_matrix_with_negative_axis():
    a = np.arange(16).reshape(2, 2, 4)

    mx = Tensor(a, requires_grad=True)

    my = mx.max(-2)

    tx = torch.tensor(a, dtype=torch.float32, requires_grad=True)
    ty = tx.max(-2)

    assert np.allclose(my.data, ty.values.data)

    my.sum().backward()
    ty.values.sum().backward()

    np.testing.assert_array_almost_equal(tx.grad, mx.grad)
