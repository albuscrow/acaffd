#version 450

struct SamplePointInfo {
    vec4 parameter;
    vec4 sample_point_original_normal;
    uvec4 knot_left_index;
};
struct SplitedTriangle {
    SamplePointInfo samplePoint[37];
    vec4 normal_adj[3];
    vec4 adjacency_normal[6];
    vec4 original_normal[3];
    vec4 original_position[3];
    int is_sharp[4];
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

////input
//layout(location=0) uniform float triangleNumber;

//output
layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
};

//output
layout(std430, binding=7) buffer TesselatedNormalBuffer{
    vec4[] tessellatedNormal;
};

//output
layout(std430, binding=8) buffer TesselatedIndexBuffer{
    uint[] tessellatedIndex;
};

//debug
layout(std430, binding=14) buffer OutputDebugBuffer{
    vec4[] myOutputBuffer;
};

layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

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

layout(location=0) uniform uint triangleNumber;
layout(location=1) uniform uint vw;
layout(location=2) uniform uint w;
layout(location=3) uniform vec3 stride;
layout(location=4) uniform uint tessellatedParameterLength;
layout(location=5) uniform uint tessellateIndexLength;

layout(std140, binding=2) uniform TessellatedParameter{
    uniform vec4[66] tessellatedParameter;
};

layout(std140, binding=3) uniform TessellateIndex{
    uniform uvec4[100] tessellateIndex;
};

const vec3 ZERO3 = vec3(0.0001, 0.0001, 0.0001);

vec3 sample_bspline_position_fast(SamplePointInfo bsi);
vec3 sample_bspline_normal_fast(SamplePointInfo bsi);

vec3 bezierPositionControlPoint[10];
vec3 bezierNormalControlPoint[10];
vec4 getPosition(vec3 parameter);
vec4 getNormal(vec3 parameter);

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= triangleNumber) {
        return;
    }
    SplitedTriangle currentTriangle = input_triangles[triangleIndex];

    // 计算采样点
    vec3 sample_points[37];
    vec3 sample_normals[37];
    for (int i = 0; i < 37; ++i) {
        sample_points[i] = sample_bspline_position_fast(currentTriangle.samplePoint[i]);
        sample_normals[i] = sample_bspline_normal_fast(currentTriangle.samplePoint[i]);
    }

    // 计算Bezier曲面片控制顶点
    for (int i = 0; i < 10; ++i) {
        bezierPositionControlPoint[i] = vec3(0);
        bezierNormalControlPoint[i] = vec3(0);
        for (int j = 0; j < 37; ++j) {
            bezierPositionControlPoint[i] += sample_points[j] * Mr[i * 37 + j];
            bezierNormalControlPoint[i] += sample_normals[j] * Mr[i * 37 + j];
        }
    }

    vec3 position[3];
    position[0] = sample_points[0];
    position[1] = sample_points[21];
    position[2] = sample_points[27];

    uint normal_aux[3] = {0,21,27};
    for (int i = 0; i < 3; ++i) {
        SamplePointInfo current_normal_spi = currentTriangle.samplePoint[normal_aux[i]];
        current_normal_spi.sample_point_original_normal = currentTriangle.normal_adj[i];
        currentTriangle.normal_adj[i].xyz = sample_bspline_normal_fast(current_normal_spi);
    }

    uint oppo_point_index[6] =    {2,1,0,2,1,0};
    uint move_control_point[6] =  {2,1,3,7,8,5};
    uint is_sharp_index[6] = {0,1,1,2,2,0};
    vec3 delta = vec3(0);
    for (int i = 0; i < 6; ++i) {
        vec3 current_normal = currentTriangle.normal_adj[i/2].xyz;
        vec3 current_point = position[i/2].xyz;
        vec3 p = bezierPositionControlPoint[move_control_point[i]];
        vec3 result;
        if (currentTriangle.is_sharp[is_sharp_index[i]] > 0) {
            SamplePointInfo spi = currentTriangle.samplePoint[normal_aux[i/2]];
            spi.sample_point_original_normal = currentTriangle.adjacency_normal[i];
            vec3 adj_normal = sample_bspline_normal_fast(spi);
            vec3 n_ave = cross(current_normal, adj_normal);
            n_ave = normalize(n_ave);
            result = current_point + dot(p - current_point, n_ave) * n_ave;
        } else {
            result = p - dot((p - current_point), current_normal) * current_normal;
        }
        delta += (result - p);
        bezierPositionControlPoint[move_control_point[i]] = result;
    }

    bezierPositionControlPoint[4] += delta * 1.5 / 6;

    // 输出分割三角形
    // 生成顶点数据
//    uint point_index[100];
//    for (int i = 0; i < 3; ++i) {
//        vec3 pointParameter = tessellatedParameter[i];
//        uint point_offset = triangleIndex * 3 + i;
//        tessellatedVertex[point_offset] = vec4(sample_points[normal_aux[i]], 1);
//        tessellatedNormal[point_offset] = vec4(sample_normals[normal_aux[i]], 0);
//        point_index[i] = point_offset;
//    }
//    // 生成index数据
//    uint index_offset = triangleIndex;
//    tessellatedIndex[index_offset * 3] = point_index[0];
//    tessellatedIndex[index_offset * 3 + 1] = point_index[1];
//    tessellatedIndex[index_offset * 3 + 2] = point_index[2];


    // 细分
    // 生成顶点数据
    uint point_index[100];
    for (int i = 0; i < tessellatedParameterLength; ++i) {
        vec3 pointParameter = tessellatedParameter[i].xyz;
        uint point_offset = triangleIndex * tessellatedParameterLength + i;
        tessellatedVertex[point_offset] = getPosition(pointParameter);
        tessellatedNormal[point_offset] = getNormal(pointParameter);
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
    //todo mark
    return vec4(normalize(result), 0);
//    return vec4(result, 0);
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

vec3 sample_helper(SamplePointInfo spi, float[4] un, float[4] vn, float[4] wn){
    uint uli = spi.knot_left_index.x;
    uint vli = spi.knot_left_index.y;
    uint wli = spi.knot_left_index.z;
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

vec3 sample_bspline_normal_fast(SamplePointInfo spi) {
    float u = spi.parameter.x;
    float v = spi.parameter.y;
    float w = spi.parameter.z;

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
    wn[3] = w * wn[2];

    float wn_[4];
    wn_[0] = 0;
    wn_[1] = 1;
    wn_[2] = 2 * w;
    wn_[3] = 3 * w * w;

    vec3 fu = sample_helper(spi, un_, vn, wn);
    vec3 fv = sample_helper(spi, un, vn_, wn);
    vec3 fw = sample_helper(spi, un, vn, wn_);


    vec4 n = spi.sample_point_original_normal;

    //todo should modify when spline body modify
    vec3 result = vec3(1);
    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第一行三个元素
    float J_bar_star_T_0 = fv.y * fw.z - fw.y * fv.z;
    float J_bar_star_T_1 = fw.y * fu.z - fu.y * fw.z;
    float J_bar_star_T_2 = fu.y * fv.z - fv.y * fu.z;
    result.x = n.x * J_bar_star_T_0 * stride[0] + n.y * J_bar_star_T_1 * stride[1] + n.z * J_bar_star_T_2 * stride[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第二行三个元素
    J_bar_star_T_0 = fv.z * fw.x - fw.z * fv.x;
    J_bar_star_T_1 = fw.z * fu.x - fu.z * fw.x;
    J_bar_star_T_2 = fu.z * fv.x - fv.z * fu.x;
    result.y = n.x * J_bar_star_T_0 * stride[0] + n.y * J_bar_star_T_1 * stride[1] + n.z * J_bar_star_T_2 * stride[2];

    // J_bar_star_T_[012]表示J_bar的伴随矩阵的转置(即J_bar*T)的第三行三个元素
    J_bar_star_T_0 = fv.x * fw.y - fw.x * fv.y;
    J_bar_star_T_1 = fw.x * fu.y - fu.x * fw.y;
    J_bar_star_T_2 = fu.x * fv.y - fv.x * fu.y;
    result.z = n.x * J_bar_star_T_0 * stride[0] + n.y * J_bar_star_T_1 * stride[1] + n.z * J_bar_star_T_2 * stride[2];

//todo mark
    return normalize(result);
//    return result;

}
vec3 sample_bspline_position_fast(SamplePointInfo spi) {

    float u = spi.parameter.x;
    float v = spi.parameter.y;
    float w = spi.parameter.z;

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
    wn[3] = w * wn[2];

    return sample_helper(spi, un, vn, wn);
}

