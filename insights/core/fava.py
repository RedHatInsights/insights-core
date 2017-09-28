#
# This module implements 'fava', an alternative way to write Insights Rule Plugins.
#
# Much of the framework of Insights assumes that each Rule Plugin is implemented in and
# by a python module.  Rather than break or fix this assumption, we implement fava by
# translating a rule to a Python module, and then importing it.
#
# The fava language itself doesn't assume or require that rule plugins are modules, so
# if at some point the Insights framework removes this assumption, fava can be implemented
# otherwise.
#
# The main entry points of this module are
#    fava_load - read, translate, and install all the Fava rules files found within
#                the directory tree,
#                similiar to 'insights.plugins.load' or 'insights.core.load_package' but
#                for fava files.
#    load_fava_plugin - read, translate, and install a single fava file
#                       similar to (python) import or __import__ but for fava files.
#
# Before the above entry points are called, the fava translator must be initialized
#    add_shared_parser - this tells the fava translator about a shared parser
#
#

import os
import imp
import insights
import logging
import pkgutil
import types
import sys

import jinja2
from jinja2 import meta as jinja2_meta
from jinja2 import nodes as jinja2_nodes
from jinja2.parser import Parser as jinja2_Parser

import ast
from ast import Expression, Lambda, arguments, Param, Name, Subscript, Index, Load, Call, keyword, Num, List, Str, IfExp, Module, FunctionDef, Return, And, BoolOp


log = logging.getLogger(__name__)


def fava_load(package_name):
    # read, translate, and install all the Fava rules files found within the directory tree,
    # similiar to 'insights.plugins.load' or 'insights.core.load_package' but for fava files.
    #
    # Find all the fava files in or under the directory of *package_name*,
    # translate them to modules, and import them as if they were python modules at that
    # location.

    directory_name = _package_name_to_directory_name(package_name)

    for (dirpath, dirnames, filenames) in os.walk(directory_name):
        for each_filename in filenames:
            if each_filename.endswith('.yaml'):
                module_name = each_filename[:-len('.yaml')]
                subpackage_name = os.path.relpath(dirpath, directory_name).replace('/', '.').strip('.')
                if subpackage_name:
                    full_name = package_name + '.' + subpackage_name + '.' + module_name
                else:
                    full_name = package_name + '.' + module_name
                FavaRule(open(os.path.join(dirpath, each_filename)).read()).as_module(full_name)


def load_fava_plugin(full_module_name):
    # read, translate, and install a single fava file
    # similar to (python) import or __import__ but for fava files.
    #
    # This function returns the imported module.
    #
    # The file is expected to be in the directory of python package
    # and will be loaded and imported as a module in that python package
    # *full_module_name* is dotted python package and module name (without the '.yaml')

    lastdot = full_module_name.rfind('.')
    assert lastdot != -1

    package_name = full_module_name[:lastdot]
    module_element_name = full_module_name[lastdot + 1:]

    directory_name = _package_name_to_directory_name(package_name)

    full_file_name = os.path.join(directory_name, module_element_name + '.yaml')

    return FavaRule(open(full_file_name)).as_module(full_module_name)


def add_shared_parser(parser_name, parser_class):
    # Tell the fava translator about the name and class of a shared parser
    #  and make that parser available for use under that name in rules.
    FavaCode._add_shared_parser(parser_name, parser_class)


def _package_name_to_directory_name(package_name):
    # take a dotted package name (without the module name)
    # of an actual importable package
    # and return the directory associate with it

    firstdot = package_name.find('.')
    if firstdot != -1:
        toppackage_name = package_name[:firstdot]
    else:
        toppackage_name = package_name

    toppackage = __import__(toppackage_name, globals(), locals())
    toppackage_dir_name = os.path.dirname(toppackage.__file__)

    if firstdot != -1:
        subpackage_names = package_name[firstdot + 1:]
        subdirectory_names = subpackage_names.replace('.', '/')
        directory_name = os.path.join(toppackage_dir_name, subdirectory_names)
    else:
        directory_name = toppackage_dir_name
    return directory_name


#
#
#
# The translate_XXX functions are the main set of functions that translate a fava document
# to a Python module. 'translate' is the main entry point.
#
# Generally of the translate_XXX functions either call other translate_XXX functions or
# make_XXX functions.
#
# Most of the translate functions take part of a loaded YAML document and check it for
# 'syntax' (does it have the expected python types, and dictionary keys).
#
# Most of the translate functions also take a 'ctx' (context) argument.  This is primarly
# used to tell what variables (Shared Parsers and user defined variables) are useable within
# this part of the YAML tree.
#
# The translate_XXX functions, like the make_XXX functions, all return a FavaCode, which
# represents the code needed to produce part of a Python module.
#

class FavaTranslationError(Exception):
    pass


def translation_error(sss, value):
    raise FavaTranslationError(sss, value)


def translate(document):
    """
    The only top level document we support is a rule.
    """
    if 'rule' in document:
        ctx = set(FavaCode.get_known_parsers().keys())
        return make_plugin_module(translate_rule(document['rule'], ctx))
    else:
        translation_error("top level document", document)


def translate_rule(rule, ctx):
    """
    A rule translates to a insights rule, which conditionally calls 'make_response'.

    A rule must have a 'name', which must be a string, and translates to it's error key.
    A rule may have a 'when', which determines if make_response is called, see below
       for what it may contain, if absent make_response is always called.
    A rule may have 'pydata', which must be a mapping, and is added to 'make_response'.
    A rule may have 'vars', which must be a mapping, and provides variables useable in
       other parts of a rule.
    """
    if 'name' in rule:
        if 'vars' in rule:
            return translate_vars(rule, translate_rule, ctx)

        else:
            name = translate_name(rule['name'], ctx)

            if 'when' in rule:
                when = translate_when(rule['when'], ctx)
            else:
                when = translate_when(True, ctx)

            if 'pydata' in rule:
                pydata = translate_pydata(rule['pydata'], ctx)
            else:
                pydata = {}

            return make_rule_body(name, when, pydata)

    else:
        translation_error("rule", rule)


def translate_name(name, ctx):
    if isinstance(name, str):
        if not name.startswith('$'):
            return make_str(name)
        else:
            translation_error("Name must not start with '$'", name)

    else:
        translation_error("Name must be a string", name)


def translate_when(condition, ctx):
    """
    A condition must be a value, which is converted to a boolean.
    """
    if isinstance(condition, int):
        return make_num(condition)

    elif isinstance(condition, str):
        return translate_when_expression(condition, ctx)

    elif isinstance(condition, list):
        return make_all([translate_when(each, ctx) for each in condition])

    else:
        return translate_value(condition, ctx)


def translate_when_expression(string_value, ctx):
    # a when expression must be a jinja expression (without the surrounding {{ }}
    return make_render_jinja_expression(string_value, ctx)


def translate_value_string(string_value, ctx):
    # a value string can either be a jinja expression surrounded with {{ }}
    #   in which case it is rendered
    # or it is just treated as a string
    jinja_expression_string = find_jinja_expression(string_value)
    if isinstance(jinja_expression_string, str):
        return make_render_jinja_expression(jinja_expression_string, ctx)

    else:
        return make_str(string_value)


def find_jinja_expression(string_value):
    # if string_value starts and ends with {{ }},
    #    return what's between the surrounding {{ }}
    # else don't return a str
    stripped = string_value.strip()
    if stripped.startswith('{{') and stripped.endswith('}}'):
        return stripped[2:-2]
    else:
        return None


def translate_pydata(pydata, ctx):
    """
    pydata must be a mapping, whose values are values.
    this returns a dictionary of translated values.
    """
    if isinstance(pydata, dict):
        return [make_pydata_entry(key, translate_value(value, ctx))
                for key, value in pydata.iteritems()]
    else:
        translation_error("pydata must be a dict", pydata)


def translate_vars(outer, retranslate_function, ctx):
    """
    # This needs to be changed to populate ctx with known variables so translate_value,
    # can tell the difference between variables and constants.
    Many mappings can have an optional 'vars' member.

    This translates to a wrapping around the mapping, which defines
    all the variables to be used in the mapping itself.
    """
    if 'vars' in outer:
        # take vars out of what we are processing
        # but don't change the original
        new_outer = outer.copy()
        new_vars = new_outer['vars']
        del new_outer['vars']
        return make_wrapper(dict((key, translate_value(value, ctx)) for key, value in new_vars.iteritems()),
                            retranslate_function(new_outer,
                                                 ctx.union(new_vars.keys())))
    else:
        return retranslate_function(outer, ctx)


def translate_value(value, ctx):
    """
    if value is a string, it must refer to a variable in ctx, or it will be treated as a constant
    if value is an array, it's result will an array of translated elements
    if value is a mapping, it must be a known 'expression' mapping, and is translated
       according to that mapping's translation.
    """

    if isinstance(value, int):
        return make_num(value)

    elif isinstance(value, str):
        return translate_value_string(value, ctx)

    elif isinstance(value, list):
        return make_list([translate_value(each, ctx) for each in value])

    elif isinstance(value, dict):
        if 'vars' in value:
            return translate_vars(value, translate_value, ctx)

        else:
            if 'in' in value:
                return translate_value(value['in'], ctx)

            else:
                translation_error("dict used as value", value)
    else:
        translation_error("unknown value", value)


# The make_XXX functions actually produce instances of FavaCode
#
# In general they take and return instances of FavaCode, combining subtrees into larger
# trees.
#


def make_plugin_module(rule_body):
    return FavaCode(
        Module(
            body=[
                FunctionDef(
                    name='report',
                    args=arguments(
                        args=[
                            Name(id='shared', ctx=Param()),
                        ],
                        vararg=None,
                        kwarg=None,
                        defaults=[]),
                    body=[
                        Return(
                            value=rule_body.get_ast())],
                    decorator_list=[
                        Call(
                            func=Name(id='fava_rule', ctx=Load()),
                            args=[Name(id=each, ctx=Load()) for each in rule_body.get_parsers()],
                            keywords=[],
                            starargs=None, kwargs=None),
                    ])
            ]),
        [rule_body])


def make_rule_function(rule_body):
    """
    Create a rule function as a lambda expression.
    """
    return FavaCode(
        Expression(
            body=Lambda(
                args=arguments(
                    args=[Name(id='shared', ctx=Param())],
                    vararg=None, kwarg=None, defaults=[]),
                body=rule_body.get_ast())),
        [rule_body])


def make_rule_body(name, when, pydata):
    return FavaCode(
        IfExp(test=when.get_ast(),
              body=Call(func=Name(id='make_response', ctx=Load()),
                        args=[name.get_ast()],
                        keywords=[each.get_ast() for each in pydata],
                        starargs=None, kwargs=None),
              orelse=Name(id='None', ctx=Load())),
        [name, when] + pydata)


def make_pydata_entry(key, value):
    return FavaCode(
        keyword(arg=key, value=value.get_ast()),
        [value])


def make_wrapper(new_variables, value):
    """
    Define a set of new variables by createing a call to a lambda function.
    The value becomes the body of the lambda.
    The names of the new_variables become the names of the formal parameters to the lambda.
    The values of the new_variables become the values of the actual arguments to the call.
    """
    return FavaCode(
        Call(
            func=Lambda(
                args=arguments(
                    args=[Name(id=key, ctx=Param()) for key, val in new_variables.iteritems()],
                    vararg=None, kwarg=None, defaults=[]),
                body=value.get_ast()),
            args=[val.get_ast() for key, val in new_variables.iteritems()],
            keywords=[],
            starargs=None,
            kwargs=None),
        [value] + [val for key, val in new_variables.iteritems()])


def make_all(ll):
    # if ll is a list, this function is like 'all(ll)'
    # otherwise this function is like 'll'
    if isinstance(ll, list):
        if len(ll) == 0:
            return make_num(False)

        else:
            return FavaCode(
                BoolOp(op=And(),
                       values=[each.get_ast() for each in ll]),
                ll)

    else:
        return ll


def make_num(number_value):
    return FavaCode(
        Num(n=number_value),
        [])


def make_str(string_value):
    return FavaCode(
        Str(s=string_value),
        [])


def fava_render_jinja_expression(src, **variables):
    env = jinja2.Environment()
    return env.compile_expression(src)(variables)


def find_undeclared_variables_from_expression(source):
    try:
        env = jinja2.Environment()
        parser = jinja2_Parser(env, source, state='variable')
        expr = jinja2_nodes.Template(
            [jinja2_nodes.Assign(
                jinja2_nodes.Name('result', 'store'), parser.parse_expression(), lineno=1)], lineno=1)
        expr.set_environment(env)
        return set(jinja2_meta.find_undeclared_variables(expr))

    except Exception as e:
        translation_error("exception while parsing jinja expression: % s" % e, source)


def _build_subscript(value1, value2):
    return Subscript(
        value=value1,
        slice=Index(value=value2),
        ctx=Load())


def make_jinja_call(render_function_name, used_variables, string_value, ctx):
    used_defined_variables = ctx & used_variables
    undefined_variables = used_variables - ctx
    if len(undefined_variables) > 0:
        translation_error("Undefined variables: " + ", ".join(undefined_variables), string_value)
    used_parsers = used_defined_variables & set(FavaCode.get_known_parsers().keys())
    used_user_variables = used_defined_variables - used_parsers

    keyword_arguments = [keyword(arg=key, value=Name(id=key, ctx=Load()))
                           for key in used_user_variables] + \
                        [keyword(arg=key,
                                 value=_build_subscript(Name(id='shared', ctx=Load()),
                                                        Name(id=key, ctx=Load())))
                         for key in used_parsers]

    return FavaCode(
        Call(func=Name(id=render_function_name, ctx=Load()),
             args=[Str(s=string_value)],
             keywords=keyword_arguments,
             starargs=None, kwargs=None),
        [],
        parsers=used_parsers)


def make_render_jinja_expression(string_value, ctx):
    used_variables = find_undeclared_variables_from_expression(string_value)
    return make_jinja_call('fava_render_jinja_expression',
                           used_variables,
                           string_value,
                           ctx)


def make_list(value):
    return FavaCode(
        List(elts=[each.get_ast() for each in value], ctx=Load()),
        value)


def make_variable_reference(name):
    return FavaCode(
        Name(id=name, ctx=Load()),
        [])


class FavaCode:
    def __init__(self, the_ast, deps, parsers=[]):
        def get_all_deps(xdeps):
            all_deps = set()
            for each_dep in xdeps:
                all_deps = all_deps.union(each_dep.get_dependencies())
            return all_deps

        def get_all_parsers(xdeps, new_parsers):
            all_parsers = set(new_parsers)
            for each_dep in xdeps:
                all_parsers = all_parsers.union(each_dep.get_parsers())
            return all_parsers

        self._itsast = the_ast
        self._alldeps = get_all_deps(deps)
        self._allparsers = get_all_parsers(deps, parsers)

    def get_dependencies(self):
        return self._alldeps

    def get_parsers(self):
        return self._allparsers

    def get_ast(self):
        ast.fix_missing_locations(self._itsast)
        return self._itsast

    KnownSharedParsers = {}

    def get_globals(self):
        the_globals = {
            '__builtins__': {},
            'make_response': insights.make_response,
            'fava_render_jinja_expression': fava_render_jinja_expression,
            'fava_rule': insights.core.plugins.fava_rule,
        }
        parsers = self.get_parsers()
        for each_key, each_value in self.get_known_parsers().items():
            if each_key in parsers:
                the_globals[each_key] = each_value
        return the_globals

    @classmethod
    def get_known_parsers(cls):
        return cls.KnownSharedParsers.copy()

    @classmethod
    def get_known_shared_parsers(cls):
        return cls.KnownSharedParsers.copy()

    @classmethod
    def _add_shared_parser(cls, name, value):
        """
        This makes a shared parser available for use in all Fava plugins as the name *name*.

        If *name* is used in a plugin, it is translated to 'shared[*value*]'.

        If *name* is used in a plugin, then this plugin will depend upon *value*, that is
        'require=[*value*]' will be added to the rule decorator for this plugin.

        For example:
          FavaCode.add_shared_parser('Uname', insights.parsers.uname.Uname)
        """
        cls.KnownSharedParsers[name] = value


class FavaRule:

    def __init__(self, yaml_string=None, json_dict=None):
        if yaml_string and json_dict:
            raise Exception("FavaRule: must specify ONLY one of: yaml_string or json_dict")

        elif yaml_string:
            self._favacode = translate(self.yaml_deserialize(yaml_string))

        elif json_dict:
            self._favacode = translate(json_dict)

        else:
            raise Exception("FavaRule: must specify AT LEAST one of: yaml_string or json_dict")

        self.fake_package = None
        self.fake_module = None

    def as_module(self, full_module_name):
        return create_module(full_module_name,
                             self._favacode.get_ast(),
                             self._favacode.get_globals())

    def as_function(self):
        # FIXME
        # The module name needs to be uniqified so that different testing plugins don't
        # overwrite each others modules.
        if self.fake_package is None:
            self.fake_package = create_fake_package("fake_package")
        if self.fake_module is None:
            self.fake_module = self.as_module("fake_package.goober")
        return self.fake_module.report

    @classmethod
    def yaml_deserialize(cls, yaml_string):
        import yaml
        # 'Loader=yaml.Loader' is just to turn off the annoying warning about safe load
        return yaml.load(yaml_string, Loader=yaml.Loader)


def create_fake_package(full_package_name):
    # this is for creating fake packages.
    #  it should not be used for real packages, otherwise this will overwrite any existing
    #  package and make the import system will refuse to load the real code real package
    return create_module(full_package_name, Module(body=[]), {})


def create_module(full_module_name, the_ast, the_globals):
    lastdot = full_module_name.rfind('.')
    if lastdot != -1:
        package_name = full_module_name[:lastdot]
        module_element_name = full_module_name[lastdot + 1:]

        package = __import__(package_name, globals(), locals(), [module_element_name])

    module_code = compile(the_ast, "ast for " + full_module_name, 'exec')
    mod = types.ModuleType(full_module_name)

    for key, value in the_globals.iteritems():
        mod.__dict__[key] = value

    exec(module_code, mod.__dict__)
    sys.modules[mod.__name__] = mod

    if lastdot != -1:
        package.__dict__[module_element_name] = mod

    return mod


class FavaImporter(object):
    """ Hook into python's import machinery so standard import statements
        can be used for .fava files.
    """
    ext = ".fava"

    def __init__(self, path):
        path = os.path.realpath(path)
        if os.path.exists(path):
            # punt if we don't see any fava files in the path
            if not any(n.endswith(self.ext) for n in os.listdir(path)):
                raise ImportError()
            self.path = path
        else:
            raise ImportError()

    def find_module(self, fullname, paths=None):
        """ Returns a FavaLoader for fava files and a pkgutil.ImpLoader
            for standard python files. The ImpLoader is a PEP-302 wrapper
            for python's regular import machinery.
        """
        name = fullname.split(".")[-1]
        filename = os.path.join(self.path, name + self.ext)
        if os.path.exists(filename):
            return FavaLoader(filename)
        return pkgutil.ImpLoader(fullname, *imp.find_module(name, [self.path]))

    def iter_modules(self, prefix=''):
        """ Allows this importer to work with other pkgutil functions like
            walk_packages.
        """
        if self.path is None or not os.path.isdir(self.path):
            return

        yielded = {}
        import inspect
        try:
            filenames = os.listdir(self.path)
        except OSError:
            # ignore unreadable directories like import does
            filenames = []
        filenames.sort()  # handle packages before same-named modules

        for fn in filenames:
            modname = inspect.getmodulename(fn)
            if not modname and fn.endswith(self.ext):
                modname = fn.rpartition(".")[0]

            if modname == '__init__' or modname in yielded:
                continue

            path = os.path.join(self.path, fn)
            ispkg = False

            if not modname and os.path.isdir(path) and '.' not in fn:
                modname = fn
                try:
                    dircontents = os.listdir(path)
                except OSError:
                    # ignore unreadable directories like import does
                    dircontents = []
                for fn in dircontents:
                    subname = inspect.getmodulename(fn)
                    if not subname and fn.endswith(self.ext):
                        subname = fn.partition(".")[0]
                    if subname == '__init__':
                        ispkg = True
                        break
                else:
                    continue    # not a package

            if modname and '.' not in modname:
                yielded[modname] = 1
                yield prefix + modname, ispkg


class FavaLoader(object):
    def __init__(self, filename):
        self.filename = filename
        self.source = None
        self.favacode = None
        self.code = None

    def _refresh(self):
        self.source = self._get_source()
        self.favacode = self._compile_favacode(self.source)
        self.code = self._get_code(self.favacode)

    def _compile_favacode(self, source):
        return translate(FavaRule.yaml_deserialize(source))

    def is_package(fullname):
        return False

    def get_source(self, fullname=None):
        if self.source is None:
            return self._get_source()
        return self.source

    def _get_source(self):
        try:
            with open(self.filename, "rU") as f:
                return f.read()
        except Exception as ex:
            raise ImportError(str(ex))

    def get_code(self, fullname=None):
        if self.code is None:
            return self._get_code(self._get_source())
        return self.code

    def _get_code(self, favacode):
        try:
            the_ast = favacode.get_ast()
            return compile(the_ast, self.filename, "exec")
        except Exception as ex:
            raise ImportError(str(ex))

    def get_filename(self, path=None):
        return self.filename

    def load_module(self, fullname):
        already_exists = fullname in sys.modules
        if already_exists:
            mod = sys.modules[fullname]
        else:
            mod = imp.new_module(fullname)
            mod.__file__ = self.filename
            mod.__loader__ = self
            mod.__package__ = None
            sys.modules[fullname] = mod

        try:
            self._refresh()
            for k, v in self.favacode.get_globals().items():
                mod.__dict__[k] = v

            exec(self.code, mod.__dict__, mod.__dict__)
            return mod
        except Exception as ex:
            log.exception(ex)
            if already_exists:
                sys.modules[fullname] = mod
            raise ImportError(str(ex))


sys.path_hooks.append(FavaImporter)
