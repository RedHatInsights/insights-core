import doctest
import pytest

from insights.parsers import rpm_pkgs
from insights.parsers.rpm_pkgs import RpmPkgsWritable
from insights.tests import context_wrap


DATASOURCE_OUTPUT = ["httpd-core|httpd-core-2.4.53-7.el9.x86_64|Red Hat, Inc."]

RPM_PKGS_WRITABLE_OUTPUT = [("httpd-core", "httpd-core-2.4.53-7.el9.x86_64", "Red Hat, Inc.")]


@pytest.mark.parametrize("parser, output", [
    (RpmPkgsWritable, RPM_PKGS_WRITABLE_OUTPUT)
])
def test_rpm_pkgs(parser, output):
    test = parser(context_wrap(DATASOURCE_OUTPUT))
    assert test.packages == output


def test_doc_examples():
    env = {
        "rpm_pkgs_writable": RpmPkgsWritable(context_wrap(DATASOURCE_OUTPUT))
    }
    failed, total = doctest.testmod(rpm_pkgs, globs=env)
    assert failed == 0
