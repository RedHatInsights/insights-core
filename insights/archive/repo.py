from __future__ import print_function
import hashlib
import os
import sys
from .tool import TestArchive, Transform, MultiArchive
from insights.tests import InputData
from insights.core import load_package

ARCHIVES = [
    TestArchive("base_rhel67", base_archive="rhel6.7"),
    TestArchive("insights_heartbeat", transforms=[
        Transform("hostname").replace("insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614")
    ], machine_id=hashlib.sha224("TEST-HEARTBEAT-RHAI2").hexdigest())
]


DEFAULT_DEST = "./integration_tests"
console = False
archive_map = {}
for archive in ARCHIVES:
    archive_map[archive.name] = archive


def build_all(archives, dest="./archives", clean=False):
    if not os.path.exists(dest):
        os.mkdir(dest)
    files = []
    for archive in archives:
        files.append(archive.build(dest, force=clean))
        print("%s: %s" % (archive.name, archive.machine_id))
    return files


def build(archive_name, dest="."):
    return archive_map[archive_name].build(dest)


def get_integration_archive_name(module_name, input_data, i):
    invalid_chars = [" ", "/", "$", "%", "*", "(", ")", ":", "%"]
    if isinstance(input_data, InputData) and input_data.name:
        name = input_data.name.lower()
        for invalid_char in invalid_chars:
            name = name.replace(invalid_char, "_")
    elif isinstance(input_data, list):
        name = "multinode-%d" % i
    else:
        name = str(i)
    return "_".join([module_name, name])


def build_integration_test_archive(module_name, i, test_tuple, dest, machine_id=None):
    module, test_func, input_data, expected_response = test_tuple
    test_name = get_integration_archive_name(module.__name__, input_data, i)
    try:
        if isinstance(input_data, list):
            archive = MultiArchive(test_name, machine_id=machine_id)
        else:
            archive = TestArchive(test_name, machine_id=machine_id)
        archive.apply_input_data(input_data)
        archive_path = archive.build(dest)
    except Exception:
        print("X", end="")
    else:
        if console:
            print("m" if isinstance(input_data, list) else ".", end="")
            sys.stdout.flush()
        return {
            "module": module_name,
            "test_func": test_func,
            "input_data": input_data,
            "expected_response": expected_response,
            "archive_path": archive_path,
            "test_archive": archive
        }


def build_integration_test_archives(package, dest=DEFAULT_DEST, machine_id=None):
    if not os.path.exists(dest):
        os.mkdir(dest)
    for func in get_integration_generators(package):
        module_name = func.__module__
        if console:
            print("\nBuilding {0} ".format(module_name), end="")
        for i, test_tuple in enumerate(func()):
            archive = build_integration_test_archive(module_name, i, test_tuple, dest, machine_id)
            if archive:
                yield archive
    if console:
        print()


def get_integration_generators(package):
    load_package(package)
    from insights.tests import ARCHIVE_GENERATORS
    for func in sorted(ARCHIVE_GENERATORS, key=lambda f: f.__module__):
        if not func.slow:
            yield func
