import functools
import pickle

import numpy as np
import torch


def to_numpy(tensor, flat=False):
    if type(tensor) != torch.Tensor:
        return tensor
    if flat:
        return tensor.flatten().detach().cpu().numpy()
    else:
        return tensor.detach().cpu().numpy()


def set_weights(model, param_loc: str, tensor: torch.Tensor, fixed: bool = False):
    param = dict(model.named_parameters())[param_loc]
    param.data = tensor
    if fixed:
        param.requires_grad = False


def set_weights_by_file(model, param_loc: str, tensor_file: str, fixed: bool = False):
    param = dict(model.named_parameters())[param_loc]
    with open(f"weights/{tensor_file}", "rb") as fh:
        param.data = pickle.load(fh)
    if fixed:
        param.requires_grad = False


@functools.lru_cache(maxsize=None)
def fourier_basis(k):
    fourier_basis = []
    fourier_basis.append(torch.ones(k) / np.sqrt(k))
    fourier_basis_names = ["Const"]
    # Note that if p is even, we need to explicitly add a term for cos(kpi), ie
    # alternating +1 and -1
    for i in range(1, k // 2 + 1):
        fourier_basis.append(torch.cos(2 * torch.pi * torch.arange(k) * i / k))
        fourier_basis.append(torch.sin(2 * torch.pi * torch.arange(k) * i / k))
        fourier_basis[-2] /= fourier_basis[-2].norm()
        fourier_basis[-1] /= fourier_basis[-1].norm()
        fourier_basis_names.append(f"cos {i}")
        fourier_basis_names.append(f"sin {i}")
    return torch.stack(fourier_basis, dim=0).to("cuda")