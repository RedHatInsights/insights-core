"""
LuksDump - command ``cryptsetup luksDump``
==========================================
This class provides parsing for the output of cryptsetup luksDump
<device_name>. Outputs from LUKS1 and LUKS2 are supported.
"""
import string

from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsr import (AnyChar, Char, EOF, HangingString, Lift,
                            Literal, Many, Opt, String, WithIndent, WS)
from insights.specs import Specs


class DocParser(object):
    def __init__(self):
        value_chars = set(string.printable) - set("\n\r")

        FirstLine = Literal("LUKS header information", value="header") << AnyChar.until(Char("\n")) + Opt(Many(Char("\n")))
        FirstIndent = Literal("  ")
        # we need to replace the \t by 8 spaces in the input,
        # otherwise WithIndent does not work properly
        # SecondIndent = Literal("\t")
        SecondIndent = Literal(" " * 8)

        Key = String(value_chars - set(":")) << Char(":") % "Key"
        Value = WS >> HangingString(value_chars) % "Value"

        MultilineContinuation = Many((Char("\n") + Literal(" " * 15) + SecondIndent) >> String(value_chars))
        Value1 = WS >> String(value_chars) + Opt(MultilineContinuation).map(lambda x: "".join(x)) << Char("\n")
        Value1 = Value1.map(lambda x: ("".join(x)).strip())

        ZeroLevelKVPair = Key + Value1
        FirstLevelKVPair = FirstIndent >> Key + Value1
        SecondLevelKVPair = SecondIndent >> WithIndent(Key + Value) << Opt(Many(Char("\n")))

        Luks2SectionName = Key << Char("\n")
        Luks2SectionEntry = (FirstLevelKVPair + Many(SecondLevelKVPair).map(dict)).map(self.convert_type)
        Luks2Section = Luks2SectionName + Many(Luks2SectionEntry).map(dict) << Opt(Many(Char("\n")))
        Luks2Body = Many(Luks2Section, lower=1)

        Luks1Section = ZeroLevelKVPair + Many(SecondLevelKVPair).map(dict) << Opt(Many(Char("\n")))
        Luks1Body = Many(Luks1Section.map(self.convert_status), lower=1)

        KVBlock = Many(Key + Value1).map(dict)
        LuksHeader = (FirstLine + KVBlock) << Opt(Many(Char("\n")))

        # Luks2Body has to go first, because Luks1Body consumes also valid Luks2 bodies
        self.Top = Lift(self.join_header_and_body) * LuksHeader * (Luks2Body | Luks1Body) << EOF

    def join_header_and_body(self, header, body):
        return dict([header] + body)

    def convert_type(self, section):
        section[1]["type"] = section[0][1]
        return [section[0][0], section[1]]

    def convert_status(self, section):
        section[2]["status"] = section[1]
        return [section[0], section[2]]

    def __call__(self, content):
        try:
            return self.Top(content)
        except Exception:
            raise ParseException("There was an exception when parsing one of the outputs of cryptsetup luksDump commands.")


@parser(Specs.cryptsetup_luksDump)
class LuksDump(Parser):
    """
    Sample input data is in the format::

        LUKS header information
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
                Salt:       3d c4 1b 52 fe 1c 90 d8 2a 35 b2 62 34 e9 0a 59 
                            e9 0e 48 57 b2 dd 45 
                AF stripes: 4000
                AF hash:    sha256
                Area offset:32768 [bytes]
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
                            4d cd 4d f9 de 69 39 97 
                Digest:     21 aa b3 dc 9d 46 9b 0f 3a 0f 57 13 80 c6 0b bf 
                            67 66 9e 73 ed 7d 09 2c 

    Examples:
        >>> type(parsed_result)
        <class 'insights.parsers.cryptsetup_luksDump.LuksDump'>

        >>> from pprint import pprint
        >>> pprint(parsed_result.dump["header"])
        {'Epoch': '6',
         'Flags': '(no flags)',
         'Keyslots area': '16744448 [bytes]',
         'Label': '(no label)',
         'Metadata area': '16384 [bytes]',
         'Subsystem': '(no subsystem)',
         'UUID': 'cfbcc942-e06b-4c4a-952f-e9c9b2011c27',
         'Version': '2'}

        >>> pprint(parsed_result.dump["Keyslots"]["0"])
        {'AF hash': 'sha256',
         'AF stripes': '4000',
         'Area length': '258048 [bytes]',
         'Area offset': '32768 [bytes]',
         'Cipher': 'aes-xts-plain64',
         'Cipher key': '512 bits',
         'Digest ID': '0',
         'Key': '512 bits',
         'Memory': '1048576',
         'PBKDF': 'argon2id',
         'Priority': 'normal',
         'Salt': '3d c4 1b 52 fe 1c 90 d8 2a 35 b2 62 34 e9 0a 59 e9 0e 48 57 b2 dd 45',
         'Threads': '4',
         'Time cost': '7',
         'type': 'luks2'}

        >>> parsed_result.dump["Tokens"]["0"]["type"]
        'systemd-tpm2'


    Attributes:
        dump(dict of dicts): A top level dict containing the dictionaries
            representing the header, data segments, keyslots, digests
            and tokens.
    """  # noqa

    def __init__(self, context):
        self.parse_dump = DocParser()
        super(LuksDump, self).__init__(context)

    def parse_content(self, content):
        if len(content) == 0 or (len(content) == 1 and "not a valid LUKS" in content[0]):
            raise SkipComponent
        self.dump = self.parse_dump("\n".join(content).replace("\t", " " * 8) + "\n")
