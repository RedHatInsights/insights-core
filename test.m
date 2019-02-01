# Insights Core Run (01/31/19 11:55:36)

## Command Line
`/home/bfahr/.virtualenvs/insights-insights-core/bin/insights-run -t -f _markdown -p telemetry.rules.plugins ../insights-devbox-20180625112444.tar.gz`


## Tracebacks
```
Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/smart_proxy_dynflow_core/settings.yml does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/ssh/ssh_config does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/usr/share/foreman/.ssh/ssh_config does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/swift/etc/swift/object-expirer.conf, /etc/swift/object-expirer.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/swift/etc/swift/proxy-server.conf, /etc/swift/proxy-server.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/auditctl_-s does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/libvirt-guests does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ceph_df_detail_-f_json-pretty does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/ntpd does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/prelink does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/virt-who does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/gnocchi/etc/gnocchi/gnocchi.conf, /etc/gnocchi/gnocchi.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/gnocchi/gnocchi-metricd.log, /var/log/gnocchi/metricd.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/boot/grub/grub.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/boot/efi/EFI/redhat/grub.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/boot/efi/EFI/redhat/grub.cfg does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/etc/rhn/rhn.conf, /conf/rhn/rhn/rhn.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/sysconfig/rhn/rhn-entitlement-cert.xml*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/conf/rhn/sysconfig/rhn/rhn-entitlement-cert.xml*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/usr/share/rhn/config-defaults/rhn_hibernate.conf, /config-defaults/rhn_hibernate.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg, /etc/haproxy/haproxy.cfg] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/odbc.ini does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/odbcinst.ini does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/heat/etc/heat/heat.conf, /etc/heat/heat.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/rhn/search/rhn_search_daemon.log, /rhn-logs/rhn/search/rhn_search_daemon.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/rhn/rhn_taskomatic_daemon.log, rhn-logs/rhn/rhn_taskomatic_daemon.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/rhsm/rhsm.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/root/.config/openshift/hosts does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/samba/smb.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/httpd/conf/httpd.conf, /etc/httpd/conf.d/*.conf] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/origin/master/master-config.yaml does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/origin/node/node-config.yaml does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/httpd/error_log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ovirt-engine/server.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ovirt-engine/ui.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/rhsm/facts/virt_uuid.facts does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/usr/share/foreman/lib/satellite/version.rb does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/pacemaker.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/sys/class/scsi_host/host[0-9]*/eh_deadline] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/sysconfig/network-scripts/route-*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/sys/class/scsi_host/host[0-9]*/fwrev] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/usr.sap.hostctrl.exe.saphostexec_-status does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/usr.sap.hostctrl.exe.saphostexec_-version does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/sys/fs/cgroup/cpuset/cpuset.cpus does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ss_-tupna does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/subscription-manager_release_--show does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lsinitrd_.boot.initramfs-_kdump.img_-f_.etc.sysctl.conf_.etc.sysctl.d._.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [var/log/dirsrv/*/errors] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/var/opt/amq-broker/*/etc/broker.xml] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/systemctl_show_smart_proxy_dynflow_core does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/systool_-b_scsi_-v does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/docker-storage-setup does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/vgdisplay does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/docker does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/vgs_--nameprefixes_--noheadings_--separator_-a_-o_vg_all_--config_global_locking_type_0_devices_filter_a does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/virsh_--readonly_list_--all does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/md5sum_.dev.null_.etc.pki._product_product-default_.69.pem does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_pvc_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_rc_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_role_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_rolebinding_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/find_.sys.devices.virtual.net._-name_multicast_querier_-print_-exec_cat does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_route_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_service_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lsinitrd_-f_.etc.multipath.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_configmap_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/passenger-status does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/pcs_status does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/nmcli_conn_show does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/nmcli_dev_show does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/pvs_-a_-v_-o_pv_mda_free_pv_mda_size_pv_mda_count_pv_mda_used_count_pe_count_--config_global_locking_type_0 does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/id_-u_nova does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/id_-u_nova_migration does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/pvs_--nameprefixes_--noheadings_--separator_-a_-o_pv_all_vg_name_--config_global_locking_type_0_devices_filter_a does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/qpid-stat_-g_--ssl-certificate_.etc.pki.katello.qpid_client_striped.crt_-b_amqps_..localhost_5671 does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/qpid-stat_-q_--ssl-certificate_.etc.pki.katello.qpid_client_striped.crt_-b_amqps_..localhost_5671 does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_bc_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_build_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_clusterrole_--config_.etc.origin.master.admin.kubeconfig does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_clusterrolebinding_--config_.etc.origin.master.admin.kubeconfig does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_dc_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_egressnetworkpolicy_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_nodes_-o_yaml does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_pod_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_project_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/usr.sap.hostctrl.exe.saphostctrl_-function_GetCIMObject_-enuminstances_SAPInstance does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/oc_get_pv_-o_yaml_--all-namespaces does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/grubby_--default-index does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/grubby_--default-kernel does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/gluster_volume_info does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/hammer_ping does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/mariadb/mariadb.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-l_.var.lib.cni.networks.openshift-sdn does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/usr/lib/systemd/system/docker.service does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-la_.var.lib.mongodb does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/systemd/logind.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/hostname_-f does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-laR_.var.lib.nova.instances does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/usr/lib/systemd/system/atomic-openshift-node.service does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-laRZ_.var.lib.nova.instances does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/rhn/systemid does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/conf/rhn/sysconfig/rhn/systemid does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/hponcfg_-g does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [etc/sysconfig/mongod, etc/opt/rh/rh-mongodb26/sysconfig/mongod] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-ln_.var.spool.clientmqueue does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/mongod.conf, /etc/mongodb.conf, /etc/opt/rh/rh-mongodb26/mongod.conf] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-ln_.var.tmp does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-lnL_.var.run does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-ln_.var.spool.postfix.maildrop does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/multipath.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/var/log/mysql.log, /var/opt/rh/rh-mysql*/log/mysql/mysqld.log] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ls_-lanR_.lib.firmware does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ipcs_-m does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/ipcs_-m_-p does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lsof does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lspci_-k does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lvs_--nameprefixes_--noheadings_--separator_-a_-o_lv_name_lv_size_lv_attr_mirror_log_vg_name_devices_region_size_data_percent_metadata_percent_segtype_seg_monitor_--config_global_locking_type_0 does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/tuned.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/crontab_-l_-u_keystone does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/lvs_--nameprefixes_--noheadings_--separator_-a_-o_lv_name_lv_size_lv_attr_mirror_log_vg_name_devices_region_size_data_percent_metadata_percent_segtype_--config_global_locking_type_0_devices_filter_a does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/ceph/etc/ceph/ceph.conf, /etc/ceph/ceph.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ceph/ceph.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/proc/1/cgroup does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/audit/audit.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [var/log/ceph/ceph-osd*.log] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ipaupgrade.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/sys/fs/selinux/avc/hash_stats does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/sys/fs/selinux/avc/cache_threshold does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/chrony.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/proc/net/bonding/bond*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/sys/class/net/bond[0-9]*/bonding/tlb_dynamic_lb] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/lib/pacemaker/cib/cib.xml does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf, /etc/cinder/cinder.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/cinder/volume.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/cluster/cluster.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/splice/checkin.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/etc/cobbler/settings, /conf/cobbler/settings] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/etc/cobbler/modules.conf, /conf/cobbler/modules.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/corosync does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/corosync/corosync.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/proc/driver/cciss/cciss*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ceilometer/collector.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/ceilometer/compute.log, /var/log/ceilometer/compute.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/ceilometer/etc/ceilometer/ceilometer.conf, /etc/ceilometer/ceilometer.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/insights_commands/foreman-rake_db_migrate_status does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod[a-f0-9_]*.slice/cpu.cfs_quota_us] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf, /etc/neutron/neutron.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/ovirt-engine/engine.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini, /etc/neutron/l3_agent.ini] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/neutron/l3-agent.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/neutron/etc/neutron/metadata_agent.ini, /etc/neutron/metadata_agent.ini] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/neutron/metadata-agent.log, /var/log/neutron/metadata-agent.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/neutron/openvswitch-agent.log, /var/log/neutron/openvswitch-agent.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugin.ini, /etc/neutron/plugin.ini] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/proc/net/netfilter/nfnetlink_queue does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/exports does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/exports.d/*.exports] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/nginx/nginx.conf, /opt/rh/nginx*/root/etc/nginx/nginx.conf, /etc/opt/rh/rh-nginx*/nginx/nginx.conf] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/nova/nova-api.log, /var/log/nova/nova-api.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/log/containers/nova/nova-compute.log, /var/log/nova/nova-compute.log] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf, /etc/nova/nova.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/nscd.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/ntp.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/foreman-tasks does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/config-data/puppet-generated/mysql/etc/my.cnf.d/galera.cnf, /etc/my.cnf.d/galera.cnf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/sys/devices/system/node/node[0-9]*/cpulist] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 620, in __call__
    raise ContentException("None of [%s] found." % ', '.join(self.paths))
insights.core.plugins.ContentException: None of [/var/lib/pgsql/data/postgresql.conf, /opt/rh/postgresql92/root/var/lib/pgsql/data/postgresql.conf, database/postgresql.conf] found.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/var/lib/pgsql/data/pg_log/postgresql-*.log] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/opt/rh/postgresql92/root/var/lib/pgsql/data/pg_log/postgresql-*.log] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/vdsm/vdsm.log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/database/postgresql-*.log] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/vdsm/logger.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/sysconfig/puppetserver does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [etc/virt-who.conf, etc/virt-who.d/*.conf] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/libvirt/virtlogd.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/proc/stat does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/default/pulp_workers does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/pam.d/vsftpd does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/libvirt/qemu.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/libvirt/qemu/*.xml] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/qpid/qpidd.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 569, in __call__
    raise ContentException("[%s] didn't match." % ', '.join(self.patterns))
insights.core.plugins.ContentException: [/etc/xinetd.conf, /etc/xinetd.d/*] didn't match.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/rabbitmq/rabbitmq-env.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/etc/zipl.conf does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/plugins.py", line 60, in invoke
    return self.component(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 519, in __call__
    return self.kind(ctx.locate_path(self.path), root=ctx.root, ds=self, ctx=ctx)
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 137, in __init__
    self.validate()
  File "/home/bfahr/work/insights/insights-core/insights/core/spec_factory.py", line 144, in validate
    raise ContentException("%s does not exist." % self.path)
insights.core.plugins.ContentException: /tmp/insights-wrcvv4tr/insights-devbox-20180625112444/var/log/rabbitmq/startup_log does not exist.

Traceback (most recent call last):
  File "/home/bfahr/work/insights/insights-core/insights/core/dr.py", line 952, in run
    result = DELEGATES[component].process(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/dr.py", line 673, in process
    return self.invoke(broker)
  File "/home/bfahr/work/insights/insights-core/insights/core/dr.py", line 653, in invoke
    return self.component(*args)
  File "/home/bfahr/work/merges/insights-plugins/telemetry/rules/plugins/storage/lun_via_qlogic_hba_undiscovered.py", line 143, in not_workaround_in_modprobe_qla2xxx
    options = all_mod_probe['options']
  File "/home/bfahr/work/insights/insights-core/insights/core/__init__.py", line 422, in __getitem__
    return self.data[item]
KeyError: 'options'

```

## Rules Executed
### [META] telemetry.rules.plugins.container.docker_container_metadata.report
```
None:
    host_system_id: 'f8413a61-73c1-48e2-bda9-c2e2c5b59619'

```

### [META] telemetry.rules.plugins.container.docker_host_metadata.report
```
None

```

### [META] telemetry.rules.plugins.container.docker_image_metadata.report
```
None:
    host_system_id: 'f8413a61-73c1-48e2-bda9-c2e2c5b59619'

```

### [META] telemetry.rules.plugins.kernel.dmidecode_virtwhat_metadata.report
```
None:
    bios_information  : {'bios_revision': '0.0',
                         'release_date': '04/01/2014',
                         'vendor': 'SeaBIOS',
                         'version': '1.10.2-2.fc27'}
    system_information: {'family': 'Not Specified',
                         'manufacturer': 'QEMU',
                         'product_name': 'Standard PC (i440FX + PIIX, 1996)',
                         'virtual_machine': True}

```

### [FAIL] telemetry.rules.plugins.kernel.tzdata_need_upgrade.report
```
TZDATA_NEED_UPGRADE_NEED_MANUAL_ACTION_INFO

```

### [META] telemetry.rules.plugins.non_kernel.rpm_listing.report
```
Number of packages installed: 445
```

### [FAIL] telemetry.rules.plugins.non_kernel.rsyslog_log_time_jumps.report
```
RSYSLOGD_LOG_TIME_JUMPS:
    configuration: ['$ModLoad imjournal', '$IMJournalStateFile imjournal.state']
    crash        : False
    package      : 'rsyslog-8.24.0-16.el7_5.4'

```

### [META] telemetry.rules.plugins.non_kernel.timezone_metadata.report
```
None:
    timezone_information: {'timezone': 'CDT', 'utcoffset': -18000}

```

### [META] telemetry.rules.plugins.release_metadata.report
```
None:
    rhel_version: '7.5'

```


## Rule Execution Summary
```
 Missing Deps: 314
 Passed      : 0
 Failed      : 2
 Metadata    : 6
 Metadata Key: 1
 Exceptions  : 1
```
