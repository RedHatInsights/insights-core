from .. import Parser, parser


@parser("puppet_ssl_cert_ca_pem")
class PuppetSSLCertCA(Parser):
    """Class for checking does ``/var/lib/puppet/ssl/certs/ca.pem`` exist.

    Attributes:
        None
    """
    pass
