import unittest
from unittest.mock import MagicMock

import numpy as np

from __context__ import src
from src import dataset
from src import mathutils as mu


class TestCheckerboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.numCornersWidth = 9
        cls.numCornersHeight = 6
        spacing = 0.050
        cls.checkerboard = dataset.Checkerboard(
                cls.numCornersWidth, cls.numCornersHeight, spacing)

    def testgetCornerPositions(self):
        cornerPositions = self.checkerboard.getCornerPositions()
        self.assertIsInstance(cornerPositions, np.ndarray)
        expectedNumPositions = self.numCornersWidth * self.numCornersHeight
        self.assertEqual(cornerPositions.shape, (expectedNumPositions, 3))


class TestVirtualCamera(unittest.TestCase):
    def testmeasureDetectedPoints(self):
        imageWidth = 720
        imageHeight = 480
        intrinsicMatrix = np.array([
            [450,   0, 360],
            [  0, 450, 240],
            [  0,   0,   1],
        ], dtype=np.float64)
        k1 = 0.5
        k2 = 0.2
        p1 = 0
        p2 = 0
        k3 = 0
        distortionCoeffients = (k1, k2, p1, p2, k3)
        checkerboard = MagicMock()
        cornerPositions = np.array([
            [0.0, 0.0, 0],
            [0.1, 0.0, 0],
            [0.2, 0.0, 0],
            [0.3, 0.0, 0],
            [0.0, 0.1, 0],
            [0.1, 0.1, 0],
            [0.2, 0.1, 0],
            [0.3, 0.1, 0],
        ])
        checkerboard.getCornerPositions.return_value = cornerPositions

        virtualCamera = dataset.VirtualCamera(intrinsicMatrix, distortionCoeffients,
                imageWidth, imageHeight)

        R = mu.eulerToRotationMatrix((0, 0, 180))
        t = (0.05, 0.05, 2)
        cameraPoseInBoard = mu.poseFromRT(R, t)
        boardPoseInCamera = np.linalg.inv(cameraPoseInBoard)

        measuredPointsSensor, measuredPointsPosition = virtualCamera.measureDetectedPoints(
                checkerboard, boardPoseInCamera)

        self.assertEqual(measuredPointsSensor.shape[0], measuredPointsPosition.shape[0])
        self.assertEqual(measuredPointsSensor.shape[1], 2)
        self.assertEqual(measuredPointsPosition.shape[1], 3)


if __name__ == "__main__":
    unittest.main()

