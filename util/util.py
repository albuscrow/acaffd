import numpy as np


def static_var(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def normalize(n):
    l = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    if l < ZERO:
        return n
    for i in range(3):
        n[i] /= l
    return n


ZERO = 0.000001


def equal_vec(v1, v2):
    return all(abs(v1 - v2) < ZERO)
