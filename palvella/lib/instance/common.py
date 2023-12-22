
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from jsonschema import validate as jsonschema_validate
from ruamel.yaml import YAML
import importlib_resources

from palvella.lib.plugin import Plugin, PluginDependency, WalkPlugins, match_class_dependencies

from ..logging import makeLogger, logging


_logger = makeLogger(__name__)


@dataclass
class ComponentHook:
    component = None
    hook_type = None
    hook = None
    match_data = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class ComponentHooks:
    """
    Manages hooks for components.

    Attributes:
        parent:         A reference to the parent Instance() object.
    """

    _hooks = []

    def __init__(self, parent):
        self.parent = parent

    def list(self):
        return self._hooks

    def register_hook(self, component_ns, plugin_type, hook_type, hook, match_data):
        """Run from a component, adds a hook for a particular function based on specific event type and data."""
        _logger.debug(f"register_hook({self}, {component_ns}, {plugin_type}, {hook_type}, {hook}, {match_data})")

        dep = PluginDependency(component_namespace=component_ns, plugin_type=plugin_type)
        _logger.debug(f"self {self} plugins {self.parent.plugins} dep {dep}")

        components = match_class_dependencies(self, self.parent.plugins.classes, [dep])
        for component in components:
            self._hooks.append(ComponentHook(component=component, hook_type=hook_type, hook=hook, match_data=match_data))

    def match_hook(self, msg):
        for hook in self.parent.hooks.list():
            for instance in self.parent.components.instances:
                if hook.component.plugin_namespace != instance.plugin_namespace \
                   or hook.component.plugin_type != instance.plugin_type:
                    continue
                _logger.debug(f"Found instance {instance} matches component {hook.component}")
                if not self.match_hook_data(hook=hook, component_instance=instance, msg=msg):
                    continue
                _logger.debug(f"Hook matched, triggering")
                # TODO: once the above works, implement 'trigger_hook' below
                yield hook

    def match_hook_data(self, hook, component_instance, msg):
        # TODO: implement some logic that looks at the message received,
        #       matches it up against the hook's expected data, and returns
        #       true if the hook matches, false if it doesn't
        _logger.debug(f"msg {msg}")

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
        self._config_objects = self.load_config_objects()
        self._all_objects = self.load_topo_objects(self._config_objects)

    async def initialize(self):
        async for x in self.create_instances(self._all_objects):
            self.instances.append(x)

    async def create_instances(self, objects):
        for x in objects:
            instance = x.instance()
            yield instance

    def get_by_class(self, classref):
        for x in self._objects:
            if x.classref == classref:
                yield x

    def load_topo_objects(self, config_objects):
        """
        Walks the graph of all plugins of class_type 'plugin', sorted topologically 
        (to handle dependencies first) and creates a list of objects to make instances of.
        """
        objects = []
        # Get all classes
        plugin_class_topo = [x for x in self.parent.plugins.topo_sort() if (x.class_type == "plugin")]
        for cls in plugin_class_topo:
            # Get component objects based on class
            component_objects = [x for x in config_objects if x.classref == cls]
            # Process the component objects that exist
            if len(component_objects) > 0:
                for obj in component_objects:
                    self._logger.debug(f"Loading new component from object: {obj.classref}")
                    objects.append(
                        ComponentObject(classref=obj.classref, parent=self.parent, config_data=obj.config_data)
                    )
            # Otherwise create based on class, not component object
            else:
                self._logger.debug(f"Loading new component {cls}")
                objects.append(
                    ComponentObject(classref=cls, parent=self.parent)
                )
        return objects

    def load_config_objects(self):
        """
        Parse configuration data and set an internal list of ComponentObject()s.

        For each key:value (in the root of 'self.data'),
            look for a key that matches the 'component_namespace'
            of a loaded plugin (of subclass_type 'plugin_base').

        For each of those, have the class of the plugin validate its own configuration
        and return objects as needed.
        Set self._objects to the resulting set of objects.
        """
        objects = []
        subclasses = self.parent.subclasses

        for component_namespace, datarootval in self.config.data.items():

            plugin_base = [x for x in subclasses if x.class_type == "plugin_base" \
                           and x.component_namespace == component_namespace]
            if len(plugin_base) < 1:
                self._logger.debug(f"could not find plugin base for '{component_namespace}'")
                continue
            elif len(plugin_base) > 1:
                self._logger.debug(f"too many plugin bases for '{component_namespace}'")
                continue

            # Validate schema
            plugin_base[0].validate_config_schema(datarootval)

            # Allow the base plugin component to override this method
            for newobj in plugin_base[0].plugin_base_config_objects(plugin_base[0], datarootval):
                objects.append(newobj)

        return objects

    def plugin_base_config_objects(self, data):
        """
        Parse the configuration for a 'plugin_base' and return component objects based on it.

        This class method is used to parse a chunk of configuration for a given 'plugin_base'
        and return the ComponentObject()s that will turn into new instances of components.

        Most 'plugin_base' data follows this format:
            plugin_base_name:
                plugin_type_name:
                    - item1
                    - item2

        The intent being to return:
            ComponentObject(classref=class_of_plugin_type_name, config_data=[item1])
            ComponentObject(classref=class_of_plugin_type_name, config_data=[item2])

        However, some 'plugin_base' may use a different configuration format. Those
        'plugin_base' can override this method and return objects however they prefer.
        """
        for plugin_type, config_data in data.items():
            assert (type(config_data) == type([])), f"Configuration entries for '{plugin_type}' must be in list format"
            dep = PluginDependency(parentclassname=self.__name__, plugin_type=plugin_type)
            import sys; print(f"self {self}", file=sys.stderr)
            _logger.debug(f"plugin_type {plugin_type} config_data {config_data}")
            _logger.debug(f"dep {dep}")
            for x in match_class_dependencies(self, self.__subclasses__(), [dep]):
                for entry in config_data:
                    _logger.debug(f"yielding new component object")
                    yield ComponentObject(classref=x, config_data=entry)


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

        self.hooks = ComponentHooks(parent=self)

        # Load plugin subclasses from the 'Component' class
        self.plugins = WalkPlugins(Component)

        if hasattr(self, 'config_path'):
            self.config = Config(parent=self, config_path=self.config_path)

        self.initialize()

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
        """
        jsonschema_validate(data, cls.schema)

    def plugin_base_config_objects(self, data):
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
