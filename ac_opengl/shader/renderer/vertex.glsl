#version 450
layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;
layout(location=7) uniform int show_real;
layout(location=9) uniform int show_original;

layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;
layout(location=2) in vec4 parameter_in_original3_triangle_quality1;
layout(location=3) in vec4 parameter_in_splited_edge;
layout(location=4) in vec4 real_normal;
layout(location=5) in vec4 real_position;
layout(location=6) in vec2 tex_coord;

out vec3 varying_normal;
out vec4 varying_parameter_in_original3_triangle_quality1;
out vec4 varying_parameter_in_splited_triangle;
out vec3 varying_diff_normal;
out vec3 varying_diff_position;
out vec3 varying_position;
out vec2 varying_tex_coord;
out vec3 varying_debug;
void main() {
    vec4 p = vec4(vertice.xyz, 1);
    if (show_original > 0) {
        gl_Position = wvp_matrix * p;
        varying_position = gl_Position.xyz;
        varying_normal.xyz = normalize(vec3(wv_matrix * normal));
        varying_tex_coord = tex_coord;
    } else {
        if (show_real > 0) {
            gl_Position = wvp_matrix * real_position;
            varying_normal.xyz = normalize(vec3(wv_matrix * real_normal));
        } else {
            gl_Position = wvp_matrix * p;
            varying_normal.xyz = normalize(vec3(wv_matrix * normal));
        }
        varying_position = gl_Position.xyz;
        varying_parameter_in_original3_triangle_quality1 = parameter_in_original3_triangle_quality1;
        varying_parameter_in_splited_triangle = parameter_in_splited_edge;
        varying_diff_normal = abs((real_normal - normal).xyz*5.2);
        varying_diff_position = abs((real_position - p).xyz*30);
//        varying_diff_normal = abs((real_normal - normal).xyz*50000);
//        varying_diff_position = (real_position - vertice).xyz*30000;
        varying_tex_coord = tex_coord;
        if (mod(gl_VertexID, 3) == 0) {
            varying_debug = vec3(1,0,0);
        } else if (mod(gl_VertexID, 3) == 1) {
            varying_debug = vec3(0,1,0);
        } else {
            varying_debug = vec3(0,0,1);
        }
    }
}