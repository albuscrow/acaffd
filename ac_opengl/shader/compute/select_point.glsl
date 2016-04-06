#version 450
//input
layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
};

//input
layout(std430, binding=21) buffer TessellatedParameterInBSplineBody{
    vec4[] tessellatedParameterInBSplineBody;
};

//input
layout(std430, binding=8) buffer TesselatedIndexBuffer{
    uint[] tessellatedIndex;
};

//output
layout(std430, binding=20) buffer selectResult{
    vec4[] selectedPoint;
};

layout(location=0) uniform uint triangleNumber;
layout(location=1) uniform vec3 startPoint;
layout(location=2) uniform vec3 direction;

layout(binding = 1) uniform atomic_uint counter;

//表示group size,这个问题中group size与具体问题无关，先取512,后面再调优
layout(local_size_x = 512, local_size_y = 1, local_size_z = 1) in;

void main() {
    uint triangleIndex = gl_GlobalInvocationID.x;
    if (triangleIndex >= triangleNumber) {
        return;
    }
    vec3 position[3];
    position[0] = tessellatedVertex[tessellatedIndex[triangleIndex * 3]].xyz;
    position[1] = tessellatedVertex[tessellatedIndex[triangleIndex * 3 + 1]].xyz;
    position[2] = tessellatedVertex[tessellatedIndex[triangleIndex * 3 + 2]].xyz;
    vec3 E1 = position[1] - position[0];
    vec3 E2 = position[2] - position[0];
    mat3 m = mat3(-direction, E1, E2);
    float D = determinant(m);
    // Singular matrix, problem...
    if(abs(D) > 0.000001) {
        mat3 im = inverse(m);
        vec3 T = startPoint - position[0];
        vec3 tvw = im * T;
        if (tvw[0] < 0 || tvw[1] > 1 || tvw[1] < 0 || tvw[2] > 1 || tvw[2] < 0) {
            return;
        } else {
            vec3 uvw = vec3(1 - tvw[1] - tvw[2], tvw[1], tvw[2]);
            vec3 res = vec3(0);
            for (int i = 0; i < 3; ++i) {
                res += tessellatedParameterInBSplineBody[tessellatedIndex[triangleIndex * 3 + i]].xyz * uvw[i];
            }
            uint i = atomicCounterIncrement(counter);
//            selectedPoint[i].xyz = startPoint + direction * tuv[0];
            selectedPoint[i].xyz = res;
            selectedPoint[i].w = tvw[0];
        }
    }
}
