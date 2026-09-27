import os

import numpy as np
from pyglet import clock
from pyglet.app import run
from pyglet.gl import *
from pyglet.window import Window, key

from terrain import *

from utils.helpers import init_axis, init_pipeline

def orbitalSunTransform(camera_position, elapsed_time, distance, period, initial_phase):

    theta = initial_phase + 2.0 * np.pi * elapsed_time / period
    c, s = np.cos(theta), np.sin(theta)

    rotation = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)

    offset = distance * np.array([0, s, -c], dtype=np.float32)
    position = np.asarray(camera_position, dtype=np.float32) + offset

    model = np.eye(4, dtype=np.float32)
    model[:3, :3] = rotation
    model[:3, 3] = position
    return model

class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.sky_color = np.array([96 / 255, 194 / 255, 224 / 255])
        self.intensity = 0.9
        self.wireframe = False

        self.currentChunks = []

        self.centerChunk = (None, None)

        self.gpu_chunks = []

        self.sun_time = 0.0
        self.sun_distance = 60.0
        self.sun_phase = 0.2
        self.sun_period = 30.0
        self.sun_transform = np.eye(4, dtype=np.float32)

if __name__ == "__main__":

    controller = Controller(1000, 1000, "Tarea 1")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(os.path.abspath(__file__))

    pipeline = init_pipeline(root + "/tarea1.vert", root + "/tarea1.frag")

    pipeline_sol = init_pipeline(root + "/tarea1_sol.vert", root + "/tarea1_sol.frag")

    n = 25

    cam = MyCam([n / 2, n / 2, n / 2])

    axis = init_axis(cam)

    DEFINITION = 100

    sun_vertices = createSunVertices(0.0, 0.0, 4.0, DEFINITION)
    sun_indices = createSunIndices(DEFINITION)

    gpu_sun = pipeline_sol.vertex_list_indexed(
        len(sun_vertices) // 3,
        GL_TRIANGLES,
        np.array(sun_indices, dtype=np.uint32),
    )
    gpu_sun.position[:] = sun_vertices

    @controller.event
    def on_draw():

        glClearColor(*(controller.sky_color * controller.intensity), 1)
        controller.clear()
        glEnable(GL_DEPTH_TEST)

        if controller.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        pipeline_sol.use()
        pipeline_sol["u_view"] = cam.get_view()
        pipeline_sol["u_projection"] = cam.get_projection()

        pipeline_sol["u_transform"] = np.reshape(
            controller.sun_transform, (16, 1), order="F"
        )

        gpu_sun.draw(GL_TRIANGLES)

        pipeline.use()
        pipeline["u_view"] = cam.get_view()
        pipeline["u_projection"] = cam.get_projection()

        for gpu_chunk in controller.gpu_chunks:
            gpu_chunk.draw(GL_TRIANGLES)

        axis.draw()

    def update(dt):

        cam.time_update(dt)

        updateChunks(n, cam, controller, pipeline)

        axis.update()

        controller.sun_time += dt
        controller.sun_transform = orbitalSunTransform(
            cam.position, controller.sun_time,
            controller.sun_distance, controller.sun_period,
            controller.sun_phase,
        )

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W:
            cam.direction[0] = 1
        if symbol == key.S:
            cam.direction[0] = -1
        if symbol == key.A:
            cam.direction[1] = 1
        if symbol == key.D:
            cam.direction[1] = -1
        if symbol == key._1:
            controller.wireframe = not controller.wireframe

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.S:
            cam.direction[0] = 0

        if symbol == key.A or symbol == key.D:
            cam.direction[1] = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
        cam.yaw += dx * 0.001
        cam.pitch += dy * 0.001
        cam.pitch = max(
            -(np.pi / 2 - 0.01),
            min(cam.pitch, np.pi / 2 - 0.01),
        )

    @controller.event
    def on_resize(width, height):
        cam.resize(width, max(height, 1))
        glViewport(0, 0, width, height)

    update(0.0)
    clock.schedule_interval(update, 1 / 60)
    run()
