"""
AWSInstanceID
=============

These parsers read the output of commands to collect identify information
from AWS instances.

AWSInstanceIdDoc - ``curl -s http://169.254.169.254/latest/dynamic/instance-identity/document``
-----------------------------------------------------------------------------------------------

AWSInstanceIdPkcs7 - ``curl -s http://169.254.169.254/latest/dynamic/instance-identity/pkcs7``
----------------------------------------------------------------------------------------------

AWSPublicIpv4Addresses - ``curl -s http://169.254.169.254/latest/meta-data/public-ipv4``
----------------------------------------------------------------------------------------

AWSPublicHostname ``curl -s http://169.254.169.254/latest/meta-data/public-hostname``
-------------------------------------------------------------------------------------

"""
from __future__ import print_function
import json

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs

_aws_curl_invalid_keyworks = [
    'curl: ',
    '<?xml ',
]


def _validate_content(content, length=0):
    if (not content or                                 # Empty content
            (length > 0 and len(content) > length) or  # Too many lines
            any(item in content[0]                     # Unexpected keywords
                for item in _aws_curl_invalid_keyworks)):
        raise SkipComponent()


@parser(Specs.aws_instance_id_doc)
class AWSInstanceIdDoc(CommandParser, dict):
    """
    Class for parsing the AWS Instance Identity Document returned by the command::

        curl -s http://169.254.169.254/latest/dynamic/instance-identity/document

    Typical output of this command is::

        {
            "devpayProductCodes" : null,
            "marketplaceProductCodes" : [ "1abc2defghijklm3nopqrs4tu" ],
            "availabilityZone" : "us-west-2b",
            "privateIp" : "10.158.112.84",
            "version" : "2017-09-30",
            "instanceId" : "i-1234567890abcdef0",
            "billingProducts" : [ "bp-6ba54002" ],
            "instanceType" : "t2.micro",
            "accountId" : "123456789012",
            "imageId" : "ami-5fb8c835",
            "pendingTime" : "2016-11-19T16:32:11Z",
            "architecture" : "x86_64",
            "kernelId" : null,
            "ramdiskId" : null,
            "region" : "us-west-2"
        }

    Raises:
        SkipComponent: When content is empty or cannot be parsed.
        ParseException: When type cannot be recognized.

    Attributes:
        dict: Parser object is a dictionary that is a direct translation of the input key:value pairs.
        json (str): Input in JSON string format.

    Examples:
        >>> print(aws_id_doc['billingProducts'][0])
        bp-6ba54002
        >>> 'version' in aws_id_doc
        True
        >>> print(aws_id_doc['version'])
        2017-09-30
    """

    def parse_content(self, content):
        _validate_content(content)

        # Just in case curl stats are present in data
        startline = 0
        for l in content:
            if l.strip().startswith('{'):
                break
            startline += 1

        self.json = '\n'.join([l.rstrip() for l in content[startline:]])

        try:
            doc_values = json.loads(self.json)
            self.update(doc_values)
        except ValueError as e:
            raise ParseException('Failed to parse json with error: %s', str(e))


@parser(Specs.aws_instance_id_pkcs7)
class AWSInstanceIdPkcs7(CommandParser):
    """
    Class for parsing the AWS Instance Identity PKCS7 signature returned by the command::

        curl -s http://169.254.169.254/latest/dynamic/instance-identity/pkcs7

    Typical output of this command is::

        MIICiTCCAfICCQD6m7oRw0uXOjANBgkqhkiG9w0BAQUFADCBiDELMAkGA1UEBhMC
        VVMxCzAJBgNVBAgTAldBMRAwDgYDVQQHEwdTZWF0dGxlMQ8wDQYDVQQKEwZBbWF6
        b24xFDASBgNVBAsTC0lBTSBDb25zb2xlMRIwEAYDVQQDEwlUZXN0Q2lsYWMxHzAd
        BgkqhkiG9w0BCQEWEG5vb25lQGFtYXpvbi5jb20wHhcNMTEwNDI1MjA0NTIxWhcN
        MTIwNDI0MjA0NTIxWjCBiDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAldBMRAwDgYD
        VQQHEwdTZWF0dGxlMQ8wDQYDVQQKEwZBbWF6b24xFDASBgNVBAsTC0lBTSBDb25z
        b2xlMRIwEAYDVQQDEwlUZXN0Q2lsYWMxHzAdBgkqhkiG9w0BCQEWEG5vb25lQGFt
        YXpvbi5jb20wgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAMaK0dn+a4GmWIWJ
        21uUSfwfEvySWtC2XADZ4nB+BLYgVIk60CpiwsZ3G93vUEIO3IyNoH/f0wYK8m9T
        rDHudUZg3qX4waLG5M43q7Wgc/MbQITxOUSQv7c7ugFFDzQGBzZswY6786m86gpE
        Ibb3OhjZnzcvQAaRHhdlQWIMm2nrAgMBAAEwDQYJKoZIhvcNAQEFBQADgYEAtCu4
        nUhVVxYUntneD9+h8Mg9q6q+auNKyExzyLwaxlAoo7TJHidbtS4J5iNmZgXL0Fkb
        FFBjvSfpJIlJ00zbhNYS5f6GuoEDmFJl0ZxBHjJnyp378OD8uTs7fLvjx79LjSTb
        NYiytVbZPQUQ5Yaxu2jXnimvw3rrszlaEXAMPLE

    Raises:
        SkipComponent: When content is empty or cannot be parsed.

    Attributes:
        signature (str): PKCS7 signature string including header and footer.

    Examples:
        >>> aws_id_sig.signature.startswith('-----BEGIN PKCS7-----\\nMIICiTCCAfICCQD6m7oRw0uXOjANBgkqhkiG9w0BAQUFADCBiDELMAkGA1UEBhMC\\n')
        True
        >>> aws_id_sig.signature.endswith('NYiytVbZPQUQ5Yaxu2jXnimvw3rrszlaEXAMPLE\\n-----END PKCS7-----')
        True
    """
    def parse_content(self, content):
        _validate_content(content)

        # Just in case curl stats are present in data
        startline = 0
        for l in content:
            if ' ' not in l.strip() and len(l.strip()) > 0:
                break
            startline += 1

        self.signature = '-----BEGIN PKCS7-----\n' + '\n'.join([l.rstrip() for l in content[startline:]]) + "\n-----END PKCS7-----"


@parser(Specs.aws_public_ipv4_addresses)
class AWSPublicIpv4Addresses(CommandParser, list):
    """
    Class for parsing the AWS public IP. At the moment, a single instance can only have assigned one public
    IPv4 address on AWS EC2. This parsers takes the value and makes it a list just in case the capability
    is added later. The data is fetched via

        curl -s http://169.254.169.254/latest/meta-data/public-ipv4

    command and contains a pure string, e.g. "1.2.3.4" without newline.

    Raises:
        SkipComponent: When content is empty or cannot be parsed.
    """

    def parse_content(self, content):
        _validate_content(content, length=1)

        self.append(content[0])


@parser(Specs.aws_public_hostnames)
class AWSPublicHostnames(CommandParser, list):
    """
    Class for parsing the AWS public hostname. At the moment, a single instance can only have assigned one public
    IPv4 address on AWS EC2. This parsers takes the value and makes it a list just in case the capability
    is added later. The data is fetched via

        curl -s http://169.254.169.254/latest/meta-data/public-hostname

    command and contains a pure string, e.g. "ec2-1-2-3-4.us-east-1.awscloud.com" without newline.

    Raises:
        SkipComponent: When content is empty or cannot be parsed.
    """

    def parse_content(self, content):
        _validate_content(content, length=1)

        self.append(content[0])
