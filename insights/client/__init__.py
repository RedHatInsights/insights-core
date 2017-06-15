import optparse
from . import client
from .auto_config import try_auto_configuration
from .client_config import parse_config_file, InsightsClient, set_up_options


def parse_options():
    parser = optparse.OptionParser()
    set_up_options(parser)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unknown arguments: %s" % args)
    return parse_config_file(options.conf), options


def fetch():
    """
        returns (str): path to new egg.  None if no update.
    """
    pass


def collect(format="json", options=None):
    # Configure Insights uploader
    InsightsClient.config, InsightsClient.options = parse_options()
    InsightsClient.options.reregister = True
    try_auto_configuration()
    return client.collect()


def upload(path):
    client.upload(path)
