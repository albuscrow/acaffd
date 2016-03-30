#version 450
layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;

out vec3 varying_normal;
in VS_OUT {
    vec3 normal;
} gs_out;
void main() {
    gl_Position = wvp_matrix * vertice;
    gs_out.normal = normalize(vec3(wv_matrix * real_normal));
}
