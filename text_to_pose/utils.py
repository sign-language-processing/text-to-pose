from typing import Dict, List, Tuple, Union

import torch
from pose_format.torch.masked import MaskedTensor, MaskedTorch
import numpy as np


def zero_pad_collator(batch) -> Union[Dict[str, torch.Tensor], Tuple[torch.Tensor]]:
    def collate_tensors(batch: List) -> torch.Tensor:
        datum = batch[0]

        if isinstance(datum, dict):  # Recurse over dictionaries
            return zero_pad_collator(batch)

        if isinstance(datum, int) or isinstance(datum, np.int32):
            return torch.tensor(batch, dtype=torch.long)

        if isinstance(datum, MaskedTensor) or isinstance(datum, torch.Tensor):
            max_len = max([len(t) for t in batch])
            if max_len == 1:
                return torch.stack(batch)

            torch_cls = MaskedTorch if isinstance(datum, MaskedTensor) else torch

            new_batch = []
            for t in batch:
                missing = list(t.shape)
                missing[0] = max_len - t.shape[0]

                if missing[0] > 0:
                    padding_tensor = torch.zeros(missing, dtype=t.dtype, device=t.device)
                    t = torch_cls.cat([t, padding_tensor], dim=0)

                new_batch.append(t)

            return torch_cls.stack(new_batch, dim=0)

        return batch

    # For strings
    if isinstance(batch[0], str):
        return batch

    # For tuples
    if isinstance(batch[0], tuple):
        return tuple([collate_tensors([b[i] for b in batch]) for i in range(len(batch[0]))])

    # For dictionaries
    keys = batch[0].keys()
    return {k: collate_tensors([b[k] for b in batch]) for k in keys}
