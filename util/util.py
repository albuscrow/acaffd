import numpy as np
import config as conf
import math


def static_var(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def normalize(n):
    l = length_vec3(n)
    if l < ZERO:
        return n
    for i in range(3):
        n[i] /= l
    return n


def length_vec3(n):
    return (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5


def power(b, e):
    if e == 0:
        return 1
    if b < 0.00001:
        return 0
    return math.pow(b, e)


ZERO = 0.000001


def equal_vec(v1: np.ndarray, v2: np.ndarray):
    return equal_zero_vec(v1 - v2)


def equal_zero_vec(v1: np.ndarray):
    return all(abs(v1) < ZERO)


def filter_for_speed(src: str = None, file_name: str = None) -> str:
    if src:
        remain = []
        if conf.IS_FAST_MODE and not file_name.endswith('qml'):
            src = src.replace('#version 450', '#version 450\n#define TIME\n')
            remain = [src]
        else:
            status = conf.NORMAL
            for l in src.splitlines():
                if l.strip().startswith(conf.IF):
                    status = conf.TIME
                    continue
                if l.strip().startswith(conf.ELSE):
                    status = conf.ELSE_TIME
                    continue
                if l.strip().startswith(conf.ENDIF):
                    status = conf.NORMAL
                    continue
                if status == conf.NORMAL \
                        or (status == conf.TIME and conf.IS_FAST_MODE) \
                        or (status == conf.ELSE_TIME and not conf.IS_FAST_MODE):
                    remain.append(l)
        output_file_name = file_name + '.tmp'
        with open(output_file_name, 'w') as file:
            file.write('\n'.join(remain))
        return '\n'.join(remain)
    else:
        with open(file_name) as file:
            src = filter_for_speed(src=file.read(), file_name=file_name)
        output_file_name = file_name + '.tmp'
        with open(output_file_name, 'w') as file:
            file.write(src)
        return output_file_name


def create_rotate(a, x, y, z):
    rm = np.array([0] * 16, dtype='f4')
    rm[3] = 0
    rm[7] = 0
    rm[11] = 0
    rm[12] = 0
    rm[13] = 0
    rm[14] = 0
    rm[15] = 1
    a *= (math.pi / 180.0)
    s = math.sin(a)
    c = math.cos(a)
    if 1.0 == x and 0.0 == y and 0.0 == z:
        rm[5] = c
        rm[10] = c
        rm[6] = s
        rm[9] = -s
        rm[1] = 0
        rm[2] = 0
        rm[4] = 0
        rm[8] = 0
        rm[0] = 1
    elif 0.0 == x and 1.0 == y and 0.0 == z:
        rm[0] = c
        rm[10] = c
        rm[8] = s
        rm[2] = -s
        rm[1] = 0
        rm[4] = 0
        rm[6] = 0
        rm[9] = 0
        rm[5] = 1
    elif 0.0 == x and 0.0 == y and 1.0 == z:
        rm[0] = c
        rm[5] = c
        rm[1] = s
        rm[4] = -s
        rm[2] = 0
        rm[6] = 0
        rm[8] = 0
        rm[9] = 0
        rm[10] = 1
    else:
        length = length_vec3([x, y, z])
        if 1.0 != length:
            recip_len = 1.0 / length
            x *= recip_len
            y *= recip_len
            z *= recip_len
        nc = 1.0 - c
        xy = x * y
        yz = y * z
        zx = z * x
        xs = x * s
        ys = y * s
        zs = z * s
        rm[0] = x * x * nc + c
        rm[4] = xy * nc - zs
        rm[8] = zx * nc + ys
        rm[1] = xy * nc + zs
        rm[5] = y * y * nc + c
        rm[9] = yz * nc - xs
        rm[2] = zx * nc - ys
        rm[6] = yz * nc + xs
        rm[10] = z * z * nc + c
    return np.asmatrix(rm.reshape((4, 4)))
