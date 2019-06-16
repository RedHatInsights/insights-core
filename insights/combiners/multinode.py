#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights import combiner
from insights.combiners.hostname import hostname
from insights.core.context import create_product
from insights.parsers.metadata import MetadataJson
from insights.specs import Specs


@combiner(MetadataJson, [hostname, Specs.machine_id])
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
