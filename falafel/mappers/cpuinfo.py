from falafel.core.plugins import mapper
from falafel.core.mapper import MapperOutput

class CpuInfo(MapperOutput):

    def __init__(self, data):
        self.data = data

    def cpu_count(self):
        """
        returns number of cpus, this is found by number of unique processor entries in data
        returns [] if processor does not exist in data
        """
        cpus = [line.split(':')[-1].strip() for line in self.data if line.startswith('processor')]
        return len(list(set(cpus)))

    def socket_count(self):
        """
        returns number of sockets, this is found by number of unique physical id entries in data
        returns [] if physical id does not exist in data
        """
        sockets = [line.split(':')[-1].strip() for line in self.data if line.startswith('physical id')]
        return len(list(set(sockets)))

    def vendor(self):
        """
        returns field in vendor_id
        return None if vendor_id does not exist in data
        """
        for line in self.data:
            if line.startswith('vendor_id'):
                return line.split(':')[-1].strip()

    def model_name(self):
        """
        returns list of unique model names
        return [] if no model names exist in data
        """
        names = []
        for line in self.data:
            if line.startswith('model name'):
                names.append(line.split(':')[-1].strip())
        return list(set(names))

    def model(self):
        """
        returns list of unique models
        return [] if no models exist in data
        """
        models = []
        for line in self.data:
            if line.startswith('model  '):
                models.append(line.split(':')[-1].strip())
        return models

    def cpu_family(self):
        """
        returns field in cpu family
        return None if cpu family does not exist in data
        """
        for line in self.data:
            if line.startswith('cpu family'):
                return line.split(':')[-1].strip()

    def cpu_speed(self):
        """
        returns field in cpu MHz
        return None if cpu MHz does not exist in data
        """
        for line in self.data:
            if line.startswith('cpu MHz'):
                return line.split(':')[-1].strip()

    def cache_size(self):
        """
        returns field in cache size include the unit 'KB'
        return None if cache size does not exist in data
        """
        for line in self.data:
            if line.startswith('cache size'):
                return line.split(':')[-1].strip()

@mapper('cpuinfo')
def cpuinfo(context):
    return CpuInfo(context.content)
