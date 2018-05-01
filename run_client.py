#!/usr/bin/env python
from __future__ import print_function

from insights.client.config import compile_config, CONFIG as config
from insights.client import InsightsClient
from insights.client.client import set_up_logging, handle_startup


def main():
    compile_config()
    set_up_logging()
    v = handle_startup()
    if v is not None:
        if type(v) != bool:
            print(v)
        return
    else:
        client = InsightsClient()
        client.update_rules()
        tar = client.collect(check_timestamp=False,
                             image_id=(config["image_id"] or config["only"]),
                             tar_file=config["tar_file"],
                             mountpoint=config["mountpoint"])
        if not config['no_upload']:
            client.upload(tar)
        else:
            print('Archive saved to ' + tar)


if __name__ == "__main__":
    main()
