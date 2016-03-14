#version 430
#extension GL_ARB_compute_shader: enable
#extension GL_ARB_shader_storage_buffer_object: enable

layout(std430, binding=4) buffer SSBO{
    int testData[];
};

layout(local_size_x = 10, local_size_y = 1, local_size_z = 1) in;
void main() {
    testData[gl_LocalInvocationIndex] *= 2;
}