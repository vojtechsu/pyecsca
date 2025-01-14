from copy import copy
from typing import Optional
from public import public

from .base import ScalarMultiplier, ScalarMultiplicationAction
from ..formula import (
    AdditionFormula,
    DoublingFormula,
    ScalingFormula,
    LadderFormula,
    DifferentialAdditionFormula
)
from ..point import Point


@public
class LadderMultiplier(ScalarMultiplier):
    """Montgomery ladder multiplier, using a three input, two output ladder formula."""

    requires = {LadderFormula}
    optionals = {DoublingFormula, ScalingFormula}
    complete: bool

    def __init__(
            self,
            ladd: LadderFormula,
            dbl: Optional[DoublingFormula] = None,
            scl: Optional[ScalingFormula] = None,
            complete: bool = True,
            short_circuit: bool = True,
    ):
        super().__init__(short_circuit=short_circuit, ladd=ladd, dbl=dbl, scl=scl)
        self.complete = complete
        if (not complete or short_circuit) and dbl is None:
            raise ValueError

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not isinstance(other, LadderMultiplier):
            return False
        return self.formulas == other.formulas and self.short_circuit == other.short_circuit and self.complete == other.complete

    def multiply(self, scalar: int) -> Point:
        if not self._initialized:
            raise ValueError("ScalarMultiplier not initialized.")
        with ScalarMultiplicationAction(self._point, scalar) as action:
            if scalar == 0:
                return action.exit(copy(self._params.curve.neutral))
            q = self._point
            if self.complete:
                p0 = copy(self._params.curve.neutral)
                p1 = self._point
                top = self._params.order.bit_length() - 1
            else:
                p0 = copy(q)
                p1 = self._dbl(q)
                top = scalar.bit_length() - 2
            for i in range(top, -1, -1):
                if scalar & (1 << i) == 0:
                    p0, p1 = self._ladd(q, p0, p1)
                else:
                    p1, p0 = self._ladd(q, p1, p0)
            if "scl" in self.formulas:
                p0 = self._scl(p0)
            return action.exit(p0)


@public
class SimpleLadderMultiplier(ScalarMultiplier):
    """Montgomery ladder multiplier, using addition and doubling formulas."""

    requires = {AdditionFormula, DoublingFormula}
    optionals = {ScalingFormula}
    complete: bool

    def __init__(
            self,
            add: AdditionFormula,
            dbl: DoublingFormula,
            scl: Optional[ScalingFormula] = None,
            complete: bool = True,
            short_circuit: bool = True,
    ):
        super().__init__(short_circuit=short_circuit, add=add, dbl=dbl, scl=scl)
        self.complete = complete

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not isinstance(other, SimpleLadderMultiplier):
            return False
        return self.formulas == other.formulas and self.short_circuit == other.short_circuit and self.complete == other.complete

    def multiply(self, scalar: int) -> Point:
        if not self._initialized:
            raise ValueError("ScalarMultiplier not initialized.")
        with ScalarMultiplicationAction(self._point, scalar) as action:
            if scalar == 0:
                return action.exit(copy(self._params.curve.neutral))
            if self.complete:
                top = self._params.order.bit_length() - 1
            else:
                top = scalar.bit_length() - 1
            p0 = copy(self._params.curve.neutral)
            p1 = copy(self._point)
            for i in range(top, -1, -1):
                if scalar & (1 << i) == 0:
                    p1 = self._add(p0, p1)
                    p0 = self._dbl(p0)
                else:
                    p0 = self._add(p0, p1)
                    p1 = self._dbl(p1)
            if "scl" in self.formulas:
                p0 = self._scl(p0)
            return action.exit(p0)


@public
class DifferentialLadderMultiplier(ScalarMultiplier):
    """Montgomery ladder multiplier, using differential addition and doubling formulas."""

    requires = {DifferentialAdditionFormula, DoublingFormula}
    optionals = {ScalingFormula}
    complete: bool

    def __init__(
            self,
            dadd: DifferentialAdditionFormula,
            dbl: DoublingFormula,
            scl: Optional[ScalingFormula] = None,
            complete: bool = True,
            short_circuit: bool = True,
    ):
        super().__init__(short_circuit=short_circuit, dadd=dadd, dbl=dbl, scl=scl)
        self.complete = complete

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not isinstance(other, DifferentialLadderMultiplier):
            return False
        return self.formulas == other.formulas and self.short_circuit == other.short_circuit and self.complete == other.complete

    def multiply(self, scalar: int) -> Point:
        if not self._initialized:
            raise ValueError("ScalarMultiplier not initialized.")
        with ScalarMultiplicationAction(self._point, scalar) as action:
            if scalar == 0:
                return action.exit(copy(self._params.curve.neutral))
            if self.complete:
                top = self._params.order.bit_length() - 1
            else:
                top = scalar.bit_length() - 1
            q = self._point
            p0 = copy(self._params.curve.neutral)
            p1 = copy(q)
            for i in range(top, -1, -1):
                if scalar & (1 << i) == 0:
                    p1 = self._dadd(q, p0, p1)
                    p0 = self._dbl(p0)
                else:
                    p0 = self._dadd(q, p0, p1)
                    p1 = self._dbl(p1)
            if "scl" in self.formulas:
                p0 = self._scl(p0)
            return action.exit(p0)
