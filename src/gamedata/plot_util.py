import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from typing import Callable
from IPython.display import display

_FigSize = (10, 5)
_Transparent = False

class AxisLabels:
    def __init__(self, title=None, xlabel=None, ylabel=None, legend=None):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend

class TickParams:
    def __init__(self, axis='x', which='major', labelsize=10, rotation=None):
        self.axis = axis
        self.which = which
        self.labelsize = labelsize
        self.rotation = rotation

def get_figsize() -> tuple[int, int]:
    return _FigSize

def set_figsize(width: int, height: int) -> None:
    global _FigSize
    _FigSize = (width, height)

def get_transparent_mode() -> bool:
    return _Transparent

def set_transparent_mode(mode: bool) -> None:
    global _Transparent
    _Transparent = mode

_outfunc: Callable[[Figure], None] | None = None

def auto_dispfunc(fig: Figure) -> None:
    backend = matplotlib.get_backend()
    if 'backend_inline' in backend or 'inline' in backend:
        display(fig)
    elif 'ipympl' in backend or 'nbagg' in backend or 'widget' in backend:
        plt.show()
    else:
        print(f"Unable to output figure:{backend}")
        
_outfunc = auto_dispfunc

def set_dispfunc(func: Callable[[Figure], None]) -> None:
    global _outfunc
    _outfunc = func
    
def get_dispfunc() -> Callable[[Figure], None] | None:
    return _outfunc

