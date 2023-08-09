"""
Custom datasources for aws information
"""
from insights.components.cloud_provider import IsAWS
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by aws datasources """
    aws_imdsv2_token = simple_command(
        '/usr/bin/curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" --connect-timeout 5',
        deps=[IsAWS]
    )


@datasource(LocalSpecs.aws_imdsv2_token, HostContext)
def aws_imdsv2_token(broker):
    """
    This datasource provides a session token for use by other specs to collect
    metadata information on AWS EC2 nodes with IMDSv2 support..

    Typical output of the input spec, which is also the output of this datasource::

        AQAEABcCFaLcKRfXhLV9_ezugiVzra-qMBoPbdWGLrbdfqSLEJzP8w==

    Returns:
        str: String that is the actual session token to be used in other commands

    Raises:
        SkipComponent: When an error occurs or no token is generated
    """
    try:
        token = broker[LocalSpecs.aws_imdsv2_token].content[0].strip()
        if token:
            return str(token)
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
