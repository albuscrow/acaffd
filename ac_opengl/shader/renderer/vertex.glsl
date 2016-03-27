#version 450
layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;
layout(location=2) in vec4 parameter_in_original3_triangle_quality1;
layout(location=3) in vec4 parameter_in_splited_edge;
layout(location=4) in vec4 real_normal;
layout(location=5) in vec4 real_position;

out vec3 varying_normal;
out vec4 varying_parameter_in_original3_triangle_quality1;
out vec3 varying_parameter_in_splited_triangle;
out vec3 varying_diff_normal;
out vec3 varying_diff_position;
void main() {
    gl_Position = wvp_matrix * vertice;
    varying_normal.xyz = normalize(vec3(wv_matrix * normal));
    varying_parameter_in_original3_triangle_quality1 = parameter_in_original3_triangle_quality1;
    varying_parameter_in_splited_triangle = parameter_in_splited_edge.xyz;
    varying_diff_normal = abs((real_normal - normal).xyz);
    varying_diff_position = abs((real_position - vertice).xyz * 100);
}