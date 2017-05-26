import sys
import os
import yaml

INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
NAME = "insights.yaml"
DEFAULTS_NAME = "defaults.yaml"

PATHS = [
    os.path.join(INSTALL_DIR, DEFAULTS_NAME),  # Defaults
    os.path.join("/etc", NAME),  # System-wide config
    os.path.join(os.path.expanduser("~/.local"), NAME),  # User-specific config
    "." + NAME  # Directory-specific config
]

config = {}

for path in PATHS:
    if os.path.exists(path):
        try:
            with open(path) as fp:
                y = yaml.load(fp.read())
                for name, section in y.iteritems():
                    if name in config:
                        config[name].update(section)
                    else:
                        config[name] = section
        except:
            pass

# The defaults section is for keys that belong in every section and can be
# overridden in particular sections if desired.  This adds the default values
# to each section if they aren't already there.

for k in config["defaults"]:
    for section in {s for s in config if s != "defaults"}:
        if k not in config[section]:
            config[section][k] = config["defaults"][k]

# Flatten the attribute hierarchy a bit by cutting out "config".
for name, section in config.iteritems():
    setattr(sys.modules[__name__], name, section)
