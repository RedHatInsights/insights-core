from insights.parsers.nscd_conf import NscdConf, NscdConfLine
from insights.tests import context_wrap

NSCD_CONF = """
#
# /etc/nscd.conf
#
# An example Name Service Cache config file.  This file is needed by nscd.
#
# Legal entries are:
#
#       logfile                 <file>
#       debug-level             <level>
#       threads                 <initial #threads to use>
#       max-threads             <maximum #threads to use>
#       server-user             <user to run server as instead of root>
#               server-user is ignored if nscd is started with -S parameters
#       stat-user               <user who is allowed to request statistics>
#       reload-count            unlimited|<number>
#       paranoia                <yes|no>
#       restart-interval        <time in seconds>
#
#       enable-cache            <service> <yes|no>
#       positive-time-to-live   <service> <time in seconds>
#       negative-time-to-live   <service> <time in seconds>
#       suggested-size          <service> <prime number>
#       check-files             <service> <yes|no>
#       persistent              <service> <yes|no>
#       shared                  <service> <yes|no>
#       max-db-size             <service> <number bytes>
#       auto-propagate          <service> <yes|no>
#
# Currently supported cache names (services): passwd, group, hosts, services
#


#       logfile                 /var/log/nscd.log
#       threads                 4
#       max-threads             32
        server-user             nscd
#       stat-user               somebody
        debug-level             0
#       reload-count            5
        paranoia                no
#       restart-interval        3600

        enable-cache            passwd          no
        positive-time-to-live   passwd          600
        negative-time-to-live   passwd          20
        suggested-size          passwd          211
        check-files             passwd          yes
        persistent              passwd          yes
        shared                  passwd          yes
        max-db-size             passwd          33554432
        auto-propagate          passwd          yes

        enable-cache            group           no
        positive-time-to-live   group           3600
        negative-time-to-live   group           60
        suggested-size          group           211
        check-files             group           yes
        persistent              group           yes
        shared                  group           yes
        max-db-size             group           33554432
        auto-propagate          group           yes

        enable-cache            hosts           yes
        positive-time-to-live   hosts           3600
        negative-time-to-live   hosts           20
        suggested-size          hosts           211
        check-files             hosts           yes
        persistent              hosts           yes
        shared                  hosts           yes
        max-db-size             hosts           33554432

        enable-cache            services        yes
        positive-time-to-live   services        28800
        negative-time-to-live   services        20
        suggested-size          services        211
        check-files             services        yes
        persistent              services        yes
        shared                  services        yes
        max-db-size             services        33554432

        enable-cache            netgroup        no
        positive-time-to-live   netgroup        28800
        negative-time-to-live   netgroup        20
        suggested-size          netgroup        211
        check-files             netgroup        yes
        persistent              netgroup        yes
        shared                  netgroup        yes
        max-db-size             netgroup        33554432

"""


def test_nscd_conf():
    conf = NscdConf(context_wrap(NSCD_CONF))
    assert conf is not None
    lines = [l for l in conf]
    assert len(lines) == 45
    assert len(conf.data) == 45
    assert lines[0] == conf.data[0]

    # Service Attributes tests
    assert conf.service_attributes("bad-name") == []
    assert conf.service_attributes("hosts") == [
        NscdConfLine("enable-cache", "hosts", "yes"),
        NscdConfLine("positive-time-to-live", "hosts", "3600"),
        NscdConfLine("negative-time-to-live", "hosts", "20"),
        NscdConfLine("suggested-size", "hosts", "211"),
        NscdConfLine("check-files", "hosts", "yes"),
        NscdConfLine("persistent", "hosts", "yes"),
        NscdConfLine("shared", "hosts", "yes"),
        NscdConfLine("max-db-size", "hosts", "33554432")
    ]

    # Attribute tests
    assert conf.attribute("server-user") == "nscd"
    assert conf.attribute("restart-interval") is None

    # Filter tests
    assert conf.filter("server-user") == [
        NscdConfLine(attribute="server-user", service=None, value="nscd")
    ]
    assert conf.filter("log-file") == []
    assert conf.filter("enable-cache", "netgroup") == [
        NscdConfLine(attribute="enable-cache", service="netgroup", value="no")
    ]
    assert conf.filter("enable-cache") == [
        NscdConfLine(attribute="enable-cache", service="passwd", value="no"),
        NscdConfLine(attribute="enable-cache", service="group", value="no"),
        NscdConfLine(attribute="enable-cache", service="hosts", value="yes"),
        NscdConfLine(attribute="enable-cache", service="services", value="yes"),
        NscdConfLine(attribute="enable-cache", service="netgroup", value="no")
    ]
    assert conf.filter("cache") == [
        NscdConfLine(attribute="enable-cache", service="passwd", value="no"),
        NscdConfLine(attribute="enable-cache", service="group", value="no"),
        NscdConfLine(attribute="enable-cache", service="hosts", value="yes"),
        NscdConfLine(attribute="enable-cache", service="services", value="yes"),
        NscdConfLine(attribute="enable-cache", service="netgroup", value="no")
    ]
