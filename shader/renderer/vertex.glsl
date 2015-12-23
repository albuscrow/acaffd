#version 450
uniform mat4 wvp_matrix;
uniform mat4 wv_matrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;

out vec3 varying_normal;
void main() {
    gl_Position = wvp_matrix * vertice;
    varying_normal = vec3(wv_matrix * normal);
//    varying_normal = vec3(normal);
}