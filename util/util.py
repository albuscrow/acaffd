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


def equal_zero_vec(v1):
    return all(abs(v1) < ZERO)


def filter_for_speed(src: str = None, file_name: str = None) -> str:
    if src:
        status = conf.NORMAL
        remain = []
        for l in src.splitlines():
            if l.strip().startswith(conf.IF):
                if l.strip().endswith(conf.TIME):
                    status = conf.TIME
                else:
                    status = conf.TESS
                continue
            if l.strip().startswith(conf.ELSE):
                if status == conf.TIME:
                    status = conf.ELSE_TIME
                else:
                    status = conf.ELSE_TESS
                continue
            if l.strip().startswith(conf.ENDIF):
                status = conf.NORMAL
                continue
            if status == conf.NORMAL \
                    or (status == conf.TIME and conf.IS_FAST_MODE) \
                    or (status == conf.ELSE_TIME and not conf.IS_FAST_MODE) \
                    or (status == conf.TESS and conf.IS_TESS_MODE) \
                    or (status == conf.ELSE_TESS and not conf.IS_TESS_MODE):
                remain.append(l)
        # print('\n'.join([str(i) + " " + s for i, s in zip(range(len(remain)), remain)]))
        return '\n'.join(remain)
    else:
        with open(file_name) as file:
            src = filter_for_speed(src=file.read())
        output_file_name = file_name + '.tmp'
        with open(output_file_name, 'w') as file:
            file.write(src)
        return output_file_name
