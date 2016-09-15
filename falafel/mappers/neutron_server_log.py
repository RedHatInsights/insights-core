from falafel.core import LogFileOutput
from falafel.core.plugins import mapper


@mapper('neutron_server_log')
class NeutronServerLog(LogFileOutput):
    def get(self, keywords):
        """
        Returns all lines that contain all keywords. keywords can be str or str list.
        -- Sample --
        keywords is a list. Example: ["WARNING","Could not find token", "404"]
        ------------
        2016-09-13 06:06:46.131 30586 WARNING keystonemiddleware.auth_token [-] Identity response: {"error":
        {"message": "Could not find token: bc029dbe33f84fbcb67ef7d592458e60", "code": 404, "title": "Not Found"}}
        """
        r = []
        for l in self.lines:
            if type(keywords) == list and all([word in l for word in keywords]):
                r.append(l)
            elif type(keywords) == str and keywords in l:
                r.append(l)
        return r
