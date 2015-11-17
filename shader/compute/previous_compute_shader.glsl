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

layout(std430, binding=5) buffer SplitedIndexBuffer{
    uint[] splitedIndex;
};

struct BSplineInfo {
    vec3 t;
    uvec3 knot_left_index;
    uvec3 aux_matrix_offset;
};

layout(std430, binding=10) buffer SplitedBSplineInfoBuffer{
    BSplineInfo[] BSplineInfos;
};

layout(binding = 0) uniform atomic_uint index_counter;
layout(binding = 0) uniform atomic_uint point_counter;

layout(std140, binding=0) uniform BSplineBodyData{
    uniform float orderU;
    uniform float orderV;
    uniform float orderW;

    uniform float controlPointNumU;
    uniform float controlPointNumV;
    uniform float controlPointNumW;

    uniform float maxU;
    uniform float maxV;
    uniform float maxW;
    uniform float minU;
    uniform float minV;
    uniform float minW;
};

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

float getTempParameter(float t, int order, int controlPointNum, out int leftIndex){
    int interNumber = controlPointNum - order + 1;
    float step = 1.0 / interNumber;
    leftIndex = int(t / step);
    if (t < step) {
        leftIndex = 2;
        return t / step;
    } else if (t < 2 * step) {
        leftIndex = 3;
        return t / step - 1;
    }else{
        leftIndex = 4;
        return t / step - 2;
    }
}

int matrixCase(in int order,in int ctrlPointNum,in int leftIdx) {
    if (order == 1){
        return 0;                // MB1
    } else if (order == 2) {
        return 1;                // MB2
    } else if (order == 3) {
        if (ctrlPointNum == 3){
            return 5;            // MB30
        } else {
            if (leftIdx == 2){
                return 14;    // MB31
            } else if (leftIdx == ctrlPointNum - 1){
                return 23;    // MB32
            } else{
                return 32;    // MB33
            }
        }
    } else {
        if (ctrlPointNum == 4){
            return 41;        // MB40
        } else if (ctrlPointNum == 5) {
            if (leftIdx == 3){
                return 57;    // MB41
            } else {
                return 73;    // MB42
            }
        } else if (ctrlPointNum == 6) {
            if (leftIdx == 3){
                return 89;    // MB43
            } else if (leftIdx == 4) {

                return 105;    // MB44
            } else {
                return 121;    // MB45
            }
        } else {
            if (leftIdx == 3){
                return 89;    // MB43
            } else if (leftIdx == 4) {
                return 137;    // MB46
            } else if (leftIdx == ctrlPointNum - 2) {
                return 153;    // MB47
            } else if (leftIdx == ctrlPointNum - 1) {
                return 121;    // MB45
            }else {
                return 169;    // MB48
            }
        }
    }
}

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
//    vec4 new_point_vertex = (originalVertex[original_index_2] + originalVertex[original_index_3]) / 2;
//    vec4 new_point_normal = (originalNormal[original_index_2] + originalNormal[original_index_3]) / 2;

    vec4 new_point_vertex = vec4(minU, minV, minW, 0.5);
    vec4 new_point_normal = vec4(maxU, maxV, maxW, 0.6);
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
