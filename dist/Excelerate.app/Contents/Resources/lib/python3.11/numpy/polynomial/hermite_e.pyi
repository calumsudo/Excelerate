from typing import Any

from numpy import ndarray, dtype, int_
from numpy.polynomial._polybase import ABCPolyBase
from numpy.polynomial.polyutils import trimcoef

__all__: list[str]

hermetrim = trimcoef

def poly2herme(pol): ...
def herme2poly(c): ...

hermedomain: ndarray[Any, dtype[int_]]
hermezero: ndarray[Any, dtype[int_]]
hermeone: ndarray[Any, dtype[int_]]
hermex: ndarray[Any, dtype[int_]]

def hermeline(off, scl): ...
def hermefromroots(roots): ...
def hermeadd(c1, c2): ...
def hermesub(c1, c2): ...
def hermemulx(c): ...
def hermemul(c1, c2): ...
def hermediv(c1, c2): ...
def hermepow(c, pow, maxpower=...): ...
def hermeder(c, m=..., scl=..., axis=...): ...
def hermeint(c, m=..., k=..., lbnd=..., scl=..., axis=...): ...
def hermeval(x, c, tensor=...): ...
def hermeval2d(x, y, c): ...
def hermegrid2d(x, y, c): ...
def hermeval3d(x, y, z, c): ...
def hermegrid3d(x, y, z, c): ...
def hermevander(x, deg): ...
def hermevander2d(x, y, deg): ...
def hermevander3d(x, y, z, deg): ...
def hermefit(x, y, deg, rcond=..., full=..., w=...): ...
def hermecompanion(c): ...
def hermeroots(c): ...
def hermegauss(deg): ...
def hermeweight(x): ...

class HermiteE(ABCPolyBase):
    domain: Any
    window: Any
    basis_name: Any
