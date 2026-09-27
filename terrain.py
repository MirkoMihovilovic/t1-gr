import numpy as np
import trimesh as tm
from pyglet.gl import GL_TRIANGLES

from perlin_noise import PerlinNoise
from utils.camera import FreeCamera

def calculateNormals(vertices, indices):

    tri = tm.Trimesh(
        vertices=np.array(vertices).reshape(len(vertices) // 3, 3),
        faces=np.array(indices).reshape(len(indices) // 3, 3),
        process=False,
    )

    return np.array(tri.vertex_normals, dtype=np.float32).flatten()

def createSunVertices(x, y, radius, DEFINITION):

    vertices = [float(x), float(y), 0.0]

    for i in range(DEFINITION):
        theta = 2.0 * np.pi * i / DEFINITION
        px = x + radius * np.cos(theta)
        py = y + radius * np.sin(theta)
        vertices.extend([float(px), float(py), 0.0])

    return vertices

def createSunIndices(DEFINITION):

    indices = []

    for i in range(DEFINITION):
        current = i + 1
        following = ((i + 1) % DEFINITION) + 1
        indices.extend([0, current, following])

    return indices

def generateChunkVertices(n, chunk_x, chunk_z):
    noise = PerlinNoise(octaves=4, seed=12)
    vertices = []
    indices = []

    offset_x = chunk_x * n
    offset_z = chunk_z * n

    height_scale = 5.0

    for iz in range(n + 1):
        for ix in range(n + 1):
            x = offset_x + ix
            z = offset_z + iz

            y = height_scale * noise([x / n, z / n])

            vertices.extend([float(x), float(y), float(z)])

    row_size = n + 1

    for iz in range(n):
        for ix in range(n):
            v00 = iz * row_size + ix
            v10 = v00 + 1
            v01 = (iz + 1) * row_size + ix
            v11 = v01 + 1

            indices.extend([v00, v01, v10])
            indices.extend([v10, v01, v11])

    normals = calculateNormals(vertices, indices)
    return (vertices, indices, normals)

def makeChunks(resolucion, controller, pipeline):

    for gpu_chunk in controller.gpu_chunks:
        try:
            gpu_chunk.delete()
        except AttributeError:
            pass

    controller.gpu_chunks = []

    for chunk_x, chunk_z in controller.currentChunks:
        vertices, indices, normals = generateChunkVertices(resolucion, chunk_x, chunk_z)

        gpu_chunk = pipeline.vertex_list_indexed(
            len(vertices) // 3,
            GL_TRIANGLES,
            np.array(indices, dtype=np.uint32),
        )

        gpu_chunk.position[:] = vertices
        gpu_chunk.normal[:] = normals

        controller.gpu_chunks.append(gpu_chunk)

def updateChunks(resolucion, camara, controller, pipeline):
    x_pos = camara.position[0]
    z_pos = camara.position[2]

    center_x = int(np.floor(x_pos / resolucion))
    center_z = int(np.floor(z_pos / resolucion))
    new_center = (center_x, center_z)

    if new_center == controller.centerChunk:
        return

    controller.centerChunk = new_center

    new_chunks = []
    for dz in (-1, 0, 1):
        for dx in (-1, 0, 1):
            new_chunks.append((center_x + dx, center_z + dz))

    controller.currentChunks = new_chunks
    makeChunks(resolucion, controller, pipeline)

class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0, 0, 0])
        self.speed = 10

    def time_update(self, dt):
        self.update()
        old_forward = np.array([self.forward[0], 0, self.forward[2]])
        dir = self.direction[0] * old_forward + self.direction[1] * self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm

        self.position += dir * self.speed * dt
        self.focus = self.position + self.forward
