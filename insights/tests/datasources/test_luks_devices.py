import pytest
from mock.mock import Mock

from insights import SkipComponent
from insights.parsers.blkid import BlockIDInfo
from insights.specs.datasources.luks_devices import LocalSpecs, luks_data_sources, luks_block_devices
from insights.tests import context_wrap


LUKS1_DUMP = """LUKS header information for luks1

Version:       	1
Cipher name:   	aes
Cipher mode:   	xts-plain64
Hash spec:     	sha256
Payload offset:	4096
MK bits:       	512
MK digest:     	ca fe ba be df 8c c4 b4 b8 0a cc dd 98 b5 d8 64 3a 95 3e 9e 
MK salt:       	ca fe ba be 04 3b 77 d8 ff 08 1e 0a 41 68 45 a5 
               	ca fe ba be 7b 3f a9 69 9c 9b 51 24 58 47 8d a2 
               	ca fe ba be 7b 3f a9 69 9c 9b 51 24 58 47 8d a2 
               	ca fe ba be 7b 3f a9 69 9c 9b 51 24 58 47 8d a2 
               	ca fe ba be 7b 3f a9 69 9c 9b 51 24 58 47 8d a2 
               	ca fe ba be 7b 3f a9 69 9c de ad be ef 
MK iterations: 	106562
UUID:          	263902da-5f0c-43a9-82eb-cc6f14d90448

Key Slot 0: ENABLED
	Iterations:         	2099250
	Salt:               	de ad be ef 
	Salt:               	ca fe ba be a1 f3 ae cb 4a 3f f0 2d de ad be ef 
	                      	de ad be ef 
	Key material offset:	8
	AF stripes:            	4000
Key Slot 1: ENABLED
	Iterations:         	1987820
	Salt:               	ca fe ba be f2 b7 7d f3 29 c2 c8 80 de ad be ef 
	                      	ca fe ba be 9f a1 87 07 c6 4f aa cd de ad be ef 
	                      	ca fe ba be 9f a1 87 07 c6 4f aa de ad be ef 
	Key material offset:	512
	AF stripes:            	4000
Key Slot 2: ENABLED
	Iterations:         	2052006
	Salt:               	ca fe ba be 47 94 e7 40 22 c1 bb 4a de ad be ef 
	                      	ca fe ba be 52 e8 8d 70 b2 1e 9d 47 de ad be ef 
	Key material offset:	1016
	AF stripes:            	4000
Key Slot 3: DISABLED
Key Slot 4: DISABLED
Key Slot 5: DISABLED
Key Slot 6: DISABLED
Key Slot 7: DISABLED
"""  # noqa

LUKS2_DUMP = """LUKS header information
Version:       	2
Epoch:         	6
Metadata area: 	16384 [bytes]
Keyslots area: 	16744448 [bytes]
UUID:          	cfbcc942-e06b-4c4a-952f-e9c9b2011c27
Label:         	(no label)
Subsystem:     	(no subsystem)
Flags:       	(no flags)

Data segments:
  0: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 4096 [bytes]

Keyslots:
  0: luks2
	Key:        512 bits
	Priority:   normal
	Cipher:     aes-xts-plain64
	Cipher key: 512 bits
	PBKDF:      argon2id
	Time cost:  7
	Memory:     1048576
	Threads:    4
	Salt:       ca fe ba be fe 1c 90 d8 2a 35 b2 b2 de ad be ef 
	            ca fe ba be b2 dd 45 9e ed 9a 33 b2 de ad be ef 
                    de ad be ef 
	AF stripes: 4000
	AF hash:    sha256
	Area offset:32768 [bytes]
	Area length:258048 [bytes]
	Digest ID:  0
  1: luks2
	Key:        512 bits
	Priority:   normal
	Cipher:     aes-xts-plain64
	Cipher key: 512 bits
	PBKDF:      argon2id
	Time cost:  7
	Memory:     1048576
	Threads:    4
	Salt:       ca fe ba be c1 94 15 86 2a e9 26 f8 de ad be ef 
	            ca fe ba be 05 2d 80 c9 56 e8 4d 6f de ad be ef 
	AF stripes: 4000
	AF hash:    sha256
	Area offset:290816 [bytes]
	Area length:258048 [bytes]
	Digest ID:  0
  2: luks2
	Key:        512 bits
	Priority:   normal
	Cipher:     aes-xts-plain64
	Cipher key: 512 bits
	PBKDF:      pbkdf2
	Hash:       sha512
	Iterations: 1000
	Salt:       ca fe ba be d7 8f a6 de a0 cb a4 d1 de ad be ef 
	            ca fe ba be fb 53 43 06 e8 83 90 93 de ad be ef 
	AF stripes: 4000
	AF hash:    sha512
	Area offset:548864 [bytes]
	Area length:258048 [bytes]
	Digest ID:  0
Tokens:
  0: systemd-tpm2
        tpm2-pcrs:  7
        tpm2-bank:  sha256
        tpm2-primary-alg:  ecc
        tpm2-blob:  00 9e 00 20 bd 97 78 70 3f 3a 5b 93 d4 8f dc ed
                    10 16 b2 ce f5 f7 a2 c8 63 f6 19 12 63 7a f2 94
                    26 f1 b6 1b 00 10 2e 36 26 c1 3b f7 1e 8d 86 55
        tpm2-policy-hash:
                    df 06 80 28 e7 67 b1 d0 34 f4 de 1b 8e ac 33 5a
                    df 06 80 28 e7 67 b1 d0 34 f4 de 1b 8e ac 33 5a
	Keyslot:    2
Digests:
  0: pbkdf2
	Hash:       sha256
	Iterations: 129774
	Salt:       ca fe ba be e0 65 83 82 35 03 29 56 de ad be ef 
	            ca fe ba be de 69 39 97 d5 b3 ac c4 de ad be ef 
                    de ad be ef 
	Digest:     ca fe ba be 9d 46 9b 0f 3a 0f 57 13 de ad be ef 
	            ca fe ba be ed 7d 09 2c 3d b6 fa f4 de ad be ef 
"""  # noqa

BLKID_INFO = """
/dev/nvme0n1p3: UUID="3676157d-f2f5-465c-a4c3-3c2a52c8d3f4" TYPE="crypto_LUKS" PARTUUID="d403bcbd-0eea-4bff-95b9-2237740f5c8b"
/dev/nvme0n1p1: UUID="1950-8713" BLOCK_SIZE="512" TYPE="vfat" PARTLABEL="EFI System Partition" PARTUUID="004d0ca3-373f-4d44-a085-c19c47da8b5e"
/dev/nvme0n1p2: LABEL="BOOTFS" UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="f8508c37-eeb1-4598-b084-5364d489031f"
/dev/loop0: UUID="11124c1d-990b-4277-9f74-c5a34eb2cd04" TYPE="crypto_LUKS"
/dev/mapper/luks-d32e910a-c65a-4bc7-8cb8-8b0a4ec50dce: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="LVM2_member"
/dev/zram0: LABEL="zram0" UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="swap"
"""

BLKID_INFO_NO_LUKS = """
/dev/nvme0n1p1: UUID="1950-8713" BLOCK_SIZE="512" TYPE="vfat" PARTLABEL="EFI System Partition" PARTUUID="004d0ca3-373f-4d44-a085-c19c47da8b5e"
/dev/nvme0n1p2: LABEL="BOOTFS" UUID="UVTk76-UWOc-vk7s-galL-dxIP-4UXO-0jG4MH" BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="f8508c37-eeb1-4598-b084-5364d489031f"
/dev/mapper/luks-d32e910a-c65a-4bc7-8cb8-8b0a4ec50dce: UUID="c7c45f2d-1d1b-4cf0-9d51-e2b0046682f8" TYPE="LVM2_member"
/dev/zram0: LABEL="zram0" UUID="c7116820-f2de-4aee-8ea6-0b23c6491598" TYPE="swap"
"""


def test_luks_devices_listing():
    with pytest.raises(SkipComponent):
        luks_devices = luks_block_devices({BlockIDInfo: []})

    blkid = BlockIDInfo(context_wrap(BLKID_INFO_NO_LUKS))
    broker = {BlockIDInfo: blkid}
    with pytest.raises(SkipComponent):
        luks_devices = luks_block_devices(broker)

    blkid = BlockIDInfo(context_wrap(BLKID_INFO))
    broker = {BlockIDInfo: blkid}

    luks_devices = luks_block_devices(broker)
    assert set(luks_devices) == set(["/dev/loop0", "/dev/nvme0n1p3"])


def test_luks_data_sources():
    broker = {LocalSpecs.cryptsetup_luks_dump_commands: []}
    with pytest.raises(SkipComponent):
        luks_data_sources(broker)


def test_luks1_filtering():
    command = Mock()
    command.content = LUKS1_DUMP.splitlines()
    command.cmd = "cryptsetup luksDump /dev/sda"
    broker = {LocalSpecs.cryptsetup_luks_dump_commands: [command]}
    result = luks_data_sources(broker)

    assert len(result) == 1

    text_result = "\n".join(result[0].content)
    assert "MK digest:" not in text_result
    assert "MK salt:" not in text_result
    assert "MK iterations:" in text_result
    assert "ca fe ba be" not in text_result
    assert "de ad be ef" not in text_result


def test_luks2_filtering():
    command = Mock()
    command.content = LUKS2_DUMP.splitlines()
    command.cmd = "cryptsetup luksDump /dev/sda"
    broker = {LocalSpecs.cryptsetup_luks_dump_token_commands: [command]}
    result = luks_data_sources(broker)

    assert len(result) == 1

    text_result = "\n".join(result[0].content)
    assert "Salt:" not in text_result
    assert "Digest:" not in text_result
    assert "ca fe ba be" not in text_result
    assert "de ad be ef" not in text_result

    assert "AF stripes:" in text_result
    assert "Digest ID:" in text_result

    # tokens custom fields filtering
    assert "tpm2-policy-hash" not in text_result
    assert "tpm2-blob" not in text_result
    assert "tpm2-primary-alg" not in text_result
    assert "tpm2-bank" not in text_result
    assert "tpm2-pcrs" not in text_result
