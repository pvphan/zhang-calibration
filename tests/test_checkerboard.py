import unittest

import numpy as np

from __context__ import src
from src import checkerboard


class TestCheckerboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.numCornersWidth = 9
        cls.numCornersHeight = 6
        spacing = 0.050
        cls.checkerboard = checkerboard.Checkerboard(
                cls.numCornersWidth, cls.numCornersHeight, spacing)

    def testgetCornerPositions(self):
        cornerPositions = self.checkerboard.getCornerPositions()
        self.assertIsInstance(cornerPositions, np.ndarray)
        expectedNumPositions = self.numCornersWidth * self.numCornersHeight
        self.assertEqual(cornerPositions.shape, (expectedNumPositions, 3))


if __name__ == "__main__":
    unittest.main()

