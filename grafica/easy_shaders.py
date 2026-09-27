from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image

import grafica.basic_shapes as bs
from grafica.gpu_shape import GPUShape

__author__ = "Daniel Calderon"
__license__ = "MIT"

SIZE_IN_BYTES = 4

def textureSimpleSetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = Image.open(imgName)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, image.size[0], image.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)

    return texture

class SimpleShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec3 color;\n\n            out vec3 newColor;\n            void main()\n            {\n                gl_Position = vec4(position, 1.0f);\n                newColor = color;\n            }\n            '

        fragment_shader = '\n            #version 330\n            in vec3 newColor;\n\n            out vec4 outColor;\n            void main()\n            {\n                outColor = vec4(newColor, 1.0f);\n            }\n            '

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

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTextureShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec2 texCoords;\n\n            out vec2 outTexCoords;\n\n            void main()\n            {\n                gl_Position = vec4(position, 1.0f);\n                outTexCoords = texCoords;\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            in vec2 outTexCoords;\n\n            out vec4 outColor;\n\n            uniform sampler2D samplerTex;\n\n            void main()\n            {\n                outColor = texture(samplerTex, outTexCoords);\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTransformShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n            \n            uniform mat4 transform;\n\n            in vec3 position;\n            in vec3 color;\n\n            out vec3 newColor;\n\n            void main()\n            {\n                gl_Position = transform * vec4(position, 1.0f);\n                newColor = color;\n            }\n            '

        fragment_shader = '\n            #version 330\n            in vec3 newColor;\n\n            out vec4 outColor;\n\n            void main()\n            {\n                outColor = vec4(newColor, 1.0f);\n            }\n            '

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def setupVAO(self, gpuShape):
        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTextureTransformShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            uniform mat4 transform;\n\n            in vec3 position;\n            in vec2 texCoords;\n\n            out vec2 outTexCoords;\n\n            void main()\n            {\n                gl_Position = transform * vec4(position, 1.0f);\n                outTexCoords = texCoords;\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            in vec2 outTexCoords;\n\n            out vec4 outColor;\n\n            uniform sampler2D samplerTex;\n\n            void main()\n            {\n                outColor = texture(samplerTex, outTexCoords);\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleModelViewProjectionShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n            \n            uniform mat4 projection;\n            uniform mat4 view;\n            uniform mat4 model;\n\n            in vec3 position;\n            in vec3 color;\n\n            out vec3 newColor;\n            void main()\n            {\n                gl_Position = projection * view * model * vec4(position, 1.0f);\n                newColor = color;\n            }\n            '

        fragment_shader = '\n            #version 330\n            in vec3 newColor;\n\n            out vec4 outColor;\n            void main()\n            {\n                outColor = vec4(newColor, 1.0f);\n            }\n            '

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTextureModelViewProjectionShaderProgram:

    def __init__(self):

        vertex_shader = '\n            #version 330\n            \n            uniform mat4 projection;\n            uniform mat4 view;\n            uniform mat4 model;\n\n            in vec3 position;\n            in vec2 texCoords;\n\n            out vec2 outTexCoords;\n\n            void main()\n            {\n                gl_Position = projection * view * model * vec4(position, 1.0f);\n                outTexCoords = texCoords;\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            uniform sampler2D samplerTex;\n\n            in vec2 outTexCoords;\n\n            out vec4 outColor;\n\n            void main()\n            {\n                outColor = texture(samplerTex, outTexCoords);\n            }\n            '

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))

    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

