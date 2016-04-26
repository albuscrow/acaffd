#version 450

?!time
layout(location=3) uniform int show_splited_edge;
layout(location=4) uniform int show_triangle_quality;
layout(location=5) uniform int show_normal_diff;
layout(location=6) uniform int show_position_diff;
layout(location=9) uniform int show_original;
?!time

layout(location=8) uniform int has_texture;
layout(binding=1) uniform sampler2D acTextureSampler;

?!time
in vec4 varying_parameter_in_original3_triangle_quality1;
in vec4 varying_parameter_in_splited_triangle;
in vec3 varying_diff_normal;
in vec3 varying_diff_position;
in vec3 varying_debug;
?!time

in vec3 varying_position;
in vec3 varying_normal;
in vec2 varying_tex_coord;
out vec4 color;

void main() {

    vec3 lightPosition = vec3(0,1,1);
    vec3 L = normalize(lightPosition - varying_position);
    vec3 E = normalize(-varying_position); // we are in Eye Coordinates, so EyePos is (0,0,0)
    vec3 R = normalize(-reflect(L, varying_normal));

    //calculate Ambient Term:
    vec4 Iamb = vec4(0.6);

    //calculate Diffuse Term:
    vec4 Idiff = vec4(0.3) * max(dot(varying_normal,L), 0.0);
    Idiff = clamp(Idiff, 0.0, 1.0);

    // calculate Specular Term:
    vec4 Ispec = vec4(0.2) * pow(max(dot(R, E), 0.0), 30);
    Ispec = clamp(Ispec, 0.0, 1.0);

    lightPosition = vec3(-1, -1, 1);
    L = normalize(lightPosition - varying_position);
    R = normalize(-reflect(L, varying_normal));

    //calculate Diffuse Term:
    vec4 Idiff2 = vec4(0.2) * max(dot(varying_normal,L), 0.0);
    Idiff2 = clamp(Idiff2, 0.0, 1.0);

    color = Iamb + Idiff + Ispec + Idiff2;
    color.w = 1;
    ?!time
    if (show_original > 0) {
        return;
    }
    if (show_splited_edge > 0) {
        vec3 temp;
        temp.xy = varying_parameter_in_splited_triangle.zw;
        temp.z = 1 - temp.x - temp.y;
        if (any(lessThan(temp, vec3(0.01)))) {
            color = vec4(0,0,1,1);
            return;
        }
        temp.xy = varying_parameter_in_original3_triangle_quality1.xy;
        temp.z = 1 - temp.x - temp.y;
        if (any(lessThan(temp, vec3(0.01)))) {
            color = vec4(1,0,0,1);
            return;
        }

        temp.xy = varying_parameter_in_splited_triangle.xy;
        temp.z = 1 - temp.x - temp.y;
        if (any(lessThan(temp, vec3(0.01)))) {
            color = vec4(0,1,0,1);
            return;
        }
    }
    if (show_triangle_quality > 0) {
        color = vec4(1 - varying_parameter_in_original3_triangle_quality1.w,
                    varying_parameter_in_original3_triangle_quality1.w, 0,1);
        return;
    }
    if (show_normal_diff > 0) {
        float l = min(length(varying_diff_normal), 1);
        color = vec4(l, 1-l, 0, 1);
        return;
    }
    if (show_position_diff > 0) {
        float l = min(length(varying_diff_position), 1);
        color = vec4(l, 1-l, 0, 1);
        return;
    }
    if (has_texture > 0) {
        color = texture(acTextureSampler, varying_tex_coord);
        return;
    }
    ?!time
    return;
}
