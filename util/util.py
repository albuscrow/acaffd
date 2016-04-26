import numpy as np
import config as conf


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


def filter_for_speed(file_name: str):
    with open(file_name) as file:
        if not conf.IS_FAST_MODE:
            src = file.read()
        remove = False
        remain = []
        for l in file:
            if l.startswith(conf.QML_COMMENT_FOR_TIME):
                remove = not remove
                continue
            if not remove:
                remain.append(l)
        src = ''.join(remain)
    output_file_name = file_name + '.tmp'
    with open(output_file_name, 'w') as file:
        file.write(src)
    return output_file_name
