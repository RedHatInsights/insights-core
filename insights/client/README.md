## Insights Client (Core) Developer Notes

* ### **See https://github.com/RedHatInsights/insights-client for build and usage instructions, and details about configuration and runtime.**

* To rebuild the egg from source, run `./build_client_egg.sh` from the repo root. This will generate a file `insights.zip` that you can pass to `insights-client` with the `EGG` environment variable.

* The `uploader_json_map.json` file is **NOT** `uploader.json`. Its purpose is to serve as a compatibility layer between denylist configurations for classic collection and core collection. Changes to this file will not affect the commands or files that are collected. It is advised not to make changes to this file as it is copied from the production-ready uploader.json file at release time and not intended to be modified further.
