import doctest
from insights.parsers.installed_product_ids import InstalledProductIDs
from insights.parsers import installed_product_ids
from insights.tests import context_wrap


COMMAND_OUTPUT = """
Product Certificate
Path: /etc/pki/product-default/69.pem
ID: 69
Product Certificate
Path: /etc/pki/product/69.pem
ID: 69
"""

COMMAND_OUTPUT2 = """
Product Certificate
Path: /etc/pki/product-default/69.pem
ID: 69
Brand Type:
Brand Name:
Tags: rhel-7,rhel-7-server
Product Certificate
Path: /etc/pki/product/479.pem
ID: 479
Tags: rhel-8,rhel-8-x86_64
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
    assert results.data[0]['Path'] == '/etc/pki/product-default/69.pem'
    assert results.data[0]['ID'] == '69'
    assert results.data[1]['Path'] == '/etc/pki/product/69.pem'
    assert results.data[1]['ID'] == '69'

    results = InstalledProductIDs(context_wrap(COMMAND_OUTPUT2))
    assert results.data[0]['Path'] == '/etc/pki/product-default/69.pem'
    assert results.data[0]['ID'] == '69'
    assert results.data[0]['Brand Type'] == ''
    assert results.data[0]['Brand Name'] == ''
    assert results.data[0]['Tags'] == 'rhel-7,rhel-7-server'
    assert results.data[1]['Path'] == '/etc/pki/product/479.pem'
    assert results.data[1]['ID'] == '479'
    assert results.data[1]['Brand Type'] == ''
    assert results.data[1]['Brand Name'] == ''
    assert results.data[1]['Tags'] == 'rhel-8,rhel-8-x86_64'
    assert len(results.data) == 2
    assert results.ids == set(['69', '479'])

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
