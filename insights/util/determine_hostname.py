import socket


def determine_hostname():
    """
    Find fqdn if we can
    """
    socket_gethostname = socket.gethostname()
    socket_fqdn = socket.getfqdn()

    try:
        socket_ex = socket.gethostbyname_ex(socket_gethostname)[0]
    except (LookupError, socket.gaierror):
        socket_ex = ''

    gethostname_len = len(socket_gethostname)
    fqdn_len = len(socket_fqdn)
    ex_len = len(socket_ex)

    if fqdn_len > gethostname_len or ex_len > gethostname_len:
        if "localhost" not in socket_ex and len(socket_ex):
            return socket_ex
        if "localhost" not in socket_fqdn:
            return socket_fqdn

    return socket_gethostname
