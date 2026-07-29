from dataclasses import dataclass, field
import numpy as np
from .arrays.infrastructure import emm_pattern_types
from .arrays.transitions import get_current_transitions, set_transitions
from .generic.external import patterns
from .generic.geometry import is_vertex_macro
from .generic.minus_one import get_minus_one

# This module is responsible for packing all primary information of a vertex into an instance of Vertex class.
# There are no derivation algorithms present here.

@dataclass
class MicroVertex:
    landscape_name    : str  = None
    landscape_valency : int  = 0
    landscape_player  : int  = -1
    infrastructure    : str  = None
    fishes            : int  = 0

@dataclass
class MacroVertex:
    height            : int  = 0
    pattern_a         : str  = patterns.editnames_ordered[0]                      # triangle Δ
    pattern_b         : str  = patterns.editnames_ordered[0]                      # triangle ∇
    transition_upper_a: list = field(default_factory=lambda: [None, None, None])  # corners: down+right, down+left, up
    transition_upper_b: list = field(default_factory=lambda: [None, None, None])  # corners: down, up+right, up+left
    transition_lower_a: list = field(default_factory=lambda: [None, None, None])  # corners: down+right, down+left, up
    transition_lower_b: list = field(default_factory=lambda: [None, None, None])  # corners: down, up+right, up+left
    vertexcolor       : int  = None  # palette index for "data\engine2d\bin\palettes\misc\vertexcolors.pcx" file

@dataclass
class Vertex:
    macro_vertex : MacroVertex | None = None  # Not every vertex is a macro vertex.
    micro_vertex : MicroVertex = field(default_factory=lambda: MicroVertex())


def get_micro_vertex(data_object, coordinates) -> MicroVertex:
    x, y = coordinates
    assert 0 <= x < 2 * data_object.lsiz.width and \
           0 <= y < 2 * data_object.lsiz.height

    landscape_id = data_object.emla[y, x]
    landscape_name = None if landscape_id == get_minus_one(data_object.emla.dtype) else data_object.eald[landscape_id]

    return MicroVertex(landscape_name=landscape_name,
                       landscape_valency=int(data_object.lmlv[y, x]),
                       landscape_player=int(np.uint8(data_object.lmlp[coordinates[::-1]]).view(np.int8)),
                       infrastructure=emm_pattern_types.get(int(data_object.emmi[y, x]).bit_length(), None),
                       fishes=data_object.lafm.get((x, y), 0))

def get_macro_vertex(data_object, coordinates) -> MacroVertex:
    x, y = coordinates
    assert 0 <= x < data_object.lsiz.width and \
           0 <= y < data_object.lsiz.height

    transitions_a = get_current_transitions(data_object, coordinates, "a")
    transitions_b = get_current_transitions(data_object, coordinates, "b")

    return MacroVertex(height=int(data_object.lmhe[y, x]),
                       pattern_a=data_object.eapd[data_object.empa[y, x]],
                       pattern_b=data_object.eapd[data_object.empb[y, x]],
                       transition_upper_a=transitions_a[0],
                       transition_upper_b=transitions_b[0],
                       transition_lower_a=transitions_a[1],
                       transition_lower_b=transitions_b[1],
                       vertexcolor=None if data_object.emvc is None else data_object.emvc[y, x])

def _to_numeric(ea_d, value):
    try:
        return ea_d.index(value)
    except ValueError:
        ea_d.append(value)
        return len(ea_d) - 1

def set_micro_vertex(data_object, coordinates, micro_vertex):
    x, y = coordinates
    assert 0 <= x < 2 * data_object.lsiz.width and \
           0 <= y < 2 * data_object.lsiz.height

    if micro_vertex.landscape_name is None: data_object.emla[y, x] = get_minus_one(data_object.emla.dtype)
    else: data_object.emla[y, x] = _to_numeric(data_object.eald, micro_vertex.landscape_name)

    data_object.lmlv[y, x] = micro_vertex.landscape_valency
    data_object.lmlp[coordinates[::-1]] = np.int8(micro_vertex.landscape_player).view(np.uint8)

    emmi_value = next((k for k, v in emm_pattern_types.items() if v == micro_vertex.infrastructure), None)

    if emmi_value is not None and emmi_value > 0: data_object.emmi[y, x] = 1 << (emmi_value - 1)
    else:                                         data_object.emmi[y, x] = 0

    if micro_vertex.fishes == 0: data_object.lafm.pop((x, y), None)
    else:                        data_object.lafm[(x, y)] = micro_vertex.fishes

    return data_object

def set_macro_vertex(data_object, coordinates, macro_vertex):
    x, y = coordinates
    assert 0 <= x < data_object.lsiz.width and \
           0 <= y < data_object.lsiz.height

    data_object.lmhe[y, x] = macro_vertex.height
    data_object.empa[y, x] = _to_numeric(data_object.eapd, macro_vertex.pattern_a)
    data_object.empb[y, x] = _to_numeric(data_object.eapd, macro_vertex.pattern_b)

    data_object = set_transitions(data_object, coordinates, "a", [macro_vertex.transition_upper_a,
                                                                  macro_vertex.transition_lower_a])

    data_object = set_transitions(data_object, coordinates, "b", [macro_vertex.transition_upper_b,
                                                                  macro_vertex.transition_lower_b])

    if data_object.emvc is not None: data_object.emvc[y, x] = macro_vertex.vertexcolor

    return data_object

def get_vertex(data_object, coordinates) -> Vertex:
    if is_vertex_macro(coordinates):
        macro_coordinates = type(coordinates)(v // 2 for v in coordinates)
        macro_vertex = get_macro_vertex(data_object, macro_coordinates)
    else:
        macro_vertex = None

    return Vertex(macro_vertex=macro_vertex,
                  micro_vertex=get_micro_vertex(data_object, coordinates))

def set_vertex(data_object, coordinates, vertex):
    set_micro_vertex(data_object, coordinates, vertex.micro_vertex)

    if is_vertex_macro(coordinates):
        macro_coordinates = type(coordinates)(v // 2 for v in coordinates)
        data_object = set_macro_vertex(data_object, macro_coordinates, vertex.macro_vertex)
        assert vertex.macro_vertex is not None
    else:
        assert vertex.macro_vertex is None

    return data_object
