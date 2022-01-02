import numpy as np

from __context__ import src
from src import checkerboard
from src import mathutils as mu


class VirtualCamera:
    def __init__(self, intrinsicMatrix: np.ndarray, distortionVector: tuple,
            imageWidth: int, imageHeight: int):
        self._intrinsicMatrix = intrinsicMatrix
        self._distortionVector = distortionVector
        self._imageWidth = imageWidth
        self._imageHeight = imageHeight

    def getGroundTruthIntrinsicMatrix(self):
        return self._intrinsicMatrix

    def getGroundTruthDistortionVector(self):
        return self._distortionVector

    def getImageWidth(self):
        return self._imageWidth

    def getImageHeight(self):
        return self._imageHeight

    def measureDetectedPoints(self, checkerboard: checkerboard.Checkerboard,
            boardPoseInCamera: np.ndarray):
        cornerPointsInBoard = checkerboard.getCornerPositions()
        camera_M_board = boardPoseInCamera
        cornerPointsInCamera = (camera_M_board @ mu.homog(cornerPointsInBoard).T).T
        projectedPointsInSensor = mu.project(
                self._intrinsicMatrix, np.eye(4), cornerPointsInCamera)
        measuredPoints = projectedPointsInSensor[:,:2]
        pointInImageSlice = np.s_[
                (measuredPoints[:,0] > 0) & (measuredPoints[:,0] < self._imageWidth)
                & (measuredPoints[:,1] > 0) & (measuredPoints[:,1] < self._imageHeight)
        ]
        return measuredPoints[pointInImageSlice], cornerPointsInBoard[pointInImageSlice]

