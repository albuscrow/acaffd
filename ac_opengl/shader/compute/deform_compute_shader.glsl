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
    vec4 n;
    uvec4 knot_left_index;
    uvec4 aux_matrix_offset;
};

//layout(std430, binding=10) buffer SplitedBSplineInfoBuffer{
//    BSplineInfo[] bSplineInfo;
//};

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
layout(std140, binding=1) uniform ControlPointForSample{
    uniform vec4[729] newControlPoints;
};

vec4 sample_bspline_fast(BSplineInfo bsi);
vec4 sample_bspline_normal_fast(BSplineInfo bsi);

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

vec4 bezierPositionControlPoint[10];
vec4 bezierNormalControlPoint[10];
vec4 getPosition(vec3 parameter);
vec4 getNormal(vec3 parameter);

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= uint(triangleNumber)) {
        return;
    }

    // 计算采样点
    vec4 sample_points[37];
    vec4 sample_normals[37];
    for (int i = 0; i < 37; ++i) {
        sample_points[i] = sample_bspline_fast(samplePointBSplineInfo[triangleIndex * 37 + i]);
        sample_normals[i] = sample_bspline_normal_fast(samplePointBSplineInfo[triangleIndex * 37 + i]);
//        vec4 n = samplePointBSplineInfo[triangleIndex * 37 + i].n;
//        vec3 n3 = vec3(n.xyz);
//        normalize(n3);
//        sample_normals[i] = vec4(n3, 1);
//        sample_points[i] = sample_bspline(samplePointBSplineInfo[triangleIndex * 37 + i]);
    }
    // 计算Bezier曲面片控制顶点
    for (int i = 0; i < 10; ++i) {
        bezierPositionControlPoint[i] = vec4(0);
        bezierNormalControlPoint[i] = vec4(0);
        for (int j = 0; j < 37; ++j) {
            bezierPositionControlPoint[i] += sample_points[j] * Mr[i * 37 + j];
            bezierNormalControlPoint[i] += sample_normals[j] * Mr[i * 37 + j];
        }
    }
    //todo 调整控制顶点

    //计算法向控制顶点
//    vec4 sample_normals[37];
//    for (int i = 0; i < 37; ++i) {
////        sample_points[i] = sample_bspline(samplePointBSplineInfo[triangleIndex * 37 + i]);
//    }
//    // 计算Bezier曲面片法向场控制顶点
//    for (int i = 0; i < 10; ++i) {
//        bezierNormalControlPoint[i] = vec4(0);
//        for (int j = 0; j < 37; ++j) {
//        }
//    }

    // 细分
    // 生成顶点数据
    uint temp[10] = {28, 29, 30, 31, 12, 32, 33, 34, 35, 36};
    uint point_index[100];
    for (int i = 0; i < 10; ++i) {
        vec3 pointParameter = tessellatedParameter[i];
        uint point_offset = triangleIndex * 10 + i;
        tessellatedVertex[point_offset] = getPosition(pointParameter);
//        tessellatedVertex[point_offset] = bezierControlPoint[i];
        tessellatedNormal[point_offset] = getNormal(pointParameter);
//        tessellatedNormal[point_offset] = samplePointBSplineInfo[triangleIndex * 37 + temp[i]].n;
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
//    tessellatedVertex[splited_index_1] = splitedVertex[splited_index_1];
//    tessellatedVertex[splited_index_2] = splitedVertex[splited_index_2];
//    tessellatedVertex[splited_index_3] = splitedVertex[splited_index_3];
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
    vec4 result = vec4(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6f / factorial(i) / factorial(j) / factorial(k)
                * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k);
            result += bezierNormalControlPoint[ctrlPointIndex ++] * n;
        }
    }
    return vec4(result.xyz, 1);
//    return vec4(1.0);
}

vec4 getPosition(vec3 parameter) {
    vec4 result = vec4(0);
    int ctrlPointIndex = 0;
    for (int i = 3; i >=0; --i) {
        for (int j = 3 - i; j >= 0; --j) {
            int k = 3 - i - j;
            float n = 6.0f * power(parameter.x, i) * power(parameter.y, j) * power(parameter.z, k)
                    / factorial(i) / factorial(j) / factorial(k);
            result += bezierPositionControlPoint[ctrlPointIndex ++] * n;
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

vec4 sample_helper(BSplineInfo bsi, float[4] un, float[4] vn, float[4] wn){
    vec4 result;
    vec3 tempcp1[4];
    vec3 tempcp2[4][4];

    int uli = int(bsi.knot_left_index.x);
    int vli = int(bsi.knot_left_index.y);
    int wli = int(bsi.knot_left_index.z);
    int controlPointOffset = ((uli - 2) * 9 + (vli - 2) * 3 + (wli - 2)) * 27;

    for (int i = 0; i < 3; ++i){
        for (int j = 0; j < 3; ++j){
            tempcp2[i][j] = vec3(0.0f);
            for (int k = 0; k < 3; ++k) {
                vec4 cp = newControlPoints[int(controlPointOffset + i * 9 + j * 3 + k)];
                tempcp2[i][j].x += cp.x * wn[k];
                tempcp2[i][j].y += cp.y * wn[k];
                tempcp2[i][j].z += cp.z * wn[k];
            }
        }
    }

    for (int i = 0; i < 3; ++i) {
        tempcp1[i] = vec3(0.0);
        for (int j = 0; j < 3; ++j) {
            tempcp1[i].x += tempcp2[i][j].x * vn[j];
            tempcp1[i].y += tempcp2[i][j].y * vn[j];
            tempcp1[i].z += tempcp2[i][j].z * vn[j];
        }
    }

    result = vec4(0);
    for (int i = 0; i < 3; ++i) {
        result.x += tempcp1[i].x * un[i];
        result.y += tempcp1[i].y * un[i];
        result.z += tempcp1[i].z * un[i];
    }
    result.w = 1;
    return result;

}

vec4 sample_bspline_normal_fast(BSplineInfo bsi) {
    float u = bsi.t.x;
    float v = bsi.t.y;
    float w = bsi.t.z;

    float un[4];
    un[0] = 1;
    un[1] = u;
    un[2] = u * u;
    un[3] = u * un[2];

    float un_[4];
    un_[0] = 0;
    un_[1] = 1;
    un_[2] = 2 * u;
    un_[3] = 3 * u * u;

    float vn[4];
    vn[0]= 1;
    vn[1] = v;
    vn[2] = v * v;
    vn[3] = v * vn[2];

    float vn_[4];
    vn_[0] = 0;
    vn_[1] = 1;
    vn_[2] = 2 * v;
    vn_[3] = 3 * v * v;

    float wn[4];
    wn[0] = 1;
    wn[1] = w;
    wn[2] = w * w;
    wn[3] = w * wn[3];

    float wn_[4];
    wn_[0] = 0;
    wn_[1] = 1;
    wn_[2] = 2 * w;
    wn_[3] = 3 * w * w;

    vec4 fu = sample_helper(bsi, un_, vn, wn);
    vec4 fv = sample_helper(bsi, un, vn_, wn);
    vec4 fw = sample_helper(bsi, un, vn, wn_);


    vec4 n = bsi.n;
    float x_stride = 0.333333;
    float y_stride = 0.333333;
    float z_stride = 0.333333;

    vec3 result = vec3(1);
    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第一行三个元素
    float J_bar_star_T_0 = fv.y * fw.z - fw.y * fv.z;
    float J_bar_star_T_1 = fw.y * fu.z - fu.y * fw.z;
    float J_bar_star_T_2 = fu.y * fv.z - fv.y * fu.z;
    result.x = n.x * J_bar_star_T_0 * x_stride + n.y * J_bar_star_T_1 * y_stride + n.z * J_bar_star_T_2 * z_stride;

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第二行三个元素
    J_bar_star_T_0 = fv.z * fw.x - fw.z * fv.x;
    J_bar_star_T_1 = fw.z * fu.x - fu.z * fw.x;
    J_bar_star_T_2 = fu.z * fv.x - fv.z * fu.x;
    result.y = n.x * J_bar_star_T_0 * x_stride + n.y * J_bar_star_T_1 * y_stride + n.z * J_bar_star_T_2 * z_stride;

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第三行三个元素
    J_bar_star_T_0 = fv.x * fw.y - fw.x * fv.y;
    J_bar_star_T_1 = fw.x * fu.y - fu.x * fw.y;
    J_bar_star_T_2 = fu.x * fv.y - fv.x * fu.y;
    result.z = n.x * J_bar_star_T_0 * x_stride + n.y * J_bar_star_T_1 * y_stride + n.z * J_bar_star_T_2 * z_stride;

    result = normalize(result);


    return vec4(result, 1);
//    return n;

}
vec4 sample_bspline_fast(BSplineInfo bsi) {

    float u = bsi.t.x;
    float v = bsi.t.y;
    float w = bsi.t.z;

    float un[4];
    un[0] = 1;
    un[1] = u;
    un[2] = u * u;
    un[3] = u * un[2];

    float vn[4];
    vn[0]= 1;
    vn[1] = v;
    vn[2] = v * v;
    vn[3] = v * vn[2];

    float wn[4];
    wn[0] = 1;
    wn[1] = w;
    wn[2] = w * w;
    wn[3] = w * wn[3];

    return sample_helper(bsi, un, vn, wn);
}

