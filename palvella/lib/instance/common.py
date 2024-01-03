
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from jsonschema import validate as jsonschema_validate
from ruamel.yaml import YAML
import importlib_resources

from palvella.lib.plugin import Plugin, PluginDependency, WalkPlugins, match_class_dependencies
from palvella.lib.instance.hook import Hooks

from ..logging import makeLogger, logging


_logger = makeLogger(__name__)


@dataclass(unsafe_hash=True)
class ComponentObject:
    classref = None
    parent = None
    config_data = None
    error = None
    _instance = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
    def instance(self):
        if not self._instance:
            self._instance = self.classref(parent=self.parent, config_data=self.config_data)
        return self._instance


class ComponentObjects:
    """
    A class to manage the 'component objects', which are configuration of a component before instances of it are created.

    Attributes:
        parent:     The parent Instance() object.
        config:     A Config() object.
    """

    instances = []  # The list of instantiated objects

    _config_objects = []  # The list of ComponentObject()s
    _all_objects = []  # The list of ComponentObject()s
    _logger = makeLogger(__module__ + "/ComponentObjects")

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self._config_objects = self.component_ns_config_objects(self.config.data)
        self._all_objects = self.all_component_topo_objects(self._config_objects)

    async def initialize(self):
        async for x in self.create_instances(self._all_objects):
            self.instances.append(x)

    async def create_instances(self, objects):
        for x in objects:
            instance = x.instance()
            yield instance

    def all_component_topo_objects(self, objects):
        """Retrieve a set of ComponentObject()s based on topological sort of plugin graph.

        The intent is to load plugins that have no configuration, as well as load plugins
        that do have configuration, but to load them all according to the topological
        graph of plugin dependencies.

        Gets a topological list of all plugins from `self.parent.plugins.topo_sort()`
        that have attribute `class_type` value "plugin", and iterate over the list.

        If a component object exists matching a plugin class, creates a new object
        matching that plugin class.

        Otherwise if a plugin has no matching component object, creates a new instance
        without any configuration.

        Parameters
        ---------
        objects
            A list of ComponentObject()s. These should be the objects that were created
            during parsing of configuration.

        Returns
        -------
        list
            A list of ComponentObject()s.
        """

        ret_objects = []

        # Get all plugin classes, sorted topologically
        plugin_class_topo = [x for x in self.parent.plugins.topo_sort() if (x.class_type == "plugin")]

        for plugin_class in plugin_class_topo:

            # Get any component objects we created for this plugin class, based on config data
            component_objects = [x for x in objects if x.classref == plugin_class]

            # If any were found, process them
            if len(component_objects) > 0:
                for obj in component_objects:
                    self._logger.debug(f"Loading new component from object: {obj.classref}")
                    ret_objects.append(
                        ComponentObject(classref=obj.classref, parent=self.parent, config_data=obj.config_data)
                    )
            # Otherwise create new objects with no configuration
            else:
                self._logger.debug(f"Loading new component {plugin_class}")
                ret_objects.append(
                    ComponentObject(classref=plugin_class, parent=self.parent)
                )

        return ret_objects

    def component_ns_config_objects(self, data):
        """
        Parse `data` and return a list of ComponentObject()s.

        For each key:value (in the root of `data`) look for a key that matches the
        'component_namespace' of a loaded plugin (of subclass_type 'plugin_base').

        For each of those, method `validate_config_schema()` is run against the `misc_data`
        value, and a new ComponentObject() is created based on `misc_data`.

        Parameters
        ----------
        data
            A dict of the following format:
            
                component_namespace:
                    misc_data
            
            The `component_namespace` must be a subclass in `self.parent.subclasses`
            whose attribute `class_type` is "plugin_base" and attribute
            `component_namespace` is the same as `component_namespace` above.

            The `misc_data` entry is defined by the function `plugin_base_config_objects()`
            which may be overloaded by the plugin class.

        Returns
        -------
        list
            A list of ComponentObject()s.
        """
        objects = []
        subclasses = self.parent.subclasses

        for component_namespace, datarootval in data.items():

            plugin_base = [x for x in subclasses
                             if x.class_type == "plugin_base" \
                             and x.component_namespace == component_namespace]
            if len(plugin_base) < 1:
                self._logger.debug(f"could not find plugin base for '{component_namespace}'")
                continue
            elif len(plugin_base) > 1:
                self._logger.debug(f"too many plugin bases for '{component_namespace}'")
                continue

            # Validate schema
            plugin_base[0].validate_config_schema(datarootval)

            # Allow the base plugin component to override the 'plugin_base_config_objects'
            # method (if for example it wants a different configuration format).
            for newobj in plugin_base[0].plugin_base_config_objects(plugin_base[0], datarootval):
                objects.append(newobj)

        return objects

    def plugin_base_config_objects(self, data):
        """Parse the configuration and return ComponentObject()s.

        Parses `data` for plugins whose parent class is `self` and plugin type
        matches `data` dict's `plugin_type` value (see below).

        Parameters
        ---------
        data
            A dict of the following format (shown as YAML):
                plugin_type:
                    - item1
                    - item2

        Returns
        -------
        list
            A list of ComponentObject()s, with their `classref` and `config_data`
            attributes set.
        """

        _logger.debug(f"self {self}")
        for plugin_type, config_data in data.items():
            assert (type(config_data) == type([])), f"Configuration entries for '{plugin_type}' must be in list format"
            _logger.debug(f"plugin_type {plugin_type} config_data {config_data}")
            dep = PluginDependency(parentclassname=self.__name__, plugin_type=plugin_type)
            #dep = PluginDependency(parentclassname=self.__class__.__name__, plugin_type=plugin_type)
            for plugin_class in match_class_dependencies(self, self.__subclasses__(), [dep]):
                for item in config_data:
                    _logger.debug(f"yielding new component object ({plugin_class})")
                    yield ComponentObject(classref=plugin_class, config_data=item)


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    _config_path = None

    def __init__(self, parent, config_path):
        """Initialize new configuration.

        Arguments:
            parent:         A reference to the parent Instance() object
            config_path:    A path to a YAML file to load configuration from.
        """
        self.parent = parent
        self.config_path = config_path
        self.load_config()

    def load_config(self, config_path=None):
        config_path = config_path if config_path != None else self.config_path
        self.data = self.loadYamlFile(file=config_path)

    def loadYamlFile(self, file):
        """Load configuration, parse it, and return the result."""
        with open(file, "r", encoding="utf-8") as f:
            yaml = YAML(typ='safe')
            return yaml.load(f)
        raise ValueError("No configuration provided")


class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application."""

    plugin_namespace = "palvella.lib.instance"

    hooks = None
    plugins = None
    components = None
    config = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hooks = Hooks(parent=self)

        # Load plugin subclasses from the 'Component' class
        self.plugins = WalkPlugins(Component)

        if hasattr(self, 'config_path'):
            self.config = Config(parent=self, config_path=self.config_path)

    async def initialize(self):
        """Initialize the new instance."""
        if self.config:
            self.components = ComponentObjects(parent=self, config=self.config)
            await self.components.initialize()


class Component(Plugin, class_type="base"):
    """A class to create Instance Components from.

    If an object inheriting this class has a function '__pre_plugins__',
    that function will be run at the end of '__init__' in this object.

    Attributes:
        name:                   The name of the particular instance of this component.
        plugin_namespace:       The namespace for this plugin module.
        component_namespace:    The namespace for configuration files relevant to this plugin.
        config_data:            A dict of configuration data for this instance of this component.
        schema:                 A pointer to a schema to validate the configuration with.
    """

    # The name of 'Component's plugin namespace. Each component needs to overload this.
    # TODO: maybe move this to the outer file itself and not in the classes?
    plugin_namespace = "palvella.lib.instance"

    #component_namespace = "instance"
    config_data = {}  # Each component gets an empty config_data by default
    schema = True
    _pre_plugins_ref_name = "__pre_plugins__"
    name = None

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Arguments:
            parent: A reference to the parent Instance() object
            config_data: A dict of key=value pairs loaded from Config.parse().
        """
        super().__init__(**kwargs)

        # For each module, load a 'config.yaml' file if one exists, to fill in
        # default configuration data. Configuration data passed to the object in
        # the 'config_data' attribute will overload this.

        for fname in [self.component_namespace + ".yaml", 'config.yaml']:
            config_yaml_file = importlib_resources.files(self.__module__).joinpath(fname)
            with importlib_resources.as_file(config_yaml_file) as filename:
                if Path(filename).exists():
                    with open(filename, "r", encoding="utf-8") as fd:
                        self._config_data_defaults = YAML(typ='safe').load(fd)

        if hasattr(self, '_config_data_defaults') and self._config_data_defaults != None:
            for k, v in self._config_data_defaults.items():
                if not k in self.config_data:
                    self.config_data[k] = v

        # Run the '_pre_plugins_ref_name' function if it was defined by a subclass
        if self._pre_plugins_ref_name != None and hasattr(self, self._pre_plugins_ref_name):
            if callable(getattr(self, self._pre_plugins_ref_name)):
                getattr(self, self._pre_plugins_ref_name)()

    @classmethod
    def validate_config_schema(cls, data):
        """
        Validate the configuration schema for a component.

        The 'schema' attribute of the class should be filled in automatically when the component
        is first loaded, based on the default configuration of the component (if it defines a schema).
        This function exists in the Component class so the component class can override
        this validation if needed.

        TODO: Document where/how to encode the schema.
        """
        jsonschema_validate(data, cls.schema)

    @staticmethod
    def plugin_base_config_objects(self, data):
        self.__doc__ = ComponentObjects.plugin_base_config_objects.__doc__
        return ComponentObjects.plugin_base_config_objects(self, data)

    def get_component(self, dep):
        """
        Pass a PluginDependency() and this function will return all of the
        matching instances of components.

        This is used by plugins to find an instance of another plugin that they
        may need to interact with, attach a hook to, etc.
        """
        results = match_class_dependencies(self, self.parent.components.instances, [dep])
        return results
