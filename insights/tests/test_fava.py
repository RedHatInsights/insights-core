
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

UNAME_TESTS = [
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


def compare(each_rule, each_shared, each_expected, test_name):
    func = fava.FavaRule(json_dict=each_rule).as_function()

    if each_expected is None:
        expected = None
    else:
        expected = insights.make_response(
            each_expected['name'],
            **each_expected['pydata'])

    assert func({}, each_shared) == expected  # "%s %s" % (test_name, each_rule))


def test_uname():
    uname1 = Uname(context_wrap(UNAME1))

    # Test all the properties
    assert uname1.arch == 'x86_64'
    assert uname1.hw_platform == 'x86_64'
    assert uname1.kernel == '2.6.32-504.el6.x86_64'
    assert uname1.kernel_date == 'Tue Sep 16 01:56:35 EDT 2014'
    assert uname1.kernel_type == 'SMP'
    assert uname1.machine == 'x86_64'
    assert uname1.name == 'Linux'
    assert uname1.nodename == 'ceehadoop1.gsslab.rdu2.redhat.com'
    assert uname1.os == 'GNU/Linux'
    assert uname1.processor == 'x86_64'
    assert uname1.release == '504.el6'
    assert uname1.release_arch == '504.el6.x86_64'
    assert uname1.release_tuple == (6, 6)
    assert uname1.rhel_release == ['6', '6']
    assert uname1.ver_rel == '2.6.32-504.el6'
    assert uname1.version == '2.6.32'
    assert uname1._rel_maj == '504'

    assert [] == uname1.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6')
    assert ['2.6.32-600.el6'] == uname1.fixed_by('2.6.32-600.el6')
    assert [] == uname1.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6')
    assert ['2.6.33-100.el6'] == uname1.fixed_by('2.6.33-100.el6')
    assert ['2.6.32-600.el6'] == uname1.fixed_by('2.6.32-220.1.el6', '2.6.32-600.el6')
    assert ['2.6.32-504.1.el6'] == uname1.fixed_by('2.6.32-504.1.el6')

    for each_input, each_intro, each_expected, test_name in UNAME_TESTS:
        if each_intro:
            assert each_expected == uname1.fixed_by(*each_input, **{'introduced_in': each_intro})
        else:
            assert each_expected == uname1.fixed_by(*each_input)


def make_uname_fixed_by_call(uname_input, intro_input):
    return "Uname.fixed_by('%s'%s)" % ("', '".join(uname_input), (", introduced_in='%s'" % intro_input if intro_input else ""))


def old_make_uname_fixed_by_call(uname_input, intro_input):
    args = {
        'fixed': uname_input,
    }
    if intro_input:
        args['introduced_in'] = intro_input
    return {
        'uname_fixed_by': args
    }


def make_uname1_compile_test1(uname_input, intro, expected, test_name):
    return ({
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': '{{ Uname.kernel }}',
            },
            'when': make_uname_fixed_by_call(uname_input, intro),
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


def make_uname1_compile_test2(uname_input, intro, expected, test_name):
    return ({
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': '{{ Uname.kernel }}',
                'fixed_by': '{{ %s }}' % make_uname_fixed_by_call(uname_input, intro),
            },
            'when': make_uname_fixed_by_call(uname_input, intro),
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


def make_uname1_compile_test3(uname_input, intro, expected, test_name):
    return ({
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': '{{ Uname.kernel }}',
                'fixed_by': '{{ check_fixed_by }}'
            },
            'when': 'check_fixed_by',
            'vars': {
                'check_fixed_by': '{{ %s }}' % make_uname_fixed_by_call(uname_input, intro),
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


def test_basic_compile():

    for each_rule, each_shared, each_expected, test_name in COMPILE_TESTS:
        compare(each_rule, each_shared, each_expected, test_name)

    for each_maker in [
            make_uname1_compile_test1,
            make_uname1_compile_test2,
            make_uname1_compile_test3,
    ]:
        for each_rule, each_shared, each_expected, test_name in [each_maker(*each_uname_test) for each_uname_test in UNAME_TESTS]:
            compare(each_rule, each_shared, each_expected, test_name)


def test_compile_test_one():
    compare(*COMPILE_TESTS[0])


def test_compile_test_two():
    compare(*COMPILE_TESTS[1])


def test_compile_test_three():
    compare(*COMPILE_TESTS[2])


def test_compile_test_four():
    compare(*COMPILE_TESTS[3])


def test_compile_test_five():
    compare(*COMPILE_TESTS[4])


def test_test1_test_one():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[0]))


def test_test1_test_two():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[1]))


def test_test1_test_three():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[2]))


def test_test1_test_four():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[3]))


def test_test1_test_five():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[4]))


def test_test1_test_six():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[5]))


def test_test1_test_seven():
    compare(*make_uname1_compile_test1(*UNAME_TESTS[6]))


def test_test2_test_one():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[0]))


def test_test2_test_two():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[1]))


def test_test2_test_three():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[2]))


def test_test2_test_four():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[3]))


def test_test2_test_five():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[4]))


def test_test2_test_six():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[5]))


def test_test2_test_seven():
    compare(*make_uname1_compile_test2(*UNAME_TESTS[6]))


def test_test3_test_one():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[0]))


def test_test3_test_two():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[1]))


def test_test3_test_three():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[2]))


def test_test3_test_four():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[3]))


def test_test3_test_five():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[4]))


def test_test3_test_six():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[5]))


def test_test3_test_seven():
    compare(*make_uname1_compile_test3(*UNAME_TESTS[6]))


def test_jinja_test1():
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
    compare(rule, shared_parsers, expected, 'test jinja test1')


def test_jinja_test2():
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
    compare(rule, shared_parsers, expected, 'test jinja test2')


def test_jinja_where_with_variable():
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
    compare(rule, shared_parsers, expected, 'test jinja where with variable true')

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
    compare(rule, shared_parsers, expected, 'test jinja where with variable false')

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


def test_jinja_test4():
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
    compare(rule, shared_parsers, expected, 'test jinja test4')


def test_jinja_error_undefined():
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


def test_jinja_test6():
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
    compare(rule, shared_parsers, expected, 'test jinja test6')


def test_jinja_test7():
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
    compare(rule, shared_parsers, expected, 'test jinja test7')


def test_jinja_test8():
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
    compare(rule, shared_parsers, expected, 'test jinja test8')


def test_jinja_test9():
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
    compare(rule, shared_parsers, expected, 'test jinja test9')


def test_when_with_list():
    # when with a list

    # of 2 elements true
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
                "v2",
            ],
            'vars': {
                'v1': True,
                'v2': True,
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
    compare(rule, shared_parsers, expected, 'test jinja test9')

    # of 2 elements false
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
                "v2",
            ],
            'vars': {
                'v1': True,
                'v2': False,
            },
        },
    }
    shared_parsers = {}
    expected = None
    compare(rule, shared_parsers, expected, 'test jinja test9')

    # of 1 elements true
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
            ],
            'vars': {
                'v1': False,
            },
        },
    }
    shared_parsers = {}
    expected = None
    compare(rule, shared_parsers, expected, 'test jinja test9')

    # of 1 elements false
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
            ],
            'vars': {
                'v1': False,
            },
        },
    }
    shared_parsers = {}
    expected = None
    compare(rule, shared_parsers, expected, 'test jinja test9')

    # of a list in a list true
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
                ["v2", "v3"],
            ],
            'vars': {
                'v1': True,
                'v2': True,
                'v3': True,
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
    compare(rule, shared_parsers, expected, 'test jinja test9')

    # of a list in a list false
    rule = {
        'rule': {
            'name': "BASIC_ONE",
            'pydata': {
                'kernel': 70,
            },
            'when': [
                "v1",
                ["v2", "v3"],
            ],
            'vars': {
                'v1': True,
                'v2': False,
                'v3': True,
            },
        },
    }
    shared_parsers = {}
    expected = None
    compare(rule, shared_parsers, expected, 'test jinja test9')


def compare_uname(jinja_expr, expected_value, test_name):
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
    compare(rule, shared_parsers, expected, test_name)


def test_uname_test1():
    compare_uname("{{ Uname.kernel }}", Uname(context_wrap(UNAME1)).kernel, "uname test1")


def test_uname_test2():
    compare_uname("{{ Uname.arch }}", Uname(context_wrap(UNAME1)).arch, "uname test2")


def test_uname_test3():
    compare_uname("{{ Uname.version }}", Uname(context_wrap(UNAME1)).version, "uname test3")


def test_uname_test4():
    compare_uname("{{ Uname.fixed_by('2.6.32-600.el6') }}",
                       Uname(context_wrap(UNAME1)).fixed_by('2.6.32-600.el6'),
                       "uname test4")


def test_uname_test5():
    compare_uname("{{ Uname.fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6') }}",
                       Uname(context_wrap(UNAME1)).fixed_by('2.6.32-220.1.el6', '2.6.32-504.el6'),
                       "uname test5")


def test_uname_test6():
    compare_uname("{{ Uname.fixed_by('2.6.32-600.el6', introduced_in='2.6.32-504.1.el6') }}",
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


def test_do_template1():
    src = 'Uname'
    assert set(['Uname']) == fava.find_undeclared_variables_from_expression(src)
    assert Uname == fava.fava_render_jinja_expression(src, **{'Uname': Uname})


def test_do_template2():
    src = "Uname['PACKAGES'][0]"
    assert set(['Uname']) == fava.find_undeclared_variables_from_expression(src)
    Uname = {}
    Uname['PACKAGES'] = ['firstpackage', 'secondpackage', 'thirdpackage']
    assert 'firstpackage' == fava.fava_render_jinja_expression(src, **{'Uname': Uname})
