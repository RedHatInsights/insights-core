
import unittest
import pytest
import string

from insights.core import fava
import insights

from insights.parsers.uname import Uname
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.fstab import FSTab
from insights.parsers.ethtool import Ethtool
from insights.parsers.ifcfg import IfCFG

from insights.combiners.hostname import hostname

from insights.tests import context_wrap


UNAME1 = "Linux ceehadoop1.gsslab.rdu2.redhat.com 2.6.32-504.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux"


class TestUname(unittest.TestCase):
    def test_uname(self):
        uname1 = Uname(context_wrap(UNAME1))

        # Test all the properties
        self.assertEqual(uname1.arch, 'x86_64')
        self.assertEqual(uname1.hw_platform, 'x86_64')
        self.assertEqual(uname1.kernel, '2.6.32-504.el6.x86_64')
        self.assertEqual(uname1.kernel_date, 'Tue Sep 16 01:56:35 EDT 2014')
        self.assertEqual(uname1.kernel_type, 'SMP')
        self.assertEqual(uname1.machine, 'x86_64')
        self.assertEqual(uname1.name, 'Linux')
        self.assertEqual(uname1.nodename, 'ceehadoop1.gsslab.rdu2.redhat.com')
        self.assertEqual(uname1.os, 'GNU/Linux')
        self.assertEqual(uname1.processor, 'x86_64')
        self.assertEqual(uname1.release, '504.el6')
        self.assertEqual(uname1.release_arch, '504.el6.x86_64')
        self.assertEqual(uname1.release_tuple, (6, 6,))
        self.assertEqual(uname1.rhel_release, ['6', '6'])
        self.assertEqual(uname1.ver_rel, '2.6.32-504.el6')
        self.assertEqual(uname1.version, '2.6.32')
        self.assertEqual(uname1._rel_maj, '504')

        self.assertEqual([], uname1.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6'))
        self.assertEqual(['2.6.32-600.el6'], uname1.fixed_by('2.6.32-600.el6'))
        self.assertEqual([], uname1.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6'))
        self.assertEqual(['2.6.33-100.el6'], uname1.fixed_by('2.6.33-100.el6'))
        self.assertEqual(['2.6.32-600.el6'], uname1.fixed_by('2.6.32-220.1.el6', '2.6.32-600.el6'))
        self.assertEqual(['2.6.32-504.1.el6'], uname1.fixed_by('2.6.32-504.1.el6'))

        UNAME1_TESTS = [
            (['2.6.32-220.1.el6', '2.6.32-504.el6'],
             None,
             []),
            (['2.6.32-600.el6'],
             None,
             ['2.6.32-600.el6']),
            (['2.6.32-600.el6'],
             '2.6.32-504.1.el6',
             []),
            (['2.6.32-600.el6'],
             '2.6.32-503.el6',
             ['2.6.32-600.el6']),
            (['2.6.33-100.el6'],
             None,
             ['2.6.33-100.el6']),
            (['2.6.32-220.1.el6', '2.6.32-600.el6'],
             None,
             ['2.6.32-600.el6']),
            (['2.6.32-504.1.el6'],
             None,
             ['2.6.32-504.1.el6'])
        ]

        for each_input, each_intro, each_expected in UNAME1_TESTS:
            if each_intro:
                self.assertEqual(
                    each_expected,
                    uname1.fixed_by(
                        *each_input,
                        **{'introduced_in': each_intro}))
            else:
                self.assertEqual(
                    each_expected,
                    uname1.fixed_by(
                        *each_input))


class TestBasicCompile(unittest.TestCase):
    longMessage = True
    UNAME1_TESTS = [
        (['2.6.32-220.1.el6', '2.6.32-504.el6'],
         None,
         [],
         'test one'),
        (['2.6.32-600.el6'],
         None,
         ['2.6.32-600.el6'],
         'test two'),
        (['2.6.32-600.el6'],
         '2.6.32-504.1.el6',
         [],
         'test three'),
        (['2.6.32-600.el6'],
         '2.6.32-503.el6',
         ['2.6.32-600.el6'],
         'test four'),
        (['2.6.33-100.el6'],
         None,
         ['2.6.33-100.el6'],
         'test five'),
        (['2.6.32-220.1.el6', '2.6.32-600.el6'],
         None,
         ['2.6.32-600.el6'],
         'test six'),
        (['2.6.32-504.1.el6'],
         None,
         ['2.6.32-504.1.el6'],
         'test seven')
    ]

    def make_uname_fixed_by_call(self, uname_input, intro_input):
        return "Uname.fixed_by('%s'%s)" % ("', '".join(uname_input), (", introduced_in='%s'" % intro_input if intro_input else ""))

    def old_make_uname_fixed_by_call(self, uname_input, intro_input):
        args = {
            'fixed': uname_input,
        }
        if intro_input:
            args['introduced_in'] = intro_input
        return {
            'uname_fixed_by': args
        }

    def make_uname1_compile_test1(self, uname_input, intro, expected, test_name):
        return ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                },
                'when': self.make_uname_fixed_by_call(uname_input, intro),
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
            },
        } if len(expected) > 0 else None,
            'test1 ' + test_name)

    def make_uname1_compile_test2(self, uname_input, intro, expected, test_name):
        return ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                    'fixed_by': '{{ %s }}' % self.make_uname_fixed_by_call(uname_input, intro),
                },
                'when': self.make_uname_fixed_by_call(uname_input, intro),
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
                'fixed_by': expected,
            },
        } if len(expected) > 0 else None,
            'test2 ' + test_name)

    def make_uname1_compile_test3(self, uname_input, intro, expected, test_name):
        return ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                    'fixed_by': '{{ check_fixed_by }}'
                },
                'when': 'check_fixed_by',
                'vars': {
                    'check_fixed_by': '{{ %s }}' % self.make_uname_fixed_by_call(uname_input, intro),
                },
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
                'fixed_by': expected,
            },
        } if len(expected) > 0 else None,
            'test3 ' + test_name)

    COMPILE_TESTS = [
        ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                },
                'when': False,
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        },
            None,
            'compile test one'
        ),
        ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                },
                'when': True,
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
            },
        },
            'compile test two'
        ),
        ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                },
                'when': 'Uname.kernel',
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
            },
        },
            'compile test three'
        ),
        ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ k }}",
                },
                'when': "k",
                'vars': {
                    'k': '{{ Uname.kernel }}',
                },
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
            },
        },
            'compile test four'
        ),
        ({
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ Uname.kernel }}',
                },
                'when': "Uname.fixed_by('2.6.32-509.el6')",
            },
        }, {
            Uname: Uname(context_wrap(UNAME1))
        }, {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': Uname(context_wrap(UNAME1)).kernel,
            },
        },
            'compile test five'
        ),
    ]

    def test_basic_compile(self):

        for each_rule, each_shared, each_expected, test_name in self.COMPILE_TESTS:
            self.compare(each_rule, each_shared, each_expected, test_name)

        for each_maker in [
                self.make_uname1_compile_test1,
                self.make_uname1_compile_test2,
                self.make_uname1_compile_test3,
        ]:
            for each_rule, each_shared, each_expected, test_name in [each_maker(*each_uname_test) for each_uname_test in self.UNAME1_TESTS]:
                self.compare(each_rule, each_shared, each_expected, test_name)

    def compare(self, each_rule, each_shared, each_expected, test_name):
        test_name = each_rule
        func = fava.FavaRule(json_dict=each_rule).as_function()

        self.assertEqual(
            insights.make_response(
                each_expected['name'],
                **each_expected['pydata']
            ) if each_expected else None,
            func({}, each_shared),
            test_name)

    def test_compile_test_one(self):
        self.compare(*self.COMPILE_TESTS[0])

    def test_compile_test_two(self):
        self.compare(*self.COMPILE_TESTS[1])

    def test_compile_test_three(self):
        self.compare(*self.COMPILE_TESTS[2])

    def test_compile_test_four(self):
        self.compare(*self.COMPILE_TESTS[3])

    def test_compile_test_five(self):
        self.compare(*self.COMPILE_TESTS[4])

    def test_test1_test_one(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[0]))

    def test_test1_test_two(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[1]))

    def test_test1_test_three(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[2]))

    def test_test1_test_four(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[3]))

    def test_test1_test_five(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[4]))

    def test_test1_test_six(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[5]))

    def test_test1_test_seven(self):
        self.compare(*self.make_uname1_compile_test1(*self.UNAME1_TESTS[6]))

    def test_test2_test_one(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[0]))

    def test_test2_test_two(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[1]))

    def test_test2_test_three(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[2]))

    def test_test2_test_four(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[3]))

    def test_test2_test_five(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[4]))

    def test_test2_test_six(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[5]))

    def test_test2_test_seven(self):
        self.compare(*self.make_uname1_compile_test2(*self.UNAME1_TESTS[6]))

    def test_test3_test_one(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[0]))

    def test_test3_test_two(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[1]))

    def test_test3_test_three(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[2]))

    def test_test3_test_four(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[3]))

    def test_test3_test_five(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[4]))

    def test_test3_test_six(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[5]))

    def test_test3_test_seven(self):
        self.compare(*self.make_uname1_compile_test3(*self.UNAME1_TESTS[6]))


class TestJinjaExpressions(unittest.TestCase):

    longMessage = True

    def compare(self, each_rule, each_shared, each_expected, test_name):
        func = fava.FavaRule(json_dict=each_rule).as_function()
        self.assertEqual(
            insights.make_response(
                each_expected['name'],
                **each_expected['pydata']
            ) if each_expected else None,
            func({}, each_shared),
            "%s %s" % (test_name, each_rule))

    def test_jinja_test1(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ "junk" }}',
                },
                'when': True,
                'vars': {
                    'junk': 'this is a test',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 'junk'
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test1')

    def test_jinja_test2(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ junk }}',
                },
                'when': True,
                'vars': {
                    'junk': 'this is a test',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 'this is a test'
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test2')

    def test_jinja_where_with_variable(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ junk }}',
                },
                'when': "b",
                'vars': {
                    'junk': 'this is a test',
                    'b': '{{ True }}',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 'this is a test'
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja where with variable true')

        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ junk }}',
                },
                'when': "b",
                'vars': {
                    'junk': 'this is a test',
                    'b': '{{ False }}',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 'this is a test'
            },
        }
        expected = None
        self.compare(rule, shared_parsers, expected, 'test jinja where with variable false')

        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': '{{ junk }}',
                },
                'when': "{{ b }}",
                'vars': {
                    'junk': 'this is a test',
                    'b': '{{ False }}',
                },
            },
        }
        with pytest.raises(fava.FavaTranslationError):
            fava.FavaRule(json_dict=rule)

    def test_jinja_test4(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ junk + goober }}",
                },
                'when': True,
                'vars': {
                    'junk': 'hello ',
                    'goober': 'world',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 'hello world'
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test4')

    def test_jinja_error_undefined(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ junk + goober }}",
                },
                'when': True,
                'vars': {
                    'junk': 'hello ',
                },
            },
        }

        with pytest.raises(fava.FavaTranslationError):
            fava.FavaRule(json_dict=rule)

    def test_jinja_test6(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ junk + goober }}",
                },
                'when': True,
                'vars': {
                    'junk': '{ "a": 30 ',
                    'goober': 'just some stuff',
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': '{ "a": 30 just some stuff',
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test6')

    def test_jinja_test7(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'uname': "{{ Uname }}",
                },
                'when': True,
            },
        }
        shared_parsers = {
            Uname: Uname(context_wrap(UNAME1))
        }
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'uname': Uname(context_wrap(UNAME1)),
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test7')

    def test_jinja_test8(self):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'uname': "{{ Uname.kernel }}",
                },
                'when': True,
            },
        }
        shared_parsers = {
            Uname: Uname(context_wrap(UNAME1))
        }
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'uname': Uname(context_wrap(UNAME1)).kernel,
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test8')

    def test_jinja_test9(self):
        # so we now should be able to add numbers
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ junk + goober }}",
                },
                'when': True,
                'vars': {
                    'junk': 30,
                    'goober': 40,
                },
            },
        }
        shared_parsers = {}
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
        }
        self.compare(rule, shared_parsers, expected, 'test jinja test9')

    def compare_uname(self, jinja_expr, expected_value, test_name):
        rule = {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'uname': jinja_expr,
                },
                'when': True,
            },
        }
        shared_parsers = {
            Uname: Uname(context_wrap(UNAME1))
        }
        expected = {
            'name': "BASIC_ONE",
            'pydata': {
                'uname': expected_value,
            },
        }
        self.compare(rule, shared_parsers, expected, test_name)

    def test_uname_test1(self):
        self.compare_uname("{{ Uname.kernel }}", Uname(context_wrap(UNAME1)).kernel, "uname test1")

    def test_uname_test2(self):
        self.compare_uname("{{ Uname.arch }}", Uname(context_wrap(UNAME1)).arch, "uname test2")

    def test_uname_test3(self):
        self.compare_uname("{{ Uname.version }}", Uname(context_wrap(UNAME1)).version, "uname test3")

    def test_uname_test4(self):
        self.compare_uname("{{ Uname.fixed_by('2.6.32-600.el6') }}",
                           Uname(context_wrap(UNAME1)).fixed_by('2.6.32-600.el6'),
                           "uname test4")

    def test_uname_test5(self):
        self.compare_uname("{{ Uname.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6') }}",
                           Uname(context_wrap(UNAME1)).fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6'),
                           "uname test5")

    def test_uname_test6(self):
        self.compare_uname("{{ Uname.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6') }}",
                           Uname(context_wrap(UNAME1)).fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6'),
                           "uname test6")


YAML_TESTS = [
    ("""
---
rule:
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ Uname.kernel }}"
  when: true
""",
{
    'rule': {
        'name': "BASIC_ONE",
        'pydata': {
            'kernel': '{{ Uname.kernel }}',
        },
        'when': True,
    },
}
    ),
    ("""
---
rule:
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ Uname.kernel }}"
  when: True
""",
{
    'rule': {
        'name': "BASIC_ONE",
        'pydata': {
            'kernel': "{{ Uname.kernel }}",
        },
        'when': True,
    },
}),
    ("""
---
rule:
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ Uname.kernel }}"
  when: Uname.kernel
""",
{
    'rule': {
        'name': "BASIC_ONE",
        'pydata': {
            'kernel': '{{ Uname.kernel }}',
        },
        'when': 'Uname.kernel',
    },
}),
    ("""
---
rule:
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ Uname.kernel }}"
  when: Uname.fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6')
""",
{
    'rule': {
        'name': "BASIC_ONE",
        'pydata': {
            'kernel': '{{ Uname.kernel }}',
        },
        'when': "Uname.fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6')",
    },
}),
    ("""
---
rule:
  vars:
    junk: this is a test
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ junk }}"
  when: True
""",
{
    'rule': {
        'name': "BASIC_ONE",
        'pydata': {
            'kernel': "{{ junk }}",
        },
        'when': True,
        'vars': {
            'junk': 'this is a test',
        },
    },
}),
    ("""
---
rule:
  vars:
    junk: this is a test
  name: "BASIC_ONE"
  pydata:
    kernel: "{{ junk }}"
  when: True
""",
        {
            'rule': {
                'name': "BASIC_ONE",
                'pydata': {
                    'kernel': "{{ junk }}",
                },
                'when': True,
                'vars': {
                    'junk': 'this is a test',
                },
            },
        }),
]


@pytest.fixture(params=YAML_TESTS)
def yaml2jsonTest(request):
    return request.param


def test_yaml_tests(yaml2jsonTest):
    assert yaml2jsonTest[1] == fava.FavaRule.yaml_deserialize(yaml2jsonTest[0])


PARSER_NAMES_TEST_TEMPLATE = string.Template("""
---
rule:
  name: "PARSER_NAME_${name}s_TEST_KEY"
  pydata:
    kernel: "{{ ${name} }}"
  when: True
""")


PARSERS_TO_TEST = [
    Uname,
    InstalledRpms,
    FSTab,
    IfCFG,
    Ethtool,
]


@pytest.fixture(params=PARSERS_TO_TEST)
def each_parser_to_test(request):
    return request.param


def test_parser_names_test(each_parser_to_test):
    # this should not raise exception
    fava.FavaRule(PARSER_NAMES_TEST_TEMPLATE.substitute({"name": each_parser_to_test.__name__}))


def test_parser_names_nosuchparser():
    # arbitrary names should not work in Fava
    with pytest.raises(fava.FavaTranslationError):
        fava.FavaRule(PARSER_NAMES_TEST_TEMPLATE.substitute({"name": "Nosuchparser"}))


def test_parser_names_combiner():
    # combiner names should not work in Fava
    with pytest.raises(fava.FavaTranslationError):
        fava.FavaRule(PARSER_NAMES_TEST_TEMPLATE.substitute({"name": hostname.__name__}))


class TestFAVA3(unittest.TestCase):

    def test_do_template1(self):
        src = 'Uname'
        self.assertEqual(set(['Uname']),
                         fava.find_undeclared_variables_from_expression(src))
        self.assertEqual(Uname,
                         fava.fava_render_jinja_expression(
                             src,
                             **{'Uname': Uname}))

    def test_do_template2(self):
        src = "Uname['PACKAGES'][0]"
        self.assertEqual(set(['Uname']),
                         fava.find_undeclared_variables_from_expression(src))
        Uname = {}
        Uname['PACKAGES'] = ['firstpackage', 'secondpackage', 'thirdpackage']
        self.assertEqual('firstpackage', fava.fava_render_jinja_expression(src, **{'Uname': Uname}))
