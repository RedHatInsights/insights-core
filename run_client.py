#!/usr/bin/env python
#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
