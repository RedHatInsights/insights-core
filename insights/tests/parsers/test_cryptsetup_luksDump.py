import doctest
import pytest

from insights.parsers import cryptsetup_luksDump
from insights.tests import context_wrap
from insights import SkipComponent


LUKS1_DUMP = """LUKS header information for luks1

Version:       	1
Cipher name:   	aes
Cipher mode:   	xts-plain64
Hash spec:     	sha256
Payload offset:	4096
MK bits:       	512
MK digest:     	db b8 55 5e df 8c c4 b4 b8 0a cc dd 98 b5 d8 64 3a 95 3e 9e 
MK salt:       	1b 16 42 cb 04 3b 77 d8 ff 08 1e 0a 41 68 45 a5 
               	c3 2e 76 04 7b 3f a9 69 9c 9b 51 24 58 47 8d a2 
               	ca fe ba be 7b 3f a9 69 9c 9b 51 24 58 
MK iterations: 	106562
UUID:          	263902da-5f0c-43a9-82eb-cc6f14d90448

Key Slot 0: ENABLED
	Iterations:         	2099250
	Salt:               	3d 99 94 f5 a1 f3 ae cb 4a 3f f0 2d 29 46 22 6b 
	                      	3d 99 94 f5 a1 f3 ae cb 4a 3f f0 2d 29 46 22 6b 
	                      	4d 25 
	Key material offset:	8
	AF stripes:            	4000
Key Slot 1: ENABLED
	Iterations:         	1987820
	Salt:               	27 3c 70 b5 f2 b7 7d f3 29 c2 c8 80 6b ff de cd 
	                      	aa 58 b3 85 9f a1 87 07 c6 4f aa cd 59 28 97 ea 
	                      	aa 58 b3 85 9f a1 87 07 c6 4f aa cd 59 28 97 
	Key material offset:	512
	AF stripes:            	4000
Key Slot 2: ENABLED
	Iterations:         	2052006
	Salt:               	33 28 f2 0c 47 94 e7 40 22 c1 bb 4a 06 aa f0 5c 
	                      	38 cc e4 a8 52 e8 8d 70 b2 1e 9d 47 70 a9 f1 2d 
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

  1: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 4096 [bytes]
	flags : backup-previous

  2: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 4096 [bytes]
	flags : backup-final

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
	Salt:       3d c4 1b 52 fe 1c 90 d8 2a 35 b2 62 34 e9 0a 59 
	            e9 0e 48 57 b2 dd 45 
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
	Salt:       bb b4 33 41 c1 94 15 86 2a e9 26 f8 d8 16 83 b1 
	            d0 00 f9 25 05 2d 80 
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
	Salt:       a8 53 27 a8 d7 8f a6 de a0 cb a4 d1 d4 2c 60 19 
	            f0 32 a2 b0 fb 53 43 
	AF stripes: 4000
	AF hash:    sha512
	Area offset:548864 [bytes]
	Area length:258048 [bytes]
	Digest ID:  0
Tokens:
  0: systemd-tpm2
	Keyslot:    2
Digests:
  0: pbkdf2
	Hash:       sha256
	Iterations: 129774
	Salt:       e6 31 d5 74 e0 65 83 82 35 03 29 56 0e 80 36 5c 
	            4d cd 4d f9 de 69 39 
	Digest:     21 aa b3 dc 9d 46 9b 0f 3a 0f 57 13 80 c6 0b bf 
	            67 66 9e 73 ed 7d 09 
"""  # noqa

LUKS_BAD_DUMP = "Device /dev/nvme0n1p1 is not a valid LUKS device."


def test_cryptsetup_luks_dump_luks1():
    luks1_parsed = cryptsetup_luksDump.LuksDump(context_wrap(LUKS1_DUMP))
    print(luks1_parsed.dump)
    assert luks1_parsed.dump is not None
    assert set(luks1_parsed.dump.keys()) == set(["header"] + ["Key Slot " + str(x) for x in range(8)])
    assert luks1_parsed.dump["header"]["Version"] == "1"
    assert luks1_parsed.dump["Key Slot 0"]["status"] == "ENABLED"
    assert luks1_parsed.dump["Key Slot 7"]["status"] == "DISABLED"


def test_cryptsetup_luks_dump_luks2():
    luks2_parsed = cryptsetup_luksDump.LuksDump(context_wrap(LUKS2_DUMP))
    assert luks2_parsed.dump is not None
    assert set(luks2_parsed.dump.keys()) == set(["header", "Data segments", "Keyslots", "Tokens", "Digests"])
    assert luks2_parsed.dump["header"]["Version"] == "2"
    assert len(luks2_parsed.dump["Keyslots"].keys()) == 3
    assert luks2_parsed.dump["Keyslots"]["0"]["type"] == "luks2"
    assert len(luks2_parsed.dump["Data segments"].keys()) == 3
    assert len(luks2_parsed.dump["Tokens"].keys()) == 1
    assert len(luks2_parsed.dump["Digests"].keys()) == 1

    assert luks2_parsed.dump["Tokens"]["0"]["type"] == "systemd-tpm2"
    assert luks2_parsed.dump["Keyslots"]["0"]["type"] == "luks2"


def test_cryptsetup_luks_dump_bad():
    with pytest.raises(SkipComponent):
        cryptsetup_luksDump.LuksDump(context_wrap(LUKS_BAD_DUMP)).dump
    with pytest.raises(SkipComponent):
        cryptsetup_luksDump.LuksDump(context_wrap("")).dump


def test_doc_examples():
    env = {
            'parsed_result': cryptsetup_luksDump.LuksDump(context_wrap(LUKS2_DUMP)),
          }
    failed, total = doctest.testmod(cryptsetup_luksDump, globs=env)
    assert failed == 0
