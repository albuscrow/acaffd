# float32 * 4
NORMAL_SIZE = 16
VERTEX_SIZE = 16

# 三个index,int32
PER_TRIANGLE_INDEX_SIZE = 12
PER_TRIANGLE_ADJACENCY_INDEX_SIZE = 12

# 六个控制顶点, float32 * 4
PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE = 6 * 4 * 4

# 十个控制顶点, float32 * 4
PER_TRIANGLE_PN_POSITION_TRIANGLE_SIZE = 10 * 4 * 4

#
MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE = 20

CONTROL_POINT_NUMBER = 10
CONTROL_POINT_TRIANGLE_NUMBER = 9

SHOW_NORMAL_POINT_NUMBER_PER_TRIANGLE = 3


#struct SplitedTriangle {
#    vec4 pn_position[3];
#    vec4 pn_normal[3];
#    vec4 original_normal[3];
#    vec4 adjacency_pn_normal3_is_sharp1[6];
#    vec4 parameter_in_original[3];
#    float triangle_quality;
#    uint original_triangle_index;
#};

SPLITED_TRIANGLE_SIZE = 340

ZERO = 0.00001
