#version 450
in vec3 varying_normal;
out vec4 color;
void main() {
    vec3 lightVector = normalize(vec3(0, 0, -1));
    float diffuse = max(dot(lightVector, normalize(varying_normal)), 0) * 0.7;
    vec3 temp_color = vec3(diffuse);
    color = vec4(temp_color, 1);
//    color = vec4(1);
}