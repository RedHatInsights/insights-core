"""
Sample Specs, Parsers and Rules for Tests
-----------------------------------------

These specs, parsers and rules are used by some of the tests.
"""
from insights import make_fail, parser, Parser, rule
from insights.core.spec_factory import SpecSet, RegistryPoint, simple_file, glob_file


class TSpecs(SpecSet):
    sample_multioutput_file = RegistryPoint(multi_output=True)
    sample_nonexistent = RegistryPoint()
    sample_raw_file = RegistryPoint(raw=True)


class TDefaultSpecs(TSpecs):
    sample_multioutput_file = glob_file('/var/log/sample_*.log')
    sample_nonexistent = simple_file('/nonexistent_file.txt')
    sample_raw_file = simple_file('/var/log/sample_2.log')


class TParser(Parser):
    def parse_content(self, content):
        self.data = content


@parser(TSpecs.sample_multioutput_file)
class TMultioutputParser(TParser):
    pass


@parser(TSpecs.sample_nonexistent)
class TNonexistentParser(TParser):
    pass


@parser(TSpecs.sample_raw_file)
class TRawParser(TParser):
    pass


@rule(TMultioutputParser)
def report_multioutput(mop):
    return make_fail('MO_SPEC', data=mop[0].data, number=len(mop))


@rule(TNonexistentParser)
def report_nonexistent(nep):
    return make_fail('NE_SPEC', data=nep.data)


@rule(TRawParser)
def report_raw(rp):
    return make_fail('RA_SPEC', data=rp.data)
