#version 450
in vec4 vertice;
in float isHit;
out vec4 varying_color;

uniform mat4 mmatrix;

void main() {
    gl_Position = mmatrix * vertice;
    gl_PointSize = 10.0;
    if (isHit > 0.5f) {
        varying_color = vec4(0,1,0,1);
    } else {
        varying_color = vec4(1,0,0,1);
    }
}