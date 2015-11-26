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
    int[] adjacencyBuffer;
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

layout(std430, binding=12) buffer OutputDebugBuffer{
    vec4[] myOutputBuffer;
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

BSplineInfo getBSplineInfo(vec4 parameter);


vec3 PNTriangleP[10];
vec3 PNTriangleN[6];

// 这些变量在求PNtriangle中也会用到，所以写成全区的
// 三角形三个顶点的index
uint original_index_0;
uint original_index_1;
uint original_index_2;

// 30,01,12这三条边对应的邻接三角形
int adjacency_triangle_index_0;
int adjacency_triangle_index_1;
int adjacency_triangle_index_2;

// 三个顶点位置
vec3 point0;
vec3 point1;
vec3 point2;

// 三个顶点法向
vec3 normal0;
vec3 normal1;
vec3 normal2;

const vec3 ZERO3 = vec3(0.000001);
const vec4 ZERO4 = vec4(0.000001);

// 生成PN-Triangle
void genPNTriangleP();

const vec3 splitParameter[10] = {
    {1,0,0},
    {0.6667, 0.3333, 0}, {0.6667, 0, 0.3333},
    {0.3333, 0.6667, 0}, {0.3333, 0.3333, 0.3333}, {0.3333, 0, 0.6667},
    {0, 1, 0}, {0, 0.6667, 0.3333}, {0, 0.3333, 0.6667}, {0, 0, 1}
};

const uvec3 splitIndex[9] = {
    {0, 1, 2},
    {1, 3 ,4}, {1, 4, 2}, {2, 4, 5},
    {3, 6, 7}, {3, 7, 4}, {4, 7, 8}, {4, 8, 5}, {5, 8, 9}
};

// 根据三角形形状，取得splite pattern
void getSplitePattern(vec3 p1, vec3 p2, vec3 p3, out uint parameterOffset, out uint indexOffset, out uint triangleNumber, out uint pointNumber);

// 根据 parameter 获得PNTriangle中的位置
vec4 getPosition(vec3 parameter);

// 根据 parameter 获得PNTriangle中的法向
vec4 getNormal(vec3 parameter);

// 计算采样点的BSpline body 信息
void genSamplePointBsplineInfo(uint index_offset);

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 3) {
        return;
    }

    // 初始化全局变量
    // get current original tirangle index
    original_index_0 = originalIndex[triangleIndex * 3];
    original_index_1 = originalIndex[triangleIndex * 3 + 1];
    original_index_2 = originalIndex[triangleIndex * 3 + 2];

    adjacency_triangle_index_0 = adjacencyBuffer[triangleIndex * 3];
    adjacency_triangle_index_1 = adjacencyBuffer[triangleIndex * 3 + 1];
    adjacency_triangle_index_2 = adjacencyBuffer[triangleIndex * 3 + 2];

    point0 = vec3(originalVertex[original_index_0]);
    point1 = vec3(originalVertex[original_index_1]);
    point2 = vec3(originalVertex[original_index_2]);

    normal0 = vec3(originalNormal[original_index_0]);
    normal1 = vec3(originalNormal[original_index_1]);
    normal2 = vec3(originalNormal[original_index_2]);

    // 生成pn-triangle
    genPNTriangleP();

    // 获取pattern
    uint splitParameterOffset;
    uint splitIndexOffset;
    uint subTriangleNumber;
    uint pointNumber;
    getSplitePattern(point0, point1, point2, splitParameterOffset, splitIndexOffset, subTriangleNumber, pointNumber);
    uint point_index[100];
    // 生成顶点数据
    for (int i = 0; i < pointNumber; ++i) {
        vec3 pointParameter = splitParameter[splitParameterOffset + i];
        uint point_offset = atomicCounterIncrement(point_counter);
        splitedVertex[point_offset] = getPosition(pointParameter);
        splitedNormal[point_offset] = getNormal(pointParameter);
        bSplineInfo[point_offset] = getBSplineInfo(splitedVertex[point_offset]);
        point_index[i] = point_offset;

    }
    // 生成index数据
    for (int i = 0; i < 9; ++i) {
        uvec3 index = splitIndex[splitIndexOffset + i];
        uint index_offset = atomicCounterIncrement(index_counter);
        splitedIndex[index_offset * 3] = point_index[index.x];
        splitedIndex[index_offset * 3 + 1] = point_index[index.y];
        splitedIndex[index_offset * 3 + 2] = point_index[index.z];
        genSamplePointBsplineInfo(index_offset);
    }
}

const vec3 sampleParameter[37] = {
    {1.000000, 0.000000, 0.000000},

    {0.833333, 0.166667, 0.000000},
    {0.833333, 0.000000, 0.166667},

    {0.666667, 0.333333, 0.000000},
    {0.666667, 0.166667, 0.166667},
    {0.666667, 0.000000, 0.333333},

    {0.500000, 0.500000, 0.000000},
    {0.500000, 0.333333, 0.166667},
    {0.500000, 0.166667, 0.333333},
    {0.500000, 0.000000, 0.500000},

    {0.333333, 0.666667, 0.000000},
    {0.333333, 0.500000, 0.166667},
    {0.333333, 0.333333, 0.333333},
    {0.333333, 0.166667, 0.500000},
    {0.333333, 0.000000, 0.666667},

    {0.166667, 0.833333, 0.000000},
    {0.166667, 0.666667, 0.166667},
    {0.166667, 0.500000, 0.333333},
    {0.166667, 0.333333, 0.500000},
    {0.166667, 0.166667, 0.666667},
    {0.166667, 0.000000, 0.833333},

    {0.000000, 1.000000, 0.000000},
    {0.000000, 0.833333, 0.166667},
    {0.000000, 0.666667, 0.333333},
    {0.000000, 0.500000, 0.500000},
    {0.000000, 0.333333, 0.666667},
    {0.000000, 0.166667, 0.833333},
    {0.000000, 0.000000, 1.000000},

    {1,0,0},
    {0.6667, 0.3333, 0}, {0.6667, 0, 0.3333},
    {0.3333, 0.6667, 0}, /*{0.3333, 0.3333, 0.3333},*/ {0.3333, 0, 0.6667},
    {0, 1, 0}, {0, 0.6667, 0.3333}, {0, 0.3333, 0.6667}, {0, 0, 1}

};


void genSamplePointBsplineInfo(uint index_offset) {
    vec4 p0 = splitedVertex[splitedIndex[index_offset * 3]];
    vec4 p1 = splitedVertex[splitedIndex[index_offset * 3 + 1]];
    vec4 p2 = splitedVertex[splitedIndex[index_offset * 3 + 2]];
    for (int i = 0; i < 37; ++i) {
        vec3 uvw = sampleParameter[i];
        vec4 position = p0 * uvw.x + p1 * uvw.y + p2 * uvw.z;
        samplePointBSplineInfo[index_offset * 37 + i] = getBSplineInfo(position);
    }
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
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;
    for (int i = 2; i >=0; --i) {
        for (int j = 2 - i; j >= 0; --j) {
            int k = 2 - i - j;
            float n = 2f / factorial(i) / factorial(j) / factorial(k)
                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            result += PNTriangleN[ctrlPointIndex ++] * n;
        }
    }
    return vec4(result, 1);
}

vec4 getPosition(vec3 parameter) {
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;

            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += PNTriangleP[ctrlPointIndex ++] * n;
        }
    }
    return vec4(result, 1);
}

void getSplitePattern(vec3 p1, vec3 p2, vec3 p3, out uint parameterOffset, out uint indexOffset, out uint triangleNumber, out uint pointNumber) {
    parameterOffset = 0;
    indexOffset = 0;
    triangleNumber = 9;
    pointNumber = 10;
}

vec3 getAdjacencyNormal(int triangleIndex, vec3 point, vec3 normal) {
    if (triangleIndex == -1) {
        return normal;
    }
    uint index0 = originalIndex[triangleIndex];
    uint index1 = originalIndex[triangleIndex + 1];
    uint index2 = originalIndex[triangleIndex + 2];
    if (all(lessThan(abs(vec3(originalVertex[index0]) - point), ZERO3))) {
        return vec3(originalNormal[index0]);
    } else if (all(lessThan(abs(vec3(originalVertex[index1]) - point), ZERO3))) {
        return vec3(originalNormal[index1]);
    } else {
        return vec3(originalNormal[index2]);
    }
}

vec3 genPNControlPoint(vec3 p_s, vec3 p_e, vec3 n, vec3 n_adj) {
    if (all(lessThan(abs(n - n_adj), ZERO3))) {
        return (2 * p_s + p_e - dot((p_e - p_s), n) * n) / 3;
    } else {
        vec3 T = cross(n, n_adj);
        return p_s + dot((p_e - p_s), T) / 3 * T;
    }
}

vec3 genPNControlNormal(vec3 p_s, vec3 p_e, vec3 n_s, vec3 n_e) {
    vec3 n = normalize(n_s + n_e);
    vec3 v = normalize(p_e - p_s);
    return normalize(n - 2 * v * dot(n, v));
}

void genPNTriangleP(){
    // 三个顶点对应的控制顶点
    PNTriangleP[0] = point0;
    PNTriangleP[6] = point1;
    PNTriangleP[9] = point2;

    //另接三角形的六个法向nij,i表示近顶点编号,j远顶点编号
    vec3 n02, n01, n10, n12, n21, n20;
    n02 = getAdjacencyNormal(adjacency_triangle_index_0, point0, normal0);
    n01 = getAdjacencyNormal(adjacency_triangle_index_1, point0, normal0);

    n10 = getAdjacencyNormal(adjacency_triangle_index_1, point1, normal1);
    n12 = getAdjacencyNormal(adjacency_triangle_index_2, point1, normal1);

    n21 = getAdjacencyNormal(adjacency_triangle_index_2, point2, normal2);
    n20 = getAdjacencyNormal(adjacency_triangle_index_0, point2, normal2);

    //two control point near p0
    PNTriangleP[2] = genPNControlPoint(point0, point2, normal0, n02);
    PNTriangleP[1] = genPNControlPoint(point0, point1, normal0, n01);
    //two control point near p1
    PNTriangleP[3] = genPNControlPoint(point1, point0, normal1, n10);
    PNTriangleP[7] = genPNControlPoint(point1, point2, normal1, n12);
    //two control point near p2
    PNTriangleP[8] = genPNControlPoint(point2, point1, normal2, n21);
    PNTriangleP[5] = genPNControlPoint(point2, point0, normal2, n20);

    vec3 E = (PNTriangleP[1] + PNTriangleP[2] + PNTriangleP[3]
    + PNTriangleP[5] + PNTriangleP[7] + PNTriangleP[8]) / 6;
    vec3 V = (point0 + point1 + point2) / 3;

    PNTriangleP[4] = E + (E - V) / 2;

    // 生成法向PN-triangle
    PNTriangleN[0] = normal0;
    PNTriangleN[3] = normal1;
    PNTriangleN[5] = normal2;

    PNTriangleN[1] = genPNControlNormal(point0, point1, normal0, normal1);
    PNTriangleN[4] = genPNControlNormal(point1, point2, normal1, normal2);
    PNTriangleN[2] = genPNControlNormal(point2, point0, normal2, normal0);

}

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

