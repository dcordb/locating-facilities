from app.utils.utils import PT
from typing import List

__repr__ = 'FussyModel'

def optimize(near: List[PT], far: List[PT], xmin: float, xmax: float, ymin: float, ymax: float):
    return PT(21, 63, w=0, kind='FussyModel'), 2346.6454646