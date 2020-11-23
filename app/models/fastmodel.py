from app.utils.utils import PT
from typing import List, Tuple
from bisect import bisect_right
from collections import namedtuple

__repr__ = 'FastModel'
C = namedtuple('C', ['c', 'w'], defaults=[0])

def fastmodel(near: List[PT], far: List[PT], xmin: float, xmax: float, ymin: float, ymax: float):
    # find optimal x
    xnear = [ C(x, w) for x, _, w, _ in near ]
    xfar = [ C(x, w) for x, _, w, _ in far ]
    xboundaries = [ C(xmin), C(xmax) ]

    x, cx = solvecoord(xnear, xfar, xboundaries)
    
    # find optimal y
    ynear = [ C(y, w) for _, y, w, _ in near ]
    yfar = [ C(y, w) for _, y, w, _ in far ]
    yboundaries = [C(ymin), C(ymax)]

    y, cy = solvecoord(ynear, yfar, yboundaries)

    return PT(x, y, kind='Fast Model'), cx + cy

def solvecoord(cnear: List[C], cfar: List[C], boundaries: List[C]) -> Tuple[float, float]:
    cnear = sorted(cnear, key=lambda x: x.c)
    cfar = sorted(cfar, key=lambda x: x.c)

    sumw_near, sumwm_near = precalc_sums(cnear)
    sumw_far, sumwm_far = precalc_sums(cfar)

    near_vals = [ c.c for c in cnear ]
    far_vals = [ c.c for c in cfar ]

    opt = 1e18
    ans = 0

    for x, _ in cnear + cfar + boundaries:
        cost = getcost(x, near_vals, sumw_near, sumwm_near)
        cost -= getcost(x, far_vals, sumw_far, sumwm_far)

        if cost < opt:
            opt = cost
            ans = x

    return ans, opt

def precalc_sums(coord: List[C]) -> Tuple[List[float], List[float]]:
    n = len(coord)
    sumW = [0.] * n
    sumWM = [0.] * n

    for i, (x, w) in enumerate(coord):
        if i > 0:
            sumW[i] = sumW[i - 1]
            sumWM[i] = sumWM[i - 1]

        sumW[i] += w
        sumWM[i] += x * w

    return sumW, sumWM

def getsum(vals: List[float], l, r) -> float:
    if l > r:
        return 0.

    assert l >= 0 and r < len(vals)
    return vals[r] - (vals[l - 1] if l >= 1 else 0.)

def getcost(x: float, vals: List[float], sumW: List[float], sumWM: List[float]) -> float:
    p = bisect_right(vals, x)

    # greater than x
    n = getsum(sumWM, p, len(sumWM) - 1)
    m = -getsum(sumW, p, len(sumW) - 1)

    # less than or equal to x
    n += -getsum(sumWM, 0, p - 1)
    m += getsum(sumW, 0, p - 1)

    return x * m + n

def eval(p: PT, near: List[PT], far: List[PT]):
    return arrcost(p, near) - arrcost(p, far)

def arrcost(p, arr):
    cost = 0
    for v in arr:
        cost += v.w * (abs(v.x - p.x) + abs(v.y - p.y))

    return cost

if __name__ == '__main__':
    optimalpt, cost = fastmodel([PT(1, 4, w=1)], [PT(5, 1, w=1)], -5, 5, -2, 7)
    print(f'pt={optimalpt}, cost={cost}')

    near = [PT(1, 4, w=1), PT(4, 2, w=1), PT(3, 2, w=1)]
    far = [PT(5, 1, w=1), PT(3, 7, w=1), PT(1.5, 1, w=1.5)]
    
    optimalpt, cost = fastmodel(near, far, -8, 8, -8, 8)
    print(f'pt={optimalpt}, cost={cost}')

    e = []
    for x in range(-8, 9):
        for y in range(-8, 9):
            e.append((x, y, eval(PT(x, y), near, far)))

    e.sort(key=lambda x: x[2])

    print(e[:10])