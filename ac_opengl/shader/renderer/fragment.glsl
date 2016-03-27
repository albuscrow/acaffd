#version 450

layout(location=3) uniform int show_splited_edge;
layout(location=4) uniform int show_triangle_quality;
in vec3 varying_normal;
in vec4 varying_parameter_in_original3_triangle_quality1;
in vec3 varying_parameter_in_splited_triangle;
in vec3 varying_diff_normal;
in vec3 varying_diff_position;
out vec4 color;

void main() {
//    color = vec4(varying_normal, 1);
//    return;
    if (show_splited_edge > 0) {
        if (any(lessThan(varying_parameter_in_original3_triangle_quality1.xyz, vec3(0.01)))) {
            color = vec4(1,0,0,1);
            return;
        }
        if (any(lessThan(varying_parameter_in_splited_triangle, vec3(0.01)))) {
            color = vec4(0,1,0,1);
            return;
        }
    }
    if (show_triangle_quality > 0) {
        color = vec4(1 - varying_parameter_in_original3_triangle_quality1.w,
                    varying_parameter_in_original3_triangle_quality1.w, 0,1);
        return;
    }
    vec3 lightVector = normalize(vec3(0, 0, 1));
    vec3 lightVector2 = normalize(vec3(-1, 0, -1));
    float diffuse = max(dot(lightVector, normalize(varying_normal)), 0);
    float diffuse2 = max(dot(lightVector2, normalize(varying_normal)), 0);
    vec3 temp_color = vec3(diffuse + diffuse2);
    color = vec4(temp_color, 1);
}
