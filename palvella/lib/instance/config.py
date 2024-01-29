

from collections import UserDict
from dataclasses import dataclass

from ruamel.yaml import YAML

from palvella.lib.plugin import PluginDependency, match_class_dependencies
from ..logging import makeLogger, logging


@dataclass
class ConfigData(UserDict):
    # subclasses UserDict because dict requires a lot more overloading to avoid bugs
    """A class (that implements a dict) to store configuration data and manipulate it.
       Mainly useful to be able to conceal data when printing it.
    """

    def __init__(self, data=None):
        return super().__init__(data)

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __repr__(self):
        return f"{self.__class__}(CONCEALED)"

@dataclass
class ConfigObject:
    def __init__(self, plugin_base=None, classref=None, plugin_type=None, config_data=None):
        self.plugin_base = plugin_base
        self.classref = classref
        self.plugin_type = plugin_type
        self.config_data = ConfigData(config_data)


class Config:
    """A class to parse a configuration file and load it into a data structure."""
    
    logger = makeLogger(__module__ + "/Config")
    objects = []  # ComponentObject()s derived from config files
    parent = None
    config_path = None
    config_data = None

    def __init__(self, parent=None, config_path=None, config_data=None):
        """Initialize new configuration.

        Parameters
        ----------
        parent
            A reference to the parent Instance() object.
        config_path
            A file path to a YAML file to load configuration data from. (Optional)
        config_data
            A dict with configuration data. (Optional)
        """
        self.logger.debug(f"Config(self={self}, parent={parent}, config_path={config_path}, config_data={config_data})")
        self.parent = parent
        self.config_path = config_path
        self.config_data = config_data

        self.load_config()
        self.objects = [ x for x in self.parse_conf_component_ns(self.data) ]
        self.logger.debug(f"Created objects: {self.objects}")

    def load_config(self):
        c = 0
        if self.config_path != None:
            self.data = loadYamlFile(file=self.config_path)
            c += 1
        if self.config_data != None:
            self.data = self.config_data
            c += 1
        if c != 1:
            raise Exception("You need to pass either config_path or config_data")

    def parse_conf_component_ns(self, data):
        """
        Parse configuration data, return plugin_type and ConfigData().

        See data parameter below. Finds a components that has registered
        *component_namespace*, finds a plugin *plugin_type* of that component,
        and yields a tuple of that plugin_type and a ConfigData(). Also
        attempts to validate the schema.

        Parameters
        ----------
        data
            A dict of the following format (shown as YAML):
            
                component_namespace:
                  plugin_type:
                    - item1
                    - item2
            
            The `component_namespace` must be a subclass in `self.parent.subclasses`
            whose attribute `class_type` is "plugin_base".
            `plugin_type` must have a parent class `component_namespace`.

        Returns
        -------
        list
            For each `item` (see above), yield the plugin_type class and ConfigData(item).
        """
        subclasses = self.parent.subclasses

        self.logger.debug(f"data {data}")

        if not isinstance(data, UserDict) and not isinstance(data, dict):
            raise ValueError(f"config data needs to be a dict (was: type {type(data)}, dict {data})")

        for component_namespace, datarootv in data.items():
            self.logger.debug(f"component_namespace {component_namespace}")

            plugin_base = [x for x in subclasses
                             if x.class_type == "plugin_base" \
                             and x.component_namespace == component_namespace]
            if len(plugin_base) < 1:
                self.logger.debug(f"could not find plugin base for '{component_namespace}'")
                continue
            elif len(plugin_base) > 1:
                self.logger.debug(f"too many plugin bases for '{component_namespace}'")
                continue

            self.logger.debug(f"datarootv {datarootv} type {type(datarootv)}")
            if type(datarootv) == type(""):
                self.logger.debug(f"Found datarootv as scalar; assuming alias to plugin_type")
                datarootv = {datarootv: []}

            # Validate schema
            plugin_base[0].validate_config_schema(datarootv)

            if type(datarootv) != type({}):
                self.logger.debug(f"Configuration entry for {plugin_type} must be a scalar or dict; skipping")
                continue

            for plugin_type, config_data in datarootv.items():
                self.logger.debug(f"plugin_type {plugin_type} config_data {config_data}")
                if type(config_data) != type([]):
                    self.logger.debug(f"Config_data argument to plugin_type must be a list; skipping")
                    continue

                dep = PluginDependency(parentclassname=plugin_base[0].__name__, plugin_type=plugin_type)
                self.logger.debug(f"dep {dep}")

                for classref in match_class_dependencies(self, plugin_base[0].__subclasses__(), [dep]):
                    self.logger.debug(f"class {classref}")

                    if len(config_data) < 1:
                        config_data = [None]

                    for item in config_data:
                        self.logger.debug(f"yielding new component object ({classref})")
                        yield ConfigObject(plugin_base=plugin_base, classref=classref,
                                           plugin_type=plugin_type, config_data=item)


def loadYamlFile(file):
    """Load configuration, parse it, and return the result."""
    with open(file, "r", encoding="utf-8") as f:
        yaml = YAML(typ='safe')
        return yaml.load(f)
    raise ValueError("No configuration provided")
