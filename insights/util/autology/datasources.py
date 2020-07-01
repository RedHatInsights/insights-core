"""
datasources - Provides introspection functionality for datasources in insights-core

This module provides classes to provide introspection for each of the datasource
definition classes in the :py:mod`insights.specs` package.
"""
import inspect
import insights.core.spec_factory
import insights.specs
from insights.specs.default import DefaultSpecs as InDefaultSpecs
from insights.specs.insights_archive import InsightsArchiveSpecs as InArchiveSpecs
from insights.specs.sos_archive import SosSpecs as InSosSpecs
from . import AutologyError


SIMPLE_COMMAND_TYPE = 'simple_command'
""" str: Literal constant for a simple_comment Spec object """
SIMPLE_FILE_TYPE = 'simple_file'
""" str: Literal constant for a simple_file Spec object """
GLOB_FILE_TYPE = 'glob_file'
""" str: Literal constant for a simple_file Spec object """
FOREACH_EXECUTE_TYPE = 'foreach_execute'
""" str: Literal constant for a foreach_execute Spec object """
LISTDIR_TYPE = 'listdir'
""" str: Literal constant for a listdir Spec object """
LIST_TYPE = 'list'
""" str: Literal constant for a list Spec object """
STRING_TYPE = 'string'
""" str: Literal constant for a string Spec object """
NONE_TYPE = 'none'
""" str: Literal constant for a Spec object with None type """
FUNCTION_TYPE = 'function'
""" str: Literal constant for a function Spec object """
FIRST_FILE_TYPE = 'first_file'
""" str: Literal constant for a first_file Spec object """
FOREACH_COLLECT_TYPE = 'foreach_collect'
""" str: Literal constant for a foreach_collect Spec object """
FIRST_OF_TYPE = 'first_of'
""" str: Literal constant for a first_of Spec object """
COMMAND_WITH_ARGS_TYPE = 'command_with_args'
""" str: Literal constant for a command_with_args Spec object """
HEAD_TYPE = 'head'
""" str: Literal constant used for a head Spec object """
UNKNOWN_TYPE = 'unknown'
""" str: Literal constant for a Spec object with unknown type """
ANONYMOUS_SPEC_NAME = 'anonymous'
""" str: Literal constant used for Specs with no ``name`` attribute """


def is_simple_command(m_obj):
    """ bool: True if broker object is a simple_command object """
    return isinstance(m_obj, insights.core.spec_factory.simple_command)


def is_simple_file(m_obj):
    """ bool: True if broker object is a simple_file object """
    return isinstance(m_obj, insights.core.spec_factory.simple_file)


def is_glob_file(m_obj):
    """ bool: True if broker object is a glob_file object """
    return isinstance(m_obj, insights.core.spec_factory.glob_file)


def is_foreach_execute(m_obj):
    """ bool: True if broker object is a foreach_execute object """
    return isinstance(m_obj, insights.core.spec_factory.foreach_execute)


def is_first_file(m_obj):
    """ bool: True if broker object is a first_file object """
    return isinstance(m_obj, insights.core.spec_factory.first_file)


def is_first_of(m_obj):
    """ bool: True if broker object is a is_first_of object """
    return isinstance(m_obj, insights.core.spec_factory.first_of)


def is_foreach_collect(m_obj):
    """ bool: True if broker object is a is_foreach_collect object """
    return isinstance(m_obj, insights.core.spec_factory.foreach_collect)


def is_listdir(m_obj):
    """ bool: True if broker object is a is_listdir object """
    return isinstance(m_obj, insights.core.spec_factory.listdir)


def is_command_with_args(m_obj):
    """ bool: True if broker object is a is_command_with_args object """
    return isinstance(m_obj, insights.core.spec_factory.command_with_args)


def is_head(m_obj):
    """ bool: True if object is a head object """
    return isinstance(m_obj, insights.core.spec_factory.head)


def is_function(m_obj):
    """ bool: True if object is a function object """
    return inspect.isfunction(m_obj)


class Spec(dict):
    """
    Class to identify and describe datasources and related objects

    The normal way to create one of these objects is to use the factory
    method :py:meth:`from_object` and provide as input one of the datasource
    objects from :py:mod:`insights.core.spec_factory`.  This class is implemented
    as a dictionary and all attributes of the object are stored as dictionary keys.
    A ``repr`` string must be included in ``kwargs`` to __init__ and it will be
    removed and stored in the ``repr_str`` attribute.  If a ``name`` attributed
    is not provided, a default name of ``anonymous`` will be used.  This is a special
    name recognized when formatting Spec output to be used when specs have other
    specs as providers/dependents.

    Attributes:
        repr_str (str): String to be used to implement the __repr__ method for this object
            Supports jinja2 formatting using dictionary attributes of this object
        self (dict): All attributes of this object are included in the dictionary except
            the repr string.

    Raises:
        AutologyError: Raised if a ``repr`` string is not provided or if an unsupported
            object type is passed to the constructor or to the factory method.
    """
    def __init__(self, **kwargs):
        super(Spec, self).__init__(kwargs)
        try:
            self.repr_str = self.pop('repr')
        except KeyError:
            raise AutologyError('A repr items must be supplied for the spec name: {}'.format(self.get('name', 'no name')))

        if 'name' not in self:
            self['name'] = ANONYMOUS_SPEC_NAME

    def __repr__(self):
        try:
            formatted_str = self.repr_str.format(**self)
        except KeyError:
            if '{name} =' in self.repr_str:
                _, r = self.repr_str.split('{name} =')
                fixed = r.replace('{', '{{').replace('}', '}}')
                formatted_str = (''.join(['{name} =', fixed])).format(**self)
            else:
                formatted_str = self.repr_str.replace('{', '{{').replace('}', '}}').format(**self)
        return formatted_str

    @classmethod
    def from_object(cls, m_type, m_name=ANONYMOUS_SPEC_NAME):
        """
        Factory method to create Spec objects

        This method evaluates the m_type object type and extract the Spec
        attributes based on that type.

        Attributes:
            m_type (obj): One of the datasource objects from :py:mod:`insights.core.spec_factory`.
            m_name (str): Name of the datasource object, if not provided ``ANONYMOUS_SPEC_NAME``

        Raises:
            AutologyError: Raises this error if it cannot determine the object type

        Returns:
            Spec: Returns an object of type `Spec`
        """
        m_members = inspect.getmembers(m_type)
        m_spec = {'name': m_name, 'type': m_type}
        m_spec['kind'] = next((v for k, v in m_members if k == "kind"), None)
        m_spec['context'] = next((v for k, v in m_members if k == "context"), None)
        m_spec['multi_output'] = next((v for k, v in m_members if k == "multi_output"), None)
        if is_simple_command(m_type):
            m_spec['type_name'] = SIMPLE_COMMAND_TYPE
            m_spec['cmd'] = next((v for k, v in m_members if k == "cmd"), None)
            m_spec['repr'] = 'simple_command("{cmd}")'

        elif is_simple_file(m_type):
            m_spec['type_name'] = SIMPLE_FILE_TYPE
            m_spec['path'] = next((v for k, v in m_members if k == "path"), None)
            m_spec['repr'] = 'simple_file("{path}")'

        elif is_glob_file(m_type):
            m_spec['type_name'] = GLOB_FILE_TYPE
            m_spec['patterns'] = next((v for k, v in m_members if k == "patterns"), None)
            m_spec['repr'] = 'glob_file({patterns})'

        elif is_first_file(m_type):
            m_spec['type_name'] = FIRST_FILE_TYPE
            m_spec['paths'] = next((v for k, v in m_members if k == "paths"), None)
            m_spec['repr'] = 'first_file({paths})'

        elif is_listdir(m_type):
            m_spec['type_name'] = LISTDIR_TYPE
            m_spec['path'] = next((v for k, v in m_members if k == 'path'), None)
            m_spec['repr'] = 'listdir("{path}")'

        elif is_foreach_execute(m_type):
            m_spec['cmd'] = next((v for k, v in m_members if k == "cmd"), None)
            m_spec['type_name'] = FOREACH_EXECUTE_TYPE
            provider = next((v for k, v in m_members if k == "provider"), None)
            if provider:
                m_spec['provider'] = cls.from_object(provider)

            else:
                m_spec['provider'] = Spec(
                    name=ANONYMOUS_SPEC_NAME,
                    type=None,
                    type_name=NONE_TYPE,
                    repr='NONE PROVIDER')

            m_spec['repr'] = 'foreach_execute("{cmd}", provider={provider})'

        elif is_first_of(m_type):
            m_spec['type_name'] = FIRST_OF_TYPE
            deps = next((v for k, v in m_members if k == "deps"), None)
            m_spec['deps'] = [cls.from_object(d) for d in deps]
            deps_repr = ', '.join(['{0}'.format(d) for d in m_spec['deps']])
            m_spec['repr'] = 'first_of([{0}])'.format(deps_repr)

        elif is_command_with_args(m_type):
            m_spec['type_name'] = COMMAND_WITH_ARGS_TYPE
            m_spec['cmd'] = next((v for k, v in m_members if k == "cmd"), None)
            provider = next((v for k, v in m_members if k == "provider"), None)
            if provider:
                m_spec['provider'] = cls.from_object(provider)
            m_spec['repr'] = 'command_with_args("{cmd}", provider={provider})'

        elif is_foreach_collect(m_type):
            m_spec['type_name'] = FOREACH_COLLECT_TYPE
            m_spec['path'] = next((v for k, v in m_members if k == 'path'), None)
            provider = next((v for k, v in m_members if k == "provider"), None)
            if provider:
                m_spec['provider'] = cls.from_object(provider)
            m_spec['repr'] = 'foreach_collect("{path}", provider={provider})'

        elif is_head(m_type):
            m_spec['type_name'] = HEAD_TYPE
            dep = next((v for k, v in m_members if k == "dep"), None)
            m_spec['dep'] = cls.from_object(dep)
            m_spec['repr'] = 'head({0})'.format(m_spec['dep'])

        elif m_type is None:
            m_spec['type_name'] = NONE_TYPE
            m_spec['repr'] = 'NONE TYPE'

        elif inspect.isfunction(m_type):
            m_spec['type_name'] = FUNCTION_TYPE
            f_members = inspect.getmembers(m_type)
            m_spec['fxn_name'] = next((v for k, v in f_members if k == '__name__'), 'function')
            m_spec['source'] = inspect.getsource(m_type)
            m_spec['repr'] = '{fxn_name}()'

        elif isinstance(m_type, list):
            m_spec['type_name'] = LIST_TYPE
            m_spec['list'] = m_type
            m_spec['repr'] = '{list}'

        elif isinstance(m_type, str):
            m_spec['type_name'] = STRING_TYPE
            m_spec['string'] = m_type
            m_spec['repr'] = '{string}'

        else:
            raise AutologyError('Unsupported name {} object {}, please add it'.format(m_name, m_type))

        m_spec['repr'] = ''.join(['{name} = ', m_spec['repr']]) if m_name != ANONYMOUS_SPEC_NAME else m_spec['repr']

        return cls(**m_spec)

    @property
    def is_simple_command(self):
        """ bool: True if this spec is a simple_command """
        return self.get('type_name', UNKNOWN_TYPE) == SIMPLE_COMMAND_TYPE

    @property
    def is_simple_file(self):
        """ bool: True if this spec is a simple_file """
        return self.get('type_name', UNKNOWN_TYPE) == SIMPLE_FILE_TYPE

    @property
    def is_glob_file(self):
        """ bool: True if this spec is a glob_file """
        return self.get('type_name', UNKNOWN_TYPE) == GLOB_FILE_TYPE

    @property
    def is_foreach_execute(self):
        """ bool: True if this spec is a foreach_execute """
        return self.get('type_name', UNKNOWN_TYPE) == FOREACH_EXECUTE_TYPE

    @property
    def is_first_file(self):
        """ bool: True if this spec is a first_file """
        return self.get('type_name', UNKNOWN_TYPE) == FIRST_FILE_TYPE

    @property
    def is_first_of(self):
        """ bool: True if this spec is a first_of """
        return self.get('type_name', UNKNOWN_TYPE) == FIRST_OF_TYPE

    @property
    def is_foreach_collect(self):
        """ bool: True if this spec is a foreach_collect """
        return self.get('type_name', UNKNOWN_TYPE) == FOREACH_COLLECT_TYPE

    @property
    def is_listdir(self):
        """ bool: True if this spec is a listdir """
        return self.get('type_name', UNKNOWN_TYPE) == LISTDIR_TYPE

    @property
    def is_command_with_args(self):
        """ bool: True if this spec is a command_with_args """
        return self.get('type_name', UNKNOWN_TYPE) == COMMAND_WITH_ARGS_TYPE

    @property
    def is_head(self):
        """ bool: True if this spec is a head """
        return self.get('type_name', UNKNOWN_TYPE) == HEAD_TYPE

    @property
    def is_function(self):
        """ bool: True if this spec is a function """
        return self.get('type_name', UNKNOWN_TYPE) == FUNCTION_TYPE

    @property
    def is_unknown_type(self):
        """ bool: True if this spec has an unknown type """
        return self.get('type_name', UNKNOWN_TYPE) == UNKNOWN_TYPE


class RegistrySpecs(dict):
    """
    Class to provide introspection for Registry objects in :py:class:`insights.specs.Specs`

    Dictionary of `Spec` objects with spec names as the keys and a Spec object as each value.
    Each value has the set of attributes::

        name - Name of the spec
        type - The spec object
        filterable - Whether or not the Registry object is ``filterable``
        multi_output - Whether or not the Registry object is ``multi_output``
        raw - Whether or not the Registry object is ``raw``
    """
    REGISTRY_REPR = '{name} = RegistryPoint(filterable={filterable}, multi_output={multi_output}, raw={raw})'
    """ str: repr string for all Registry objects """

    def __init__(self):
        members = inspect.getmembers(insights.specs.Specs)
        for m_name, m_type in members:
            if m_name.startswith('__') or m_name == 'context_handlers':
                # Don't care about dunder members or context handlers
                continue

            m_members = inspect.getmembers(m_type)
            self.update({
                m_name: Spec(
                    name=m_name,
                    type=m_type,
                    filterable=next((v for k, v in m_members if k == 'filterable'), None),
                    multi_output=next((v for k, v in m_members if k == 'multi_output'), None),
                    raw=next((v for k, v in m_members if k == 'raw'), None),
                    repr=self.REGISTRY_REPR
                )
            })

    def is_registered(self, spec_name):
        """ bool: Whether ``spec_name`` is in Registry specs. """
        return spec_name in self


class DefaultSpecs(dict):
    """
    Class to provide introspection for datasource objects in :py:class:`insights.specs.default.DefaultSpecs`

    Dictionary of `Spec` objects with spec names as the keys and a Spec object as each value.
    Each Spec has different attributes depending on the type of spec.  See the
    :py:meth:`Spec.from_object` factory method for more information.

    """
    _SPECS_OBJECT_CLASS = InDefaultSpecs
    """ obj: Datasource class to use for introspection """

    def __init__(self):
        for m_name, m_type in inspect.getmembers(self._SPECS_OBJECT_CLASS):
            if (m_name.startswith('__') or m_name == 'context_handlers' or
                    m_name == 'registry' or str(m_type).startswith('insights.specs.Spec')):
                # Don't care about dunder members or context handlers
                # or registry entries
                continue

            m_spec = Spec.from_object(m_type, m_name)
            self.update({m_name: m_spec})


class InsightsArchiveSpecs(DefaultSpecs):
    """
    Class to provide introspection for datasource objects in
    :py:class:`insights.specs.insights_archive.InsightsArchiveSpecs`

    Dictionary of `Spec` objects with spec names as the keys and a Spec object as each value.
    Each Spec has different attributes depending on the type of spec.  See the
    :py:meth:`Spec.from_object` factory method for more information.

    """
    _SPECS_OBJECT_CLASS = InArchiveSpecs
    """ obj: Datasource class to use for introspection """

    pass


class SosSpecs(DefaultSpecs):
    """
    Class to provide introspection for datasource objects in :py:class:`insights.specs.sos_archive.SosSpecs`

    Dictionary of `Spec` objects with spec names as the keys and a Spec object as each value.
    Each Spec has different attributes depending on the type of spec.  See the
    :py:meth:`Spec.from_object` factory method for more information.

    """
    _SPECS_OBJECT_CLASS = InSosSpecs
    """ obj: Datasource class to use for introspection """

    pass

if __name__ == "__main__":
    specs = DefaultSpecs()
    for k, v in specs.items():
        try:
            print(v)
        except Exception as e:
            print('======= Error with spec: ', k)
            print('repr_str :', v.repr_str)
            for dk, dv in v.items():
                print('\t', dk, ":", dv)
            raise
