
import importlib_resources
from pathlib import Path
from dataclasses import dataclass

from jsonschema import validate as jsonschema_validate

from palvella.lib.instance.config import ConfigData, loadYamlFile
from palvella.lib.plugin import match_class_dependencies, PluginDependency, Plugin
from ..logging import makeLogger, logging


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
    config_data = ConfigData()  # Each component gets an empty config_data by default
    schema = True
    _pre_plugins_ref_name = "__pre_plugins__"
    name = None

    def __init__(self, **kwargs):
        """
        Initialize the new Component object.

        Parameters
        ----------
        parent
            A reference to the parent Instance() object
        config_data
            A dict of key=value pairs loaded from Config.parse().
        """
        super().__init__(**kwargs)

        # For each module, load a 'config.yaml' file if one exists, to fill in
        # default configuration data. Configuration data passed to the object in
        # the 'config_data' attribute will overload this.

        for fname in [self.component_namespace + ".yaml", 'config.yaml']:
            config_yaml_file = importlib_resources.files(self.__module__).joinpath(fname)
            with importlib_resources.as_file(config_yaml_file) as filename:
                if Path(filename).exists():
                    self._config_data_defaults = loadYamlFile(filename)

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

    def get_component(self, dep):
        """
        Pass a PluginDependency() and this function will return all of the
        matching instances of components.

        This is used by plugins to find an instance of another plugin that they
        may need to interact with, attach a hook to, etc.

        Parameters
        ----------
        dep
            A PluginDependency()

        Returns
        -------
        list
            A list of matching instances of components
        """
        results = match_class_dependencies(self, self.parent.components.instances, [dep])
        return results

    def register_hook(self, component_namespace, callback, hook_type=None):
        """
        Register a callback function for each plugin section configured in self.config_data.

        For every 'plugin_type', 'data' section in self.config_data[component_namespace],
        registers a 'callback' function, optionally passing 'hook_type'.

        The end result is that the function will be called if any of the configured plugins
        run a trigger() function.

        Parameters
        ----------
        component_namespace
            The name of a component namespace.
        callback
            A function to call.
        hook_type
            (Optional) The name of the type of hook being registered.
        """

        if not component_namespace in self.config_data:
            self.logger.debug(f"Warning: could not find component namespace '{component_namespace}' in self.config_data")
            return

        # Register a hook if this component (Job) has been configured
        # with a component namespace section, and a particular plugin type in each
        # section. Basically the configuration determines what plugins can trigger
        # this job.
        for plugin_type, data in self.config_data[component_namespace].items():
            for item in data:
                plugin_dep = PluginDependency(component_namespace=component_namespace, plugin_type=plugin_type)
                self.parent.hooks.register_hook(
                    plugin_dep=plugin_dep,
                    hook_type=hook_type,
                    callback=self.receive_alert,
                    data=item
                )


@dataclass(unsafe_hash=True)
class ComponentObject:
    classref = None
    parent = None
    config_data = None
    error = None
    _instance = None

    logger = makeLogger(__module__ + "/ComponentObjects")

    def __init__(self, classref=None, config_data=None, parent=None, error=None):
        self.classref = classref
        self.config_data = config_data
        self.parent = parent
        self.error = error
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
    def instance(self):
        if not self._instance:
            self.logger.debug(f"making {self.classref}(parent={self.parent}, config_data={self.config_data})")
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
    objects = []  # The list of ComponentObject()s

    logger = makeLogger(__module__ + "/ComponentObjects")

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __init__(self, root, parent, config):
        self.logger.debug(f"ComponentObjects(self={self}, root={root}, parent={parent}, config={config}")
        self.root = root
        self.parent = parent
        self.config = config

        # Take config.objects, make self.objects
        self.add_all_component_topo_objects(self.config.objects, self.objects)

    async def initialize(self):
        for x in self.objects:
            self.instances.append(x.instance())

    def add_all_component_topo_objects(self, objects, array):
        """Retrieve a set of ComponentObject()s based on topological sort of plugin graph.

        The intent is to load plugins that have no configuration, as well as load plugins
        that do have configuration, but to load them all according to the topological
        graph of plugin dependencies.

        Parameters
        ---------
        objects
            A list of ComponentObject()s. These should be the objects that were created
            during parsing of configuration.
        array
            An array to append ComponentObject()s to.
        """

        self.logger.debug(f"add_all_component_topo_objects(self={self}, objects={objects}, array={array})")

        # Get all plugin classes, sorted topologically
        plugin_class_topo = [x for x in self.root.plugins.topo_sort() if (x.class_type == "plugin")]
        for plugin_class in plugin_class_topo:

            # Get any component objects we created for this plugin class, based on config data
            component_objects = [x for x in objects if x.classref == plugin_class]

            # If any were found, process them
            if len(component_objects) > 0:
                for obj in component_objects:
                    self.logger.debug(f"Loading component from object {obj.classref}")
                    array.append(
                        ComponentObject(classref=obj.classref, 
                                        config_data=obj.config_data,
                                        parent=self.parent)
                    )
                    # NOTE: might want to set classref, parent, config_data in that obj
            # Otherwise create new objects with no configuration
            else:
                self.logger.debug(f"Loading new component object from plugin_class {plugin_class}")
                array.append(
                    ComponentObject(classref=plugin_class, parent=self.parent)
                )

