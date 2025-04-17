import pkgutil

_VERSION_ = pkgutil.get_data(__name__, "VERSION").strip().decode("utf-8")
