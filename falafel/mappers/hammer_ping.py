
from .. import mapper, Mapper


@mapper("hammer_ping")
class HammerPing(Mapper):
    """
    After input hammer_ping command .you will receive the feedback messsage.suah as:
    ==============================================================
    candlepin:
        Status:          FAIL
        Server Response: Message: 404 Resource Not Found
        ...
        ...
    elasticsearch:
        Status:          ok
        Server Response: Duration: 35ms
    foreman_tasks:
        Status:          ok
    Server Response: Duration: 1ms
    ==============================================================
    this class aims to change all message into directory format.such as :
    ==============================================================
    {
        'candlepin':
                {   'FAIL': '404 Resource Not Found'},
        'candlepin_auth':
                {   'FAIL': 'Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)'},
        'foreman_tasks':
                {'ok': '1ms'},
        'elasticsearch':
                {'ok': '35ms'},
        'pulp':
                {'ok': '61ms'}
    }
    """
    def __len__(self):
        return len(self.data)

    def parse_content(self, context):
        content = list(context)
        i = 0
        dic = {}
        while i < len(content):
            dic_r = {}
            value_1 = content[i + 1].split(':', 1)[1]
            value_2 = content[i + 2].split(':', 2)[2]
            dic_r[value_1.strip()] = value_2.strip()
            dic[content[i].strip(': ')] = dic_r
            # every circulation,variate i add 3,that is to say:
            # 1st:  index = 0 1 2
            # 2nd:  index = 3 4 5 ...  every index on behalf of input's line
            i += 3
        self.data = dic
