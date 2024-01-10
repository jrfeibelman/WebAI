from yaml import load, SafeLoader
from os import path, environ
from re import compile
from io import StringIO

from rtai.utils.cache import Cache, Index, Item, CacheDict
from rtai.utils.logging import error

class Config(Cache):
    """ _summary_ Class to represent a configuration file with nested sections"""
    _curSection: str

    __slots__= '_dict', '_curSection', '_idx', '_dict'

    def __init__(self, cache_dict: CacheDict, curSection: str=''):
        """ _summary_ Constructor for the Config 
        
        Args:
            cache_dict (CacheDict): dictionary to initialize cache with
            curSection (str, optional): current section of the config. Defaults to ''.
        """
        super().__init__(cache_dict=cache_dict)
        self._curSection: str = curSection

    def initialize(self) -> bool:
        pass

    def update(self, event) -> None:
        pass

    def contains(self, key: str) -> bool:
        """ _summary_ Check if the config contains the key
        
        Args:
            key (str): key to check for
            
        Returns:
            bool: whether or not the config contains the key
        """
        return str(key) in self._dict

    def _get(self, key : str) -> Item:
        """ _summary_ Get the value of the key
        
        Args:
            key (str): key to get the value for
            
        Returns:
            Item: value of the key
        
        Raises:
            KeyError: if the key is not found
        """
        
        try:
            return self[key]
        except KeyError:
            errStr = "Key [%s] not found in config %s." % (key, '' if self._curSection == '' else "  {'%s': %s}" % (self._curSection, self._dict))
            raise KeyError(errStr)

    def get_value(self, key: str, default_value: bool=None) -> str:
        """ _summary_ Get the value of the key
        
        Args:
            key (str): key to get the value for
            default_value (str, optional): default value to return if key is not found. Defaults to None.
            
        Returns:
            str: value of the key
        """
        try:
            value = self._get(key)
            return str(value)
        except KeyError as err:
            if default_value is None:
                error("%s  No default_value provided" % err)
            return default_value
            
    def expand(self, key: str) -> str:
        """ _summary_ Expand a key to its value

        Args:
            key (str): key to expand

        Returns:
            str: expanded value of the key
        """
        try:
            value = self._get(key)
            return Config(value, key)
        except KeyError:
            return Config(dict(), key)
      
    def __str__(self) -> str:
        return "{%s: %s}" % (self._curSection, str(self._dict))

class YamlLoader(SafeLoader):
    """ Custom Yaml Loader that allows for !include and !path tags"""
    path_matcher = compile(r'(\$\{([^}^{]+)\})')

    def __init__(self, stream):
        """ _summary_ Constructor for the YamlLoader
        
        Args:
            stream: stream to create yaml with
        """
        super(YamlLoader, self).__init__(stream)

        YamlLoader.add_constructor('!include', YamlLoader.include)
        YamlLoader.add_constructor('!path', YamlLoader.path_constructor)
        YamlLoader.add_implicit_resolver('!path', YamlLoader.path_matcher, None)

    @classmethod
    def load(cls, config: str) -> Config:
        """ _summary_ Factory method to generate a Config from a yaml config file
        
        Args:
            config (str): path to the yaml config file
        """
        with open(config) as yaml:
            return Config(load(yaml, YamlLoader))
        
    @classmethod
    def load_from_string(cls, config: str) -> Config:
        """ _summary_ Factory method to generate a Config from a yaml config string
        
        Args:
            config (str): string contents of the yaml file
        """
        with StringIO(config) as yaml:
            return Config(load(yaml, YamlLoader))

    def include(self, node) -> Config:
        filename = YamlLoader.path_constructor(self, node)
        with open(filename, 'r') as f:
            return load(f, YamlLoader)

    def path_constructor(loader, node) -> str:
        ''' Extract the matched value, expand env variable, and replace the match '''
        value = node.value
        match = YamlLoader.path_matcher.match(value)
        env_var = match.group()[2:-1]
        return environ.get(env_var) + value[match.end():]