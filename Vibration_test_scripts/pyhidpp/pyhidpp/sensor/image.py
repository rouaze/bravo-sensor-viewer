import numpy as np

class ImageCalibration:

    c_100: np.ndarray
    c_500: np.ndarray
    k: np.ndarray
    q: np.ndarray

    def __init__(self, c_100, c_500) -> None:
        self.c_100 = c_100
        self.c_500 = c_500
        self.k = 400 / (self.c_500 - self.c_100)
        self.q = 100 - self.k * self.c_100
