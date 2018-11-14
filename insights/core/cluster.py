#!/usr/bin/env python
import itertools
import pandas as pd
from collections import defaultdict

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

from insights.core import dr, plugins
from insights.core.archives import extract
from insights.core.hydration import create_context
from insights.specs import Specs


ID_GENERATOR = itertools.count()


class ClusterMeta(dict):
    def __init__(self, num_members, kwargs):
        self.num_members = num_members
        self.update(**kwargs)


@plugins.combiner(optional=[Specs.machine_id, Specs.hostname])
def machine_id(mid, hn):
    ds = mid or hn
    if ds:
        return ds.content[0].strip()
    return str(next(ID_GENERATOR))


def parse_inventory(path):
    inventory = InventoryManager(loader=DataLoader(), sources=path)
    return inventory.get_groups_dict()


def attach_machine_id(result, mid):
    key = "machine_id"
    if isinstance(result, list):
        for r in result:
            r[key] = mid
    else:
        result[key] = mid
    return result


def process_archives(archives):
    for archive in archives:
        with extract(archive) as ex:
            ctx = create_context(ex.tmp_dir)
            broker = dr.Broker()
            broker[ctx.__class__] = ctx
            yield dr.run(broker=broker)


def extract_facts(brokers):
    results = defaultdict(list)
    for b in brokers:
        mid = b[machine_id]
        for k, v in b.get_by_type(plugins.fact).items():
            r = attach_machine_id(v, mid)
            if isinstance(r, list):
                results[k].extend(r)
            else:
                results[k].append(r)
    return results


def process_facts(facts, meta, broker):
    broker[ClusterMeta] = meta
    for k, v in facts.items():
        broker[k] = pd.DataFrame(v)
    return dr.run(dr.COMPONENTS[dr.GROUPS.cluster], broker=broker)


def process_cluster(archives, broker, inventory=None):
    inventory = parse_inventory(inventory) if inventory else {}

    brokers = process_archives(archives)
    facts = extract_facts(brokers)
    meta = ClusterMeta(len(archives), inventory)

    return process_facts(facts, meta, broker)
