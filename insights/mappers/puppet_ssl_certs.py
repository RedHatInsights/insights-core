from .. import Mapper, mapper


@mapper("puppet_ssl_cert_ca_pem")
class PuppetSSLCertCA(Mapper):
    """Class for checking does ``/var/lib/puppet/ssl/certs/ca.pem`` exist.

    Attributes:
        None
    """
    pass
