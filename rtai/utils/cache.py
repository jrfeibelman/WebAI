from abc import abstractmethod, ABC
from typing import Dict, TypeAlias
from rtai.utils.logging import warn

Index: TypeAlias = int
Item: TypeAlias = object
CacheDict: TypeAlias = Dict[Index, Item]

class Cache(ABC):
    """ _summary_ Abstract class to represent a cache of objects"""

    def __init__(self, cache_dict: Dict[Index, Item]=dict()):
        """ _summary_ Constructor for the cache

        Args:
            cache_dict (dict, optional): dictionary to initialize cache with. Defaults to dict().
        """
        self._dict: CacheDict = cache_dict
        self._idx: Index = -1

    @abstractmethod
    def initialize(self) -> bool:
        """ _summary_ Abstract method to initialize the cache
        
        Returns:
            bool: whether or not the cache was initialized successfully
        """
        pass

    @abstractmethod
    def update(self, event) -> None:
        """ _summary_ Abstract method to update the cache"""
        pass

    def getDict(self) -> CacheDict:
        """ _summary_ Get the cache dictionary
        
        Returns:
            Dict[Index, Item]: Dictionary of the cache
        """
        return self._dict

    def isEmpty(self) -> bool:
        """ _summary_ Check if the cache is empty
        
        Returns:
            bool: whether or not the cache is empty
        """
        return not self._dict

    def __iter__(self) -> iter:
        """ _summary_ Iterator for the cache
        
        Returns:
            iter: iterator for the cache
        """
        self._idx = -1
        return iter(self._dict)

    def __next__(self) -> Item:
        """ _summary_ Next element in the cache
        
        Returns:
            Item: next element in the cache

        Raises:
            StopIteration: when there are no more elements in the cache
        """
        self._idx += 1
        if self._idx < len(self._dict):
            return self._dict[self._idx]
        else:
            raise StopIteration

    def __getitem__(self, key: Index) -> Item:
        """ _summary_ Get an item from the cache

        Args:
            key (Index): index of the item to get

        Returns:
            Item: item at the given index

        Raises:
            KeyError: when the key is not in the cache
        """
        if key in self._dict:
            return self._dict[key]
        else:
            errStr = "Key [%s] not found in %s@[%s]." % (key, self.__class__, hex(id(self)))
            warn(errStr)
            raise KeyError(errStr)

    def __setitem__(self, key, value) -> None:
        """ _summary_ Set an item in the cache

        Args:
            key (Index): index of the item to set
            value (Item): item to set at the given index
        """
        self._dict[key] = value

    def __contains__(self, key) -> bool:
        """ _summary_ Check if the cache contains a key

        Args:
            key (Index): index to check for

        Returns:
            bool: whether or not the cache contains the key
        """
        return key in self._dict

    def __str__(self) -> str: 
        return "%s@[%s]:\n%s" % (self.__class__, hex(id(self)),[e for e in self._dict.values()])
    
    def __repr__(self) -> str:
        return str(self)