#version 450
uniform mat4 mmatrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;

out vec3 varying_normal;
void main() {
    gl_Position = mmatrix * vertice;
    varying_normal = vec3(mmatrix * normal);
}