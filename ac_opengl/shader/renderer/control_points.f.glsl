#version 450
in vec3 varying_parameter;
out vec4 color;
void main() {
    if (any(lessThan(varying_parameter, vec3(0.05)))) {
        color = vec4(0,0,1,1);
    } else {
        color = vec4(0,1,1,1);
    }
}
