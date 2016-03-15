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
    vec4 sample_point_original_normal;
    uvec4 knot_left_index;
};

struct SplitedTriangle {
    SamplePointInfo samplePoint[37];
    vec4 normal_adj[3];
    vec4 adjacency_normal[6];
    bool need_adj[6];
    vec4 original_normal[3];
    vec4 original_position[3];
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
uint original_index[3];

// 20,01,12这三条边对应的邻接三角形, 以及邻接三角形的边
int adjacency_triangle_index[3];
int adjacency_triangle_edge[3];

// 三个顶点位置
vec3 point[3];

// 三个顶点法向
vec3 normal[3];

// switch
uvec3 parameterSwitch;

const vec3 ZERO3 = vec3(0.000001);
const float ZERO = 0.000001;
const vec4 ZERO4 = vec4(0.000001);

//以下几个参数都是要经过预编译来初始化的
layout(std430, binding=9) buffer SplitedData{
    uvec4 splitIndex[];
    vec4 splitParameter[];
    uint offset_number[];
};
const int max_splite_factor = 0;
const uint look_up_table_for_i[0] = {0};
////////////////////////////////////////////////

//todo 改成可以由程序输入的
const float splite_factor = 0.3f;

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

uint getEdgeInfo(vec3 parameter);

vec3 changeParameter(vec3 parameter);

// 根据在整个bspline体中的参数求该采样点的相关信息
SamplePointInfo getBSplineInfo(SplitedTriangle st, int index);

// 根据三角形形状，取得splite pattern
void getSplitePattern(out uint indexOffset, out uint triangleNumber);

// 生成切割后的子三角形
SplitedTriangle genSubSplitedTriangle();

// 转化parameter
vec3 translate_parameter(vec3 parameter, uint edgeNo);


uint triangleIndex;
void main() {
    triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 3) {
        return;
    }

    // 初始化全局变量
    // get current original tirangle index
    original_index[0] = originalIndex[triangleIndex * 3];
    original_index[1] = originalIndex[triangleIndex * 3 + 1];
    original_index[2] = originalIndex[triangleIndex * 3 + 2];

    for (int i = 0; i < 3; ++i) {
        if (adjacencyBuffer[triangleIndex * 3 + i] == -1) {
            adjacency_triangle_index[i] = -1;
            adjacency_triangle_edge[i] = -1;
        } else {
            adjacency_triangle_index[i] = int(adjacencyBuffer[triangleIndex * 3 + i] / 4);
            adjacency_triangle_edge[i] = adjacencyBuffer[triangleIndex * 3 + i] & 3;
        }
    }

    point[0] = vec3(originalVertex[original_index[0]]);
    point[1] = vec3(originalVertex[original_index[1]]);
    point[2] = vec3(originalVertex[original_index[2]]);

    normal[0] = vec3(originalNormal[original_index[0]]);
    normal[1] = vec3(originalNormal[original_index[1]]);
    normal[2] = vec3(originalNormal[original_index[2]]);

    // 生成pn-triangle
    genPNTriangle();
    for (int i = 0; i < 6; ++i) {
        PNTriangleN_shared[triangleIndex * 6  + i] = PNTriangleN[i];
    }

//    for (int i = 0; i < 10; ++i) {
//        myOutputBuffer[triangleIndex * 10 + i].xyz = PNTriangleP[i];
//    }
    memoryBarrierBuffer();

    // 获取pattern
//    uint splitParameterOffset;
//    uint splitIndexOffset;
//    uint subTriangleNumber;
//    uint pointNumber;
//    getSplitePattern(splitIndexOffset, subTriangleNumber);

    uint splitIndexOffset;
    uint subTriangleNumber;
    getSplitePattern(splitIndexOffset, subTriangleNumber);


//    vec4 new_position[100];
//    vec4 new_normal_adj[100];
//    vec4 new_normal_org[100];
//    vec3 new_parameter[100];
//    uint new_edgeInfo[100];
//    // 生成顶点数据
//    for (int i = 0; i < pointNumber; ++i) {
//        new_parameter[i] = splitParameter[splitParameterOffset + i];
//        new_position[i] = getPosition(new_parameter[i]);
//        new_normal_adj[i] = getNormalAdj(new_parameter[i]);
//        new_normal_org[i] = getNormalOrg(new_parameter[i]);
//        new_edgeInfo[i] = splitParameterEdgeInfo[splitParameterOffset + i];
//    }

    //生成分割三角形
    uint aux1[6] = {5,0,1,2,3,4};
    uint aux2[6] = {2,0,0,1,1,2};
    for (uint i = splitIndexOffset; i < splitIndexOffset + subTriangleNumber; ++i) {
        uvec4 index = splitIndex[i];

        vec3 parameter[3];
        parameter[0] = changeParameter(splitParameter[index.x].xyz);
        parameter[1] = changeParameter(splitParameter[index.y].xyz);
        parameter[2] = changeParameter(splitParameter[index.z].xyz);

        SplitedTriangle st;

        st.original_normal[0] = getNormalOrg(parameter[0]);
        st.original_normal[1] = getNormalOrg(parameter[1]);
        st.original_normal[2] = getNormalOrg(parameter[2]);

        st.original_position[0] = getPosition(parameter[0]);
        st.original_position[1] = getPosition(parameter[1]);
        st.original_position[2] = getPosition(parameter[2]);

        st.normal_adj[0] = getNormalAdj(parameter[0]);
        st.normal_adj[1] = getNormalAdj(parameter[1]);
        st.normal_adj[2] = getNormalAdj(parameter[2]);

        uint edgeInfo[3];
        edgeInfo[0] = getEdgeInfo(parameter[0]);
        edgeInfo[1] = getEdgeInfo(parameter[1]);
        edgeInfo[2] = getEdgeInfo(parameter[2]);

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
            st.samplePoint[j] = getBSplineInfo(st, j);
        }

        output_triangles[atomicCounterIncrement(triangle_counter)] = st;
    }
//    for (int i = 0; i < 25344; ++i) {
//        myOutputBuffer[i*4] = splitParameter[i].x;
//        myOutputBuffer[i*4 + 1] = splitParameter[i].y;
//        myOutputBuffer[i*4 + 2] = splitParameter[i].z;
//        myOutputBuffer[i*4 + 3] = splitParameter[i].w;
//    }
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
    //todo
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
    vec3 result = normal[0] * parameter.x + normal[1] * parameter.y + normal[2] * parameter.z;
    //todo mark
    return vec4(normalize(result), 0);
}

vec4 getAdjacencyNormalPN(vec3 parameter,uint adjacency_triangle_index_) {
    vec3 result = vec3(0);
    uint ctrlPointIndex = adjacency_triangle_index_ * 6;
    //todo
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
    //todo
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


uint get_offset(int i, int j, int k){
    if (j - i + 1 <= max_splite_factor - 2 * i){
        return look_up_table_for_i[i - 1] + (j - i) * (i + 1) + k - j;
    } else {

        int qianmianbudongpaishu = max((max_splite_factor - 2 * i), 0);
        int shouxiang = min(i, max_splite_factor - i);
        int xiangshu = j - i - qianmianbudongpaishu;
        return look_up_table_for_i[i - 1] + (i + 1) * qianmianbudongpaishu + xiangshu * (shouxiang + (shouxiang + 1 - xiangshu)) / 2 + k - j;
    }
}

void getSplitePattern(out uint indexOffset, out uint triangleNumber) {
    float l01 = distance(point[0], point[1]);
    float l12 = distance(point[1], point[2]);
    float l20 = distance(point[2], point[0]);

    if (l01 < l12 && l01 < l20){
        if (l12 < l20){
            parameterSwitch.x = 0;
            parameterSwitch.y = 1;
            parameterSwitch.z = 2;
        } else {
            parameterSwitch.x = 1;
            parameterSwitch.y = 0;
            parameterSwitch.z = 2;
        }
    } else if (l12 < l20){
        if (l01 < l20) {
            parameterSwitch.x = 2;
            parameterSwitch.y = 1;
            parameterSwitch.z = 0;
        } else {
            parameterSwitch.x = 2;
            parameterSwitch.y = 0;
            parameterSwitch.z = 1;
        }
    } else {
        if (l12 < l01) {
            parameterSwitch.x = 0;
            parameterSwitch.y = 2;
            parameterSwitch.z = 1;
        } else {
            parameterSwitch.x = 1;
            parameterSwitch.y = 2;
            parameterSwitch.z = 0;
        }
    }

    float i, j, k;
    i = min(l01, min(l12, l20));
    k = max(l01, max(l12, l20));
    j = (l01 + l12 + l20) - i - k;
    i /= splite_factor;
    j /= splite_factor;
    k /= splite_factor;
    int i_i, j_i, k_i;
    i_i = int(ceil(i));
    j_i = int(ceil(j));
    k_i = int(ceil(k));

    uint offset = get_offset(i_i, j_i, k_i);
    indexOffset = offset_number[offset * 2];
    triangleNumber = offset_number[offset * 2 + 1];
}

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
    PNTriangleP[0] = point[0];
    PNTriangleP[6] = point[1];
    PNTriangleP[9] = point[2];

    //邻接三角形的六个法向nij,i表示近顶点编号,j远顶点编号
    vec3 n02, n01, n10, n12, n21, n20;
    n02 = getAdjacencyNormal(0, true, normal[0]);
    n01 = getAdjacencyNormal(1, false, normal[0]);
    n10 = getAdjacencyNormal(1, true, normal[1]);
    n12 = getAdjacencyNormal(2, false, normal[1]);
    n21 = getAdjacencyNormal(2, true, normal[2]);
    n20 = getAdjacencyNormal(0, false, normal[2]);


    //two control point near p0
    PNTriangleP[2] = genPNControlPoint(point[0], point[2], normal[0], n02);
    PNTriangleP[1] = genPNControlPoint(point[0], point[1], normal[0], n01);
    //two control point near p1
    PNTriangleP[3] = genPNControlPoint(point[1], point[0], normal[1], n10);
    PNTriangleP[7] = genPNControlPoint(point[1], point[2], normal[1], n12);
    //two control point near p2
    PNTriangleP[8] = genPNControlPoint(point[2], point[1], normal[2], n21);
    PNTriangleP[5] = genPNControlPoint(point[2], point[0], normal[2], n20);

    vec3 E = (PNTriangleP[1] + PNTriangleP[2] + PNTriangleP[3]
    + PNTriangleP[5] + PNTriangleP[7] + PNTriangleP[8]) / 6;
    vec3 V = (point[0] + point[1] + point[2]) / 3;

    PNTriangleP[4] = E + (E - V) / 2;

    // 生成法向PN-triangle
    PNTriangleN[0] = normal[0];
    PNTriangleN[3] = normal[1];
    PNTriangleN[5] = normal[2];

    PNTriangleN[1] = genPNControlNormal(point[0], point[1], normal[0], normal[1]);
    PNTriangleN[4] = genPNControlNormal(point[1], point[2], normal[1], normal[2]);
    PNTriangleN[2] = genPNControlNormal(point[2], point[0], normal[2], normal[0]);

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

SamplePointInfo getBSplineInfo(SplitedTriangle st, int index) {

            vec3 uvw = sampleParameter[index];
            vec4 parameter = st.original_position[0] * uvw.x + st.original_position[1] * uvw.y + st.original_position[2] * uvw.z;
//            vec4 normal = st.original_normal[0] * uvw.x + st.original_normal[1] * uvw.y + st.original_normal[2] * uvw.z;

//            st.samplePoint[j].original_normal = st.original_normal[0] * uvw.x + st.original_normal[1] * uvw.y + st.original_normal[2] * uvw.z;

    SamplePointInfo result;

    uint knot_left_index_u, knot_left_index_v, knot_left_index_w;
    float u = getBSplineInfoU(parameter.x, knot_left_index_u);
    float v = getBSplineInfoV(parameter.y, knot_left_index_v);
    float w = getBSplineInfoW(parameter.z, knot_left_index_w);

    result.parameter = vec4(u, v, w, 0);
    result.knot_left_index = uvec4(knot_left_index_u, knot_left_index_v, knot_left_index_w, 0);
    result.sample_point_original_normal = st.original_normal[0] * uvw.x + st.original_normal[1] * uvw.y + st.original_normal[2] * uvw.z;

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

uint getEdgeInfo(vec3 parameter) {
    uint result = 0;
    if (parameter.x < ZERO) {
        result += 1;
    }
    if (parameter.y < ZERO) {
        result += 2;
    }
    if (parameter.z < ZERO) {
        result += 4;
    }
    return result;
}

vec3 changeParameter(vec3 parameter) {
    if (parameterSwitch.x == 0) {
        if (parameterSwitch.y == 1) {
            return parameter.xyz;
        } else {
            return parameter.xzy;
        }
    } else if (parameterSwitch.x == 1){
        if (parameterSwitch.y == 2) {
            return parameter.yzx; //special
        } else {
            return parameter.yxz;
        }
    } else {
        if (parameterSwitch.y == 0) {
            return parameter.zxy; //special
        } else {
            return parameter.zyx;
        }
    }
}
