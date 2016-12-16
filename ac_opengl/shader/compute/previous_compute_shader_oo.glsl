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
layout(std430, binding=22) buffer OrinigalTexCoordBuffer{
    vec2[] orinigalTexCoord;
};

//input
layout(std430, binding=24) buffer OrinigalUVBuffer{
    vec2[] originalUV;
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



struct SplitedTriangle {
    vec4 pn_position[3];
    vec4 pn_normal[3];
    vec4 original_position[3];
    vec4 adjacency_pn_normal[6];
    uvec4 range;
#ifndef TIME
    ivec4 adjacency_triangle_index3_original_triangle_index1;
    vec4 parameter_in_original2_texcoord2[3];
    vec4 original_normal[3];
    vec2 bezier_uv[3];
    uint bezier_patch_id;
    float triangle_quality;
#endif
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

//input
layout(std140, binding=0) uniform BSplineBodyInfo{
    uniform vec3 BSplineBodyOrder;
    uniform vec3 BSplineBodyControlPointNum;
    uniform vec3 BSplineBodyLength;
};

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

const float ZERO = 0.000001;
const vec3 ZERO3 = vec3(ZERO);
const vec4 ZERO4 = vec4(ZERO);

//以下几个参数都是要经过预编译来初始化的
layout(std430, binding=9) buffer SplitedData{
    uvec4 splitIndex[];
    vec4 splitParameter[];
    uint offset_number[];
};
const int max_split_factor = 0;
const uint look_up_table_for_i[0] = {0};

layout(location=0) uniform float split_factor;

const int splitParameterEdgeInfoAux[7] = {-1,2,0,-1,1,-1,-1};

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

// 生成PN-Triangle
void genPNTriangle();

// 根据 parameter 获得PNTriangle中的法向
vec3 getPNNormal(vec3 parameter);

// 根据 parameter 获得普通插值法向
vec3 getNormalOrg(vec3 parameter);

// 根据 parameter 获得普通插值position
vec3 getPositionOrg(vec3 parameter);

// 根据 parameter 获得普通插值TexCoord
vec2 getTecCoordOrg(vec3 parameter);

// 根据 parameter 获得普通插值UV
vec2 getUV(vec3 parameter);

// 根据 parameter 获得邻接PNTriangle中的法向
vec4 getAdjacencyNormalPN(vec3 parameter,uint adjacency_triangle_index_);

// 根据 parameter 获得PNTriangle中的位置
vec3 getPNPosition(vec3 parameter);

uint getEdgeInfo(vec3 parameter);

vec4 changeParameter(vec4 parameter);

// 根据三角形形状，取得splite pattern
void getSplitePattern(out uint indexOffset, out uint triangleNumber);

// 转化parameter
vec3 translate_parameter(vec3 parameter, uint edgeNo);

uint triangleIndex;
const int isBezier = -1;


void main() {
    triangleIndex = gl_GlobalInvocationID.x;
    if (gl_GlobalInvocationID.x >= originalIndex.length() / 4 || originalIndex[triangleIndex * 4 + 3] == 0) {
        return;
    }

    // 初始化全局变量
    float BSplineBodyMinParameter[3];
    float BSplineBodyStep[3];
    uint BSplineBodyIntervalNumber[3];
    for (int i = 0; i < 3; ++i) {
        BSplineBodyIntervalNumber[i] = uint(BSplineBodyControlPointNum[i] - BSplineBodyOrder[i] + 1);
        BSplineBodyMinParameter[i] = -BSplineBodyLength[i] / 2;
        BSplineBodyStep[i] = BSplineBodyLength[i] / BSplineBodyIntervalNumber[i];
    }
    uvec3 rangeOffset = uvec3(BSplineBodyIntervalNumber[1] * BSplineBodyIntervalNumber[2],
                              BSplineBodyIntervalNumber[2],
                              1);

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

    for (int i = 0; i < 6; ++i) {
        PNTriangleN[i] = PNTriangleN_shared[triangleIndex * 6  + i].xyz;
    }
    for (int i = 0; i < 10; ++i) {
        PNTriangleP[i] = PNTriangleP_shared[triangleIndex * 10  + i].xyz;
    }

    // 获取pattern
    uint splitIndexOffset;
    uint subTriangleNumber;
    getSplitePattern(splitIndexOffset, subTriangleNumber);


    //生成分割三角形
    uint adjacency_normal_index_aux[6] = {5,0,1,2,3,4};
    uint edgeInfo[3];
    for (uint i = splitIndexOffset; i < splitIndexOffset + subTriangleNumber; ++i) {
        uvec4 index = splitIndex[i];
        SplitedTriangle st;
        vec3 parameter_in_original[3];
        for (int j = 0; j < 3; ++j) {
            parameter_in_original[j] = changeParameter(splitParameter[index[j]]).xyz;
            st.pn_position[j] = vec4(getPNPosition(parameter_in_original[j]), 1);
//            st.pn_position[j] = vec4(getPositionOrg(parameter_in_original[j]), 1);
            st.range[j] = 0;
            for (int k = 0; k < 3; ++k) {
                float temp = (st.pn_position[j][k] - BSplineBodyMinParameter[k]) / BSplineBodyStep[k];
                st.range[j] += (uint(min(floor(temp), BSplineBodyIntervalNumber[k] - 1)) * rangeOffset[k]);
            }

            st.pn_normal[j] = vec4(getPNNormal(parameter_in_original[j]), 0);
            st.original_position[j] = vec4(getPositionOrg(parameter_in_original[j]), 1);
            edgeInfo[j] = getEdgeInfo(parameter_in_original[j]);
#ifndef TIME
            st.parameter_in_original2_texcoord2[j].xy = parameter_in_original[j].xy;
            st.parameter_in_original2_texcoord2[j].zw = getTecCoordOrg(parameter_in_original[j]);
            st.original_normal[j] = vec4(getNormalOrg(parameter_in_original[j]), 0);
            if (isBezier > 0) {
                st.bezier_uv[j] = getUV(parameter_in_original[j]);
            }
#endif
        }

        int adjacency_triangle_index_edge[3];
        adjacency_triangle_index_edge[0] = splitParameterEdgeInfoAux[edgeInfo[2] & edgeInfo[0]];
        adjacency_triangle_index_edge[1] = splitParameterEdgeInfoAux[edgeInfo[0] & edgeInfo[1]];
        adjacency_triangle_index_edge[2] = splitParameterEdgeInfoAux[edgeInfo[1] & edgeInfo[2]];

        for (int j = 0; j < 3; ++j) {
            int currentEdge = adjacency_triangle_index_edge[j];
            int current_adjacency_triangle_index = -1;
            if (currentEdge != -1) {
                current_adjacency_triangle_index = adjacency_triangle_index[currentEdge];
            }

            if (current_adjacency_triangle_index != -1) {
                for (int k = 0; k < 2; ++k) {
                    uint temp = adjacency_normal_index_aux[j * 2 + k];
                    vec3 normal_parameter = translate_parameter(parameter_in_original[temp / 2], currentEdge);
                    vec4 adjacency_pn_normal = getAdjacencyNormalPN(normal_parameter, current_adjacency_triangle_index);
                    if (all(lessThan(abs(adjacency_pn_normal.xyz - st.pn_normal[temp / 2].xyz), ZERO3))) {
                        st.adjacency_pn_normal[temp] = vec4(0, 0, 1, -1);
                    } else {
                        st.adjacency_pn_normal[temp] = adjacency_pn_normal;
                    }
                }
            } else {
                for (int k = 0; k < 2; ++k) {
                    uint temp = adjacency_normal_index_aux[j * 2 + k];
                    st.adjacency_pn_normal[temp] = vec4(0, 0, 1, -1);
                }
            }
        }

#ifndef TIME
        vec3 t[3];
        for (int i = 0; i < 3; ++i) {
            t[i] = (st.pn_position[i] - st.pn_position[int(mod((i + 1), 3))]).xyz;
        }
        vec3 l;
        for (int i = 0; i < 3; ++i) {
            l[i] = sqrt(t[i].x * t[i].x + t[i].y * t[i].y + t[i].z * t[i].z);
        }

        float perimeter = l[0] + l[1] + l[2];
        float double_area = sqrt(perimeter * (-l[0] + l[1] + l[2]) * (l[0] - l[1] + l[2]) * (l[0] + l[1] - l[2])) / 2;
        float radius = double_area / perimeter;
        st.triangle_quality = radius / max(l[0], max(l[1], l[2])) * 3.4641016151377544;
        st.adjacency_triangle_index3_original_triangle_index1[3] = int(triangleIndex);
        if (isBezier > 0) {
            st.bezier_patch_id = uint(originalVertex[original_index[0]].w);
        }
#endif
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
vec3 getPNNormal(vec3 parameter) {
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
    return normalize(result);
}

vec2 getTecCoordOrg(vec3 parameter) {
    vec2 result = vec2(0);
    for (int i = 0; i < 3; ++i) {
        result += orinigalTexCoord[original_index[i]] * parameter[i];
    }
    return result;
}

vec2 getUV(vec3 parameter) {
    vec2 result = vec2(0);
    for (int i = 0; i < 3; ++i) {
        result += originalUV[original_index[i]] * parameter[i];
    }
    return result;
}

vec3 getPositionOrg(vec3 parameter) {
    vec3 result = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result += point[i] * parameter[i];
    }
    return result;
}

vec3 getNormalOrg(vec3 parameter) {
    vec3 result = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result += normal[i] * parameter[i];
    }
    return result;
}

vec4 getAdjacencyNormalPN(vec3 parameter,uint adjacency_triangle_index_) {
    vec3 result = vec3(0);
    uint ctrlPointIndex = adjacency_triangle_index_ * 6;
    for (int i = 2; i >=0; --i) {
        for (int j = 2 - i; j >= 0; --j) {
            int k = 2 - i - j;
            float n = 2f / factorial(i) / factorial(j) / factorial(k)
                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            result += PNTriangleN_shared[ctrlPointIndex ++].xyz * n;
        }
    }
    return vec4(normalize(result), 0);
}

// 根据 parameter 获得PNTriangle中的位置
vec3 getPNPosition(vec3 parameter) {
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;

    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += PNTriangleP_shared[triangleIndex * 10  + ctrlPointIndex].xyz * n;
            ++ ctrlPointIndex;
        }
    }
    return result;
}


uint get_offset(int i, int j, int k){
    if (j - i + 1 <= max_split_factor - 2 * i){
        return look_up_table_for_i[i - 1] + (j - i) * (i + 1) + k - j;
    } else {
        int qianmianbudongpaishu = max((max_split_factor - 2 * i), 0);
        int shouxiang = min(i, max_split_factor - i);
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
    i /= split_factor;
    j /= split_factor;
    k /= split_factor;
    int i_i, j_i, k_i;
    i_i = max(int(ceil(i)), 1);
    j_i = max(int(ceil(j)), 1);
    k_i = max(int(ceil(k)), 1);

    uint offset = get_offset(i_i, j_i, k_i);
    indexOffset = offset_number[offset * 2];
    triangleNumber = offset_number[offset * 2 + 1];
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

vec4 changeParameter(vec4 parameter) {
    if (parameterSwitch.x == 0) {
        if (parameterSwitch.y == 1) {
            return parameter.xyzw;
        } else {
            return parameter.xzyw;
        }
    } else if (parameterSwitch.x == 1){
        if (parameterSwitch.y == 2) {
            return parameter.yzxw; //special
        } else {
            return parameter.yxzw;
        }
    } else {
        if (parameterSwitch.y == 0) {
            return parameter.zxyw; //special
        } else {
            return parameter.zyxw;
        }
    }
}
