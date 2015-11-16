#version 450
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

layout(binding = 0) uniform atomic_uint index_counter;
layout(binding = 0) uniform atomic_uint point_counter;

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length()) {
        return;
    }

    // get current original tirangle index
    uvec4 original_triangle_index = originalIndex[triangleIndex];

    // gen new point
    vec4 new_point_vertex = (originalVertex[original_triangle_index.y] + originalVertex[original_triangle_index.z]) / 2;
    vec4 new_point_normal = (originalNormal[original_triangle_index.y] + originalNormal[original_triangle_index.z]) / 2;
    uint point_offset = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset] = new_point_vertex;
    splitedNormal[point_offset] = new_point_normal;

    // gen added triangle
    uint index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset] = uvec4(original_triangle_index.x, original_triangle_index.y, point_offset, 0);
    index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset] = uvec4(original_triangle_index.x, point_offset, original_triangle_index.z, 0);

//    uvec4 new_triangle_index = uvec4(original_triangle_index.);
//    for (uint i = 0; i < 3; ++i) {
//    splitedIndex[index_offset] = original_triangle_index;
//    splitedVertex[original_triangle_index.x] = originalVertex[original_triangle_index.x];
//    splitedVertex[original_triangle_index.y] = originalVertex[original_triangle_index.y];
//    splitedVertex[original_triangle_index.z] = originalVertex[original_triangle_index.z];
//
//    splitedNormal[original_triangle_index.x] = originalNormal[original_triangle_index.x];
//    splitedNormal[original_triangle_index.y] = originalNormal[original_triangle_index.y];
//    splitedNormal[original_triangle_index.z] = originalNormal[original_triangle_index.z];
//    }
}
