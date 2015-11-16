#version 450

layout(std430, binding=3) buffer SplitedVertexBuffer{
    vec4[] splitedVertex;
};

layout(std430, binding=4) buffer SplitedNormalBuffer{
    vec4[] splitedNormal;
};

layout(std430, binding=5) buffer SplitedIndexBuffer{
    uint[] splitedIndex;
};

layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
};

layout(std430, binding=7) buffer TesselatedNormalBuffer{
    vec4[] tessellatedNormal;
};

layout(std430, binding=8) buffer TesselatedIndexBuffer{
    uint[] tessellatedIndex;
};

layout(location=0) uniform float triangleNumber;

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= uint(triangleNumber)) {
        return;
    }

    uint splited_index_1 = splitedIndex[triangleIndex * 3];
    uint splited_index_2 = splitedIndex[triangleIndex * 3 + 1];
    uint splited_index_3 = splitedIndex[triangleIndex * 3 + 2];

    tessellatedIndex[triangleIndex * 3] = splited_index_1;
    tessellatedIndex[triangleIndex * 3 + 1] = splited_index_2;
    tessellatedIndex[triangleIndex * 3 + 2] = splited_index_3;
    tessellatedVertex[splited_index_1] = splitedVertex[splited_index_1];
    tessellatedVertex[splited_index_2] = splitedVertex[splited_index_2];
    tessellatedVertex[splited_index_3] = splitedVertex[splited_index_3];

    tessellatedNormal[splited_index_1] = splitedNormal[splited_index_1];
    tessellatedNormal[splited_index_2] = splitedNormal[splited_index_2];
    tessellatedNormal[splited_index_3] = splitedNormal[splited_index_3];
}

//控制顶点
uniform vec3[125] controlPoints;

//Bspline body中采样时要用到的矩阵
const float[185] sample_aux_matrix = {
        /*------------------ MB1f, 首地址0 ------------------*/
        1.0,
        /*------------------ MB2, 首地址1 ------------------*/
        1.0, 0.0, -1.0, 1.0,
        /*------------------ MB30, 首地址5 -----------------*/
        1.0, 0.0, 0.0, -2.0, 2.0, 0.0, 1.0, -2.0, 1.0,
        /*------------------ MB31, 首地址14 -----------------*/
        1.0, 0.0, 0.0, -2.0, 2.0, 0.0, 1.0, -1.5, 0.5,
        /*------------------ MB32, 首地址23 -----------------*/
        0.5, 0.5, 0.0, -1.0, 1.0, 0.0, 0.5, -1.5, 1.0,
        /*------------------ MB33, 首地址32 -----------------*/
        0.5, 0.5, 0.0, -1.0, 1.0, 0.0, 0.5, -1.0, 0.5,
        /*------------------ MB40, 首地址41 -----------------*/
        1.0, 0.0, 0.0, 0.0, -3.0, 3.0, 0.0, 0.0, 3.0, -6.0, 3.0, 0.0, -1.0, 3.0, -3.0, 1.0,
        /*------------------ MB41, 首地址57 -----------------*/
        1.0, 0.0, 0.0, 0.0, -3.0, 3.0, 0.0, 0.0, 3.0, -4.5, 1.5, 0.0, -1.0, 1.75, -1.0, 0.25,
        /*------------------ MB42, 首地址73 -----------------*/
        0.25, 0.5, 0.25, 0.0, -0.75, 0.0, 0.75, 0.0, 0.75, -1.5, 0.75, 0.0, -0.25, 1.0, -1.75, 1.0,
        /*------------------ MB43, 首地址89 -----------------*/
        1.0, 0.0, 0.0, 0.0, -3.0, 3.0, 0.0, 0.0, 3.0, -4.5, 1.5, 0.0, -1.0, 1.75, -0.91666666666666666666, 0.16666666666666666666,
        /*------------------ MB44, 首地址105 -----------------*/
        0.25, 0.58333333333333333333, 0.16666666666666666666, 0.0, -0.75, 0.25, 0.5, 0.0, 0.75, -1.25, 0.5, 0.0, -0.25, 0.58333333333333333333, -0.58333333333333333333, 0.25,
        /*------------------ MB45, 首地址121 -----------------*/
        0.16666666666666666666, 0.58333333333333333333, 0.25, 0.0, -0.5, -0.25, 0.75, 0.0, 0.5, -1.25, 0.75, 0.0, -0.16666666666666666666, 0.91666666666666666666, -1.75, 1.0,
        /*------------------ MB46, 首地址137 -----------------*/
        0.25, 0.58333333333333333333, 0.16666666666666666666, 0.0, -0.75, 0.25, 0.5, 0.0, 0.75, -1.25, 0.5, 0.0, -0.25, 0.58333333333333333333, -0.5, 0.16666666666666666666,
        /*------------------ MB47, 首地址153 -----------------*/
        0.16666666666666666666, 0.66666666666666666666, 0.16666666666666666666, 0.0, -0.5, 0.0, 0.5, 0.0, 0.5, -1.0, 0.5, 0.0, -0.16666666666666666666, 0.5, -0.58333333333333333333, 0.25,
        /*------------------ MB48, 首地址169 -----------------*/
        0.16666666666666666666, 0.66666666666666666666, 0.16666666666666666666, 0.0, -0.5, 0.0, 0.5, 0.0, 0.5, -1.0, 0.5, 0.0, -0.16666666666666666666, 0.5, -0.5, 0.16666666666666666666};


layout(std140, binding=0) uniform BSplineBodyData{
    uniform int orderU;
    uniform int orderV;
    uniform int orderW;

    uniform int controlPointNumU;
    uniform int controlPointNumV;
    uniform int controlPointNumW;

    uniform float[20] knotListU;
    uniform float[20] knotListV;
    uniform float[20] knotListW;
};



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

float getTempParameter(float t, out int leftIndex){
    t += 0.5;
    float step = 1.0 / 3;
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

//void main() {
//    if (gl_GlobalInvocationID.x >= parameters.length()) {
//        return;
//    }
//    vec4 result;
//    vec3 tempcp1[4];
//    vec3 tempcp2[4][4];
//
//    vec4 p = parameters[gl_GlobalInvocationID.x];
//    int uli = 0;
//    float u = getTempParameter(p.x, uli);
//    int vli = 0;
//    float v = getTempParameter(p.y, vli);
//    int wli = 0;
//    float w = getTempParameter(p.z, wli);
//    vertices[gl_GlobalInvocationID.x] = vec4(u, v, w, 677);
//
//    float temp[4];
//    float muli[4];
//    temp[0] = 1.0f;
//    temp[1] = w;
//    temp[2] = w * w;
//    temp[3] = temp[2] * w;
//
//    int matrix_offset = matrixCase(3, 5, wli);
//
//    for (int i = 0; i < 3; ++i) {
//        muli[i] = 0.0f;
//        for (int j = 0; j < 3; ++j) {
//            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
//        }
//    }
//
//    for (int i = 0; i < 3; ++i){
//        for (int j = 0; j < 3; ++j){
//            tempcp2[i][j] = vec3(0.0f);
//            for (int k = 0; k < 3; ++k) {
//                vec3 cp = controlPoints[int((uli - i) * 25 + (vli - j) * 5 + wli - k)];
//                tempcp2[i][j].x += cp.x * muli[2 - k];
//                tempcp2[i][j].y += cp.y * muli[2 - k];
//                tempcp2[i][j].z += cp.z * muli[2 - k];
//            }
//        }
//    }
//
////    temp[0] = 1.0f;
//    temp[1] = v;
//    temp[2] = v * v;
//    temp[3] = temp[2] * v;
//
//    matrix_offset = matrixCase(3, 5, vli);
//    for (int i = 0; i < 3; ++i) {
//        muli[i] = 0.0;
//        for (int j = 0; j < 3; ++j) {
//            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
//        }
//    }
//
//    for (int i = 0; i < 3; ++i) {
//        tempcp1[i] = vec3(0.0);
//        for (int j = 0; j < 3; ++j) {
//            tempcp1[i].x += tempcp2[i][j].x * muli[2 - j];
//            tempcp1[i].y += tempcp2[i][j].y * muli[2 - j];
//            tempcp1[i].z += tempcp2[i][j].z * muli[2 - j];
//        }
//    }
//
//    temp[1] = u;
//    temp[2] = u * u;
//    temp[3] = temp[2] * u;
//
//    matrix_offset = matrixCase(3, 5, uli);
//
//    for (int i = 0; i < 3; ++i) {
//        muli[i] = 0.0;
//        for (int j = 0; j < 3; ++j) {
//            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
//        }
//    }
//
//    result = vec4(0);
//    for (int i = 0; i < 3; ++i) {
//        result.x += tempcp1[i].x * muli[2 - i];
//        result.y += tempcp1[i].y * muli[2 - i];
//        result.z += tempcp1[i].z * muli[2 - i];
//    }
//    result.w = 1;
////    if (result.x == 0 && result.y == 0 && result.z ==0) {
////        parameters[gl_GlobalInvocationID.x].x = 1;
////    }
//    vertices[gl_GlobalInvocationID.x] = result;
//
////    if (gl_GlobalInvocationID.x >= parameters.length()) {
////        return;
////    }
//////    vec3 param = parameters[gl_GlobalInvocationID.x];
////    int index = int(mod(gl_GlobalInvocationID.x, 125));
////    vec3 ctrlPoint = controlPoints[index];
////    if (ctrlPoint.x == 0f && ctrlPoint.y == 0f && ctrlPoint.z == 0f && index != 62) {
////        parameters[gl_GlobalInvocationID.x].x = 1.5;
////    }else{
////        parameters[gl_GlobalInvocationID.x].x = -parameters[gl_GlobalInvocationID.x].x;
////    }
////    parameters[gl_GlobalInvocationID.x].y += 0.5;
////    parameters[gl_GlobalInvocationID.x].z += 0.5;
//
//}

