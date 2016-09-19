from falafel.core import LogFileOutput
from falafel.core.plugins import mapper


@mapper('nova-api_log')
class NovaApiLog(LogFileOutput):
    def get(self, keywords):
        """
        Returns all lines that contain all keywords. keywords can be str or str list.
        -- Sample --
        keywords is a list. Example: ["WARNING","Could not find token", "404"]
        ------------
       2016-08-12 13:15:46.343 32386 WARNING nova.api.ec2.cloud [-] Deprecated: The in tree EC2 API is deprecated as
        of Kilo release and may be removed in a future release. The stackforge ec2-api project
        http://git.openstack.org/cgit/stackforge/ec2-api/ is the target replacement for this functionality.
        """
        r = []
        for l in self.lines:
            if type(keywords) == list and all([word in l for word in keywords]):
                r.append(l)
            elif type(keywords) == str and keywords in l:
                r.append(l)
        return r
