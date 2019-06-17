# -*- coding: utf-8 -*-
#
from __future__ import division

import collections

import numpy
import sympy


TriangleScheme = collections.namedtuple(
    "TriangleScheme", ["name", "degree", "weights", "bary"]
)


def _s3(symbolic):
    frac = sympy.Rational if symbolic else lambda x, y: x / y
    return numpy.full((1, 3), frac(1, 3))


def _s21(a):
    a = numpy.array(a)
    b = 1 - 2 * a
    return numpy.array([[a, a, b], [a, b, a], [b, a, a]])


def _s111(a, b):
    c = 1 - a - b
    return numpy.array(
        [[a, b, c], [c, a, b], [b, c, a], [b, a, c], [c, b, a], [a, c, b]]
    )


def _s111ab(a, b):
    c = 1 - a - b
    out = numpy.array(
        [[a, b, c], [c, a, b], [b, c, a], [b, a, c], [c, b, a], [a, c, b]]
    )
    out = numpy.swapaxes(out, 0, 1)
    return out


def _rot_ab(a, b):
    c = 1 - a - b
    out = numpy.array([[a, b, c], [c, a, b], [b, c, a]])
    out = numpy.swapaxes(out, 0, 1)
    return out


def _collapse0(a):
    """Collapse all dimensions of `a` except the first.
    """
    return a.reshape(a.shape[0], -1)


def untangle2(data, symbolic=False):
    bary = []
    weights = []

    if "s3" in data:
        d = numpy.array(data["s3"]).T
        bary.append(_s3(symbolic).T)
        weights.append(numpy.tile(d[0], 1))

    if "s2" in data:
        d = numpy.array(data["s2"]).T
        s2_data = _s21(d[1])
        bary.append(_collapse0(s2_data))
        weights.append(numpy.tile(d[0], 3))

    if "s1" in data:
        d = numpy.array(data["s1"]).T
        s1_data = _s111ab(*d[1:])
        bary.append(_collapse0(s1_data))
        weights.append(numpy.tile(d[0], 6))

    if "rot" in data:
        d = numpy.array(data["rot"]).T
        rot_data = _rot_ab(*d[1:])
        bary.append(_collapse0(rot_data))
        weights.append(numpy.tile(d[0], 3))

    bary = numpy.column_stack(bary).T
    weights = numpy.concatenate(weights)
    return bary, weights


def s3(weight, symbolic=False):
    frac = sympy.Rational if symbolic else lambda x, y: x / y
    return numpy.array([weight]), numpy.full((1, 3), frac(1, 3))


def s2(*data):
    w, a = numpy.array(data).T
    b = 1 - 2 * a
    points = _stack_first_last([[a, a, b], [a, b, a], [b, a, a]])
    weights = numpy.tile(w, 3)
    return weights, points


def s1(*data):
    w, a, b = numpy.array(data).T
    c = 1 - a - b
    points = _stack_first_last(
        [[a, b, c], [c, a, b], [b, c, a], [b, a, c], [c, b, a], [a, c, b]]
    )
    weights = numpy.tile(w, 6)
    return weights, points


def r(*data):
    w, r = numpy.array(data).T
    a = r + (1 - r) / 3
    b = (1 - a) / 2
    points = _stack_first_last([[a, b, b], [b, a, b], [b, b, a]])
    weights = numpy.tile(w, 3)
    return weights, points


def rot_ab(*data):
    w, a, b = numpy.array(data).T
    c = 1 - a - b
    points = _stack_first_last([[a, b, c], [c, a, b], [b, c, a]])
    weights = numpy.tile(w, 3)
    return weights, points


def mirror(*data):
    w, a, b = numpy.array(data).T
    c = 1 - a - b
    points = _stack_first_last([[a, b, c], [b, a, c]])
    weights = numpy.tile(w, 2)
    return weights, points


def alpha(*data):
    """From the article Liu-Vinokur:

    mu_i = (1 + (n-1) alpha) / n,
    mu_j = (1 - alpha) / n    for j!=i,

    where n is the number of vertices
    """
    w, alpha = numpy.array(data).T
    a = (1 + 2 * alpha) / 3
    b = (1 - alpha) / 3
    points = _stack_first_last([[a, b, b], [b, a, b], [b, b, a]])
    weights = numpy.tile(w, 3)
    return weights, points


def gamma_delta(*data):
    """From the article Liu-Vinokur:

    mu_i = (1 + (n-1) gamma - delta) / n,
    mu_j = (1 + (n-1) delta - gamma) / n,
    mu_k = (1 - gamma - delta) / n    for k!=i, k!=j,

    where n is the number of vertices
    """
    w, gamma, delta = numpy.array(data).T
    a = (1 + 2 * gamma - delta) / 3
    b = (1 + 2 * delta - gamma) / 3
    c = (1 - gamma - delta) / 3
    points = _stack_first_last(
        [[a, b, c], [c, a, b], [b, c, a], [a, c, b], [b, a, c], [c, b, a]]
    )
    weights = numpy.tile(w, 6)
    return weights, points


def _stack_first_last(arr):
    """Stacks an input array of shape (i, j, k) such that the output array is of shape
    (i*k, j).
    """
    arr = numpy.swapaxes(arr, 0, 1)
    return arr.reshape(arr.shape[0], -1).T


def concat(*data):
    weights = numpy.concatenate([t[0] for t in data])
    points = numpy.vstack([t[1] for t in data])
    return weights, points
