# float32 * 4
NORMAL_SIZE = 16
VERTEX_SIZE = 16

# 三个index,int32
PER_TRIANGLE_INDEX_SIZE = 12
PER_TRIANGLE_ADJACENCY_INDEX_SIZE = 12

# 六个控制顶点, float32 * 4
PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE = 6 * 4 * 4

#
MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE = 250

#
# struct SamplePointInfo {
#     vec4 parameter;          16
#     vec4 original_normal;    16
#     uvec4 knot_left_index;   16
# };
#
# struct SplitedTriangle {
#     SamplePointInfo samplePoint[37];  48 * 37
#     vec4 adjacency_normal[6];         16 * 6
#     vec4 original_normal[3];          16 * 3
#     vec4 original_position[3];        16 * 3
#     bool need_adj[6];                 1 * 6
# };

# struct SamplePointInfo {
#     vec4 parameter;
#     vec4 sample_point_original_normal;
#     uvec4 knot_left_index;
# };
# struct SplitedTriangle {
#     SamplePointInfo samplePoint[37];
#     vec4 normal_adj[3];
#     vec4 adjacency_normal[6];
#     vec4 original_normal[3];
#     vec4 original_position[3];
#     bool need_adj[6];
# };

SPLITED_TRIANGLE_SIZE = 48 * 37 + 15 * 16 + 16

ZERO = 0.000001
