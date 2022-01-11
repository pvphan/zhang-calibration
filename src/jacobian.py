import numpy as np
import sympy

from __context__ import src
from src import distortion
from src import mathutils as mu


class ProjectionJacobian:
    """
    Uses sympy to compute expressions and evaluate the partial derivatives
    of the projection function with respect to the variables in the
    parameter vector P (intrinsics, distortion, extrinsics).
    """
    _numExtrinsicParamsPerView = 6
    _epsilon = 1e-100
    def __init__(self, distortionModel: distortion.DistortionModel):
        if distortionModel == distortion.DistortionModel.RadialTangential:
            self._uvExpr = createExpressionIntrinsicProjectionRadTan()
            self._intrinsicSymbols = getIntrinsicRadTanSymbols()
            self._orderedSymbols = getAllOrderedSymbols()
        elif distortionModel == distortion.DistortionModel.FishEye:
            raise NotImplementedError("Fish eye distortion model not yet supported")
        else:
            raise NotImplementedError("Unknown distortion model: {distortionModel}")

        self._intrinsicJacobianBlockExpr = self._createJacobianBlockExpression(self._intrinsicSymbols)
        self._intrinsicJacobianBlockFunction = createLambdaFunction(self._intrinsicJacobianBlockExpr,
                self._orderedSymbols)

        self._extrinsicSymbols = getExtrinsicSymbols()
        self._extrinsicJacobianBlockExpr = self._createJacobianBlockExpression(self._extrinsicSymbols)
        self._extrinsicJacobianBlockFunctions = createLambdaFunction(self._extrinsicJacobianBlockExpr,
                self._orderedSymbols)

    def _createIntrinsicsJacobianBlock(self, intrinsicValues, extrinsicValues, modelPoints):
        intrinsicBlock = self._computeJacobianBlock(self._intrinsicJacobianBlockFunction,
                intrinsicValues, extrinsicValues, modelPoints)
        return intrinsicBlock

    def _createExtrinsicsJacobianBlock(self, intrinsicValues, extrinsicValues, modelPoints):
        extrinsicBlock = self._computeJacobianBlock(self._extrinsicJacobianBlockFunctions,
                intrinsicValues, extrinsicValues, modelPoints)
        return extrinsicBlock

    def _computeJacobianBlock(self, functionBlock, intrinsicValues, extrinsicValues, modelPoints):
        """
        Evaluates the values of J (general purpose)

        Input:
            functionBlock -- (2*N, T) matrix of callable functions to compute the values of
                    the Jacobian for that specific block
            intrinsicValues -- intrinsic parameter values held fixed for this block of J
            extrinsicValues -- extrinsic parameter values held fixed for this block of J
            allModelPoints -- (N, 3) model points which are projected into the camera

        Output:
            blockValues -- (2*N, T) matrix block of the Jacobian J
        """
        P = list(intrinsicValues) + list(extrinsicValues)
        P = [p + self._epsilon for p in P]
        X = mu.col(modelPoints[:,0]) + self._epsilon
        Y = mu.col(modelPoints[:,1]) + self._epsilon
        Z = mu.col(modelPoints[:,2]) + self._epsilon
        N = modelPoints.shape[0]
        functionResults = functionBlock(*P, X, Y, Z)
        blockValues = np.zeros((2*N, functionResults.shape[1]))
        for i in range(functionResults.shape[1]):
            uResult = functionResults[0,i]
            if isinstance(uResult, np.ndarray):
                uResult = uResult.ravel()
            vResult = functionResults[1,i]
            if isinstance(vResult, np.ndarray):
                vResult = vResult.ravel()
            blockValues[::2, i] = uResult
            blockValues[1::2, i] = vResult
        return blockValues

    def _createJacobianBlockExpression(self, derivativeSymbols):
        """
        Input:
            derivativeSymbols -- the symbols with which to take the partial derivative
                    of the projection expression (left-to-right along column dimension)

        Output:
            jacobianBlockExpr -- matrix containing the expressions for the partial
                    derivative of the point projection expression wrt the corresponding
                    derivative symbol
        """
        uExpr, vExpr = self._uvExpr.ravel()
        uExprs = []
        vExprs = []
        for i, paramSymbol in enumerate(derivativeSymbols):
            uExprs.append(sympy.diff(uExpr, paramSymbol))
            vExprs.append(sympy.diff(vExpr, paramSymbol))

        jacobianBlockExpr = sympy.Matrix([uExprs, vExprs])
        return jacobianBlockExpr

    def compute(self, P, allModelPoints):
        """
        Input:
            P -- parameter value vector (intrinsics, distortion, extrinsics)
            allModelPoints -- (N, 3) model points which are projected into the camera

        Output:
            J -- Jacobian matrix made up of the partial derivatives of the
                    projection function wrt each of the input parameters in P
        """
        if isinstance(P, np.ndarray):
            P = P.ravel()
        M = len(allModelPoints)
        intrinsicValues = P[:-M * self._numExtrinsicParamsPerView]
        MN = sum([modelPoints.shape[0] for modelPoints in allModelPoints])
        L = len(self._intrinsicSymbols)
        K = L + self._numExtrinsicParamsPerView * M
        J = np.zeros((2*MN, K))

        rowIndexJ = 0
        for i in range(M):
            modelPoints = allModelPoints[i]
            intrinsicStartCol = L+i*self._numExtrinsicParamsPerView
            intrinsicEndCol = intrinsicStartCol + self._numExtrinsicParamsPerView
            extrinsicValues = P[intrinsicStartCol:intrinsicEndCol]
            N = len(modelPoints)
            colIndexJ = L+i*self._numExtrinsicParamsPerView

            intrinsicBlock = self._createIntrinsicsJacobianBlock(
                    intrinsicValues, extrinsicValues, modelPoints)
            extrinsicBlock = self._createExtrinsicsJacobianBlock(
                    intrinsicValues, extrinsicValues, modelPoints)

            J[rowIndexJ:rowIndexJ + 2*N, :L] = intrinsicBlock
            J[rowIndexJ:rowIndexJ + 2*N, colIndexJ:colIndexJ+self._numExtrinsicParamsPerView] = \
                    extrinsicBlock
            rowIndexJ += 2*N
        return J


def createJacRadTan() -> ProjectionJacobian:
    distortionModel = distortion.DistortionModel.RadialTangential
    jac = ProjectionJacobian(distortionModel)
    return jac


def createExpressionIntrinsicProjectionRadTan():
    """
    Creates the base expression for point projection (u, v) from P vector symbols
    and a single world point wP = (X, Y, Z), with
            P = (α, β, γ, uc, uv, k1, k2, p1, p2, k3, ρx, ρy, ρz, tx, ty, tz)
    """
    isSymbolic = True
    α, β, γ, uc, vc, k1, k2, p1, p2, k3 = getIntrinsicRadTanSymbols()
    A = np.array([
        [α, γ, uc],
        [0, β, vc],
        [0, 0,  1],
    ])
    ρx, ρy, ρz, tx, ty, tz = getExtrinsicSymbols()
    R = mu.eulerToRotationMatrix((ρx, ρy, ρz), isSymbolic=isSymbolic)
    cMw = np.array([
        [R[0,0], R[0,1], R[0,2], tx],
        [R[1,0], R[1,1], R[1,2], ty],
        [R[2,0], R[2,1], R[2,2], tz],
        [     0,      0,      0,  1],
    ])
    X, Y, Z = getModelPointSymbols()
    wPHom = mu.col((X, Y, Z, 1))
    cPHom = (cMw @ wPHom).T
    cP = mu.unhom(cPHom)
    k = (k1, k2, p1, p2, k3)
    uvExpr = distortion.projectWithDistortion(A, cP, k, isSymbolic=isSymbolic)
    return uvExpr


def getIntrinsicRadTanSymbols():
    return tuple(sympy.symbols("α β γ uc vc k1 k2 p1 p2 k3"))


def getExtrinsicSymbols():
    return tuple(sympy.symbols("ρx ρy ρz tx ty tz"))


def getModelPointSymbols():
    return tuple(sympy.symbols("X Y Z"))


def getAllOrderedSymbols():
    intrinsicSymbols = getIntrinsicRadTanSymbols()
    extrinsicSymbols = getExtrinsicSymbols()
    modelPointSymbol = getModelPointSymbols()
    return intrinsicSymbols + extrinsicSymbols + modelPointSymbol


def createLambdaFunction(expression, orderedSymbols):
    f = sympy.lambdify(orderedSymbols, expression, "numpy")
    return f

