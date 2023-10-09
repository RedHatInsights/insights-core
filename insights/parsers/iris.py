"""
Iris - InterSystems
===================
Parsers included in this module are:

IrisList - Command ``/usr/bin/iris list``
=========================================

IrisCpf - Files ``iris.cpf``
============================

IrisMessages - Files ``messages.log``
=====================================
"""

from insights.core import CommandParser, IniConfigFile, LogFileOutput
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.iris_list)
class IrisList(CommandParser, list):
    """
    Parse the output of the ``/usr/bin/iris list`` command.

    Attributes:
        default (dict): the default instance

    Sample Input::

        Configuration 'IRIS'   (default)
            directory:    /intersystems
            versionid:    2023.1.0.235.1com
            datadir:      /intersystems
            conf file:    iris.cpf  (SuperServer port = 1972, WebServer = 52773)
            status:       running, since Tue Jun 27 01:55:25 2023
            state:        ok
            product:      InterSystems IRIS

    Examples:
        >>> iris_info[0]['status']
        'running, since Tue Jun 27 01:55:25 2023'
        >>> iris_info.is_running
        True
        >>> iris_info.default['status']
        'running, since Tue Jun 27 01:55:25 2023'
    """

    def parse_content(self, content):
        self.default = {}
        item_instance = {}

        for line in content:
            if not line.strip():
                continue
            if line.strip().startswith('Configuration'):
                instance_name = line.split()[1].strip('\'"')
                item_instance = {"instance_name": instance_name}
                if "(default)" in line:
                    self.default = item_instance
                self.append(item_instance)
            elif ":" in line and item_instance:
                key, value = line.split(":", 1)
                item_instance[key.strip()] = value.strip()

        if len(self) == 0:
            raise SkipComponent("The result is empty")

    @property
    def is_running(self):
        """Return True when the iris instance is running, and False when it is down"""
        return any(item.get('status', "").startswith('running') for item in self)


@parser(Specs.iris_cpf)
class IrisCpf(IniConfigFile):
    """
    Parse the content of "iris.cpf" file.

    Sample Input::

        [ConfigFile]
        Product=IRIS
        Version=2023.1

        [Databases]
        IRISSYS=/intersystems/mgr/
        IRISLIB=/intersystems/mgr/irislib/
        IRISTEMP=/intersystems/mgr/iristemp/
        IRISLOCALDATA=/intersystems/mgr/irislocaldata/
        IRISAUDIT=/intersystems/mgr/irisaudit/
        ENSLIB=/intersystems/mgr/enslib/
        USER=/intersystems/mgr/user/

        [Namespaces]
        %SYS=IRISSYS
        USER=USER

    Examples:
        >>> "Namespaces" in iris_cpf
        True
        >>> iris_cpf.has_option('Databases', 'IRISSYS')
        True
        >>> iris_cpf.get("Databases", "IRISSYS")
        '/intersystems/mgr/'
    """
    pass


@parser(Specs.iris_messages_log)
class IrisMessages(LogFileOutput):
    """
    Parse the content of "messages.log" file.

    Sample Input::

        06/26/23-08:02:17:828 (144145) 0 [Generic.Event] Allocated 495MB shared memory
        06/26/23-08:02:17:828 (144145) 0 [Generic.Event] 32MB global buffers, 80MB routine buffers, 64MB journal buffers, 4MB buffer descriptors, 300MB heap, 5MB ECP, 9MB miscellaneous
        06/26/23-08:02:17:831 (144145) 0 [Crypto.IntelSandyBridgeAESNI] Intel Sandy Bridge AES-NI instructions detected.
        06/26/23-08:02:17:831 (144145) 0 [SIMD] SIMD optimization level: DEFAULT X86
        06/26/23-08:02:17:903 (144145) 0 [WriteDaemon.UsingWIJFile] Using WIJ file: /intersystems/mgr/IRIS.WIJ
        06/26/23-08:02:17:903 (144145) 0 [Generic.Event] No journaling info from prior system
        06/26/23-08:02:18:110 (144145) 0 [Generic.Event]
        Startup of InterSystems IRIS [IRIS for UNIX (Red Hat Enterprise Linux 8 for x86-64) 2023.1 (Build 235.1) Fri Jun 2 2023 13:26:47 EDT]
                in ../bin/
                with mgr: /intersystems/mgr
                with wij: /intersystems/mgr/IRIS.WIJ
                from: /intersystems/mgr/
        OS=[Linux], version=[#1 SMP Fri Sep 30 11:45:06 EDT 2022], release=[4.18.0-425.3.1.el8.x86_64], machine=[x86_64]
        nodename=[rhel8].
        numasyncwijbuf: 2, wdwrite_asyncio_max: 64, wijdirectio: on, synctype: 3
        System Initialized.
        06/26/23-08:02:18:136 (144182) 0 [WriteDaemon.Started] Write daemon started.
                [Namespaces]
                %SYS=IRISSYS
                USER=USER

    Examples:
        >>> len(list(iris_log.get('Generic.Event')))
        4
    """
    time_format = '%m/%d/%y-%H:%M:%S:%f'
