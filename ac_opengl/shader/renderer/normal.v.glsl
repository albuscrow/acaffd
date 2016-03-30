#version 450
layout(location=0) in vec4 vertice;
layout(location=1) in vec4 normal;

out VS_OUT {
    vec4 normal;
} gs_out;
void main() {
    gl_Position = vertice;
    gs_out.normal = normal;
}
