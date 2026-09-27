from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.font8x8_basic as f88

__author__ = "Daniel Calderon"
__license__ = "MIT"

def toBit(number, bit):
    return int((number & bit) != 0)

def generateTextBitsTexture():

    assert f88.font8x8_basic.shape == (128,8)

    bits = np.zeros(shape=(8,8,128), dtype=np.uint8)

    for k in range(128):
        for i in range(8):
            row = f88.font8x8_basic[k, i]
            bits[0, i, k] = toBit(row, 1)
            bits[1, i, k] = toBit(row, 2)
            bits[2, i, k] = toBit(row, 4)
            bits[3, i, k] = toBit(row, 8)
            bits[4, i, k] = toBit(row, 16)
            bits[5, i, k] = toBit(row, 32)
            bits[6, i, k] = toBit(row, 64)
            bits[7, i, k] = toBit(row, 128)

    return bits

def toOpenGLTexture(textBitsTexture):

    assert textBitsTexture.shape == (8, 8, 128)

    data = np.copy(textBitsTexture)
    data.reshape((8*8*128,1), order='C')

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_3D, texture)

    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexImage3D(GL_TEXTURE_3D, 0, GL_RED, 128, 8, 8, 0, GL_RED, GL_UNSIGNED_BYTE, data)

    return texture

def getCharacterShape(char):

    k = ord(char)

    vertices = [

        0, 0, 0, k, 8, 0, \
        1, 0, 0, k, 8, 8, \
        1, 1, 0, k, 0, 8, \
        0, 1, 0, k, 0, 0
    ]

    indices = [

        0,1,2,\

        2,3,0
    ]

    return bs.Shape(vertices, indices)

def textToShape(text, charWidth, charHeight):

    shape = bs.Shape([],[])

    for i in range(len(text)):
        char = text[i]
        charShape = getCharacterShape(char)
        bs.applyOffset(charShape, 6, [i, 0, 0])
        bs.scaleVertices(charShape, 6, [charWidth, charHeight, 1])
        bs.merge(shape, 6, charShape)

    return shape

class TextureTextRendererShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            uniform mat4 transform;\n\n            in vec3 position;\n            in vec3 texCoords;\n\n            out vec3 outTexCoords;\n\n            void main()\n            {\n                gl_Position = transform * vec4(position, 1.0f);\n                outTexCoords = texCoords;\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            in vec3 outTexCoords;\n\n            out vec4 outColor;\n\n            uniform vec4 fontColor;\n            uniform vec4 backColor;\n\n            uniform sampler3D samplerTex;\n\n            void main()\n            {\n                vec4 data = texelFetch(samplerTex, ivec3(outTexCoords.xyz), 0);\n                if (data.r != 0)\n                {\n                    outColor = fontColor;\n                }\n                else\n                {\n                    outColor = backColor;\n                }\n            }\n            '

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    def setupVAO(self, gpuShape):
        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, es.GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_3D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

