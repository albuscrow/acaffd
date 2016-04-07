#version 450

//input
layout(std140, binding=0) uniform BSplineBodyInfo{
    uniform vec3 BSplineBodyOrder;
    uniform vec3 BSplineBodyControlPointNum;
    uniform vec3 BSplineBodyLength;
};

struct SamplePoint {
    vec3 position;
    vec3 normal;
    uvec3 knot_left_index;
};

struct SplitedTriangle {
    vec4 pn_position[3];
    vec4 pn_normal[3];
    vec4 original_position[3];
    vec4 original_normal[3];
    vec4 adjacency_pn_normal_parameter[6];
    vec4 parameter_in_original[3];
    ivec4 adjacency_triangle_index3_original_triangle_index1;
    float triangle_quality;
};

//input
coherent layout(std430, binding=4) buffer PNTriangleNShareBuffer{
    vec3[] PNTriangleN_shared;
};

//input
layout(std430, binding=5) buffer TriangleBuffer{
    SplitedTriangle[] input_triangles;
};

//input
//用于加速计算的控制顶点
layout(std140, binding=1) uniform ControlPointForSample{
    uniform vec4[729] newControlPoints;
};


//output
layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
};

//input
layout(std430, binding=21) buffer TessellatedParameterInBSplineBody{
    vec4[] tessellatedParameterInBSplineBody;
};

//output
layout(std430, binding=7) buffer TesselatedNormalBuffer{
    vec4[] tessellatedNormal;
};

//output
layout(std430, binding=8) buffer TesselatedIndexBuffer{
    uint[] tessellatedIndex;
};

//output
layout(std430, binding=15) buffer ControlPoint{
    vec4[] controlPoint3pointParameter1;
};

//output
layout(std430, binding=16) buffer ControlPointIndex{
    uint[] controlPointIndex;
};

//output
layout(std430, binding=17) buffer PositionSplitedTriangle{
    vec4[] positionSplitedTriangle;
};

//output
layout(std430, binding=18) buffer NormalSplitedTriangle{
    vec4[] normalSplitedTriangle;
};

//input
layout(std430, binding=19) buffer PNTrianglePShareBuffer{
    vec3[] PNTriangleP_shared;
};


//output
layout(std430, binding=10) buffer ParameterInOriginalBuffer{
    vec4[] parameterInOriginal3_triangle_quality1;
};

//output
layout(std430, binding=11) buffer ParameterInSplitBuffer{
    vec4[] parameterInSplit;
};


//output
layout(std430, binding=12) buffer RealPosition{
    vec4[] realPosition;
};

//output
layout(std430, binding=13) buffer RealNormal{
    vec4[] realNormal;
};


//debug
layout(std430, binding=14) buffer OutputDebugBuffer{
    vec4[] myOutputBuffer;
};

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;
const vec3 ZERO3 = vec3(0.000001);
const float Mr[370] = {
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
const float aux_control_parameter[10] = {
   0,
   1,2,
   2,0,1,
   0,1,2,0
};

const uvec3 aux_control_index[9] =
{{1 ,2 ,0},
{3 ,4 ,1},
{2 ,1 ,4},
{4 ,5 ,2},
{6 ,7 ,3},
{4 ,3 ,7},
{7 ,8 ,4},
{5 ,4 ,8},
{8 ,9 ,5}};

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



layout(location=0) uniform uint triangleNumber;
layout(location=1) uniform uint vw;
layout(location=2) uniform uint w;
layout(location=4) uniform uint tessellatedParameterLength;
layout(location=5) uniform uint tessellateIndexLength;
layout(location=6) uniform int adjust_control_point;

layout(std140, binding=2) uniform TessellatedParameter{
    uniform vec4[66] tessellatedParameter;
};

layout(std140, binding=3) uniform TessellateIndex{
    uniform uvec4[100] tessellateIndex;
};

vec3 bezierPositionControlPoint[10];
vec3 bezierNormalControlPoint[10];
vec4 getPosition(vec3 parameter);
vec3 getPositionInOriginalPNTriangle(vec3 parameter, uint original_triangle_index);
vec3 getNormalInOriginalPNTriangle(vec3 parameter, uint original_triangle_index);
vec4 getNormal(vec3 parameter);
vec4 getTessellatedSplitParameter(vec4[3] split_parameter, vec4 tessellatedParameter);

void getSamplePointHelper(inout SamplePoint samplePoint);
SamplePoint getSamplePointBeforeSample(vec3 parameter);

void sampleFast(inout SamplePoint spi);
vec3 sampleFastNormal(in SamplePoint spi);
vec4 getParameterInBSplineBody(vec3 pointParameter);

// 代表三个方向B spline body的区间数
float BSplineBodyMinParameter[3];
float BSplineBodyStep[3];
float BSplineBodyIntervalNumber[3];

SplitedTriangle currentTriangle;
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= triangleNumber) {
        return;
    }

    for (int i = 0; i < 3; ++i) {
        BSplineBodyIntervalNumber[i] = BSplineBodyControlPointNum[i] - BSplineBodyOrder[i] + 1;
        BSplineBodyMinParameter[i] = -BSplineBodyLength[i] / 2;
        BSplineBodyStep[i] = BSplineBodyLength[i] / BSplineBodyIntervalNumber[i];
    }


    currentTriangle = input_triangles[triangleIndex];
    // 计算采样点
    SamplePoint samplePoint[37];
    for (int i = 0; i < 37; ++i) {
        samplePoint[i] = getSamplePointBeforeSample(sampleParameter[i]);
    }

    uint vertexIndexInSamplePoint[3] = {0,21,27};
    SamplePoint samplePointForNormal[3];
    for (int i = 0; i < 3; ++i) {
        samplePointForNormal[i] = samplePoint[vertexIndexInSamplePoint[i]];
        samplePointForNormal[i].normal = currentTriangle.pn_normal[i].xyz;
        currentTriangle.pn_normal[i].xyz = sampleFastNormal(samplePointForNormal[i]);
    }

    for (int i = 0; i < 37; ++i) {
        sampleFast(samplePoint[i]);
    }

    for (int i = 0; i < 3; ++i) {
        currentTriangle.pn_position[i].xyz = samplePoint[vertexIndexInSamplePoint[i]].position;
    }

    // 计算Bezier曲面片控制顶点
    for (int i = 0; i < 10; ++i) {
        bezierPositionControlPoint[i] = vec3(0);
        bezierNormalControlPoint[i] = vec3(0);
        for (int j = 0; j < 37; ++j) {
            bezierPositionControlPoint[i] += samplePoint[j].position * Mr[i * 37 + j];
            bezierNormalControlPoint[i] += samplePoint[j].normal * Mr[i * 37 + j];
        }
    }

    vec4 temp_sharp_parameter[3] = currentTriangle.parameter_in_original;
    for (int i = 0; i < 3; ++i) {
        temp_sharp_parameter[i].w = 0;
    }

    if (adjust_control_point > 0) {
        //调整控制顶点
        uint move_control_point[6] =  {2,1,3,7,8,5};
        uint adjacency_normal_index_to_edge_index[6] = {0,1,1,2,2,0};
        vec3 E = vec3(0);
        for (int i = 0; i < 6; ++i) {
            vec3 currentNormal = currentTriangle.pn_normal[i / 2].xyz;
            vec3 currentPosition = currentTriangle.pn_position[i / 2].xyz;
            vec3 controlPoint = bezierPositionControlPoint[move_control_point[i]];
            vec3 result;
            if (currentTriangle.adjacency_triangle_index3_original_triangle_index1[adjacency_normal_index_to_edge_index[i]] > 0) {
                samplePointForNormal[i / 2].normal =
                    getNormalInOriginalPNTriangle(currentTriangle.adjacency_pn_normal_parameter[i].xyz,
                        currentTriangle.adjacency_triangle_index3_original_triangle_index1[adjacency_normal_index_to_edge_index[i]]);
                vec3 adj_normal = sampleFastNormal(samplePointForNormal[i / 2]);
                if (! all(lessThan(abs(adj_normal - currentNormal), ZERO3))) {
                    vec3 n_ave = cross(currentNormal, adj_normal);
                    result = currentPosition + dot(controlPoint - currentPosition, n_ave) * n_ave;
                    ++ temp_sharp_parameter[i / 2].w;
                } else {
                    currentTriangle.adjacency_triangle_index3_original_triangle_index1[adjacency_normal_index_to_edge_index[i]] = -1;
                    result = controlPoint - dot((controlPoint - currentPosition), currentNormal) * currentNormal;
                }
            } else {
                result = controlPoint - dot(controlPoint - currentPosition, currentNormal) * currentNormal;
            }
            bezierPositionControlPoint[move_control_point[i]] = result;
            E += result;
        }
        E /= 6;
        vec3 V = (bezierPositionControlPoint[0] + bezierPositionControlPoint[6] + bezierPositionControlPoint[9]) / 3;
        bezierPositionControlPoint[4] = E + (E - V) / 2;
    }

    for (int i = 0; i < 3; ++i) {
        if (temp_sharp_parameter[i].w <= 0) {
            temp_sharp_parameter[i] = vec4(0.333, 0.333, 0.333, 0);
        }
    }

    for (int i = 0; i < 3; ++i) {
        positionSplitedTriangle[triangleIndex * 3 + i] = currentTriangle.pn_position[i];
        normalSplitedTriangle[triangleIndex * 3 + i] =  currentTriangle.pn_normal[i];
    }

    // 细分
    // 生成顶点数据
    uint point_index[100];
    for (int i = 0; i < 10; ++i) {
        uint point_offset = triangleIndex * 10 + i;
        controlPoint3pointParameter1[point_offset].xyz = bezierPositionControlPoint[i];
        controlPoint3pointParameter1[point_offset].w = aux_control_parameter[i];
        point_index[i] = point_offset;
    }

    // 生成index数据
    for (int i = 0; i < 9; ++i) {
        uvec3 index = aux_control_index[i];
        uint index_offset = triangleIndex * 9 + i;
        for (int j = 0; j < 3; ++j) {
            controlPointIndex[index_offset * 3 + j] = point_index[index[j]];
        }
    }

    // 细分
    // 生成顶点数据
    for (int i = 0; i < tessellatedParameterLength; ++i) {
        vec3 pointParameter = tessellatedParameter[i].xyz;
        uint point_offset = triangleIndex * tessellatedParameterLength + i;
        parameterInSplit[point_offset] = tessellatedParameter[i];
        parameterInSplit[point_offset].zw =
            getTessellatedSplitParameter(temp_sharp_parameter, tessellatedParameter[i]).xy;
        parameterInOriginal3_triangle_quality1[point_offset] =
            getTessellatedSplitParameter(currentTriangle.parameter_in_original, tessellatedParameter[i]);
        parameterInOriginal3_triangle_quality1[point_offset][3] = currentTriangle.triangle_quality;
        tessellatedVertex[point_offset] = getPosition(pointParameter);
        tessellatedNormal[point_offset] = getNormal(pointParameter);
        tessellatedParameterInBSplineBody[point_offset] = getParameterInBSplineBody(pointParameter);
        // get background data
        vec3 temp = parameterInOriginal3_triangle_quality1[point_offset].xyz;
        SamplePoint sp;
        sp.position = getPositionInOriginalPNTriangle(temp, currentTriangle.adjacency_triangle_index3_original_triangle_index1[3]);
        sp.normal = getNormalInOriginalPNTriangle(temp, currentTriangle.adjacency_triangle_index3_original_triangle_index1[3]);
        getSamplePointHelper(sp);
        sampleFast(sp);
        realPosition[point_offset] = vec4(sp.position, 1);
        realNormal[point_offset] = vec4(sp.normal, 0);
        point_index[i] = point_offset;
    }
    // 生成index数据
    for (int i = 0; i < tessellateIndexLength; ++i) {
        uvec4 index = tessellateIndex[i];
        uint index_offset = triangleIndex * tessellateIndexLength + i;
        for (int j = 0; j < 3; ++j) {
            tessellatedIndex[index_offset * 3 + j] = point_index[index[j]];
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


vec4 getTessellatedSplitParameter(vec4[3] parameterInOriginal, vec4 tessellatedParameter){
    vec4 res = vec4(0);
    for (int i = 0; i < 3; ++i) {
        res += parameterInOriginal[i] * tessellatedParameter[i];
    }
    return res;
}

vec4 getNormal(vec3 parameter) {
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6f / factorial(i) / factorial(j) / factorial(k)
                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            result += bezierNormalControlPoint[ctrlPointIndex ++] * n;
        }
    }
    return vec4(normalize(result), 0);
}

vec4 getPosition(vec3 parameter) {
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += bezierPositionControlPoint[ctrlPointIndex ++] * n;
        }
    }
    return vec4(result, 1);
}

vec3 sample_helper(uvec3 knot_left_index, float[3] un, float[3] vn, float[3] wn){
    uint uli = knot_left_index.x;
    uint vli = knot_left_index.y;
    uint wli = knot_left_index.z;
    //todo
    uint controlPointOffset = ((uli - 2) * vw + (vli - 2) * w + (wli - 2)) * 27;

    vec3 tempcp2[4][4];
    for (int i = 0; i < 3; ++i){
        for (int j = 0; j < 3; ++j){
            tempcp2[i][j] = vec3(0.0f);
            for (int k = 0; k < 3; ++k) {
                vec4 cp = newControlPoints[controlPointOffset + i * 9 + j * 3 + k];
                tempcp2[i][j].x += cp.x * wn[k];
                tempcp2[i][j].y += cp.y * wn[k];
                tempcp2[i][j].z += cp.z * wn[k];
            }
        }
    }

    vec3 tempcp1[4];
    for (int i = 0; i < 3; ++i) {
        tempcp1[i] = vec3(0.0);
        for (int j = 0; j < 3; ++j) {
            tempcp1[i].x += tempcp2[i][j].x * vn[j];
            tempcp1[i].y += tempcp2[i][j].y * vn[j];
            tempcp1[i].z += tempcp2[i][j].z * vn[j];
        }
    }

    vec3 result = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result.x += tempcp1[i].x * un[i];
        result.y += tempcp1[i].y * un[i];
        result.z += tempcp1[i].z * un[i];
    }
    return result;
}

vec3 sampleFastNormal(in SamplePoint samplePoint) {
    float u = samplePoint.position.x;
    float v = samplePoint.position.y;
    float w = samplePoint.position.z;

    float un[3] = {1, u, u * u};
    float vn[3] = {1, v, v * v};
    float wn[3] = {1, w, w * w};

    float un_[3] = {0, 1, 2 * u};
    float vn_[3] = {0, 1, 2 * v};
    float wn_[3] = {0, 1, 2 * w};

    vec3 fu = sample_helper(samplePoint.knot_left_index, un_, vn, wn);
    vec3 fv = sample_helper(samplePoint.knot_left_index, un, vn_, wn);
    vec3 fw = sample_helper(samplePoint.knot_left_index, un, vn, wn_);

    vec3 n = samplePoint.normal;

    vec3 result = vec3(1);
    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第一行三个元素
    float J_bar_star_T_0 = fv.y * fw.z - fw.y * fv.z;
    float J_bar_star_T_1 = fw.y * fu.z - fu.y * fw.z;
    float J_bar_star_T_2 = fu.y * fv.z - fv.y * fu.z;
    result.x = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第二行三个元素
    J_bar_star_T_0 = fv.z * fw.x - fw.z * fv.x;
    J_bar_star_T_1 = fw.z * fu.x - fu.z * fw.x;
    J_bar_star_T_2 = fu.z * fv.x - fv.z * fu.x;
    result.y = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第三行三个元素
    J_bar_star_T_0 = fv.x * fw.y - fw.x * fv.y;
    J_bar_star_T_1 = fw.x * fu.y - fu.x * fw.y;
    J_bar_star_T_2 = fu.x * fv.y - fv.x * fu.y;
    result.z = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];
    return normalize(result);
}

void sampleFast(inout SamplePoint samplePoint) {
    float u = samplePoint.position.x;
    float v = samplePoint.position.y;
    float w = samplePoint.position.z;

    float un[3] = {1, u, u * u};
    float vn[3] = {1, v, v * v};
    float wn[3] = {1, w, w * w};

    //sample position
    samplePoint.position = sample_helper(samplePoint.knot_left_index, un, vn, wn);

    float un_[3] = {0, 1, 2 * u};
    float vn_[3] = {0, 1, 2 * v};
    float wn_[3] = {0, 1, 2 * w};

    vec3 fu = sample_helper(samplePoint.knot_left_index, un_, vn, wn);
    vec3 fv = sample_helper(samplePoint.knot_left_index, un, vn_, wn);
    vec3 fw = sample_helper(samplePoint.knot_left_index, un, vn, wn_);

    vec3 n = samplePoint.normal;

    vec3 result = vec3(1);
    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第一行三个元素
    float J_bar_star_T_0 = fv.y * fw.z - fw.y * fv.z;
    float J_bar_star_T_1 = fw.y * fu.z - fu.y * fw.z;
    float J_bar_star_T_2 = fu.y * fv.z - fv.y * fu.z;
    result.x = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第二行三个元素
    J_bar_star_T_0 = fv.z * fw.x - fw.z * fv.x;
    J_bar_star_T_1 = fw.z * fu.x - fu.z * fw.x;
    J_bar_star_T_2 = fu.z * fv.x - fv.z * fu.x;
    result.y = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第三行三个元素
    J_bar_star_T_0 = fv.x * fw.y - fw.x * fv.y;
    J_bar_star_T_1 = fw.x * fu.y - fu.x * fw.y;
    J_bar_star_T_2 = fu.x * fv.y - fv.x * fu.y;
    result.z = n.x * J_bar_star_T_0 * BSplineBodyStep[0] + n.y * J_bar_star_T_1 * BSplineBodyStep[1] + n.z * J_bar_star_T_2 * BSplineBodyStep[2];
    samplePoint.normal = normalize(result);
}

void getSamplePointHelper(inout SamplePoint samplePoint) {
    for (int i = 0; i < 3; ++i) {
        float temp = (samplePoint.position[i] - BSplineBodyMinParameter[i]) / BSplineBodyStep[i];

        samplePoint.knot_left_index[i] = uint(temp);
        if (samplePoint.knot_left_index[i] >= BSplineBodyIntervalNumber[i]) {
            samplePoint.knot_left_index[i] -= 1;
        }
        samplePoint.position[i] = temp - samplePoint.knot_left_index[i];
        samplePoint.knot_left_index[i] += uint(BSplineBodyOrder[i] - 1);
    }
}

SamplePoint getSamplePoint(vec3 position[3], vec3 normal[3], vec3 parameter) {
    SamplePoint result;
    result.position = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result.position += position[i] * parameter[i];
    }
    result.normal = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result.normal += normal[i] * parameter[i];
    }
    getSamplePointHelper(result);
    return result;
}

SamplePoint getSamplePointBeforeSample(vec3 parameter) {
    SamplePoint result;
    result.position = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result.position += (currentTriangle.pn_position[i] * parameter[i]).xyz;
    }

    result.normal = vec3(0);
    for (int i = 0; i < 3; ++i) {
        result.normal += (currentTriangle.original_normal[i] * parameter[i]).xyz;
    }
    getSamplePointHelper(result);

    return result;
}

// 根据 parameter 获得PNTriangle中的法向
vec3 getNormalInOriginalPNTriangle(vec3 parameter, uint triangle_index) {
    vec3 result = vec3(0);
    uint ctrlPointIndex = triangle_index * 6;
    for (int i = 2; i >=0; --i) {
        for (int j = 2 - i; j >= 0; --j) {
            int k = 2 - i - j;
            float n = 2.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += PNTriangleN_shared[ctrlPointIndex ++] * n;
        }
    }
    return normalize(result);
}

// 根据 parameter 获得PNTriangle中的位置
vec3 getPositionInOriginalPNTriangle(vec3 parameter, uint original_triangle_index) {
    vec3 result = vec3(0);
    int ctrlPointIndex = 0;
    int offset = int(original_triangle_index * 10);
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += PNTriangleP_shared[offset + ctrlPointIndex ++] * n;
        }
    }
    return result;
}

vec4 getParameterInBSplineBody(vec3 pointParameter) {
    vec4 result = vec4(0);
    for (int i = 0; i < 3; ++i) {
        result += currentTriangle.original_position[i] * pointParameter[i];
    }
    return result;
}
