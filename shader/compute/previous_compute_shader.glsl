#version 450
layout(std140, binding=0) uniform BSplineBodyData{
    uniform int orderU;
    uniform int orderV;
    uniform int orderW;

    uniform int controlPointNumU;
    uniform int controlPointNumV;
    uniform int controlPointNumW;
};

layout(std430, binding=0) buffer OriginalVertexBuffer{
    vec4[] originalVertex;
};

layout(std430, binding=1) buffer OrinigalNormalBuffer{
    vec4[] originalNormal;
};

layout(std430, binding=2) buffer OriginalNormalBuffer{
    uvec4[] originalIndex;
};

layout(std430, binding=3) buffer SplitedVertexBuffer{
    vec4[] splitedVertex;
};

layout(std430, binding=4) buffer SplitedNormalBuffer{
    vec4[] splitedNormal;
};

layout(std430, binding=5) buffer SpliteNormalBuffer{
    uvec4[] splitedIndex;
};

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length()) {
        return;
    }
    uvec4 index = originalIndex[triangleIndex];
    splitedIndex[triangleIndex] = index;
    splitedVertex[index.x] = originalVertex[index.x];
    splitedVertex[index.y] = originalVertex[index.y];
    splitedVertex[index.z] = originalVertex[index.z];

    splitedNormal[index.x] = originalNormal[index.x];
    splitedNormal[index.y] = originalNormal[index.y];
    splitedNormal[index.z] = originalNormal[index.z];
}
