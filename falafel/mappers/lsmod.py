from .. import Mapper, mapper


@mapper("lsmod")
class LsMod(Mapper):

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def parse_content(self, content):
        """
        Analysis each line and return a list with all modules info

        --- Sample ---
        Module                  Size  Used by
        xt_CHECKSUM            12549  1
        ipt_MASQUERADE         12678  3
        nf_nat_masquerade_ipv4    13412  1 ipt_MASQUERADE

        --- Construct a dict with the module name as the key ---
        { 'xt_CHECKSUM':
            { 'size': '12549',
            'depnum': 1,
            'deplist': ''
            },
        }
        """
        module_dict = {}
        memb_keys = ['size', 'depnum', 'deplist']
        # skip the title
        for line in content[1:]:
            if line.strip():
                line_split = line.split()
                # make sure the deplist element exists
                if len(line_split) == 3:
                    line_split.append('')
                if len(line_split) == 4:
                    mod_attrs = {}
                    for i, key in enumerate(memb_keys):
                        mod_attrs[key] = line_split[i + 1]
                    module_dict[line_split[0]] = mod_attrs
        self.data = module_dict
