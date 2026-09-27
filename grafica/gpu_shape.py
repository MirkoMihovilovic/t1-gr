from OpenGL.GL import *
import numpy as np

__author__ = "Daniel Calderon"
__license__ = "MIT"

SIZE_IN_BYTES = 4

class GPUShape:
    def __init__(self):

        self.vao = None
        self.vbo = None
        self.ebo = None
        self.texture = None
        self.size = None

    def initBuffers(self):

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        return self

    def __str__(self):
        return "vao=" + str(self.vao) +\
            "  vbo=" + str(self.vbo) +\
            "  ebo=" + str(self.ebo) +\
            "  tex=" + str(self.texture)

    def fillBuffers(self, vertices, indices, usage):

        vertexData = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        self.size = len(indices)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, usage)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, usage)

    def clear(self):

        if self.texture != None:
            glDeleteTextures(1, [self.texture])

        if self.ebo != None:
            glDeleteBuffers(1, [self.ebo])

        if self.vbo != None:
            glDeleteBuffers(1, [self.vbo])

        if self.vao != None:
            glDeleteVertexArrays(1, [self.vao])

def createGPUShape(pipeline, shape):

    gpuShape = GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape
