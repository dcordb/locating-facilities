from app.utils.utils import PT
from typing import List
import pulp

__repr__ = 'FussyModel'

def optimize(near: List[PT], far: List[PT], xmin: float, xmax: float, ymin: float, ymax: float):
    xs_near, ys_near, ws_near = extractconstants(near)
    xs_far, ys_far, ws_far = extractconstants(far)

    xca = dot(xs_near, ws_near) / len(near)
    yca = dot(ys_near, ws_near) / len(near)

    xcb = dot(xs_far, ws_far) / len(far)
    ycb = dot(ys_far, ws_far) / len(far)

    X1, Y1 = solveZ1(xs_near, ys_near, ws_near, xmin, xmax, ymin, ymax)
    X2, Y2 = solveZ2(xca, yca, xcb, ycb, xmin, xmax, ymin, ymax)

    U1 = max(evalZ1(near, X1, Y1), evalZ1(near, X2, Y2))
    U2 = max(evalZ2(xca, yca, xcb, ycb, X1, Y1), evalZ2(xca, yca, xcb, ycb, X2, Y2))

    L1 = evalZ1(near, X1, Y1)
    L2 = evalZ2(xca, yca, xcb, ycb, X2, Y2)

    prob = pulp.LpProblem('FussyModel', pulp.LpMaximize)

    # for first model
    ps = [ pulp.LpVariable(f'p_{i}') for i in range(len(near)) ]
    qs = [ pulp.LpVariable(f'q_{i}') for i in range(len(near)) ]

    # for second model
    ts = [ pulp.LpVariable(f't_{i}', 0) for i in range(4) ]

    lmb = pulp.LpVariable('lambda', 0, 1)
    Z1 = pulp.LpVariable('Z1', 0)
    Z2 = pulp.LpVariable('Z2', 0)
    X = pulp.LpVariable('X', xmin, xmax)
    Y = pulp.LpVariable('Y', ymin, ymax)

    # objective function
    prob += lmb

    # restrictions
    prob += U1 * lmb - L1 * lmb <= U1 - Z1
    prob += U2 * lmb - L2 * lmb <= U2 - Z2

    # from Z1 model
    for p, q, x, y, w in zip(ps, qs, xs_near, ys_near, ws_near):
        prob += p >= x - X
        prob += p >= X - x
        prob += q >= y - Y
        prob += q >= Y - y
        prob += w * p + w * q <= Z1

    # from Z2 model
    prob += Z2 == ts[0] + ts[1] + ts[2] + ts[3]
    
    prob += ts[0] >= X - xca
    prob += ts[0] >= xca - X
    prob += ts[1] >= Y - yca
    prob += ts[1] >= yca - Y

    prob += ts[2] >= X - xcb
    prob += ts[2] >= xcb - X
    prob += ts[3] >= Y - ycb
    prob += ts[3] >= ycb - Y

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    assert pulp.LpStatus[prob.status] == 'Optimal'

    return PT(X.varValue, Y.varValue, w=0, kind='FussyModel'), Z1.varValue + Z2.varValue

def evalZ1(near: List[PT], X: float, Y: float):
    return max(w * (abs(x - X) + abs(y - Y)) for x, y, w, _ in near)

def evalZ2(xca, yca, xcb, ycb, X, Y):
    return abs(xca - X) + abs(yca - Y) + abs(X - xcb) + abs(Y - ycb)

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def extractconstants(arr: List[PT]):
    xs = [ x for x, _, _, _ in arr ]
    ys = [ y for _, y, _, _ in arr ]
    ws = [ w for _, _, w, _ in arr ]

    return xs, ys, ws

def solveZ1(xs: List[float], ys: List[float], ws: List[float], xmin: float, xmax: float, ymin: float, ymax: float):
    n = len(xs)

    prob = pulp.LpProblem('Z1_objective')

    Z1 = pulp.LpVariable('Z1', 0)
    X = pulp.LpVariable('X', xmin, xmax)
    Y = pulp.LpVariable('Y', ymin, ymax)
    ps = [ pulp.LpVariable(f'p_{i}') for i in range(n) ]
    qs = [ pulp.LpVariable(f'q_{i}') for i in range(n) ]

    prob += Z1
    for p, q, x, y, w in zip(ps, qs, xs, ys, ws):
        prob += p >= x - X
        prob += p >= X - x
        prob += q >= y - Y
        prob += q >= Y - y
        prob += w * p + w * q <= Z1

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    assert pulp.LpStatus[prob.status] == 'Optimal'

    return X.varValue, Y.varValue

def solveZ2(xca: float, yca: float, xcb: float, ycb: float, xmin: float, xmax: float, ymin: float, ymax: float):
    prob = pulp.LpProblem('Z2_objective')

    Z2 = pulp.LpVariable('Z2', 0)
    X = pulp.LpVariable('X', xmin, xmax)
    Y = pulp.LpVariable('Y', ymin, ymax)
    ts = [ pulp.LpVariable(f't_{i}', 0) for i in range(4) ]

    prob += Z2
    prob += Z2 == ts[0] + ts[1] + ts[2] + ts[3]
    
    prob += ts[0] >= X - xca
    prob += ts[0] >= xca - X
    prob += ts[1] >= Y - yca
    prob += ts[1] >= yca - Y

    prob += ts[2] >= X - xcb
    prob += ts[2] >= xcb - X
    prob += ts[3] >= Y - ycb
    prob += ts[3] >= ycb - Y

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    assert pulp.LpStatus[prob.status] == 'Optimal'

    return X.varValue, Y.varValue

if __name__ == '__main__':
    near = [ PT(2.5, 2.5, 1), PT(4, 3, 1), PT(7, 2, 1) ]
    far = [ PT(0, 0, 1), PT(5, 0, 1), PT(5, 5, 1), PT(0, 5, 1) ]
    xmin = ymin = -5
    xmax = ymax = 10

    opt, cost = optimize(near, far, xmin, xmax, ymin, ymax)

    print(opt)
    print(cost)