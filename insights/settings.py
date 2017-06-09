import sys
import os
import yaml
import pkgutil

INSTALL_DIR = os.path.dirname(os.path.abspath(__file__))
NAME = "insights.yaml"
DEFAULTS_NAME = "defaults.yaml"

PATHS = [
    ("resource", DEFAULTS_NAME),  # Defaults
    ("path", os.path.join("/etc", NAME)),  # System-wide config
    ("path", os.path.join(os.path.expanduser("~/.local"), NAME)),  # User-specific config
    ("path", "." + NAME),  # Directory-specific config
]

config = {}

for type, path in PATHS:

    try:
        if type == "path":
            with open(path) as fp:
                content = fp.read()
        elif type == "resource":
            # content = pkg_resources.resource_string(__name__, path)
            content = pkgutil.get_data(__name__, path)
        else:
            raise ValueError("unknown type = %s" % type)

        y = yaml.load(content)
        for name, section in y.iteritems():
            if name in config:
                config[name].update(section)
            else:
                config[name] = section
    except ValueError:
        raise
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
