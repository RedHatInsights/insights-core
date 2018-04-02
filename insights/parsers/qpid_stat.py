from .. import Parser, parser


@parser("qpid_stat_q")
class QpidStatQ(Parser):
    """
    --- Sample ---
COMMAND> qpid-stat -q --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671

Queues
  queue                                                                      dur  autoDel  excl  msg   msgIn  msgOut  bytes  bytesIn  bytesOut  cons  bind
  ==========================================================================================================================================================
  00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                        Y        Y        0     2      2       0    486      486         1     2
  0f7f1a3d-daff-42a6-a994-29050a2eabde:1.0                                        Y        Y        0     8      8       0   4.88k    4.88k        1     2
    -------
    list
    [
        {
            'queue'    : '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0',
            'dur'      : '',
            'autoDel'  : 'Y',
            'excl'     : 'Y',
            'msg'      : '0',
            'msgIn'    : '2',
            'msgOut'   : '2',
            'bytes'    : '0',
            'bytesIn'  : '486',
            'bytesOut' : '486',
            'cons'     : '1',
            'bind'     : '2'
        },
    ]
    """
    def __iter__(self):
        return iter(self.data)

    def parse_content(self, content):
        qpid_list = []
        header_idx = header_row = None
        qpid_keys = ['msg', 'msgIn', 'msgOut', 'bytes', 'bytesIn', 'bytesOut', 'cons', 'bind']
        for i, l in enumerate(content):
            if 'queue' in l:
                header_idx = i
                header_row = l
                break
        sec_list = ["queue", "dur", "autoDel", "excl", "msg"]
        idx_list = [header_row.index(i) for i in sec_list] if header_row else []
        if idx_list and header_idx:
            for line in content[header_idx + 2:]:
                qpid_dic = {}
                for i in range(0, len(idx_list) - 1):
                    qpid_dic[sec_list[i]] = line[idx_list[i]:idx_list[i + 1]].strip()
                lines = line[idx_list[-1]:].split()
                for i, key in enumerate(qpid_keys):
                    qpid_dic[key] = lines[i]
                qpid_list += [qpid_dic]
        self.data = qpid_list


@parser("qpid_stat_u")
class QpidStatU(Parser):

    """
    --- Sample ---
    subscr queue                                      conn                                  procName         procId browse acked excl creditMode  delivered  sessUnacked
    0      00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0   qpid.10.20.1.10:5671-10.20.1.10:33787 celery           21409                    CREDIT      2          0
    1      prrhss001058.example.com:event             qpid.10.20.1.10:5671-10.20.1.10:33848 Qpid Java Client 21066         Y     Y    WINDOW      2,623      0

    Returns
    -------
    list
    [
        {
            'subscr'       : '1',
            'queue'        : 'prrhss001058.example.com:event',
            'conn'         : 'qpid.10.20.1.10:5671-10.20.1.10:33848',
            'procName'     : 'Qpid Java Client',
            'procId'       : '21066',
            'acked'        : 'Y',
            'excl'         : 'Y',
            'creditMode'   : 'WINDOW',
            'delivered'    : '2,623',
            'sessUnacked'  : '0',

        },
    ]
    """
    def __iter__(self):
        return iter(self.data)

    def parse_content(self, content):
        qpid_list = []
        header_idx = header_row = None
        qpid_keys1 = ['subscr', 'queue', 'conn']
        qpid_keys2 = ['creditMode', 'delivered', 'sessUnacked']
        for i, l in enumerate(content):
            if 'subscr' in l:
                header_idx = i
                header_row = l
                break
        sec_list = ["procName", "procId", "browse", "acked", "excl", "creditMode"]
        idx_list = [header_row.index(i) for i in sec_list] if header_row else []
        if idx_list and header_idx:
            for line in content[header_idx + 2:]:
                lines = line[:idx_list[0]].split()
                qpid_dic = {}
                for i, key in enumerate(qpid_keys1):
                    qpid_dic[key] = lines[i]
                for i in range(0, len(idx_list) - 1):
                    qpid_dic[sec_list[i]] = line[idx_list[i]:idx_list[i + 1]].strip()
                lines = line[idx_list[-1]:].split()
                for i, key in enumerate(qpid_keys2):
                    qpid_dic[key] = lines[i]
                qpid_list += [qpid_dic]
        self.data = qpid_list
