#version 450
uniform mat4 mmatrix;

in vec4 vertice;
in vec3 normal;

out vec3 varying_normal;
void main() {
    gl_Position = mmatrix * vertice;
    varying_normal = vec3(mmatrix * vec4(normal, 1.0));
}