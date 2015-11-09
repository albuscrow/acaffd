#version 450
uniform mat4 perspective_matrix;
uniform mat4 view_matrix;
uniform mat4 world_matrix;
in vec4 vertice;
in vec3 normal;
out vec3 varying_normal;
void main() {
    gl_Position = perspective_matrix * view_matrix * world_matrix * vertice;
    varying_normal = vec3(perspective_matrix * view_matrix * world_matrix * vec4(normal, 1.0));

//    gl_Position = view_matrix * world_matrix * vertice;
}