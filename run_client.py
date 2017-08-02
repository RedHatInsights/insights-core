from insights.client.config import compile_config, CONFIG as config
from insights.client import InsightsClient
from insights.client.client import set_up_logging, handle_startup

compile_config()
set_up_logging()
v = handle_startup()
if v is not None:
    if v is not False:
        print v
else:
    client = InsightsClient()
    tar = client.collect(check_timestamp=False)
    if not config['no_upload']:
        client.upload(tar)
    else:
        print tar
