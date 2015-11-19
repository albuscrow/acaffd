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

layout(std430, binding=11) buffer AdjacencyBuffer{
    uint[] adjacencyBuffer;
};

struct BSplineInfo {
    vec4 t;
    uvec4 knot_left_index;
    uvec4 aux_matrix_offset;
};

layout(std430, binding=10) buffer SplitedBSplineInfoBuffer{
    BSplineInfo[] bSplineInfo;
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

    uniform float lengthU;
    uniform float lengthV;
    uniform float lengthW;
    uniform float minU;
    uniform float minV;
    uniform float minW;
};

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

// uvw 为 1 2 3分别代表u v w
float getNewT(uint uvw, float t) {
    if (uvw == 1u) {
        return (t - minU) / lengthU;
    } else if (uvw == 2u) {
        return (t - minV) / lengthV;
    } else {
        return (t - minW) / lengthW;
    }
}

// uvw 为 1 2 3分别代表u v w
float getBSplineInfoU(float t, out uint leftIndex){
    float newT = getNewT(1u, t);
    uint interNumber = uint(controlPointNumU - orderU + 1);
    float step = 1.0 / float(interNumber);
    leftIndex = uint(newT / step);
    if (leftIndex == interNumber) {
        leftIndex -= 1;
    }
    t = newT / step - leftIndex;
    leftIndex += uint(orderU - 1);
    return t;
}

float getBSplineInfoV(float t, out uint leftIndex){
    float newT = getNewT(2u, t);
    uint interNumber = uint(controlPointNumV - orderV + 1);
    float step = 1.0 / float(interNumber);
    leftIndex = uint(newT  / step);
    if (leftIndex == interNumber) {
        leftIndex -= 1;
    }
    t = newT / step - leftIndex;
    leftIndex += uint(orderV - 1);
    return t;
}

float getBSplineInfoW(float t, out uint leftIndex){
    float newT = getNewT(3u, t);
    uint interNumber = uint(controlPointNumW - orderW + 1);
    float step = 1.0 / float(interNumber);
    leftIndex = uint(newT / step);
    if (leftIndex == interNumber) {
        leftIndex -= 1;
    }
    t = newT / step - leftIndex;
    leftIndex += uint(orderW - 1);
    return t;
}


int getAuxMatrixOffset(in int order,in int ctrlPointNum,in int leftIdx) {
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

BSplineInfo getBSplineInfo(vec4 parameter) {
    BSplineInfo result;
    uint knot_left_index_u, knot_left_index_v, knot_left_index_w;
    float u = getBSplineInfoU(parameter.x, knot_left_index_u);
    float v = getBSplineInfoV(parameter.y, knot_left_index_v);
    float w = getBSplineInfoW(parameter.z, knot_left_index_w);
    uint aux_matrix_offset_u, aux_matrix_offset_v, aux_matrix_offset_w;
    aux_matrix_offset_u = getAuxMatrixOffset(int(orderU), int(controlPointNumU), int(knot_left_index_u));
    aux_matrix_offset_v = getAuxMatrixOffset(int(orderV), int(controlPointNumV), int(knot_left_index_v));
    aux_matrix_offset_w = getAuxMatrixOffset(int(orderW), int(controlPointNumW), int(knot_left_index_w));

    result.t = vec4(u, v, w, 0);
    result.knot_left_index = uvec4(knot_left_index_u, knot_left_index_v, knot_left_index_w, 0);
    result.aux_matrix_offset = uvec4(aux_matrix_offset_u, aux_matrix_offset_v, aux_matrix_offset_w, 0);

    return result;
}

vec3 positionBezierTriangle[10];
vec3 normalBezierTriangle[6];

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 3) {
        return;
    }

    // get current original tirangle index
    uint original_index_1 = originalIndex[triangleIndex * 3];
    uint original_index_2 = originalIndex[triangleIndex * 3 + 1];
    uint original_index_3 = originalIndex[triangleIndex * 3 + 2];


    uint adjacency_triangle_1 = adjacencyBuffer[triangleIndex * 3];
    uint adjacency_triangle_2 = adjacencyBuffer[triangleIndex * 3 + 1];
    uint adjacency_triangle_3 = adjacencyBuffer[triangleIndex * 3 + 2];

    // gen new point
    vec4 new_point_vertex = (originalVertex[original_index_2] + originalVertex[original_index_3]) / 2;
    vec4 new_point_normal = (originalNormal[original_index_2] + originalNormal[original_index_3]) / 2;

    uint point_offset1 = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset1] = originalVertex[original_index_1];
    splitedNormal[point_offset1] = originalNormal[original_index_1];
    bSplineInfo[point_offset1] = getBSplineInfo(originalVertex[original_index_1]);


    uint point_offset2 = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset2] = originalVertex[original_index_2];
    splitedNormal[point_offset2] = originalNormal[original_index_2];
    bSplineInfo[point_offset2] = getBSplineInfo(originalVertex[original_index_2]);

    uint point_offset3 = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset3] = originalVertex[original_index_3];
    splitedNormal[point_offset3] = originalNormal[original_index_3];
    bSplineInfo[point_offset3] = getBSplineInfo(originalVertex[original_index_3]);

    uint point_offset4 = atomicCounterIncrement(point_counter);
    splitedVertex[point_offset4] = new_point_vertex;
    splitedNormal[point_offset4] = new_point_normal;
    bSplineInfo[point_offset4] = getBSplineInfo(new_point_vertex);

    // gen added triangle
    uint index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset * 3] = point_offset1;
    splitedIndex[index_offset * 3 + 1] = point_offset2;
    splitedIndex[index_offset * 3 + 2] = point_offset4;

    index_offset = atomicCounterIncrement(index_counter);
    splitedIndex[index_offset * 3] = point_offset1;
    splitedIndex[index_offset * 3 + 1] = point_offset4;
    splitedIndex[index_offset * 3 + 2] = point_offset3;;

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
