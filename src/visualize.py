"""
Convenience functions to visualize a simple scene of points in a virtual camera.
"""
import imageio
import numpy as np


def writeDetectionsImage(measuredPointsInSensor, w, h, outputPath):
    image = createDetectionsImage(measuredPointsInSensor, w, h)
    imageio.imwrite(outputPath, image)


def createDetectionsImage(measuredPointsInSensor, w, h):
    image = createBlankImage(w, h)
    length = 9
    teal = (0, 255, 255)
    drawCrosses(image, measuredPointsInSensor, length, teal)
    return image


def drawCrosses(image, points, length, color):
    for point in points:
        drawCross(image, point, length, color)


def drawCross(image, point, length, color):
    h, w = image.shape[:2]
    u, v = np.rint(point).astype(int)
    if not (0 < u < w and 0 < v < h):
        return
    rowRange = np.arange(v - length//2, v + length//2 + 1)
    rowRange = np.clip(rowRange, 0, h)
    colRange = np.arange(u - length//2, u + length//2 + 1)
    colRange = np.clip(colRange, 0, w)
    image[v, colRange] = color
    image[rowRange, u] = color


def createBlankImage(w, h):
    return np.zeros((h, w, 3), dtype=np.uint8)
