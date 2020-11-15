from app.models.utils import *
from typing import List, Tuple
from bisect import bisect_right
from collections import namedtuple

C = namedtuple('C', ['c', 'w'])

class SimpleModel:
    def __init__(self, near: List[PointW], far: List[PointW], max_x: float, max_y: float) -> None:
        for x, y, _ in near:
            assert x >= 0 and x <= max_x
            assert y >= 0 and y <= max_y

        for x, y, _ in far:
            assert x >= 0 and x <= max_x
            assert y >= 0 and y <= max_y

        self.logger = init_logger('Simple Model')

        self.logger.info('Calculating optimal x')

        # find optimal x
        xnear = [ C(x, w) for x, _, w in near ]
        xfar = [ C(x, w) for x, _, w in far ]
        xboundaries = [ C(0, 1), C(max_x, 1) ]

        x, cx = self.solvecoord(xnear, xfar, xboundaries)

        self.logger.info('Calculating optimal y')
        
        # find optimal y
        ynear = [ C(y, w) for _, y, w in near ]
        yfar = [ C(y, w) for _, y, w in far ]
        yboundaries = [C(0, 1), C(max_y, 1)]

        y, cy = self.solvecoord(ynear, yfar, yboundaries)

        self.near = near
        self.far = far
        self.optimalpt = Point(x, y)
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

if __name__ == '__main__':
    m1 = SimpleModel([PointW(1, 4)], [PointW(5, 1)], 5, 7)
    print(f'pt={m1.optimalpt}, cost={m1.cost}')

    m2 = SimpleModel([PointW(1, 4), PointW(4, 2), PointW(3, 2)], [PointW(5, 1, 1)], 8, 8)
    print(f'pt={m2.optimalpt}, cost={m2.cost}')