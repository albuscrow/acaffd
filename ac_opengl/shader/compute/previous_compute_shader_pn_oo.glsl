#version 450

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
    vec4[] PNTriangleN_shared;
};

//output
layout(std430, binding=19) buffer PNTrianglePShareBuffer{
    vec4[] PNTriangleP_shared;
};

// 20,01,12这三条边对应的邻接三角形, 以及邻接三角形的边
int adjacency_triangle_index[3];
int adjacency_triangle_edge[3];

// 三个顶点位置
vec3 point[3];

// 三个顶点法向
vec3 normal[3];

//代表PNtriangle
vec3 PNTriangleP[10];
vec3 PNTriangleN[6];

uint triangleIndex;

// 这些变量在求PNtriangle中也会用到，所以写成全区的
// 三角形三个顶点的index
uint original_index[3];

const float ZERO = 0.000001;
const vec3 ZERO3 = vec3(ZERO);
const vec4 ZERO4 = vec4(ZERO);

//todo 有优化空间
vec3 getAdjacencyNormal(uint adjacency_index, bool isFirst, vec3 normal) {
    int triangleIndex = adjacency_triangle_index[adjacency_index];
    if (triangleIndex == -1) {
        return normal;
    }
    int pointIndex = adjacency_triangle_edge[adjacency_index];
    if (isFirst) {
        if (pointIndex == 0) {
            pointIndex = 3;
        }
        pointIndex -= 1;
    }
    return vec3(originalNormal[
                               originalIndex[
                                             triangleIndex * 4
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
    vec3 n = n_s + n_e;
    vec3 v = p_e - p_s;
    if (all(lessThan(abs(v), ZERO3))) {
        return normalize(n);
    } else {
        return normalize(n - 2 * dot(v, n) / dot(v, v) * v);
    }
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

//表示group size,这个问题中group size与具体问题无关，先取512,后面再调优
layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

void main() {
    triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 4) {
        return;
    }

    // 初始化全局变量
    for (int i = 0; i < 3; ++i) {
        if (adjacencyBuffer[triangleIndex * 3 + i] == -1) {
            adjacency_triangle_index[i] = -1;
            adjacency_triangle_edge[i] = -1;
        } else {
            adjacency_triangle_index[i] = int(adjacencyBuffer[triangleIndex * 3 + i] / 4);
            adjacency_triangle_edge[i] = adjacencyBuffer[triangleIndex * 3 + i] & 3;
        }
    }

    // get current tirangle index point and normal
    for (int i = 0; i < 3; ++i) {
        original_index[i] = originalIndex[triangleIndex * 4 + i];
        point[i] = vec3(originalVertex[original_index[i]]);
        normal[i] = vec3(originalNormal[original_index[i]]);
    }

    // 生成pn-triangle
    genPNTriangle();

    for (int i = 0; i < 6; ++i) {
        PNTriangleN_shared[triangleIndex * 6  + i].xyz = PNTriangleN[i];
    }
    for (int i = 0; i < 10; ++i) {
        PNTriangleP_shared[triangleIndex * 10  + i].xyz = PNTriangleP[i];
    }
}
