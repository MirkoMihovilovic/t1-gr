from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import grafica.transformations as tr
import grafica.gpu_shape as gs

__author__ = "Daniel Calderon"
__license__ = "MIT"

class SceneGraphNode:

    def __init__(self, name):
        self.name = name
        self.transform = tr.identity()
        self.childs = []

    def clear(self):

        for child in self.childs:
            child.clear()

def findNode(node, name):

    if isinstance(node, gs.GPUShape):
        return None

    if node.name == name:
        return node

    for child in node.childs:
        foundNode = findNode(child, name)
        if foundNode != None:
            return foundNode

    return None

def findTransform(node, name, parentTransform=tr.identity()):

    if isinstance(node, gs.GPUShape):
        return None

    newTransform = np.matmul(parentTransform, node.transform)

    if node.name == name:
        return newTransform

    for child in node.childs:
        foundTransform = findTransform(child, name, newTransform)
        if isinstance(foundTransform, (np.ndarray, np.generic) ):
            return foundTransform

    return None

def findPosition(node, name, parentTransform=tr.identity()):
    foundTransform = findTransform(node, name, parentTransform)

    if isinstance(foundTransform, (np.ndarray, np.generic) ):
        zero = np.array([[0,0,0,1]], dtype=np.float32).T
        foundPosition = np.matmul(foundTransform, zero)
        return foundPosition

    return None

def drawSceneGraphNode(node, pipeline, transformName, parentTransform=tr.identity()):
    assert(isinstance(node, SceneGraphNode))

    newTransform = np.matmul(parentTransform, node.transform)

    if len(node.childs) == 1 and isinstance(node.childs[0], gs.GPUShape):
        leaf = node.childs[0]
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
        pipeline.drawCall(leaf)

    else:
        for child in node.childs:
            drawSceneGraphNode(child, pipeline, transformName, newTransform)

