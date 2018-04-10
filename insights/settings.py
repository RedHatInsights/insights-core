import sys
import os
import yaml
import pkgutil

INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
NAME = "insights.yaml"
DEFAULTS_NAME = "defaults.yaml"


def load_and_read(path):
    if os.path.exists(path):
        with open(path) as fp:
            return fp.read()


CONFIGS = [
    pkgutil.get_data('insights', 'defaults.yaml'),
    load_and_read(os.path.join("/etc", NAME)),  # System-wide config
    load_and_read(os.path.join(os.path.expanduser("~/.local"), NAME)),  # User-specific config
    load_and_read("." + NAME)  # Directory-specific config
]

config = {}

for c in CONFIGS:
    if c is None:
        continue
    try:
        y = yaml.safe_load(c)
        for name, section in y.items():
            if name in config:
                config[name].update(section)
            else:
                config[name] = section
    except Exception as e:
        print(c)
        print(e)

# The defaults section is for keys that belong in every section and can be
# overridden in particular sections if desired.  This adds the default values
# to each section if they aren't already there.

for k in config["defaults"]:
    for section in set(s for s in config if s != "defaults"):
        if k not in config[section]:
            config[section][k] = config["defaults"][k]

# Flatten the attribute hierarchy a bit by cutting out "config".
for name, section in config.items():
    setattr(sys.modules[__name__], name, section)
