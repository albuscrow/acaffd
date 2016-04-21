#version 450

layout(location=0) uniform mat4 wvp_matrix;
layout(location=1) uniform mat4 wv_matrix;

layout (triangles) in;
layout (line_strip, max_vertices = 6) out;

in VS_OUT {
    vec4 normal;
} gs_in[];

const float MAGNITUDE = 0.3f;

void GenerateLine(int index)
{
    gl_Position = wvp_matrix * gl_in[index].gl_Position;
    EmitVertex();
    gl_Position = wvp_matrix * (gl_in[index].gl_Position + gs_in[index].normal * MAGNITUDE);
    EmitVertex();
    EndPrimitive();
}

void main()
{
    GenerateLine(0); // First vertex normal
    GenerateLine(1); // Second vertex normal
    GenerateLine(2); // Third vertex normal
}
