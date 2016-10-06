# -*- coding: utf-8 -*-
#
import numpy
import numpy.testing
import quadrature
import sympy

import os
import matplotlib as mpl
if 'DISPLAY' not in os.environ:
    # headless mode, for remote executions (and travis)
    mpl.use('Agg')
from matplotlib import pyplot as plt


def _integrate_exact(f, quadrilateral):
    xi = sympy.DeferredVector('xi')
    pxi = quadrilateral[0] * 0.25*(1.0 + xi[0])*(1.0 + xi[1]) \
        + quadrilateral[1] * 0.25*(1.0 - xi[0])*(1.0 + xi[1]) \
        + quadrilateral[2] * 0.25*(1.0 - xi[0])*(1.0 - xi[1]) \
        + quadrilateral[3] * 0.25*(1.0 + xi[0])*(1.0 - xi[1])
    # determinant of the transformation matrix
    det_J = sympy.simplify(
        + sympy.diff(pxi[0], xi[0]) * sympy.diff(pxi[1], xi[1])
        - sympy.diff(pxi[1], xi[0]) * sympy.diff(pxi[0], xi[1])
        )
    # we cannot use abs(), see <https://github.com/sympy/sympy/issues/4212>.
    abs_det_J = sympy.Piecewise((det_J, det_J >= 0), (-det_J, det_J < 0))

    g_xi = sympy.simplify(f(pxi))

    exact = sympy.integrate(
        sympy.integrate(abs_det_J * g_xi, (xi[1], -1, 1)),
        (xi[0], -1, 1)
        )
    return float(exact)


def _create_test_monomials(degree):
    '''Returns a list of all monomials up to degree :max_degree:.
    '''
    monomials = []
    for k in range(degree+1):
        for i in range(k+1):
            monomials.append(lambda x: x[0]**(k-i) * x[1]**i)
    return monomials


def test_generator():
    from quadrature.quadrilateral import From1d
    quadrilateral = numpy.array([
        [-2, -1],
        [+1, -1],
        [+1, +1],
        [-2, +1],
        ])
    schemes = [
        From1d(quadrature.line.Midpoint()),
        From1d(quadrature.line.Trapezoidal()),
        From1d(quadrature.line.GaussLegendre(1)),
        From1d(quadrature.line.GaussLegendre(2)),
        From1d(quadrature.line.GaussLegendre(3)),
        From1d(quadrature.line.GaussLegendre(4)),
        From1d(quadrature.line.NewtonCotesClosed(1)),
        From1d(quadrature.line.NewtonCotesClosed(2)),
        From1d(quadrature.line.NewtonCotesClosed(3)),
        From1d(quadrature.line.NewtonCotesClosed(4)),
        From1d(quadrature.line.NewtonCotesOpen(2)),
        From1d(quadrature.line.NewtonCotesOpen(3)),
        From1d(quadrature.line.NewtonCotesOpen(4)),
        From1d(quadrature.line.NewtonCotesOpen(5)),
        ]
    for scheme in schemes:
        yield check_quadrilateral_scheme, scheme, quadrilateral


def check_quadrilateral_scheme(scheme, quadrilateral):
    # Test integration until we get to a polynomial degree `d` that can no
    # longer be integrated exactly. The scheme's degree is `d-1`.
    success = True
    degree = 0
    while success:
        for poly in _create_test_monomials(degree):
            exact_val = _integrate_exact(poly, quadrilateral)
            val = quadrature.quadrilateral.integrate(
                    poly, quadrilateral, scheme
                    )
            if abs(exact_val - val) > 1.0e-10:
                success = False
                break
        if not success:
            break
        degree += 1
    numpy.testing.assert_equal(degree-1, scheme.degree)
    return


def test_show():
    quadrilateral = numpy.array([
        [0, 0],
        [2, -0.5],
        [1.5, 1.0],
        [0.5, 0.7],
        ])
    # quadrilateral = numpy.array([
    #     [-1, -1],
    #     [+1, -1],
    #     [+1, +1],
    #     [-1, +1],
    #     ])
    quadrature.quadrilateral.show(
        quadrilateral,
        quadrature.quadrilateral.From1d(
            quadrature.line.NewtonCotesClosed(4)
            )
        )
    return


if __name__ == '__main__':
    test_show()
    plt.show()
