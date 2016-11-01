from .. import Mapper, mapper


@mapper('tuned-adm')
class Tuned(Mapper):

    def parse_content(self, content):
        self.data = {}
        self.data['available'] = []
        for line in content:
            if line.startswith('-'):
                self.data['available'].append(line.split('- ')[1])
            elif line.startswith('Current'):
                self.data['active'] = line.split(': ')[1]
            elif line.startswith('Preset'):
                self.data['preset'] = line.split(': ')[1]
            else:
                continue
