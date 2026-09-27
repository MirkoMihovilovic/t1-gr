from OpenGL.GL import *
import OpenGL.GL.shaders
from grafica.gpu_shape import GPUShape

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.assets_path import getAssetPath

class SimpleFlatShaderProgram():

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec3 color;\n            in vec3 normal;\n\n            flat out vec4 vertexColor;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            uniform vec3 lightPosition;\n            uniform vec3 viewPosition;\n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n            \n            void main()\n            {\n                vec3 vertexPos = vec3(model * vec4(position, 1.0));\n                gl_Position = projection * view * vec4(vertexPos, 1.0);\n\n                \n                vec3 ambient = Ka * La;\n                \n                \n                vec3 norm = normalize(normal);\n                vec3 toLight = lightPosition - vertexPos;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(norm, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - vertexPos);\n                vec3 reflectDir = reflect(-lightDir, norm);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                \n                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * color;\n                vertexColor = vec4(result, 1.0);\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            flat in vec4 vertexColor;\n            out vec4 fragColor;\n\n            void main()\n            {\n                fragColor = vertexColor;\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTextureFlatShaderProgram():

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec2 texCoords;\n            in vec3 normal;\n\n            out vec2 fragTexCoords;\n            flat out vec3 vertexLightColor;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            uniform vec3 lightPosition; \n            uniform vec3 viewPosition; \n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n            \n            void main()\n            {\n                vec3 vertexPos = vec3(model * vec4(position, 1.0));\n                gl_Position = projection * view * vec4(vertexPos, 1.0);\n\n                fragTexCoords = texCoords;\n\n                \n                vec3 ambient = Ka * La;\n                \n                \n                vec3 norm = normalize(normal);\n                vec3 toLight = lightPosition - vertexPos;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(norm, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - vertexPos);\n                vec3 reflectDir = reflect(-lightDir, norm);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                \n                vertexLightColor = ambient + ((diffuse + specular) / attenuation);\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            flat in vec3 vertexLightColor;\n            in vec2 fragTexCoords;\n\n            out vec4 fragColor;\n\n            uniform sampler2D samplerTex;\n\n            void main()\n            {\n                vec4 textureColor = texture(samplerTex, fragTexCoords);\n                fragColor = vec4(vertexLightColor, 1.0) * textureColor;\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleGouraudShaderProgram():

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec3 color;\n            in vec3 normal;\n\n            out vec4 vertexColor;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            uniform vec3 lightPosition;\n            uniform vec3 viewPosition;\n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n            \n            void main()\n            {\n                vec3 vertexPos = vec3(model * vec4(position, 1.0));\n                gl_Position = projection * view * vec4(vertexPos, 1.0);\n\n                \n                vec3 ambient = Ka * La;\n                \n                \n                vec3 norm = normalize(normal);\n                vec3 toLight = lightPosition - vertexPos;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(norm, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - vertexPos);\n                vec3 reflectDir = reflect(-lightDir, norm);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                \n                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * color;\n                vertexColor = vec4(result, 1.0);\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            in vec4 vertexColor;\n            out vec4 fragColor;\n\n            void main()\n            {\n                fragColor = vertexColor;\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTextureGouraudShaderProgram():

    def __init__(self):

        vertex_shader = '\n            #version 330\n\n            in vec3 position;\n            in vec2 texCoords;\n            in vec3 normal;\n\n            out vec2 fragTexCoords;\n            out vec3 vertexLightColor;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            uniform vec3 lightPosition; \n            uniform vec3 viewPosition; \n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n            \n            void main()\n            {\n                vec3 vertexPos = vec3(model * vec4(position, 1.0));\n                gl_Position = projection * view * vec4(vertexPos, 1.0);\n\n                fragTexCoords = texCoords;\n\n                \n                vec3 ambient = Ka * La;\n                \n                \n                vec3 norm = normalize(normal);\n                vec3 toLight = lightPosition - vertexPos;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(norm, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - vertexPos);\n                vec3 reflectDir = reflect(-lightDir, norm);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                \n                vertexLightColor = ambient + ((diffuse + specular) / attenuation);\n            }\n            '

        fragment_shader = '\n            #version 330\n\n            in vec3 vertexLightColor;\n            in vec2 fragTexCoords;\n\n            out vec4 fragColor;\n\n            uniform sampler2D samplerTex;\n\n            void main()\n            {\n                vec4 textureColor = texture(samplerTex, fragTexCoords);\n                fragColor = vec4(vertexLightColor, 1.0) * textureColor;\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimplePhongShaderProgram:

    def __init__(self):
        vertex_shader = '\n            #version 330 core\n\n            layout (location = 0) in vec3 position;\n            layout (location = 1) in vec3 color;\n            layout (location = 2) in vec3 normal;\n\n            out vec3 fragPosition;\n            out vec3 fragOriginalColor;\n            out vec3 fragNormal;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            void main()\n            {\n                fragPosition = vec3(model * vec4(position, 1.0));\n                fragOriginalColor = color;\n                fragNormal = mat3(transpose(inverse(model))) * normal;  \n                \n                gl_Position = projection * view * vec4(fragPosition, 1.0);\n            }\n            '

        fragment_shader = '\n            #version 330 core\n\n            out vec4 fragColor;\n\n            in vec3 fragNormal;\n            in vec3 fragPosition;\n            in vec3 fragOriginalColor;\n            \n            uniform vec3 lightPosition; \n            uniform vec3 viewPosition;\n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n\n            void main()\n            {\n                \n                vec3 ambient = Ka * La;\n                \n                \n                \n                vec3 normalizedNormal = normalize(fragNormal);\n                vec3 toLight = lightPosition - fragPosition;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(normalizedNormal, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - fragPosition);\n                vec3 reflectDir = reflect(-lightDir, normalizedNormal);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                    \n                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor;\n                fragColor = vec4(result, 1.0);\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class SimpleTexturePhongShaderProgram:

    def __init__(self):
        vertex_shader = '\n            #version 330 core\n            \n            in vec3 position;\n            in vec2 texCoords;\n            in vec3 normal;\n\n            out vec3 fragPosition;\n            out vec2 fragTexCoords;\n            out vec3 fragNormal;\n\n            uniform mat4 model;\n            uniform mat4 view;\n            uniform mat4 projection;\n\n            void main()\n            {\n                fragPosition = vec3(model * vec4(position, 1.0));\n                fragTexCoords = texCoords;\n                fragNormal = mat3(transpose(inverse(model))) * normal;  \n                \n                gl_Position = projection * view * vec4(fragPosition, 1.0);\n            }\n            '

        fragment_shader = '\n            #version 330 core\n\n            in vec3 fragNormal;\n            in vec3 fragPosition;\n            in vec2 fragTexCoords;\n\n            out vec4 fragColor;\n            \n            uniform vec3 lightPosition; \n            uniform vec3 viewPosition; \n            uniform vec3 La;\n            uniform vec3 Ld;\n            uniform vec3 Ls;\n            uniform vec3 Ka;\n            uniform vec3 Kd;\n            uniform vec3 Ks;\n            uniform uint shininess;\n            uniform float constantAttenuation;\n            uniform float linearAttenuation;\n            uniform float quadraticAttenuation;\n\n            uniform sampler2D samplerTex;\n\n            void main()\n            {\n                \n                vec3 ambient = Ka * La;\n                \n                \n                \n                vec3 normalizedNormal = normalize(fragNormal);\n                vec3 toLight = lightPosition - fragPosition;\n                vec3 lightDir = normalize(toLight);\n                float diff = max(dot(normalizedNormal, lightDir), 0.0);\n                vec3 diffuse = Kd * Ld * diff;\n                \n                \n                vec3 viewDir = normalize(viewPosition - fragPosition);\n                vec3 reflectDir = reflect(-lightDir, normalizedNormal);  \n                float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);\n                vec3 specular = Ks * Ls * spec;\n\n                \n                float distToLight = length(toLight);\n                float attenuation = constantAttenuation\n                    + linearAttenuation * distToLight\n                    + quadraticAttenuation * distToLight * distToLight;\n                    \n                vec4 fragOriginalColor = texture(samplerTex, fragTexCoords);\n\n                vec3 result = (ambient + ((diffuse + specular) / attenuation)) * fragOriginalColor.rgb;\n                fragColor = vec4(result, 1.0);\n            }\n            '

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class MultipleLightTexturePhongShaderProgram:

    def __init__(self):

        with open(getAssetPath('multiple_lights_textures.vs'), 'r') as f:
            vertex_shader = f.readlines()

        with open(getAssetPath('multiple_lights_textures.fs'), 'r') as f:
            fragment_shader = f.readlines()

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

class MultipleLightPhongShaderProgram:

    def __init__(self):

        with open(getAssetPath('multiple_lights_color.vs'), 'r') as f:
            vertex_shader = f.readlines()

        with open(getAssetPath('multiple_lights_color.fs'), 'r') as f:
            fragment_shader = f.readlines()

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
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
        glEnableVertexAttribArray(normal)

        glBindVertexArray(0)

    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
