#version 450
layout(location=0) in vec4 vertice_parameter3_info1;
out vec3 varying_parameter;
layout(location = 0) uniform mat4 wvp_matrix;

void main() {
    gl_Position = wvp_matrix * vec4(vertice_parameter3_info1.xyz, 1);
    if (vertice_parameter3_info1.w < 0.5f) {
        //w == 0
        varying_parameter = vec3(1,0,0);
    } else if (vertice_parameter3_info1.w < 1.5f){
        //w == 1
        varying_parameter = vec3(0,1,0);
    } else {
        varying_parameter = vec3(0,0,1);
    }
}