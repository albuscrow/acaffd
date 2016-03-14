#version 450
out vec4 color;
in vec4 varying_color;
void main() {
    color = varying_color;
}
