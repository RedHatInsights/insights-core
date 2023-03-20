"""
Datasources to collect the nginx configuration files from containers
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import container_execute
from insights.specs import Specs
from insights.specs.datasources.container import running_rhel_containers


class LocalSpecs(Specs):
    """ Local specs used only by nginx container datasources """
    container_find_etc_opt_conf = container_execute(running_rhel_containers, "find /etc /opt -name '*.conf'")


@datasource(LocalSpecs.container_find_etc_opt_conf, HostContext)
def nginx_conf(broker):
    """
    Returns a list of tuple of (<podman|docker>, container_id, conf_path, image)
    """
    find_list = broker[LocalSpecs.container_find_etc_opt_conf]
    ret = []
    for conf_list in find_list:
        for conf_path in conf_list.content:
            # FIXME: refine the path filter
            if 'etc/nginx' in conf_path or 'rh-nginx' in conf_path:
                ret.append((conf_list.image, conf_list.engine, conf_list.container_id, conf_path))
    if ret:
        # Return list of tuple:
        # - (image, <podman|docker>, container_id, conf_path)
        return ret

    raise SkipComponent
