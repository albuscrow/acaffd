#version 450
//input
layout(std140, binding=0) uniform BSplineBodyInfo{
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

//input
layout(std430, binding=0) buffer OriginalVertexBuffer{
    vec4[] originalVertex;
};

//input
layout(std430, binding=1) buffer OrinigalNormalBuffer{
    vec4[] originalNormal;
};

//input
layout(std430, binding=2) buffer OriginalNormalBuffer{
    uint[] originalIndex;
};

//input
layout(std430, binding=3) buffer AdjacencyBuffer{
    int[] adjacencyBuffer;
};

//share
layout(std430, binding=4) buffer PNTriangleNShareBuffer{
    vec3[] PNTriangleN_shared;
};

struct SamplePointInfo {
    vec4 parameter;
    vec4 original_normal;
    uvec4 knot_left_index;
};

struct SplitedTriangle {
    SamplePointInfo samplePoint[37];
    vec4 normal_adj[3];
    vec4 adjacency_normal[6];
    bool need_adj[6];
};


//output
layout(std430, binding=5) buffer TriangleBuffer{
    SplitedTriangle[] output_triangles;
};

//debug
layout(std430, binding=14) buffer OutputDebugBuffer{
    vec4[] myOutputBuffer;
};

//三角形计数器，因为是多个线程一起产生三角形的，并且存在同一个数组。所以需要这个计数器来同步
layout(binding = 0) uniform atomic_uint triangle_counter;

//表示group size,这个问题中group size与具体问题无关，先取512,后面再调优
layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

//代表PNtriangle
vec3 PNTriangleP[10];
vec3 PNTriangleN[6];

// 这些变量在求PNtriangle中也会用到，所以写成全区的
// 三角形三个顶点的index
uint original_index_0;
uint original_index_1;
uint original_index_2;

// 20,01,12这三条边对应的邻接三角形, 以及邻接三角形的边
int adjacency_triangle_index[3];
int adjacency_triangle_edge[3];

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

//以下两个定义切割pattern
const vec3 splitParameter[10] = {
    {1,0,0},
    {0.6667, 0.3333, 0}, {0.6667, 0, 0.3333},
    {0.3333, 0.6667, 0}, {0.3333, 0.3333, 0.3333}, {0.3333, 0, 0.6667},
    {0, 1, 0}, {0, 0.6667, 0.3333}, {0, 0.3333, 0.6667}, {0, 0, 1}
};

const uint splitParameterEdgeInfoAux[5] = {-1,2,0,-2,1};

const uint splitParameterChangeAux[3][3] =
{{1,0,2},
 {0,2,1},
 {2,1,0}};
/**
   v,u,w
   u,w,v
   w,v,u
   splitParameterChangeAux[i][j]
   i表示当前三角形的边编号
   j表示邻接三角形的边编号
   splitParameterChangeAux[i][j]表示从当前三角形的parameter转到邻接三角形,不变的那个分量,另外两个分量交换值
**/

const uint splitParameterEdgeInfo[10] = {
6,
4,2,
4,0,2,
5,1,1,3};

const uvec3 splitIndex[9] = {
    {0, 1, 2},
    {1, 3 ,4}, {1, 4, 2}, {2, 4, 5},
    {3, 6, 7}, {3, 7, 4}, {4, 7, 8}, {4, 8, 5}, {5, 8, 9}
};


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



// 生成PN-Triangle
void genPNTriangle();

// 根据 parameter 获得PNTriangle中的法向
vec4 getNormalAdj(vec3 parameter);

// 根据 parameter 获得普通插值法向
vec4 getNormalOrg(vec3 parameter);

// 根据 parameter 获得邻接PNTriangle中的法向
vec4 getAdjacencyNormalPN(vec3 parameter,uint adjacency_triangle_index_);

// 根据 parameter 获得PNTriangle中的位置
vec4 getPosition(vec3 parameter);

// 根据在整个bspline体中的参数求该采样点的相关信息
SamplePointInfo getBSplineInfo(vec4 parameter);

// 根据三角形形状，取得splite pattern
void getSplitePattern(out uint parameterOffset, out uint indexOffset, out uint triangleNumber, out uint pointNumber);

// 生成切割后的子三角形
SplitedTriangle genSubSplitedTriangle();

// 转化parameter
vec3 translate_parameter(vec3 parameter, uint edgeNo);


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

    for (int i = 0; i < 3; ++i) {
        if (adjacencyBuffer[triangleIndex * 3 + i] == -1) {
            adjacency_triangle_index[i] = -1;
            adjacency_triangle_edge[i] = -1;
        } else {
            adjacency_triangle_index[i] = int(adjacencyBuffer[triangleIndex * 3 + i] / 4);
            adjacency_triangle_edge[i] = adjacencyBuffer[triangleIndex * 3 + i] & 3;
        }
    }

    point0 = vec3(originalVertex[original_index_0]);
    point1 = vec3(originalVertex[original_index_1]);
    point2 = vec3(originalVertex[original_index_2]);

    normal0 = vec3(originalNormal[original_index_0]);
    normal1 = vec3(originalNormal[original_index_1]);
    normal2 = vec3(originalNormal[original_index_2]);

    normal0 = normalize(normal0);
    normal1 = normalize(normal1);
    normal2 = normalize(normal2);

    // 生成pn-triangle
    genPNTriangle();
    for (int i = 0; i < 6; ++i) {
        PNTriangleN_shared[triangleIndex * 6  + i] = PNTriangleN[i];
    }
    memoryBarrierBuffer();

    // 获取pattern
    uint splitParameterOffset;
    uint splitIndexOffset;
    uint subTriangleNumber;
    uint pointNumber;
    getSplitePattern(splitParameterOffset, splitIndexOffset, subTriangleNumber, pointNumber);


    vec4 new_position[100];
    vec4 new_normal_adj[100];
    vec4 new_normal_org[100];
    vec3 new_parameter[100];
    uint new_edgeInfo[100];
    // 生成顶点数据
    for (int i = 0; i < pointNumber; ++i) {
        new_parameter[i] = splitParameter[splitParameterOffset + i];
        new_position[i] = getPosition(new_parameter[i]);
        new_normal_adj[i] = getNormalAdj(new_parameter[i]);
        new_normal_org[i] = getNormalOrg(new_parameter[i]);
        new_edgeInfo[i] = splitParameterEdgeInfo[splitParameterOffset + i];
    }

    //生成分割三角形
    uint aux1[6] = {5,0,1,2,3,4};
    uint aux2[6] = {2,0,0,1,1,2};
    for (int i = 0; i < subTriangleNumber; ++i) {
        uvec3 index = splitIndex[splitIndexOffset + i];
        SplitedTriangle st;

        st.normal_adj[0] = new_normal_adj[index.x];
        st.normal_adj[1] = new_normal_adj[index.y];
        st.normal_adj[2] = new_normal_adj[index.z];

        vec3 parameter[3];
        parameter[0] = new_parameter[index.x];
        parameter[1] = new_parameter[index.y];
        parameter[2] = new_parameter[index.z];


        uint edgeInfo[3];
        edgeInfo[0] = new_edgeInfo[index.x];
        edgeInfo[1] = new_edgeInfo[index.y];
        edgeInfo[2] = new_edgeInfo[index.z];

        uint adjacency_triangle_index_edge[3];
        adjacency_triangle_index_edge[0] = splitParameterEdgeInfoAux[edgeInfo[2] & edgeInfo[0]];
        adjacency_triangle_index_edge[1] = splitParameterEdgeInfoAux[edgeInfo[0] & edgeInfo[1]];
        adjacency_triangle_index_edge[2] = splitParameterEdgeInfoAux[edgeInfo[1] & edgeInfo[2]];

        for (int j = 0; j < 3; ++j) {
            uint currentEdge = adjacency_triangle_index_edge[j];
            uint adjacency_triangle_index_ = adjacency_triangle_index[currentEdge];
            if (currentEdge == -1 || adjacency_triangle_index_ == -1) {
                st.need_adj[aux1[j * 2]] = false;
                st.need_adj[aux1[j * 2 + 1]] = false;
            } else {
                for (int k = 0; k < 2; ++k) {
                    int index = j * 2 + k;
                    vec3 adjacency_parameter = translate_parameter(parameter[aux2[index]], currentEdge);
                    st.adjacency_normal[aux1[index]] = getAdjacencyNormalPN(adjacency_parameter, adjacency_triangle_index_);
                    st.need_adj[aux1[index]] = !all(lessThan(abs(st.adjacency_normal[aux1[index]] - st.normal_adj[aux2[index]]), ZERO4));
                }
            }
        }

        for (int j = 0; j < 37; ++j) {
            vec3 uvw = sampleParameter[j];
            vec4 position = new_position[index.x] * uvw.x + new_position[index.y] * uvw.y + new_position[index.z] * uvw.z;
            vec4 normal = new_normal_org[index.x] * uvw.x + new_normal_org[index.y] * uvw.y + new_normal_org[index.z] * uvw.z;
            st.samplePoint[j] = getBSplineInfo(position);
            st.samplePoint[j].original_normal = normal;
        }

        output_triangles[atomicCounterIncrement(triangle_counter)] = st;
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


// 根据 parameter 获得PNTriangle中的法向
vec4 getNormalAdj(vec3 parameter) {
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
    return vec4(normalize(result), 0);
}

vec4 getNormalOrg(vec3 parameter) {
    vec3 result = normal0 * parameter.x + normal1 * parameter.y + normal2 * parameter.z;
    return vec4(normalize(result), 0);
}

vec4 getAdjacencyNormalPN(vec3 parameter,uint adjacency_triangle_index_) {
    vec3 result = vec3(0);
    uint ctrlPointIndex = adjacency_triangle_index_ * 6;
    for (int i = 2; i >=0; --i) {
        for (int j = 2 - i; j >= 0; --j) {
            int k = 2 - i - j;
            float n = 2f / factorial(i) / factorial(j) / factorial(k)
                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            result += PNTriangleN_shared[ctrlPointIndex ++] * n;
        }
    }
    return vec4(normalize(result), 0);
}

// 根据 parameter 获得PNTriangle中的位置
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

void getSplitePattern(out uint parameterOffset, out uint indexOffset, out uint triangleNumber, out uint pointNumber) {
    parameterOffset = 0;
    indexOffset = 0;
    triangleNumber = 9;
    pointNumber = 10;
}

//vec3 getAdjacencyNormalForSubTriangle(int triangleIndex, vec3 point, vec3 normal) {
//    if (triangleIndex == -1) {
//        return normal;
//    }
//    uint index0 = originalIndex[triangleIndex];
//    uint index1 = originalIndex[triangleIndex + 1];
//    uint index2 = originalIndex[triangleIndex + 2];
//    if (all(lessThan(abs(vec3(originalVertex[index0]) - point), ZERO3))) {
//        return vec3(originalNormal[index0]);
//    } else if (all(lessThan(abs(vec3(originalVertex[index1]) - point), ZERO3))) {
//        return vec3(originalNormal[index1]);
//    } else {
//        return vec3(originalNormal[index2]);
//    }
//}

vec3 getAdjacencyNormal(uint adjacency_index, bool isFirst, vec3 normal) {
    uint triangleIndex = adjacency_triangle_index[adjacency_index];
    if (triangleIndex == -1) {
        return normal;
    }
    uint pointIndex = adjacency_triangle_edge[adjacency_index];
    if (isFirst) {
        if (pointIndex == 0) {
            pointIndex = 3;
        }
        pointIndex -= 1;
    }
    return vec3(originalNormal[
                               originalIndex[
                                             triangleIndex * 3
                                             + pointIndex
                                            ]
                              ]);
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

void genPNTriangle(){
    // 三个顶点对应的控制顶点
    PNTriangleP[0] = point0;
    PNTriangleP[6] = point1;
    PNTriangleP[9] = point2;

    //邻接三角形的六个法向nij,i表示近顶点编号,j远顶点编号
    vec3 n02, n01, n10, n12, n21, n20;
    n02 = getAdjacencyNormal(0, true, normal0);
    n01 = getAdjacencyNormal(1, false, normal0);

    n10 = getAdjacencyNormal(1, true, normal1);
    n12 = getAdjacencyNormal(2, false, normal1);

    n21 = getAdjacencyNormal(2, true, normal2);
    n20 = getAdjacencyNormal(0, false, normal2);

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

SamplePointInfo getBSplineInfo(vec4 parameter) {
    SamplePointInfo result;

    uint knot_left_index_u, knot_left_index_v, knot_left_index_w;
    float u = getBSplineInfoU(parameter.x, knot_left_index_u);
    float v = getBSplineInfoV(parameter.y, knot_left_index_v);
    float w = getBSplineInfoW(parameter.z, knot_left_index_w);

    result.parameter = vec4(u, v, w, 0);
    result.knot_left_index = uvec4(knot_left_index_u, knot_left_index_v, knot_left_index_w, 0);

    return result;
}

vec3 translate_parameter(vec3 parameter, uint edgeNo) {
    uint unchange = splitParameterChangeAux[edgeNo][adjacency_triangle_edge[edgeNo]];
    if (unchange == 0) {
        return parameter.xzy;
    } else if(unchange == 1) {
        return parameter.zyx;
    } else {
        return parameter.yxz;
    }
}
