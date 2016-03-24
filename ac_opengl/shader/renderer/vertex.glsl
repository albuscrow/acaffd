#version 450
layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;
layout(location=2) in vec4 split_parameter;
layout(location=3) in vec4 tessellate_parameter;

out vec3 varying_normal;
out vec3 varying_split_parameter;
out vec3 varying_tessellate_parameter;
void main() {
    gl_Position = wvp_matrix * vertice;
    varying_normal = normalize(vec3(wv_matrix * normal));
    varying_split_parameter = split_parameter.xyz;
    varying_tessellate_parameter = tessellate_parameter.xyz;
//    varying_normal = vec3(normal);
}