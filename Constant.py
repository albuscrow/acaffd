# float32 * 4
NORMAL_SIZE = 16
VERTEX_SIZE = 16

# 三个index,int32
PER_TRIANGLE_INDEX_SIZE = 12
PER_TRIANGLE_ADJACENCY_INDEX_SIZE = 12

# 六个控制顶点, float32 * 4
PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE = 6 * 4 * 4

#
MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE = 200

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
#     bool need_adj[6];                 1 * 6
#     vec4 original_normal[3];          16 * 3
#     vec4 original_position[3];        16 * 3
#
# };

SPLITED_TRIANGLE_SIZE = 1926 + 48 * 2

##todo
TESSELLATED_POINT_NUMBER_PRE_SPLITED_TRIANGLE = 3
TESSELLATED_TRIANGLE_NUMBER_PRE_SPLITED_TRIANGLE = 1

