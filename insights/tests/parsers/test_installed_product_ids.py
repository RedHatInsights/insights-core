import doctest
from insights.parsers.installed_product_ids import InstalledProductIDs
from insights.parsers import installed_product_ids
from insights.tests import context_wrap


COMMAND_OUTPUT = """
Product Certificate
path: /etc/pki/product-default/69.pem
id: 69
Product Certificate
path: /etc/pki/product/69.pem
id: 69
"""

COMMAND_OUTPUT2 = """
    Product Certificate
    path: /etc/pki/product-default/69.pem
    id: 69
    brand_type:
    brand_name:
    tags: rhel-7,rhel-7-server
    Product Certificate
    path: /etc/pki/product/479.pem
    id: 479
    tags: rhel-8,rhel-8-x86_64
    brand_type:
    brand_name:
"""

COMMAND_SOME_CERT_PART_DATA_OUTPUT3 = """
Product Certificate
path: /etc/pki/product-default/69.pem
id: 69
brand_type:
brand_name:
tags: rhel-7,rhel-7-server
Product Certificate
path: /etc/pki/product/479.pem
id: 479
tags: rhel-8,rhel-8-x86_64
brand_type:
brand_name:
Product Certificate
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
    assert results.product_certs[0]['path'] == '/etc/pki/product-default/69.pem'
    assert results.product_certs[0]['id'] == '69'
    assert results.product_certs[1]['path'] == '/etc/pki/product/69.pem'
    assert results.product_certs[1]['id'] == '69'

    results = InstalledProductIDs(context_wrap(COMMAND_OUTPUT2, strip=False))
    assert results.product_certs[0]['path'] == '/etc/pki/product-default/69.pem'
    assert results.product_certs[0]['id'] == '69'
    assert results.product_certs[0]['brand_type'] == ''
    assert results.product_certs[0]['brand_name'] == ''
    assert results.product_certs[0]['tags'] == 'rhel-7,rhel-7-server'
    assert results.product_certs[1]['path'] == '/etc/pki/product/479.pem'
    assert results.product_certs[1]['id'] == '479'
    assert results.product_certs[1]['brand_type'] == ''
    assert results.product_certs[1]['brand_name'] == ''
    assert results.product_certs[1]['tags'] == 'rhel-8,rhel-8-x86_64'
    assert len(results.product_certs) == 2
    assert results.ids == set(['69', '479'])

    results = InstalledProductIDs(context_wrap(COMMAND_SOME_CERT_PART_DATA_OUTPUT3))
    assert len(results.product_certs) == 2

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
    failed, _ = doctest.testmod(installed_product_ids, globs=env)
    assert failed == 0
