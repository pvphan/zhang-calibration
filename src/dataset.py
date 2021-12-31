"""
Generates synthetic datasets to test calibration code.
"""

import numpy as np


class Checkerboard:
    def __init__(self, numCornersWidth, numCornersHeight, spacing):
        self._cornerPositions = self._createCornerPositions(
                numCornersWidth, numCornersHeight, spacing)

    def _createCornerPositions(self, numCornersWidth,
            numCornersHeight, spacing) -> np.ndarray:
        cornerPositions = []
        for j in range(numCornersHeight):
            for i in range(numCornersWidth):
                x = i * spacing
                y = j * spacing
                cornerPositions.append((x, y, 0))
        return np.array(cornerPositions).reshape(-1, 3)

    def getCornerPositions(self) -> np.ndarray:
        return self._cornerPositions


class Dataset:
    def __init__(self, checkerboard: Checkerboard, K: np.ndarray):
        pass

