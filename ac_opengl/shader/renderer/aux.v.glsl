#version 450
layout(location=0) in vec4 vertice;
out vec4 varying_color;

layout(location = 0) uniform mat4 wvp_matrix;

void main() {
    gl_Position = wvp_matrix * vec4(vertice.xyz, 1);
    gl_PointSize = 10.0;
    if (vertice.w > 0.6f) {
        varying_color = vec4(0,1,0,1);
    } else if (vertice.w < 0.4f){
        varying_color = vec4(1,0,0,1);
    } else {
        varying_color = vec4(0,0,0,0.5);
    }
}