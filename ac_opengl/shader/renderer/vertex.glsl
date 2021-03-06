#version 450
layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;

#ifndef TIME
layout(location=7) uniform int show_real;
layout(location=9) uniform int show_original;
layout(location=2) in vec4 parameter_in_original3_triangle_quality1;
layout(location=3) in vec4 parameter_in_splited_edge;
layout(location=4) in vec4 real_normal;
layout(location=5) in vec4 real_position;

out vec4 varying_parameter_in_original3_triangle_quality1;
out vec4 varying_parameter_in_splited_triangle;
out float varying_diff_normal;
out vec3 varying_diff_position;
#endif


layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;
layout(location=6) in vec2 tex_coord;

out vec3 varying_normal_ori;
out vec3 varying_position;
out vec2 varying_tex_coord;


void main() {
    vec4 p = vec4(vertice.xyz, 1);
    #ifdef TIME
        gl_Position = wvp_matrix * p;
        varying_normal_ori = normalize(vec3(wv_matrix * normal));
        varying_position = gl_Position.xyz;
        varying_tex_coord = tex_coord;
    #else
        if (show_original > 0) {
            gl_Position = wvp_matrix * p;
            varying_position = gl_Position.xyz;
            varying_normal_ori = normalize(vec3(wv_matrix * normal));
            varying_tex_coord = tex_coord;
        } else {
            if (show_real > 0) {
                gl_Position = wvp_matrix * real_position;
                varying_normal_ori = normalize(vec3(wv_matrix * real_normal));
            } else {
                gl_Position = wvp_matrix * p;
                varying_normal_ori = normalize(vec3(wv_matrix * normal));
            }
            varying_position = gl_Position.xyz;
            varying_tex_coord = tex_coord;
            varying_parameter_in_original3_triangle_quality1 = parameter_in_original3_triangle_quality1;
            varying_parameter_in_splited_triangle = parameter_in_splited_edge;

            varying_diff_normal = abs(acos(clamp(dot(normalize(normal.xyz), normalize(real_normal.xyz)), -1.0f, 1.0f)) * 30 / 3.1415926);
            varying_diff_position = abs((real_position - p).xyz * 25);
        }
    #endif
}