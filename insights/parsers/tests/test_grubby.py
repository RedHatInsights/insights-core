from insights.parsers.grubby import grub2_default_index
from insights.tests import context_wrap

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '1'
DEFAULT_INDEX_3 = ''
DEFAULT_INDEX_4 = '-2'


class TestGrub2DefaultIndex():
    def test_grub2_default_index(self):
        result1 = grub2_default_index(context_wrap(DEFAULT_INDEX_1))
        assert result1 == 0

        result2 = grub2_default_index(context_wrap(DEFAULT_INDEX_2))
        assert result2 == 1

        result3 = grub2_default_index(context_wrap(DEFAULT_INDEX_3))
        assert result3 is None

        result4 = grub2_default_index(context_wrap(DEFAULT_INDEX_4))
        assert result4 is None
