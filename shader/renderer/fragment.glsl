#version 450
in vec3 varying_normal;
out vec4 color;
void main() {
    vec3 lightVector = normalize(vec3(1,1,1));
    float diffuse = max(dot(lightVector, normalize(varying_normal)), 0) * 0.3;
    vec3 temp_color = diffuse + vec3(0.1, 0.1, 0.1);
    color = vec4(temp_color, 1);
}