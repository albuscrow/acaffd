#version 450

in vec3 varying_normal;
in vec3 varying_split_parameter;
in vec3 varying_tessellate_parameter;
out vec4 color;

void main() {
    if (any(lessThan(varying_split_parameter, vec3(0.01)))) {
        color = vec4(1,0,0,1);
        return;
    }
    if (any(lessThan(varying_tessellate_parameter, vec3(0.01)))) {
        color = vec4(0,1,0,1);
        return;
    }
    vec3 lightVector = normalize(vec3(0, 0, 1));
    vec3 lightVector2 = normalize(vec3(-1, 0, -1));
    float diffuse = max(dot(lightVector, normalize(varying_normal)), 0);
    float diffuse2 = max(dot(lightVector2, normalize(varying_normal)), 0);
//    if (diffuse > 0.8) {
//        diffuse = 1;
//    }
    vec3 temp_color = vec3(diffuse + diffuse2);
//    vec3 temp_color = vec3(normalize(varying_normal).z);
//    color = vec4(varying_normal, 1);
    color = vec4(temp_color, 1);
//    color = vec4(normalize(varying_normal), 1);
//    color = vec4(0.8, 0.8, 0.8, 1);
}
