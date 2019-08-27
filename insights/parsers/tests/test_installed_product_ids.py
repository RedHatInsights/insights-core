import doctest
from ...parsers.installed_product_ids import InstalledProductIDs
from ...parsers import installed_product_ids
from ...tests import context_wrap


COMMAND_OUTPUT = """
+-------------------------------------------+
Product Certificate
+-------------------------------------------+

Certificate:
    Path: /etc/pki/product-default/69.pem
    Version: 1.0
    Serial: 12750047592154749739
    Start Date: 2017-06-28 18:05:10+00:00
    End Date: 2037-06-23 18:05:10+00:00

Subject:
    CN: Red Hat Product ID [4f9995e0-8dc4-4b4f-acfe-4ef1264b94f3]

Issuer:
    C: US
    CN: Red Hat Entitlement Product Authority
    O: Red Hat, Inc.
    OU: Red Hat Network
    ST: North Carolina
    emailAddress: ca-support@redhat.com

Product:
    ID: 69
    Name: Red Hat Enterprise Linux Server
    Version: 7.4
    Arch: x86_64
    Tags: rhel-7,rhel-7-server
    Brand Type:
    Brand Name:


+-------------------------------------------+
    Product Certificate
+-------------------------------------------+

Certificate:
    Path: /etc/pki/product/69.pem
    Version: 1.0
    Serial: 12750047592154751271
    Start Date: 2018-04-13 11:23:50+00:00
    End Date: 2038-04-08 11:23:50+00:00

Subject:
    CN: Red Hat Product ID [f3c92a95-26be-4bdf-800f-02c044503896]

Issuer:
    C: US
    CN: Red Hat Entitlement Product Authority
    O: Red Hat, Inc.
    OU: Red Hat Network
    ST: North Carolina
    emailAddress: ca-support@redhat.com

Product:
    ID: 69
    Name: Red Hat Enterprise Linux Server
    Version: 7.6
    Arch: x86_64
    Tags: rhel-7,rhel-7-server
    Brand Type:
    Brand Name:
"""

NONE_FOUND = """
find: '/etc/pki/product-default/': No such file or directory
find: '/etc/pki/product/': No such file or directory
"""

BAD_FILE = """
Unable to read certificate file '/etc/pki/product/some_file.pem': Error loading certificate
"""


def test_installed_product_ids():
    results = InstalledProductIDs(context_wrap(COMMAND_OUTPUT))
    assert results is not None
    assert results.ids == set(['69', '69'])

    results = InstalledProductIDs(context_wrap(NONE_FOUND))
    assert results is not None
    assert results.ids == set([])

    results = InstalledProductIDs(context_wrap(BAD_FILE))
    assert results is not None
    assert results.ids == set([])


def test_installed_product_ids_docs():
    env = {
        'products': InstalledProductIDs(context_wrap(COMMAND_OUTPUT)),
    }
    failed, total = doctest.testmod(installed_product_ids, globs=env)
    assert failed == 0
