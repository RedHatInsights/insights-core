import doctest
import pytest
from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import nvidia
from insights.parsers.nvidia import NvidiaSmiL
from insights.tests import context_wrap

NVIDIA_SMI_L_INPUT_1 = """
GPU 0: NVIDIA A100-PCIE-40GB (UUID: GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
GPU 1: NVIDIA A100-PCIE-40GB (UUID: GPU-c9bd25dc-c0c4-3ab6-8f7f-3ad16d6bde4a)
""".strip()


NVIDIA_SMI_L_INPUT_2 = """
GPU 0: NVIDIA T1000 (UUID: GPU-c05fe28c-5935-1c6d-3633-2fc61d26b6d4)
GPU 1: Tesla V100-PCIE-16GB (UUID: GPU-b08ecee0-0ea5-7b07-d459-baa5b95f5e89)
"""

NVIDIA_SMI_L_INPUT_3 = """
GPU 0: Quadro RTX 8000 (UUID: GPU-6b201039-6477-dd9c-1edd-137c8c44f8d6)
GPU 1: Quadro RTX 8000 (UUID: GPU-dbd81806-9040-9cc3-9eb9-87684fa2b7a4)
GPU 2: Quadro RTX 8000 (UUID: GPU-b4524d9e-858d-1050-1b4d-4fe0c94e8ea8)
GPU 3: Quadro RTX 8000 (UUID: GPU-51c72de5-fdc2-94b1-59e6-a12d4e961695)
GPU 4: Quadro RTX 8000 (UUID: GPU-bf443bbf-8598-8e63-e10c-e23ca737da84)
GPU 5: Quadro RTX 8000 (UUID: GPU-b20d26a5-5f6f-5c96-9d2e-ba6bfbb5d9a0)
GPU 6: Quadro RTX 8000 (UUID: GPU-5a497672-18a9-95c7-5b61-74353dd9c9cb)
GPU 7: Quadro RTX 8000 (UUID: GPU-9f690c37-bb84-1e1a-1e4a-3dbfd1b1015c)
""".strip()


def test_nvidia_smi_l():
    gpus = NvidiaSmiL(context_wrap(NVIDIA_SMI_L_INPUT_1))
    assert len(gpus) == 2
    assert gpus[0] == {
        "model": "NVIDIA A100-PCIE-40GB",
        "uuid": "GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838"}
    assert gpus.gpu_count == 2
    assert len(gpus.gpu_models) == 1
    assert "NVIDIA A100-PCIE-40GB" in gpus.gpu_models

    gpus = NvidiaSmiL(context_wrap(NVIDIA_SMI_L_INPUT_2))
    assert len(gpus) == 2
    assert gpus[0] == {
        "model": "NVIDIA T1000",
        "uuid": "GPU-c05fe28c-5935-1c6d-3633-2fc61d26b6d4"}
    assert gpus.gpu_count == 2
    assert len(gpus.gpu_models) == 2
    assert "Tesla V100-PCIE-16GB" in gpus.gpu_models

    gpus = NvidiaSmiL(context_wrap(NVIDIA_SMI_L_INPUT_3))
    assert len(gpus) == 8
    assert gpus[0] == {
        "model": "Quadro RTX 8000",
        "uuid": "GPU-6b201039-6477-dd9c-1edd-137c8c44f8d6"}
    assert gpus.gpu_count == 8


NVIDIA_SMI_L_UNPARSABLE_0 = """
some other extra line  # will be skipped in parsing
""".strip()

NVIDIA_SMI_L_UNPARSABLE_1 = """
some other extra line  # will be skipped in parsing
GPU 0: NVIDIA A100-PCIE-40GB ( GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
GPU 1 NVIDIA A100-PCIE-40GB (UUID: GPU-c9bd25dc-c0c4-3ab6-8f7f-3ad16d6bde4a)
""".strip()

NVIDIA_SMI_L_UNPARSABLE_2 = """
GPU 0: NVIDIA A100-PCIE-40GB (UUID: GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
GPU 2: NVIDIA A100-PCIE-40GB (UUID: GPU-c9bd25dc-c0c4-3ab6-8f7f-3ad16d6bde4a)
""".strip()

NVIDIA_SMI_L_UNPARSABLE_3 = """
GPU 0:  (UUID: GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
GPU 1: NVIDIA A100-PCIE-40GB (UUID: GPU-c9bd25dc-c0c4-3ab6-8f7f-3ad16d6bde4a)
""".strip()

NVIDIA_SMI_L_UNPARSABLE_4 = """
GPU 0: NVIDIA A100-PCIE-40GB (UUID: GPU-63110aaa-3561-c8f5-e125-4ab40bbcf838)
GPU 1: NVIDIA A100-PCIE-40GB (UUID: )
""".strip()


def test_nvidia_smi_l_exceptions():
    with pytest.raises(SkipComponent) as err:
        NvidiaSmiL(context_wrap(" "))
    assert "Empty content" in str(err)

    with pytest.raises(ParseException) as err:
        NvidiaSmiL(context_wrap(NVIDIA_SMI_L_UNPARSABLE_0))
    assert "Empty GPU info after parse" in str(err)

    with pytest.raises(ParseException) as err:
        NvidiaSmiL(context_wrap(NVIDIA_SMI_L_UNPARSABLE_1))
    assert "Unparsable GPU model:" in str(err)

    with pytest.raises(ParseException) as err:
        NvidiaSmiL(context_wrap(NVIDIA_SMI_L_UNPARSABLE_2))
    assert "Unparsable GPU id:" in str(err)

    with pytest.raises(ParseException) as err:
        NvidiaSmiL(context_wrap(NVIDIA_SMI_L_UNPARSABLE_3))
    assert "Unparsable GPU line:" in str(err)

    with pytest.raises(ParseException) as err:
        NvidiaSmiL(context_wrap(NVIDIA_SMI_L_UNPARSABLE_4))
    assert "Unparsable GPU line:" in str(err)


def test_nvidia_doc_examples():
    env = {
        'gpus': NvidiaSmiL(context_wrap(NVIDIA_SMI_L_INPUT_1)),
    }
    failed, total = doctest.testmod(nvidia, globs=env)
    assert failed == 0
