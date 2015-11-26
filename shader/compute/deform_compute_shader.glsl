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

struct BSplineInfo {
    vec4 t;
    uvec4 knot_left_index;
    uvec4 aux_matrix_offset;
};

layout(std430, binding=10) buffer SplitedBSplineInfoBuffer{
    BSplineInfo[] bSplineInfo;
};

layout(std430, binding=13) buffer SamplePointBSplineInfoBuffer{
    BSplineInfo[] samplePointBSplineInfo;
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

//控制顶点
layout(location=1) uniform vec3[125] controlPoints;
vec4 sample_bspline(BSplineInfo bsi);

const float Mr[370] = {
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0,
//0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6585365853658537, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8780487804878049, 0.0, 0.0
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 3.0, 0.0, -1.5, 0.0, 0.3333333333333333, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 0.0, 3.0, 0.0, -1.5, 0.0, 0.0, 0.0, 0.3333333333333333,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, -1.5, 0.0, 3.0, 0.0, -0.8333333333333334, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.4390243902439024, 0.0, 0.0, 0.6585365853658537, 0.6585365853658537, 0.0, 0.0, 0.6585365853658537, 0.8780487804878049, 0.6585365853658537, 0.0, 0.0, 0.4390243902439024, 0.6585365853658537, 0.6585365853658537, 0.4390243902439024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2784552845528455, -0.9969512195121951, -0.9969512195121951, -0.9969512195121951, -0.9969512195121951, 0.2784552845528455, -0.9969512195121951, -0.9969512195121951, 0.2784552845528455,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, 0.0, -1.5, 0.0, 3.0, 0.0, 0.0, 0.0, -0.8333333333333334,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.8333333333333334, 3.0, -1.5, 0.3333333333333333,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3333333333333333, -1.5, 3.0, -0.8333333333333334,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
};

const vec3 tessellatedParameter[10] = {
    {1,0,0},
    {0.6667, 0.3333, 0}, {0.6667, 0, 0.3333},
    {0.3333, 0.6667, 0}, {0.3333, 0.3333, 0.3333}, {0.3333, 0, 0.6667},
    {0, 1, 0}, {0, 0.6667, 0.3333}, {0, 0.3333, 0.6667}, {0, 0, 1}
};

const uvec3 tessellateIndex[9] = {
    {0, 1, 2},
    {1, 3 ,4}, {1, 4, 2}, {2, 4, 5},
    {3, 6, 7}, {3, 7, 4}, {4, 7, 8}, {4, 8, 5}, {5, 8, 9}
};

vec4 bezierControlPoint[10];
vec4 getPosition(vec3 parameter);
vec4 getNormal(vec3 parameter);

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= uint(triangleNumber)) {
        return;
    }

    // 采样控制顶点
    vec4 sample_points[37];
    for (int i = 0; i < 37; ++i) {
        sample_points[i] = sample_bspline(samplePointBSplineInfo[triangleIndex * 37 + i]);
    }
    // 计算Bezier曲面片控制顶点
    for (int i = 0; i < 10; ++i) {
        bezierControlPoint[i] = vec4(0);
        for (int j = 0; j < 37; ++j) {
            bezierControlPoint[i] += sample_points[j] * Mr[i * 37 + j];
        }
    }

    // 细分
    // 生成顶点数据
    uint point_index[100];
    for (int i = 0; i < 10; ++i) {
        vec3 pointParameter = tessellatedParameter[i];
        uint point_offset = triangleIndex * 10 + i;
        tessellatedVertex[point_offset] = getPosition(pointParameter);
//        tessellatedVertex[point_offset] = bezierControlPoint[i];
        tessellatedNormal[point_offset] = getNormal(pointParameter);
        point_index[i] = point_offset;
    }
    // 生成index数据
    for (int i = 0; i < 9; ++i) {
        uvec3 index = tessellateIndex[i];
        uint index_offset = triangleIndex * 9 + i;
        tessellatedIndex[index_offset * 3] = point_index[index.x];
        tessellatedIndex[index_offset * 3 + 1] = point_index[index.y];
        tessellatedIndex[index_offset * 3 + 2] = point_index[index.z];
    }

//    uint splited_index_1 = splitedIndex[triangleIndex * 3];
//    uint splited_index_2 = splitedIndex[triangleIndex * 3 + 1];
//    uint splited_index_3 = splitedIndex[triangleIndex * 3 + 2];
//    tessellatedIndex[triangleIndex * 3] = splited_index_1;
//    tessellatedIndex[triangleIndex * 3 + 1] = splited_index_2;
//    tessellatedIndex[triangleIndex * 3 + 2] = splited_index_3;
//    tessellatedVertex[splited_index_1] = sample_bspline(bSplineInfo[splited_index_1]);
//    tessellatedVertex[splited_index_2] = sample_bspline(bSplineInfo[splited_index_2]);
//    tessellatedVertex[splited_index_3] = sample_bspline(bSplineInfo[splited_index_3]);
//    tessellatedNormal[splited_index_1] = splitedNormal[splited_index_1];
//    tessellatedNormal[splited_index_2] = splitedNormal[splited_index_2];
//    tessellatedNormal[splited_index_3] = splitedNormal[splited_index_3];
}

float factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return float(result);
}

float power(float b, int n) {
    if (b == 0 && n == 0) {
        return 1;
    } else {
        return pow(b, n);
    }
}

vec4 getNormal(vec3 parameter) {
//    vec3 result = vec3(0);
//    int ctrlPointIndex = 0;
//    for (int i = 2; i >=0; --i) {
//        for (int j = 2 - i; j >= 0; --j) {
//            int k = 2 - i - j;
//            float n = 2f / factorial(i) / factorial(j) / factorial(k)
//                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
//            result += PNTriangleN[ctrlPointIndex ++] * n;
//        }
//    }
//    return vec4(result, 1);
    return vec4(1.0);
}

vec4 getPosition(vec3 parameter) {
    vec4 result = vec4(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += bezierControlPoint[ctrlPointIndex ++] * n;
        }
    }
    return vec4(result.xyz, 1);
}

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

vec4 sample_bspline(BSplineInfo bsi) {
    vec4 result;
    vec3 tempcp1[4];
    vec3 tempcp2[4][4];

    int uli = int(bsi.knot_left_index.x);
    float u = bsi.t.x;
    int vli = int(bsi.knot_left_index.y);
    float v = bsi.t.y;
    int wli = int(bsi.knot_left_index.z);
    float w = bsi.t.z;
//    return vec4(bsi.aux_matrix_offset.z, bsi.aux_matrix_offset.y, bsi.aux_matrix_offset.z, 1);

    float temp[4];
    float muli[4];
    temp[0] = 1.0f;
    temp[1] = w;
    temp[2] = w * w;
    temp[3] = temp[2] * w;

    int matrix_offset = int(bsi.aux_matrix_offset.z);

    for (int i = 0; i < 3; ++i) {
        muli[i] = 0.0f;
        for (int j = 0; j < 3; ++j) {
            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
        }
    }

    for (int i = 0; i < 3; ++i){
        for (int j = 0; j < 3; ++j){
            tempcp2[i][j] = vec3(0.0f);
            for (int k = 0; k < 3; ++k) {
                vec3 cp = controlPoints[int((uli - i) * 25 + (vli - j) * 5 + wli - k)];
                tempcp2[i][j].x += cp.x * muli[2 - k];
                tempcp2[i][j].y += cp.y * muli[2 - k];
                tempcp2[i][j].z += cp.z * muli[2 - k];
            }
        }
    }

    temp[1] = v;
    temp[2] = v * v;
    temp[3] = temp[2] * v;

    matrix_offset = int(bsi.aux_matrix_offset.y);
    for (int i = 0; i < 3; ++i) {
        muli[i] = 0.0;
        for (int j = 0; j < 3; ++j) {
            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
        }
    }

    for (int i = 0; i < 3; ++i) {
        tempcp1[i] = vec3(0.0);
        for (int j = 0; j < 3; ++j) {
            tempcp1[i].x += tempcp2[i][j].x * muli[2 - j];
            tempcp1[i].y += tempcp2[i][j].y * muli[2 - j];
            tempcp1[i].z += tempcp2[i][j].z * muli[2 - j];
        }
    }

    temp[1] = u;
    temp[2] = u * u;
    temp[3] = temp[2] * u;

    matrix_offset = int(bsi.aux_matrix_offset.x);

    for (int i = 0; i < 3; ++i) {
        muli[i] = 0.0;
        for (int j = 0; j < 3; ++j) {
            muli[i] += temp[j] * sample_aux_matrix[matrix_offset + j * 3 + i];
        }
    }

    result = vec4(0);
    for (int i = 0; i < 3; ++i) {
        result.x += tempcp1[i].x * muli[2 - i];
        result.y += tempcp1[i].y * muli[2 - i];
        result.z += tempcp1[i].z * muli[2 - i];
    }
    result.w = 1;
    return result;
}
