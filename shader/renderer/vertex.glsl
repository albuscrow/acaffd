#version 450
uniform mat4 wvp_matrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;

out vec3 varying_normal;
void main() {
    gl_Position = wvp_matrix * vertice;
    varying_normal = vec3(wvp_matrix * normal);
}