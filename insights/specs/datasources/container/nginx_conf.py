"""
Datasources to collect the nginx configuration files
"""
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.context import HostContext
from insights.core.spec_factory import container_execute
from insights.specs import Specs
from insights.specs.datasources.container import running_rhel_containers


class LocalSpecs(Specs):
    """ Local specs used only by nginx container datasources """

    container_find_etc_opt_conf = container_execute(running_rhel_containers, "find /etc /opt -name '*.conf'")
    # container_find_opt_conf = container_execute(running_rhel_containers, "find /opt -name '*.conf'")


@datasource(LocalSpecs.container_find_etc_opt_conf, HostContext)
def nginx_conf(broker):
    """
    Returns a list of tuple of (<podman|docker>, container_id, conf_path)
    """
    find_list = broker[LocalSpecs.container_find_etc_opt_conf]
    ret = []
    for conf_list in find_list:
        for conf in conf_list.content:
            # FIXME: filter should be refined
            if 'nginx' in conf:
                ret.append((conf_list.engine, conf_list.container_id, conf))
    if ret:
        return ret

    raise SkipComponent


# @datasource(LocalSpecs.container_find_etc_opt_conf, HostContext)
# def httpd_conf(broker):
#     """
#     """
#     find_list = broker[LocalSpecs.container_find_etc_opt_conf]
#     ret = []
#     for conf_list in find_list:
#         for conf in conf_list.content:
#             if 'yum' in conf:
#                 ret.append((conf_list.engine, conf_list.container_id, conf))
#     if ret:
#         return ret

#     raise SkipComponent
