import io
from contextlib import redirect_stdout

import pytest

from pyecsca.ec.context import local
from pyecsca.ec.model import ShortWeierstrassModel
from pyecsca.ec.curve import EllipticCurve
from pyecsca.ec.mod import Mod
from pyecsca.ec.mult import (
    LTRMultiplier,
    RTLMultiplier,
    BinaryNAFMultiplier,
    WindowNAFMultiplier,
    SimpleLadderMultiplier, AccumulationOrder, ProcessingDirection, SlidingWindowMultiplier, FixedWindowLTRMultiplier,
)
from pyecsca.ec.params import DomainParameters
from pyecsca.ec.point import Point
from pyecsca.sca.re.rpa import MultipleContext, rpa_point_0y, rpa_point_x0, rpa_distinguish


@pytest.fixture()
def model():
    return ShortWeierstrassModel()


@pytest.fixture()
def coords(model):
    return model.coordinates["projective"]


@pytest.fixture()
def add(coords):
    return coords.formulas["add-2007-bl"]


@pytest.fixture()
def dbl(coords):
    return coords.formulas["dbl-2007-bl"]


@pytest.fixture()
def neg(coords):
    return coords.formulas["neg"]


@pytest.fixture()
def rpa_params(model, coords):
    p = 0x85d265945a4f5681
    a = Mod(0x7fc57b4110698bc0, p)
    b = Mod(0x37113ea591b04527, p)
    gx = Mod(0x80d2d78fddb97597, p)
    gy = Mod(0x5586d818b7910930, p)
    # (0x4880bcf620852a54, 0) RPA point
    # (0, 0x6bed3155c9ada064) RPA point

    infty = Point(coords, X=Mod(0, p), Y=Mod(1, p), Z=Mod(0, p))
    g = Point(coords, X=gx, Y=gy, Z=Mod(1, p))
    curve = EllipticCurve(model, coords, p, infty, dict(a=a, b=b))
    return DomainParameters(curve, g, 0x85d265932d90785c, 1)


def test_x0_point(rpa_params):
    res = rpa_point_x0(rpa_params)
    assert res is not None
    assert res.y == 0


def test_0y_point(rpa_params):
    res = rpa_point_0y(rpa_params)
    assert res is not None
    assert res.x == 0


def test_distinguish(secp128r1, add, dbl, neg):
    multipliers = [LTRMultiplier(add, dbl, None, False, AccumulationOrder.PeqRP, True, True),
                   LTRMultiplier(add, dbl, None, True, AccumulationOrder.PeqRP, True, True),
                   RTLMultiplier(add, dbl, None, False, AccumulationOrder.PeqRP, True),
                   RTLMultiplier(add, dbl, None, True, AccumulationOrder.PeqRP, True),
                   SimpleLadderMultiplier(add, dbl, None, True, True),
                   BinaryNAFMultiplier(add, dbl, neg, None, ProcessingDirection.LTR, AccumulationOrder.PeqRP, True),
                   WindowNAFMultiplier(add, dbl, neg, 3, None, AccumulationOrder.PeqRP, True),
                   WindowNAFMultiplier(add, dbl, neg, 4, None, AccumulationOrder.PeqRP, True),
                   SlidingWindowMultiplier(add, dbl, 3, None, ProcessingDirection.LTR, AccumulationOrder.PeqRP, True),
                   SlidingWindowMultiplier(add, dbl, 3, None, ProcessingDirection.RTL, AccumulationOrder.PeqRP, True),
                   FixedWindowLTRMultiplier(add, dbl, 3, None, AccumulationOrder.PeqRP, True),
                   FixedWindowLTRMultiplier(add, dbl, 8, None, AccumulationOrder.PeqRP, True)]
    for real_mult in multipliers:
        def simulated_oracle(scalar, affine_point):
            point = affine_point.to_model(secp128r1.curve.coordinate_model, secp128r1.curve)
            with local(MultipleContext()) as ctx:
                real_mult.init(secp128r1, point)
                real_mult.multiply(scalar)
            return any(map(lambda P: P.X == 0 or P.Y == 0, ctx.points.keys()))

        with redirect_stdout(io.StringIO()):
            result = rpa_distinguish(secp128r1, multipliers, simulated_oracle)
        assert 1 == len(result)
        assert real_mult == result[0]
