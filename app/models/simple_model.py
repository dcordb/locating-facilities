from app.utils.utils import PT, init_logger
from typing import List, Tuple
from bisect import bisect_right
from collections import namedtuple

C = namedtuple('C', ['c', 'w'], defaults=[0])

class FastModel:
    def __init__(self, near: List[PT], far: List[PT], xmin: float, xmax: float, ymin: float, ymax: float) -> None:
        self.logger = init_logger('Simple Model')
        self.logger.info('Calculating optimal x')

        # find optimal x
        xnear = [ C(x, w) for x, _, w, _ in near ]
        xfar = [ C(x, w) for x, _, w, _ in far ]
        xboundaries = [ C(xmin), C(xmax) ]

        x, cx = self.solvecoord(xnear, xfar, xboundaries)

        self.logger.info('Calculating optimal y')
        
        # find optimal y
        ynear = [ C(y, w) for _, y, w, _ in near ]
        yfar = [ C(y, w) for _, y, w, _ in far ]
        yboundaries = [C(ymin), C(ymax)]

        y, cy = self.solvecoord(ynear, yfar, yboundaries)

        self.near = near
        self.far = far
        self.optimalpt = PT(x, y, kind=self.__class__.__name__)
        self.cost = cx + cy

    def solvecoord(self, cnear: List[C], cfar: List[C], boundaries: List[C]) -> Tuple[float, float]:
        cnear = sorted(cnear, key=lambda x: x.c)
        cfar = sorted(cfar, key=lambda x: x.c)

        sumw_near, sumwm_near = self.precalc_sums(cnear)
        sumw_far, sumwm_far = self.precalc_sums(cfar)

        near_vals = [ c.c for c in cnear ]
        far_vals = [ c.c for c in cfar ]

        opt = 1e18
        ans = 0

        for x, _ in cnear + cfar + boundaries:
            cost = self.getcost(x, near_vals, sumw_near, sumwm_near)
            cost -= self.getcost(x, far_vals, sumw_far, sumwm_far)

            self.logger.info(f'For c={x} found cost={cost}')

            if cost < opt:
                opt = cost
                ans = x

        return ans, opt

    def precalc_sums(self, coord: List[C]) -> Tuple[List[float], List[float]]:
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

    def getsum(self, vals: List[float], l, r) -> float:
        if l > r:
            return 0.

        assert l >= 0 and r < len(vals)
        return vals[r] - (vals[l - 1] if l >= 1 else 0.)

    def getcost(self, x: float, vals: List[float], sumW: List[float], sumWM: List[float]) -> float:
        p = bisect_right(vals, x)

        # greater than x
        n = self.getsum(sumWM, p, len(sumWM) - 1)
        m = -self.getsum(sumW, p, len(sumW) - 1)

        # less than or equal to x
        n += -self.getsum(sumWM, 0, p - 1)
        m += self.getsum(sumW, 0, p - 1)

        return x * m + n

    def eval(p: PT, near: List[PT], far: List[PT]):
        return FastModel._arrcost(p, near) - FastModel._arrcost(p, far)

    def _arrcost(p, arr):
        cost = 0
        for v in arr:
            cost += v.w * (abs(v.x - p.x) + abs(v.y - p.y))

        return cost

if __name__ == '__main__':
    m1 = FastModel([PT(1, 4, w=1)], [PT(5, 1, w=1)], -5, 5, -2, 7)
    print(f'pt={m1.optimalpt}, cost={m1.cost}')

    near = [PT(1, 4, w=1), PT(4, 2, w=1), PT(3, 2, w=1)]
    far = [PT(5, 1, w=1), PT(3, 7, w=1), PT(1.5, 1, w=1.5)]
    m2 = FastModel(near, far, -8, 8, -8, 8)
    print(f'pt={m2.optimalpt}, cost={m2.cost}')

    e = []
    for x in range(-8, 9):
        for y in range(-8, 9):
            e.append((x, y, FastModel.eval(PT(x, y), near, far)))

    e.sort(key=lambda x: x[2])

    print(e[:10])