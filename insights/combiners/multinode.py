from insights import combiner
from insights.combiners.hostname import Hostname
from insights.core.context import create_product
from insights.parsers.metadata import MetadataJson
from insights.specs import Specs


@combiner(MetadataJson, [Hostname, Specs.machine_id])
def multinode_product(md, hn, machine_id):
    hn = hn.fqdn if hn else machine_id.content[0].rstrip()
    return create_product(md.data, hn)


@combiner(multinode_product)
def docker(product):
    if product and product.name == "docker":
        return product


@combiner(multinode_product)
def OSP(product):
    if product and product.name == "osp":
        return product


@combiner(multinode_product)
def RHEV(product):
    if product and product.name == "rhev":
        return product


@combiner(multinode_product)
def RHEL(product):
    if product and product.name == "rhel":
        return product
