from insights.specs.datasources import is_safe_username


def test_is_safe_username_accepts_normal_names():
    for name in ("root", "alice", "dbp1", "user_1", "svc.account", "app-user", "_svc"):
        assert is_safe_username(name), name


def test_is_safe_username_rejects_unsafe_names():
    unsafe = [
        "",  # empty
        None,  # not a string
        "-rf",  # leading hyphen looks like an option
        "root -c payload",  # space forges extra argv tokens
        "user;rm -rf /",  # shell metacharacters
        "user$(id)",  # command substitution
        "user`id`",  # command substitution
        "user\ttab",  # whitespace
        "user\nname",  # newline
        "user'quote",  # quote
        'user"quote',  # quote
    ]
    for name in unsafe:
        assert not is_safe_username(name), repr(name)
