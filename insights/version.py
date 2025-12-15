import pkgutil

_VERSION_ = pkgutil.get_data(__name__, "VERSION").strip().decode("utf-8")

if __name__ == "__main__":
    print(_VERSION_)
