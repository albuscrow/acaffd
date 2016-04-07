#version 450

layout(location=3) uniform int show_splited_edge;
layout(location=4) uniform int show_triangle_quality;
layout(location=5) uniform int show_normal_diff;
layout(location=6) uniform int show_position_diff;
in vec3 varying_normal;
in vec4 varying_parameter_in_original3_triangle_quality1;
in vec4 varying_parameter_in_splited_triangle;
in vec3 varying_diff_normal;
in vec3 varying_diff_position;
in vec3 varying_position;
out vec4 color;

void main() {
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
        color = vec4(varying_diff_normal, 1);
        return;
    }
    if (show_position_diff > 0) {
        color = vec4(varying_diff_position, 1);
        return;
    }
    vec3 lightPosition = vec3(0,1,1);
    vec3 eye = normalize(varying_position - vec3(0,0,-1));
    vec3 lightVector = normalize(vec3(0, 0, 1));
    vec3 lightVector2 = normalize(vec3(-1, 0, -1));
    float diffuse = max(dot(lightVector, normalize(varying_normal)), 0);
    float diffuse2 = max(dot(lightVector2, normalize(varying_normal)), 0);

    //高光
	vec3 VP = lightPosition - varying_position;	// 片元到光源的向量
	VP = normalize(VP);
	float nDotHV = max(0.0, dot(reflect(-VP, varying_normal), eye));
	float nDotVP = max(0.0, dot(varying_normal, VP));	// normal.light
	float pf = 0.0;								// power factor
    pf = pow(nDotHV, 10);
    vec3 temp_color = vec3(diffuse * 0.7 + diffuse2 * 0.5 + pf * 0.7);
    color = vec4(temp_color, 1);
}
