import pygame
import math
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("3D Engine")
clock = pygame.time.Clock()

fov = 90
width, height = screen.get_size()
center_x, center_y = width // 2, height // 2
mouse_sensitivity = 0.001
move_speed = 0.1

camera_pos = [0, 0, -5]
camera_rot = [0, 0]

def load_obj(file):
    vertices = []
    edges = []

    with open(file, "r") as objfile:
        for line in objfile:
            if line.startswith("v "):
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vertices.append([x, y, z])

            elif line.startswith("f "):
                parts = line.split()
                edge_indices = [int(p.split("/")[0]) - 1 for p in parts[1:]]
                for i in range(len(edge_indices)):
                    edges.append((edge_indices[i], edge_indices[(i + 1) % len(edge_indices)]))

    return vertices, edges

vertices, edges = load_obj("barrel.obj")

def project(vertex):
    x, y, z = vertex
    f = width / (2 * math.tan(math.radians(fov) / 2))
    if z == 0:
        z = 0.01
    x_proj = f * x / z + center_x
    y_proj = f * y / z + center_y
    return int(x_proj), int(y_proj)

def rotate(vertex, rot):
    x, y, z = vertex
    yaw, pitch = rot

    x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
    y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)

    return x, y, z

def translate(vertex, pos):
    x, y, z = vertex
    return x - pos[0], y - pos[1], z - pos[2]

def is_visible(vertex1, vertex2, vertex3):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    normal = [
        edge1[1] * edge2[2] - edge1[2] * edge2[1],
        edge1[2] * edge2[0] - edge1[0] * edge2[2],
        edge1[0] * edge2[1] - edge1[1] * edge2[0]
    ]
    camera_direction = [vertex1[0] - camera_pos[0],
                        vertex1[1] - camera_pos[1],
                        vertex1[2] - camera_pos[2]]
    dot_product = sum(n * d for n, d in zip(normal, camera_direction))
    return dot_product < 0

def handle_input():
    global camera_rot, camera_pos
    keys = pygame.key.get_pressed()

    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    camera_rot[0] += mouse_dx * mouse_sensitivity
    camera_rot[1] += mouse_dy * mouse_sensitivity
    camera_rot[1] = max(-math.pi / 2, min(math.pi / 2, camera_rot[1]))

    cos_yaw, sin_yaw = math.cos(camera_rot[0]), math.sin(camera_rot[0])
    forward = [cos_yaw, 0, sin_yaw]
    right = [-sin_yaw, 0, cos_yaw]

    move_dir = [0, 0, 0]
    if keys[pygame.K_w]:
        move_dir[2] += forward[0]
        move_dir[0] += forward[2]
    if keys[pygame.K_s]:
        move_dir[2] -= forward[0]
        move_dir[0] -= forward[2]
    if keys[pygame.K_a]:
        move_dir[2] -= right[0]
        move_dir[0] -= right[2]
    if keys[pygame.K_d]:
        move_dir[2] += right[0]
        move_dir[0] += right[2]

    camera_pos[0] += move_dir[0] * move_speed
    camera_pos[1] += move_dir[1] * move_speed
    camera_pos[2] += move_dir[2] * move_speed

running = True
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    handle_input()

    transformed_vertices = [translate(v, camera_pos) for v in vertices]
    rotated_vertices = [rotate(v, camera_rot) for v in transformed_vertices]

    for edge in edges:
        start, end = edge
        v1, v2 = rotated_vertices[start], rotated_vertices[end]

        if v1[2] > 0 and v2[2] > 0:
            pygame.draw.line(screen, (255, 255, 255), project(v1), project(v2), 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
