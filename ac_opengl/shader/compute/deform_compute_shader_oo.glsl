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

//input
layout(std430, binding=5) buffer TriangleBuffer{
    SplitedTriangle[] input_triangles;
};

//input
//用于加速计算的控制顶点
#ifdef TIME
layout(std430, binding=15) buffer ControlPointForSample{
    vec4[729] newControlPoints;
};
#else
layout(std140, binding=1) uniform ControlPointForSample{
    uniform vec4[729] newControlPoints;
};
#endif

//output
layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
};

//output
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

#ifndef TIME
//output
layout(std430, binding=23) buffer TesselatedTexCoordBuffer{
    vec2[] tessellatedTexCoord;
};
//output
layout(std430, binding=10) buffer ParameterInOriginalBuffer{
    vec4[] parameterInOriginal3_triangle_quality1;
};

//output
layout(std430, binding=11) buffer ParameterInSplitBuffer{
    vec4[] parameter_in_split2_is_sharp_info_2;
};
//output
layout(std430, binding=17) buffer PositionSplitedTriangle{
    vec4[] positionSplitedTriangle;
};

//output
layout(std430, binding=18) buffer NormalSplitedTriangle{
    vec4[] normalSplitedTriangle;
};

layout(std430, binding=12) buffer RealPosition{
    vec4[] realPosition;
};

//input
layout(std430, binding=19) buffer PNTrianglePShareBuffer{
    vec4[] PNTriangleP_shared;
};

//input
layout(std430, binding=25) buffer BezierControlPoints{
    vec4[] bezier_control_points;
};

//output
layout(std430, binding=13) buffer RealNormal{
    vec4[] realNormal;
};

//output
layout(std430, binding=15) buffer ControlPoint{
    vec4[] controlPoint3pointParameter1;
};

//output
layout(std430, binding=16) buffer ControlPointIndex{
    uint[] controlPointIndex;
};
#endif

//debug
//layout(std430, binding=14) buffer OutputDebugBuffer{
//    int myOutputBuffer[1000];
//};

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

float Mr[54] = {
      -0.8333333,        3.0000000,         0.0000000,        -1.5000000,         0.0000000,         0.3333333,        0.0000000,        0.0000000,        0.0000000,
      -0.8333333,        0.0000000,         3.0000000,         0.0000000,        -1.5000000,         0.0000000,        0.0000000,        0.0000000,        0.3333333,
       0.3333333,       -1.5000000,         0.0000000,         3.0000000,         0.0000000,        -0.8333333,        0.0000000,        0.0000000,        0.0000000,
       0.3333333,        0.0000000,        -1.5000000,         0.0000000,         3.0000000,         0.0000000,        0.0000000,        0.0000000,       -0.8333333,
       0.0000000,        0.0000000,         0.0000000,         0.0000000,         0.0000000,        -0.8333333,        3.0000000,       -1.5000000,        0.3333333,
       0.0000000,        0.0000000,         0.0000000,         0.0000000,         0.0000000,         0.3333333,       -1.5000000,        3.0000000,       -0.8333333,
};

float Mr_4[19] = {
0.2784553,
-0.9969512,
-0.9969512,
-0.9969512,
-0.9969512,
0.2784553,
-0.9969512,
-0.9969512,
0.2784553,

0.4390244,
0.6585366,
0.6585366,
0.6585366,
0.8780488,
0.6585366,
0.4390244,
0.6585366,
0.6585366,
0.4390244,
};

vec3 sampleParameter[19] = {
    { 1.0 , 0.0 , 0.0 },
    { 0.6666666666666666 , 0.3333333333333333 , 0.0 },
    { 0.6666666666666666 , 0.0 , 0.3333333333333333 },
    { 0.3333333333333333 , 0.6666666666666666 , 0.0 },
    { 0.3333333333333333 , 0.0 , 0.6666666666666666 },
    { 0.0 , 1.0 , 0.0 },
    { 0.0 , 0.6666666666666666 , 0.3333333333333333 },
    { 0.0 , 0.3333333333333333 , 0.6666666666666666 },
    { 0.0 , 0.0 , 1.0 },

    { 0.6666666666666666 , 0.16666666666666666 , 0.16666666666666666 },
    { 0.5 , 0.3333333333333333 , 0.16666666666666666 },
    { 0.5 , 0.16666666666666666 , 0.3333333333333333 },
    { 0.3333333333333333 , 0.5 , 0.16666666666666666 },
    { 0.3333333333333333 , 0.3333333333333333 , 0.3333333333333333 },
    { 0.3333333333333333 , 0.16666666666666666 , 0.5 },
    { 0.16666666666666666 , 0.6666666666666666 , 0.16666666666666666 },
    { 0.16666666666666666 , 0.5 , 0.3333333333333333 },
    { 0.16666666666666666 , 0.3333333333333333 , 0.5 },
    { 0.16666666666666666 , 0.16666666666666666 , 0.6666666666666666 },
};

layout(location=0) uniform uint triangleNumber;

#ifdef TIME
layout(std430, binding=16) buffer TessellatedParameter{
    vec4[66] tessellatedParameter;
};
layout(std430, binding=13) buffer TessellateIndex{
    uvec4[100] tessellateIndex;
};
layout(std140, binding=4) uniform TessellateAux{
    uniform vec4[30] tessellateAux;
};
#else
layout(std140, binding=2) uniform TessellatedParameter{
    uniform vec4[66] tessellatedParameter;
};
layout(std140, binding=3) uniform TessellateIndex{
    uniform uvec4[100] tessellateIndex;
};
#endif

layout(location=4) uniform uint tessellatedParameterLength;
layout(location=5) uniform uint tessellateIndexLength;


#ifndef TIME
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

layout(location=6) uniform int adjust_control_point;
layout(location=1) uniform int use_pn_normal;
#endif

layout(location=7) uniform int modifyRange[84];


vec3 bezierPositionControlPoint[12];
vec3 bezierNormalControlPoint[12];
#ifdef TIME
void getPoint(int offset, out vec4 position, out vec4 normal);
#else
void getPoint(vec3 parameter, out vec4 position, out vec4 normal);
vec3 getPositionInOriginalPNTriangle(vec3 parameter, uint original_triangle_index);
void sampleInBezier(uint id, float u, float v, out vec3 position, out vec3 normal);
vec3 getPositionInOriginal(vec3 parameter);
vec3 getNormalInOriginal(vec3 parameter);
vec2 getUV(vec3 parameter);
vec2 getTexCoord(vec3 parameter);
#endif
vec3 getNormalInOriginalPNTriangle(vec3 parameter, uint original_triangle_index);
vec4 getTessellatedSplitParameter(vec4[3] split_parameter, vec4 tessellatedParameter);
vec2 getTessellatedSplitParameter(vec2[3] split_parameter, vec4 tessellatedParameter);

void getSamplePointHelper(inout SamplePoint samplePoint);
SamplePoint getSamplePointBeforeSample(vec3 parameter);

void sampleFast(inout SamplePoint spi);
vec3 sampleFastNormal(in SamplePoint spi);
vec4 getParameterInBSplineBody(vec3 pointParameter);

// 代表三个方向B spline body的区间数
vec4 BSplineBodyMinParameter;
vec4 BSplineBodyStep;
uvec4 BSplineBodyIntervalNumber;
uint OrderProduct;

SplitedTriangle currentTriangle;
#ifndef TIME
vec3 normalizedOriginalNormal[3];
const int isBezier = -1;
#endif
void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
//    uint triangleIndex = gl_GlobalInvocationID.x * 16 + gl_GlobalInvocationID.y * 4 + gl_GlobalInvocationID.z;
    if (triangleIndex >= triangleNumber) {
        return;
    }

    //判断三角形是否在变形范围
    currentTriangle = input_triangles[triangleIndex];
    int total =  modifyRange[currentTriangle.range[0]] + modifyRange[currentTriangle.range[1]] + modifyRange[currentTriangle.range[2]];
    if (total == -3) {
        return;
    }

//    for (int j = 0; j < 100000; ++j) { 27
    OrderProduct = 1;
    for (int i = 0; i < 3; ++i) {
        OrderProduct *= uint(BSplineBodyOrder[i]);
        BSplineBodyIntervalNumber[i] = uint(BSplineBodyControlPointNum[i] - BSplineBodyOrder[i] + 1);
        BSplineBodyMinParameter[i] = -BSplineBodyLength[i] / 2;
        BSplineBodyStep[i] = BSplineBodyLength[i] / BSplineBodyIntervalNumber[i];
    }
//    }


#ifndef TIME
    for (int i = 0; i < 3; ++i) {
        normalizedOriginalNormal[i] = normalize(currentTriangle.original_normal[i].xyz);
    }
#endif
    // 计算采样点
    SamplePoint samplePoint[19];
//    for (int j = 0; j < 10000; ++j ) { 疑似第一次较慢
    for (int i = 0; i < 19; ++i) {
        samplePoint[i] = getSamplePointBeforeSample(sampleParameter[i]);
    }
//    }

    uint vertexIndexInSamplePoint[3] = {0,5,8};
    SamplePoint samplePointForNormal[3];
    for (int i = 0; i < 3; ++i) {
        samplePointForNormal[i] = samplePoint[vertexIndexInSamplePoint[i]];
        samplePointForNormal[i].normal = currentTriangle.pn_normal[i].xyz;
        currentTriangle.pn_normal[i].xyz = sampleFastNormal(samplePointForNormal[i]);
    }

    for (int i = 0; i < 19; ++i) {
        sampleFast(samplePoint[i]);
    }

    for (int i = 0; i < 3; ++i) {
        currentTriangle.pn_position[i].xyz = samplePoint[vertexIndexInSamplePoint[i]].position;
    }

    // 计算Bezier曲面片控制顶点
    for (int i = 0; i < 12; ++i) {
        bezierPositionControlPoint[i] = vec3(0);
        bezierNormalControlPoint[i] = vec3(0);
    }

    bezierPositionControlPoint[0] = samplePoint[0].position;
    bezierNormalControlPoint[0] = samplePoint[0].normal;
    bezierPositionControlPoint[6] = samplePoint[5].position;
    bezierNormalControlPoint[6] = samplePoint[5].normal;
    bezierPositionControlPoint[9] = samplePoint[8].position;
    bezierNormalControlPoint[9] = samplePoint[8].normal;

    int tempindex = -1;
    int aux1[6] = {1,2,3,5,7,8};
    for (int i = 0; i < 6; ++i) {
        for (int j = 0; j < 9; ++j) {
            bezierPositionControlPoint[aux1[i]] += samplePoint[j].position * Mr[++tempindex];
            bezierNormalControlPoint[aux1[i]] += samplePoint[j].normal * Mr[tempindex];
        }
    }
    for (int j = 0; j < 19; ++j) {
        bezierPositionControlPoint[4] += samplePoint[j].position * Mr_4[j];
        bezierNormalControlPoint[4] += samplePoint[j].normal * Mr_4[j];
    }

#ifndef TIME
    vec2 temp_sharp_parameter[3];
    for (int i = 0; i < 3; ++i) {
        temp_sharp_parameter[i] = vec2(0.333, 0.333);
    }
    if (adjust_control_point > 0) {
#endif
        //调整控制顶点
        uint move_control_point[6] =  {2,1,3,7,8,5};
        vec3 E = vec3(0);
        for (int i = 0; i < 6; ++i) {
            vec3 currentNormal = currentTriangle.pn_normal[i >> 1].xyz;
            vec3 currentPosition = currentTriangle.pn_position[i >> 1].xyz;
            vec3 controlPoint = bezierPositionControlPoint[move_control_point[i]];
            vec4 adj_normal = currentTriangle.adjacency_pn_normal[i];
            if (adj_normal[3] != -1) {
#ifndef TIME
                temp_sharp_parameter[i / 2] = currentTriangle.parameter_in_original2_texcoord2[i / 2].xy;
#endif

                samplePointForNormal[i / 2].normal = adj_normal.xyz;
                adj_normal.xyz = sampleFastNormal(samplePointForNormal[i / 2]);
                vec3 n_ave = normalize(cross(currentNormal, adj_normal.xyz));
                bezierPositionControlPoint[move_control_point[i]] = currentPosition + dot(controlPoint - currentPosition, n_ave) * n_ave;
            } else {
                bezierPositionControlPoint[move_control_point[i]] = controlPoint - dot(controlPoint - currentPosition, currentNormal) * currentNormal;
            }
            E += bezierPositionControlPoint[move_control_point[i]];
        }

        E *= 0.25;
        bezierPositionControlPoint[4] = (bezierPositionControlPoint[0] + bezierPositionControlPoint[6] + bezierPositionControlPoint[9]) * -0.166666666 + E;
#ifndef TIME
    }
#endif

#ifdef TIME
    uint point_index[496];
#else
    uint point_index[210];
    for (int i = 0; i < 3; ++i) {
        positionSplitedTriangle[triangleIndex * 3 + i] = currentTriangle.pn_position[i];
        normalSplitedTriangle[triangleIndex * 3 + i].xyz = normalizedOriginalNormal[i];
        normalSplitedTriangle[triangleIndex * 3 + i].w = 0;
//        currentTriangle.original_normal[i].xyz
//        normalSplitedTriangle[triangleIndex * 3 + i] =  currentTriangle.pn_normal[i];

    }
    // 细分显示控制顶点
    // 生成顶点数据
    for (int i = 0; i < 10; ++i) {
        point_index[i] = triangleIndex * 10 + i;
        controlPoint3pointParameter1[point_index[i]] = vec4(bezierPositionControlPoint[i], aux_control_parameter[i]);
    }

    // 生成index数据
    for (int i = 0; i < 9; ++i) {
        uvec3 index = aux_control_index[i];
        uint index_offset = triangleIndex * 9 + i;
        for (int j = 0; j < 3; ++j) {
            controlPointIndex[index_offset * 3 + j] = point_index[index[j]];
        }
    }
#endif

    // 细分
    // 生成顶点数据

    uint point_offset = triangleIndex * tessellatedParameterLength;
    for (int i = 0; i < tessellatedParameterLength; ++i) {

#ifdef TIME
        getPoint(i * 3, tessellatedVertex[point_offset], tessellatedNormal[point_offset]);
#else
        getPoint(tessellatedParameter[i].xyz, tessellatedVertex[point_offset], tessellatedNormal[point_offset]);
#endif

        mat3 tm = mat3(currentTriangle.original_position[0].xyz, currentTriangle.original_position[1].xyz, currentTriangle.original_position[2].xyz);
//        tessellatedParameterInBSplineBody[point_offset] = getParameterInBSplineBody(tessellatedParameter[i].xyz);
        tessellatedParameterInBSplineBody[point_offset].xyz = tm * tessellatedParameter[i].xyz;

#ifndef TIME
        tessellatedTexCoord[point_offset] = getTexCoord(tessellatedParameter[i].xyz);
        parameter_in_split2_is_sharp_info_2[point_offset] = tessellatedParameter[i];
        parameter_in_split2_is_sharp_info_2[point_offset].zw =
            getTessellatedSplitParameter(temp_sharp_parameter, tessellatedParameter[i]);
        parameterInOriginal3_triangle_quality1[point_offset] =
            getTessellatedSplitParameter(currentTriangle.parameter_in_original2_texcoord2, tessellatedParameter[i]);
        parameterInOriginal3_triangle_quality1[point_offset].z =
            1 - parameterInOriginal3_triangle_quality1[point_offset].x - parameterInOriginal3_triangle_quality1[point_offset].y;
        if (parameterInOriginal3_triangle_quality1[point_offset].z < 0) {
            parameterInOriginal3_triangle_quality1[point_offset].z = 0;
        }
        parameterInOriginal3_triangle_quality1[point_offset].w = currentTriangle.triangle_quality;
        // get background data
        vec3 temp = parameterInOriginal3_triangle_quality1[point_offset].xyz;
        SamplePoint sp;
        if (isBezier > 0) {
            vec3 p, n;
            vec2 uv = getUV(tessellatedParameter[i].xyz);
            sampleInBezier(currentTriangle.bezier_patch_id, uv[0], uv[1], p, n);
            sp.position = p;
            sp.normal = n;
        } else {
            if (adjust_control_point > 0) {
//                sp.position = getPositionInOriginalPNTriangle(temp, currentTriangle.adjacency_triangle_index3_original_triangle_index1[3]);
                sp.position = getPositionInOriginal(tessellatedParameter[i].xyz);
            } else {
                sp.position = getPositionInOriginal(tessellatedParameter[i].xyz);
            }
            sp.normal = getNormalInOriginal(tessellatedParameter[i].xyz);
        }
        getSamplePointHelper(sp);
        sampleFast(sp);
        realPosition[point_offset] = vec4(sp.position, 1);
        realNormal[point_offset] = vec4(sp.normal, 0);
#endif
        point_index[i] = point_offset;
        ++point_offset;
    }
    // 生成index数据


    uint index_offset = triangleIndex * tessellateIndexLength * 3 - 1;
    for (int i = 0; i < tessellateIndexLength; ++i) {
        for (int j = 0; j < 3; ++j) {
            tessellatedIndex[++index_offset] = point_index[tessellateIndex[i][j]];
        }
    }
}

//const float factorial_temp[4] = {1,1,2,6};
//float factorial(int n) {
//    return factorial_temp[n];
//}

//const float rfactorial_temp[4] = {1,1,0.5,0.166666666};
//float rfactorial(int n) {
//    return rfactorial_temp[n];
//}

float factorial[4] = {1,1,2,6};

float rfactorial[4] = {1,1,0.5,0.166666666};

float power(float b, int n) {
    if (n == 0) {
        return 1;
    }

    if (b < 0.00001) {
        return 0;
    }

    return pow(b, n);
}

vec2 getTessellatedSplitParameter(vec2[3] parameterInOriginal, vec4 tessellatedParameter){
    vec2 res = vec2(0);
    for (int i = 0; i < 3; ++i) {
        res += parameterInOriginal[i] * tessellatedParameter[i];
    }
    return res;
}


vec4 getTessellatedSplitParameter(vec4[3] parameterInOriginal, vec4 tessellatedParameter){
    vec4 res = vec4(0);
    for (int i = 0; i < 3; ++i) {
        res += parameterInOriginal[i] * tessellatedParameter[i];
    }
    return res;
}

float rfactorialt[10] = {0.166666666f,
    0.5f, 0.5f,
    0.5f, 1f, 0.5f,
    0.166666666f, 0.5f, 0.5f, 0.166666666f};

#ifdef TIME
void getPoint(int offset, out vec4 position, out vec4 normal) {
    position = vec4(0);
    normal = vec4(0);
    float temp;
    for (int i = 0; i < 10; ++i) {
        temp = tessellateAux[offset + (i >> 2)][i & 3];
        normal.xyz += bezierNormalControlPoint[i] * temp;
        position.xyz += bezierPositionControlPoint[i] * temp;
    }
    normal.xyz = normalize(normal.xyz);
    normal.w = 0;
    position.w = 1;
}
#else
void getPoint(vec3 parameter, out vec4 position, out vec4 normal) {
    int ctrlPointIndex = 0;
    position = vec4(0);
    normal = vec4(0);
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float t = 6 * rfactorialt[ctrlPointIndex] * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            normal.xyz += bezierNormalControlPoint[ctrlPointIndex] * t;
            position.xyz += bezierPositionControlPoint[ctrlPointIndex] * t;
            ++ctrlPointIndex;
        }
    }
    normal.xyz = normalize(normal.xyz);
    normal.w = 0;
    position.w = 1;
}
#endif

#ifdef TIME
vec3 sample_helper(const uvec3 knot_left_index, const float[3] un, const float[3] vn, const float[3] wn){
//    uint controlPointOffset = (((knot_left_index.x * BSplineBodyIntervalNumber[1]) +
//                             + knot_left_index.y) * BSplineBodyIntervalNumber[2]
//                             + knot_left_index.z) * OrderProduct - 1;

    uint controlPointOffset = knot_left_index.x * BSplineBodyIntervalNumber[1] + knot_left_index.y;
    controlPointOffset = controlPointOffset * BSplineBodyIntervalNumber[2] + knot_left_index.z;
    controlPointOffset = controlPointOffset * OrderProduct - 1;
    vec3 tempcp2[3][3];
    for (int i = 0; i < 3; ++i){
        for (int j = 0; j < 3; ++j){
            tempcp2[i][j] = newControlPoints[++controlPointOffset].xyz * wn[0];
            for (int k = 1; k < 3; ++k) {
                tempcp2[i][j] += newControlPoints[++controlPointOffset].xyz * wn[k];
            }
        }
    }
    vec3 tempcp1[3];
    for (int i = 0; i < 3; ++i) {
        tempcp1[i] = tempcp2[i][0] * vn[0];
        for (int j = 1; j < 3; ++j) {
            tempcp1[i] += tempcp2[i][j] * vn[j];
        }
    }
    return tempcp1[0] * un[0] + tempcp1[1] * un[1] + tempcp1[2] * un[2];
}
#else
vec3 sample_helper(const uvec3 knot_left_index, const float[4] un, const float[4] vn, const float[4] wn){
    uint controlPointOffset = knot_left_index.x * BSplineBodyIntervalNumber[1] + knot_left_index.y;
    controlPointOffset = controlPointOffset * BSplineBodyIntervalNumber[2] + knot_left_index.z;
    controlPointOffset = controlPointOffset * OrderProduct - 1;
    vec3 tempcp2[4][4];
    for (int i = 0; i < BSplineBodyOrder[0]; ++i){
        for (int j = 0; j < BSplineBodyOrder[1]; ++j){
            tempcp2[i][j] = vec3(0.0f);
            for (int k = 0; k < BSplineBodyOrder[2]; ++k) {
                vec4 cp = newControlPoints[++controlPointOffset];
                tempcp2[i][j] += cp.xyz * wn[k];
            }
        }
    }
    vec3 tempcp1[4];
    for (int i = 0; i < BSplineBodyOrder[0]; ++i){
        tempcp1[i] = vec3(0);
        for (int j = 0; j < BSplineBodyOrder[1]; ++j){
            tempcp1[i] += tempcp2[i][j] * vn[j];
        }
    }
    vec3 result = vec3(0);
    for (int i = 0; i < BSplineBodyOrder[0]; ++i){
        result += tempcp1[i] * un[i];
    }
    return result;
}
#endif

vec3 sampleFastNormal(in SamplePoint samplePoint) {
    const float u = samplePoint.position.x;
    const float v = samplePoint.position.y;
    const float w = samplePoint.position.z;

#ifdef TIME
    const float un[3] = {1, u, u * u};
    const float vn[3] = {1, v, v * v};
    const float wn[3] = {1, w, w * w};

    const float un_[3] = {0, 1, 2 * u};
    const float vn_[3] = {0, 1, 2 * v};
    const float wn_[3] = {0, 1, 2 * w};
#else
    const float un[4] = {1, u, u * u, u * u * u};
    const float vn[4] = {1, v, v * v, v * v * v};
    const float wn[4] = {1, w, w * w, w * w * w};

    const float un_[4] = {0, 1, 2 * u, 3 * u * u};
    const float vn_[4] = {0, 1, 2 * v, 3 * v * v};
    const float wn_[4] = {0, 1, 2 * w, 3 * w * w};
#endif

    const vec3 fu = sample_helper(samplePoint.knot_left_index, un_, vn, wn);
    const vec3 fv = sample_helper(samplePoint.knot_left_index, un, vn_, wn);
    const vec3 fw = sample_helper(samplePoint.knot_left_index, un, vn, wn_);

    const vec3 n = samplePoint.normal;

    vec3 result = vec3(0);
    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第一行三个元素
    vec3 J_bar_star_T;
    J_bar_star_T[0] = fv.y * fw.z - fw.y * fv.z;
    J_bar_star_T[1] = fw.y * fu.z - fu.y * fw.z;
    J_bar_star_T[2] = fu.y * fv.z - fv.y * fu.z;
    result.x = n.x * J_bar_star_T[0] * BSplineBodyStep[0] + n.y * J_bar_star_T[1] * BSplineBodyStep[1] + n.z * J_bar_star_T[2] * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第二行三个元素
    J_bar_star_T[0] = fv.z * fw.x - fw.z * fv.x;
    J_bar_star_T[1] = fw.z * fu.x - fu.z * fw.x;
    J_bar_star_T[2] = fu.z * fv.x - fv.z * fu.x;
    result.y = n.x * J_bar_star_T[0] * BSplineBodyStep[0] + n.y * J_bar_star_T[1] * BSplineBodyStep[1] + n.z * J_bar_star_T[2] * BSplineBodyStep[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第三行三个元素
    J_bar_star_T[0] = fv.x * fw.y - fw.x * fv.y;
    J_bar_star_T[1] = fw.x * fu.y - fu.x * fw.y;
    J_bar_star_T[2] = fu.x * fv.y - fv.x * fu.y;
    result.z = n.x * J_bar_star_T[0] * BSplineBodyStep[0] + n.y * J_bar_star_T[1] * BSplineBodyStep[1] + n.z * J_bar_star_T[2] * BSplineBodyStep[2];
    return normalize(result);
}

void sampleFast(inout SamplePoint samplePoint) {
    float u = samplePoint.position.x;
    float v = samplePoint.position.y;
    float w = samplePoint.position.z;

#ifdef TIME
    const float un[3] = {1, u, u * u};
    const float vn[3] = {1, v, v * v};
    const float wn[3] = {1, w, w * w};

    const float un_[3] = {0, 1, 2 * u};
    const float vn_[3] = {0, 1, 2 * v};
    const float wn_[3] = {0, 1, 2 * w};
#else
    const float un[4] = {1, u, u * u, u * u * u};
    const float vn[4] = {1, v, v * v, v * v * v};
    const float wn[4] = {1, w, w * w, w * w * w};

    const float un_[4] = {0, 1, 2 * u, 3 * u * u};
    const float vn_[4] = {0, 1, 2 * v, 3 * v * v};
    const float wn_[4] = {0, 1, 2 * w, 3 * w * w};
#endif


    samplePoint.position = sample_helper(samplePoint.knot_left_index, un, vn, wn);
    const vec3 fu = sample_helper(samplePoint.knot_left_index, un_, vn, wn);
    const vec3 fv = sample_helper(samplePoint.knot_left_index, un, vn_, wn);
    const vec3 fw = sample_helper(samplePoint.knot_left_index, un, vn, wn_);
//    for (int i = 0; i < 100; ++i) { 8
//    samplePoint.position = sample_helper(samplePoint.knot_left_index, un, vn, wn);
//    const vec3 fu = sample_helper(samplePoint.knot_left_index, un_, vn, wn);
//    const vec3 fv = sample_helper(samplePoint.knot_left_index, un, vn_, wn);
//    const vec3 fw = sample_helper(samplePoint.knot_left_index, un, vn, wn_);
//    }


    const vec3 n = samplePoint.normal;

    vec3 result;
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
//    vec3 temp = (samplePoint.position - BSplineBodyMinParameter.xyz) / BSplineBodyStep.xyz;
//    samplePoint.knot_left_index = uvec3(temp);
//    samplePoint.position = temp - samplePoint.knot_left_index;
    for (int i = 0; i < 3; ++i) {
        float temp = (samplePoint.position[i] - BSplineBodyMinParameter[i]) / BSplineBodyStep[i];
        samplePoint.knot_left_index[i] = uint(temp);
        samplePoint.position[i] = temp - samplePoint.knot_left_index[i];
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
#ifdef TIME
//    for (int i = 0; i < 100; ++i) {
//        mat3 temp = mat3(currentTriangle.pn_position[0].xyz, currentTriangle.pn_position[1].xyz, currentTriangle.pn_position[2].xyz);
//        result.position = temp * parameter;
//    }
        for (int i = 0; i < 3; ++i) {
            result.position += (currentTriangle.pn_position[i] * parameter[i]).xyz;
        }
#else
    if (adjust_control_point > 0) {
        for (int i = 0; i < 3; ++i) {
            result.position += (currentTriangle.pn_position[i] * parameter[i]).xyz;
        }

//        for (int i = 0; i < 3; ++i) {
//            result.position += (currentTriangle.original_position[i] * parameter[i]).xyz;
//        }
    } else {
//        for (int i = 0; i < 3; ++i) {
//            result.position += (currentTriangle.pn_position[i] * parameter[i]).xyz;
//        }

        for (int i = 0; i < 3; ++i) {
            result.position += (currentTriangle.original_position[i] * parameter[i]).xyz;
        }

    }
#endif

    result.normal = vec3(0);
#ifdef TIME

//        temp = mat3(currentTriangle.pn_normal[0].xyz, currentTriangle.pn_normal[1].xyz, currentTriangle.pn_normal[2].xyz);
//        result.normal = temp * parameter;
        for (int i = 0; i < 3; ++i) {
            result.normal += (currentTriangle.pn_normal[i] * parameter[i]).xyz;
        }
#else
    if (use_pn_normal > 0) {
        for (int i = 0; i < 3; ++i) {
            result.normal += (currentTriangle.pn_normal[i] * parameter[i]).xyz;
        }
    } else {
        for (int i = 0; i < 3; ++i) {
            result.normal += normalizedOriginalNormal[i] * parameter[i];
        }
    }
#endif
    result.normal = normalize(result.normal);

    for (int i = 0; i < 3; ++i) {
        float temp = (result.position[i] - BSplineBodyMinParameter[i]) / BSplineBodyStep[i];
        result.knot_left_index[i] = uint(temp);
        result.position[i] = temp - result.knot_left_index[i];
    }

    return result;
}


#ifndef TIME
vec2 getTexCoord(vec3 parameter) {
    vec2 res = vec2(0);
    for (uint i = 0; i < 3; ++i) {
        res += (currentTriangle.parameter_in_original2_texcoord2[i].zw * parameter[i]);
    }
    return res;
}

float c(int n, int r){
    return factorial[n] * rfactorial[r] * rfactorial[n - r];
}

float b(float t, int n, int i){
    return c(n, i) * power(t, i) * power(1 - t, n - i);
}

vec3 getNormalInOriginal(vec3 parameter) {
    vec3 normal = vec3(0);
    for (uint i = 0; i < 3; ++i) {
        normal += (currentTriangle.original_normal[i] * parameter[i]).xyz;
    }
    return normalize(normal);
}
vec3 getPositionInOriginal(vec3 parameter) {
    vec3 position = vec3(0);
    for (uint i = 0; i < 3; ++i) {
        position += (currentTriangle.original_position[i] * parameter[i]).xyz;
    }
    return position;
}

// 根据 parameter 获得PNTriangle中的位置
vec3 getPositionInOriginalPNTriangle(vec3 parameter, uint original_triangle_index) {
    vec3 result = vec3(0);
    int offset = int(original_triangle_index * 10);
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    * rfactorial[i] * rfactorial[j] * rfactorial[k];
            result += PNTriangleP_shared[offset ++].xyz * n;
        }
    }
    return result;
}

void sampleInBezier(uint id, float u, float v, out vec3 position, out vec3 normal) {
    position = vec3(0);
    //todo 不通用
    uint offsetId = id * 16;
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            position += b(u, 3, i) * b(v, 3, j) * bezier_control_points[offsetId ++].xyz;
        }
    }

    offsetId = id * 16;
    //以下代码是特地给犹它茶壶用的
    if (id < 4 && u < 0.000001){
        normal = vec3(0, 0, 1);
    } else if (id < 8 && u < 0.000001) {
        normal = vec3(0, 0, -1);
    } else {
        vec3 n_u = vec3(0);
        for (int j = 0; j < 4; ++j) {
            vec3 temp = vec3(0);
            for (int i = 0; i < 3; ++i) {
                temp += b(u, 2, i) * (bezier_control_points[offsetId + i * 4 + j].xyz - bezier_control_points[offsetId + (i + 1) * 4 + j].xyz);
            }
            n_u += b(v, 3, j) * temp;
        }

        vec3 n_v = vec3(0);
        for (int i = 0; i < 4; ++i) {
            vec3 temp = vec3(0);
            for (int j = 0; j < 3; ++j) {
                temp += b(v, 2, j) * (bezier_control_points[offsetId + i * 4 + j].xyz - bezier_control_points[offsetId + i * 4 + j + 1].xyz);
            }
            n_v += b(u, 3, i) * temp;
        }
        normal = normalize(cross(n_v, n_u));
    }
    return;
}
vec2 getUV(vec3 parameter) {
    vec2 res = vec2(0);
    for (uint i = 0; i < 3; ++i) {
        res += (currentTriangle.bezier_uv[i] * parameter[i]);
    }
    return res;
}

#endif

vec4 getParameterInBSplineBody(vec3 pointParameter) {
    vec4 result = vec4(0);
    for (int i = 0; i < 3; ++i) {
        result += currentTriangle.original_position[i] * pointParameter[i];
    }
    return result;
}
