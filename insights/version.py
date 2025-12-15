import pkgutil

_VERSION_ = pkgutil.get_data(__name__, "VERSION").strip().decode("utf-8")
_RELEASE_ = pkgutil.get_data(__name__, "RELEASE").strip().decode("utf-8")

if __name__ == "__main__":
    print("{0}-{1}".format(_VERSION_, _RELEASE_))
