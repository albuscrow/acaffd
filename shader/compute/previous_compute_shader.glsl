#version 450
layout(std430, binding=0) buffer OriginalVertexBuffer{
    vec4[] originalVertex;
};

layout(std430, binding=1) buffer OrinigalNormalBuffer{
    vec4[] originalNormal;
};

layout(std430, binding=2) buffer OriginalNormalBuffer{
    uint[] originalIndex;
};

layout(std430, binding=3) buffer SplitedVertexBuffer{
    vec4[] splitedVertex;
};

layout(std430, binding=4) buffer SplitedNormalBuffer{
    vec4[] splitedNormal;
};

layout(std430, binding=5) buffer SpliteNormalBuffer{
    uint[] splitedIndex;
};

layout(binding = 0) uniform atomic_uint index_counter;
layout(binding = 0) uniform atomic_uint point_counter;

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 3) {
        return;
    }

    // get current original tirangle index
    uint original_index_1 = originalIndex[triangleIndex * 3];
    uint original_index_2 = originalIndex[triangleIndex * 3 + 1];
    uint original_index_3 = originalIndex[triangleIndex * 3 + 2];

    // gen new point
    vec4 new_point_vertex = (originalVertex[original_index_2] + originalVertex[original_index_3]) / 2;
    vec4 new_point_normal = (originalNormal[original_index_2] + originalNormal[original_index_3]) / 2;
    uint point_offset = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset] = new_point_vertex;
    splitedNormal[point_offset] = new_point_normal;

    // gen added triangle
    uint index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset * 3] = original_index_1;
    splitedIndex[index_offset * 3 + 1] = original_index_2;
    splitedIndex[index_offset * 3 + 2] = point_offset;

    index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset * 3] = original_index_1;
    splitedIndex[index_offset * 3 + 1] = point_offset;
    splitedIndex[index_offset * 3 + 2] = original_index_3;;

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
