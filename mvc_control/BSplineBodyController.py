from mvc_model.aux import BSplineBody


class BSplineBodyControl:
    def __init__(self, size: list):
        if len(size) != 3:
            raise Exception('b spline body size number error')
        if any(i < 0 for i in size):
            raise Exception('b spline body size < 0, error')
        self._b_spline_body = BSplineBody(*size)
