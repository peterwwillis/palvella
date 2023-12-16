
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from jsonschema import validate as jsonschema_validate
from ruamel.yaml import YAML
import importlib_resources

from palvella.lib.plugin import Plugin, PluginDependency, match_class_dependencies

from ..logging import makeLogger, logging




class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application."""

    plugin_namespace = "palvella.lib.instance"
    _components = []  # The list of instantiated objects of each plugin

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load plugin subclasses from the 'Component' class
        self.walk_plugins_args = { 'baseclass': Component }

        if hasattr(self, 'config_path'):
            self.config = Config(parent=self, config_path=self.config_path)
        if self.config:
            self.initialize()

    def initialize(self):
        """Initialize the new instance."""
        self.load_components()

    @property
    def components(self):
        return self._components
    @components.setter
    def components(self, val):
        self._components = val

    def load_components(self):
        """Instantiate new Component objects and append them (in real time) to self.components.

           Walks the graph of all plugins of class_type 'plugin', sorted topologically 
           (to handle dependencies first).

           If there's a 'self.config.data_objects' entry for a given plugin, uses those
           'data_objects' configuration to create a new instance of that plugin.

           If no entry in 'data_objects', just creates a new instance of that plugin with
           no configuration.

           Each new object instance created is immediately appended to 'self.components',
           so that the next component being added may look for previously created ones
           (that they may depend on).
        """
        plugin_class_topo = [x for x in self.plugins.topo_sort() if (x.class_type == "plugin")]
        for cls in plugin_class_topo:
            data_objects = [x for x in self.config.data_objects.get_by_class(cls)]
            # If there's plugin classes that have configured data objects:
            if len(data_objects) > 0:
                for obj in data_objects:
                    self._logger.debug(f"Loading new component {obj.classref} from data_objects")
                    self.components.append(obj.classref(parent=self, config_data=obj.config_data))
            # Otherwise just create an object for this class with no configuration
            else:
                self._logger.debug(f"Loading new component {cls}")
                self.components.append(cls(parent=self))

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, arg):
        self._config = arg


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


    _logger = makeLogger(__module__ + "/Config")

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

    def get_component(self, dep):
        results = match_class_dependencies(self, self.parent.components, [dep])
        return results

    @classmethod
    def validate_config_schema(cls, data):
        """
        Validate the configuration schema for a component.

        The 'schema' attribute of the class should be filled in automatically when the component
        is first loaded, based on the default configuration of the component (if it defines a schema).
        This function exists in the Component class so the component class can override
        this validation if needed.
        """
        jsonschema_validate(data, cls.schema)

    @classmethod
    def plugin_base_config_objects(cls, data):
        """
        Parse the configuration for a 'plugin_base' and return component objects based on it.

        This class method is used to parse a chunk of configuration for a given 'plugin_base'
        and return the ConfigDataObject()s that will turn into new instances of components.

        Most 'plugin_base' configuration follows this format:
            plugin_base_name:
                plugin_type_name:
                    - item1
                    - item2

        The intent being to return:
            ConfigDataObject(classref=class_of_plugin_type_name, config_data=[item1])
            ConfigDataObject(classref=class_of_plugin_type_name, config_data=[item2])

        However, some 'plugin_base' may use a different configuration format. Those
        'plugin_base' can override this method and return objects however they prefer.
        """
        for plugin_type, config_data in data.items():
            assert (type(config_data) == type([])), f"Configuration entries for '{plugin_type}' must be in list format"
            dep = PluginDependency(parentclassname=cls.__name__, plugin_type=plugin_type)
            for x in match_class_dependencies(cls, cls.__subclasses__(), [dep]):
                for entry in config_data:
                    yield ConfigDataObject(classref=x, config_data=entry)


@dataclass(unsafe_hash=True)
class ConfigDataObject:
    classref = None
    config_data = None
    error = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return (f"ConfigDataObject("
                f"classref={self.classref},config_data={self.config_data}"
                f",error={self.error})")


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    _logger = makeLogger(__module__ + "/Config")
    _config_path = None


    class DataObjects:

        _objects = None

        def __init__(self, configobj):
            self.data_objects = configobj

        def get_by_class(self, classref):
            for x in self.data_objects:
                if x.classref == classref:
                    yield x

        @property
        def data_objects(self):
            return self._objects

        @data_objects.setter
        def data_objects(self, configobj):
            """
            Parse configuration data and set an internal list of ConfigDataObject()s.

            For each key:value (in the root of 'self.data'),
                look for a key that matches the 'component_namespace'
                of a loaded plugin (of subclass_type 'plugin_base').

            For each of those, have the class of the plugin validate its own configuration
            and return objects as needed.
            Set self._objects to the resulting set of objects.
            """
            objects = []
            configobj.parent.plugins  # Load plugins to get subclasses
            subclasses = configobj.parent.subclasses

            for component_namespace, datarootval in configobj.data.items():

                plugin_base = [x for x in subclasses if x.class_type == "plugin_base" \
                               and x.component_namespace == component_namespace]
                if len(plugin_base) < 1:
                    Config._logger.debug(f"could not find plugin base for '{component_namespace}'")
                    continue
                elif len(plugin_base) > 1:
                    Config._logger.debug(f"too many plugin bases for '{component_namespace}'")
                    continue

                plugin_base[0].validate_config_schema(datarootval)
                objects.extend( plugin_base[0].plugin_base_config_objects(datarootval) )

            self._objects = objects

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            parent: A reference to the parent Instance() object
            load: A string which points at a YAML configuration file to load().
        """
        self.__dict__.update(kwargs)
        self.load_config()

    def load_config(self, config_path=None):
        config_path = self.config_path if self.config_path else config_path
        if config_path:
            self.data = self.loadYamlFile(file=self.config_path)
        if self.data:
            self.data_objects = self.DataObjects(self)

    def loadYamlFile(self, file):
        """Load configuration, parse it, and return the result."""
        with open(file, "r", encoding="utf-8") as f:
            yaml = YAML(typ='safe')
            return yaml.load(f)
        raise ValueError("No configuration provided")

