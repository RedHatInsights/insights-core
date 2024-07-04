"""
Get CIFS Info
=============

This module contains the following parsers:

CIFSDebugData - file ``/proc/fs/cifs/DebugData``
------------------------------------------------
"""

from insights.core import LogFileOutput
from insights.specs import Specs
from insights.core.plugins import parser


@parser(Specs.cifs_debug_data)
class CIFSDebugData(LogFileOutput):
    r"""
    Parse the ``/proc/fs/cifs/DebugData`` file.
    Filter is added to the spec.

    Sample input of full file::

        Display Internal CIFS Data Structures for Debugging
        ---------------------------------------------------
        CIFS Version 2.41
        Features: DFS,SMB_DIRECT,STATS,DEBUG,ALLOW_INSECURE_LEGACY,CIFS_POSIX,UPCALL(SPNEGO),XATTR,ACL
        CIFSMaxBufSize: 16384
        Active VFS Requests: 0

        Servers:
        1) ConnectionId: 0x4 Hostname: CVXDFAVB1
        Number of credits: 512 Dialect 0x302 signed
        TCP status: 1 Instance: 22
        Local Users To Server: 1 SecMode: 0x3 Req On Wire: 0
        In Send: 0 In MaxReq Wait: 0
        DFS origin full path: \\ad.abc.com\DFSROOT\name1
        DFS leaf full path:   \\CVXDFAVB1\DFSRoot\name1

            Sessions:
            1) Address: 10.0.96.196 Uses: 1 Capability: 0x300067    Session Status: 1
            Security type: RawNTLMSSP  SessionId: 0x2d86cec00089d
            User: 1339601402 Cred User: 0

            Shares:
            0) IPC: \\CVXDFAVB1\IPC$ Mounts: 1 DevInfo: 0x0 Attributes: 0x0
            PathComponentMax: 0 Status: 1 type: 0 Serial Number: 0x0
            Share Capabilities: None    Share Flags: 0x30
            tid: 0x5    Maximal Access: 0x11f01ff

            1) \\CVXDFAVB1\name1 Mounts: 1 DevInfo: 0x60120 Attributes: 0xc500ff
            PathComponentMax: 255 Status: 1 type: DISK Serial Number: 0x16f0426b
            Share Capabilities: None Aligned, Partition Aligned,    Share Flags: 0x0
            tid: 0x1    Optimal sector size: 0x200  Maximal Access: 0x1f01ff


            Server interfaces: 2
            1)  Speed: 10000000000 bps
                Capabilities: rss
                IPv4: 10.9.212.196

            2)  Speed: 10000000000 bps
                Capabilities: rss
                IPv4: 10.0.96.96


            MIDs:
        --

    Examples:
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.cifs_debug_data, 'abc_def_fsf')
        >>> type(cifs_dd_obj)
        <class 'insights.parsers.cifs.CIFSDebugData'>
        >>> cifs_dd_obj.last_scan("abc_def_line", "abc_def_fsf")
    """

    time_format = None
