#version 450
in vec4 vertice;

uniform mat4 mmatrix;

void main() {
    gl_Position = mmatrix * vertice;
    gl_PointSize = 10.0;
}