# ---------------------------------------------------------------------------- #
#                                                                              #
#     This program is free software: you can redistribute it and/or modify     #
#     it under the terms of the GNU General Public License as published by     #
#     the Free Software Foundation, either version 3 of the License, or        #
#     (at your option) any later version.                                      #
#                                                                              #
#     This program is distributed in the hope that it will be useful,          #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the             #
#     GNU General Public License for more details.                             #
#                                                                              #
#     You should have received a copy of the GNU General Public License        #
#     along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                              #
# ---------------------------------------------------------------------------- #

VERSION = "0.1.3"

def init_from_key(d, key, cls, *args, **kwargs):
    d[key] = cls(d, args, kwargs)

def init_from_key_cls_pairs(d, key, cls):
    for i in key_cls_pairs:
        init_from_key(d, *key_cls_pairs[i])

def init_from_key_child(d, key, cls, *args, **kwargs):
    """Same as 'init_from_key' but for when initalizing a ChildPDict object
    within a dict type object."""
    d[key] = cls(d, args, kwargs)

def init_from_key_cls_pairs_child(d, key_cls_pairs):
    for i in key_cls_pairs:
        init_from_key_child(d, *key_cls_pairs[i])


__all__ = ["init_from_key", "init_from_key_cls_pairs", "init_from_key_child",
    "init_from_key_cls_pairs_child"]

class PDict(dict):
    """Special dict class with defaults and (optional) automatic parsing on __init__. The aim is to make loading data into a dict who's values will
    need to be stored in custom classes easier and simpler to initalize.

    All the developer has to do is simply inherit their class from PDict and
    override '_defaultdict to return a default dictionary (optional)
    and then override _parseinit to control how data will be handled and loaded
    into custom classes.


    An example to clarify usage.
    #Parsing data automatically into classes.

    class Audio(dict): pass
    class Graphics(dict): pass

    class ParseData(Pdict):

        def _defaultdict(self):
            return {"audio": 0, "graphics": 0,}

        def _parseinit(self):
            init_from_key(self, "audio", Audio)
            init_from_key(self, "graphics", Graphics)
            # could also be done as
            # init_from_key_cls_pairs(self, (
                ("audio", Audio),
                ("graphics", Graphics)
                # if you have args or kwargs you would use
                # ("graphics", Graphics, args_here, kwargs_here),
                )

    data = {'audio':
                {'volume: 21',
                'panning': 0
                },
            {'graphics':
                {'quality': 'high',
                'bilinear-filtering': False
                }
            }

    pd = ParseData(data)
    pd
    {'audio': {'volume: 21', 'panning': 0}, {'graphics': {'quality': 'high',
        'bilinear-filtering': False}}
    """
    __slots__ = dict.__slots__ + "_default_dictargs"
    def __init__(data={}, parseinit=True, parseargs=(), default_dictargs=()):
        # init the super class (dict) using _defaultdict
        self._default_dictargs = tuple(default_dictargs)
        super().__init__(self._defaultdict)
        self.update(data)

        if parseinit == ('ifdata' or 2):
            if data: self._parseinit(parseargs)
        elif parseinit == True: self._parseinit(parseargs)  # always parse
        else pass   # dont parse

    def _get_default_dictargs(self): return self._default_dictargs
    def _set_default_dictargs(self, d): self._default_dictargs = tuple(d)
        _default_dictargs = property(_get_default_dictargs, _set_default_dictargs)

    def _defaultdict(self):
        """Overload this to set the initial dict (initdict) that will be used
        for default data."""
        return {}

    def _parseinit(self, *args):
        """Overload this to control data parsing when loading data at init."""
        pass

    def reset(self):
        """Reset current values back to values in default_dict."""
        self.update(self._defaultdict)

    @property
    def default_dict(self):
        """The dict used to initalize and reset this object. Returns a new dict
        defined by '_defaultdict'."""
        return self._defaultdict()

    def modified_values(self):
        """Return an iterator of keys for values that differ from those in
        initvalues."""
        return iter(i for i in self.keys() if self[i] != self._defaultdict[i])

    def unmodified_values(self):
        """Return an iterator of keys for values that match those in
        initvalues."""
        return iter(i for i in self.keys() if self[i] == self._defaultdict[i])

    def has_modified_values(self):
        """True if any values differ from those in initvalues."""
        return any(self[i] != self._defaultdict[i] for i in self.keys())

    def has_new_keys(self):
        """True if any keys are present that do not exist in initvalues."""
        return any(i for i in self.keys() if i not in self._defaultdict.keys())

    def get_new_keys(self):
        """ Yield any keys present that do not exist in in it values."""
        return iter(i for i in self.keys() if i not in self._defaultdict.keys())


class ChildPDict(PDict):
    """Same as PDict, except adds a '_parent' attribute."""
    __slots__ = PDict.__slots__ + "_parent"
    def __init__(self, parent, data={}, parseinit=True, parseargs=(), default_dictargs=()):
        self._parent = parent
        super().__init__(data=data, parseinit=parseinit, parseargs=parseargs,
            default_dictargs=default_dictargs)
