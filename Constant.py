# float32 * 4
import config

NORMAL_SIZE = 16
VERTEX_SIZE = 16
TEX_COORD_SIZE = 8

# 三个index,int32
PER_TRIANGLE_INDEX_SIZE = 12
PER_TRIANGLE_ADJACENCY_INDEX_SIZE = 12

# 六个控制顶点, float32 * 4
PER_TRIANGLE_PN_NORMAL_TRIANGLE_SIZE = 6 * 4 * 4

# 十个控制顶点, float32 * 4
PER_TRIANGLE_PN_POSITION_TRIANGLE_SIZE = 10 * 4 * 4

#
if config.IS_FAST_MODE:
    MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE = 80
else:
    MAX_SPLITED_TRIANGLE_PRE_ORIGINAL_TRIANGLE = 400

CONTROL_POINT_NUMBER = 10
CONTROL_POINT_TRIANGLE_NUMBER = 9

SHOW_NORMAL_POINT_NUMBER_PER_TRIANGLE = 3



# vec4 pn_position[3];
# vec4 pn_normal[3];
# vec4 original_position[3];
# vec4 original_normal[3];
# vec4 adjacency_pn_normal_parameter[6];
# vec4 parameter_in_original2_texcoord2[3];
# ivec4 adjacency_triangle_index3_original_triangle_index1;
# float triangle_quality;

SPLITED_TRIANGLE_SIZE = 368

ALGORITHM_AC = 0
ALGORITHM_CYM = 1
