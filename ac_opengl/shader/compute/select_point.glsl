#version 450
//input
layout(std430, binding=6) buffer TesselatedVertexBuffer{
    vec4[] tessellatedVertex;
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
    if(abs(D) <= 0.000001) {
        selectedPoint[triangleIndex] = vec4(0,0,0,-1);
    } else {
        mat3 im = inverse(m);
        vec3 T = startPoint - position[0];
        vec3 tuv = im * T;
        if (tuv[0] < 0 || tuv[1] > 1 || tuv[1] < 0 || tuv[2] > 1 || tuv[2] < 0) {
            selectedPoint[triangleIndex] = vec4(0,0,0,-1);
        } else {
            selectedPoint[triangleIndex].xyz = startPoint + tuv[0] * direction;
            selectedPoint[triangleIndex].w = tuv[0];
        }
    }
}
