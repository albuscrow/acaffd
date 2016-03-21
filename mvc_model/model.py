import logging
from enum import Enum
import numpy as np

from mvc_model.aux import BSplineBody


class ModelFileFormatType(Enum):
    obj = 1


def normalize(n):
    l = (n[0] ** 2 + n[1] ** 2 + n[2] ** 2) ** 0.5
    return [x / l for x in n]
    pass


class OBJ:
    def __init__(self, file_path, format_type: ModelFileFormatType = ModelFileFormatType.obj):
        self._vertex = []
        self._normal = []
        self._tex_coord = []
        self._index = []
        self._adjacency = []

        if format_type == ModelFileFormatType.obj:
            temp_vertices = [[]]
            max_x = -999999
            max_y = -999999
            max_z = -999999
            min_x = 999999
            min_y = 999999
            min_z = 999999
            temp_normals = [[]]
            temp_tex_coords = [[]]
            # vertex 到 vertex_index map
            aux_vertex_map = {}
            # point 到 由该point构成的三角形index map, 这里的三角形index由该三角形的第一个顶点的self.index中的位置决定。
            aux_point_map = {}

            f_store = []
            with open(file_path, 'r') as file:
                for l in file:
                    l = l.strip()
                    if l is None or len(l) == 0 or l.startswith('#'):
                        continue
                    tokens = l.split()
                    first_token = tokens.pop(0)
                    if first_token == 'v':
                        temp_vertices.append(list(map(float, tokens)))
                        temp_vertices[-1].append(1)
                        max_x, min_x = self.find_max_min(max_x, min_x, temp_vertices[-1][0])
                        max_y, min_y = self.find_max_min(max_y, min_y, temp_vertices[-1][1])
                        max_z, min_z = self.find_max_min(max_z, min_z, temp_vertices[-1][2])
                    elif first_token == 'vn':
                        temp_normals.append(list(map(float, tokens)))
                        temp_normals[-1] = normalize(temp_normals[-1])
                        temp_normals[-1].append(0)
                    elif first_token == 'vt':
                        temp_tex_coords.append(list(map(float, tokens)))
                    elif first_token == 'f':
                        f_store.append(tokens)
                    elif first_token == 'vp':
                        logging.warning("this feature(vp) in wavefront .obj is not implement, ignore")
                        # raise Exception()
                    elif first_token in ('usemtl', 'usemat'):
                        logging.warning("this feature(usemtl, usemat) in wavefront .obj is not implement, ignore")
                        # raise Exception()
                        # material = tokens[0]
                    elif first_token == 'mtllib':
                        logging.warning("this feature(mtllib) in wavefront .obj is not implement, ignore")
                        # raise Exception()
                        # self.mtl = self.Material(tokens[0])
                for tokens in f_store:
                    if len(tokens) in (3, 4):
                        self.parse_face(aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords, temp_vertices,
                                        tokens[:3])
                        if len(tokens) == 4:
                            self.parse_face(aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords,
                                            temp_vertices,
                                            [tokens[0], tokens[2], tokens[3]])
                    else:
                        logging.error("this feature(face vertices = " + str(
                            len(tokens)) + ") in wavefront .obj is not implement")
                        raise Exception()
        else:
            logging.error('only support obj file')
            raise Exception()

        # check adjacency
        # for i in range(len(self.adjacency)):
        #     for ti in self.adjacency[i]:
        #         if i * 3 not in self.adjacency[int(ti / 3)]:
        #             print('error')
        #             print(self.adjacency[i])

        # 归一化，使模型坐标从-1,1
        mid_x = (max_x + min_x) / 2
        self.d_x = (max_x - min_x)

        mid_y = (max_y + min_y) / 2
        self.d_y = (max_y - min_y)

        mid_z = (max_z + min_z) / 2
        self.d_z = (max_z - min_z)

        # xyz三个维度中，模型跨度最大值
        d = max(self.d_x, self.d_y, self.d_z) / 2

        # 首先深拷贝各个顶点的坐标, 用于计算各个顶点在b样条体中的参数
        # self.parameters = deepcopy(self.vertices)

        temp_vertices.pop(0)
        for v in temp_vertices:
            v[0] = (v[0] - mid_x) / d
            v[1] = (v[1] - mid_y) / d
            v[2] = (v[2] - mid_z) / d

        self.d_x /= d
        self.d_y /= d
        self.d_z /= d

        logging.info('load obj finish, has vertices:' + str(len(self._vertex)))
        self.original_index_number = len(self._index)
        self.original_triangle_number = self.original_index_number / 3
        self.original_vertex_number = len(self._vertex)
        self.original_normal_number = len(self._normal)

    def parse_face(self, aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords, temp_vertices, tokens):
        # 纪录该三角形的三个顶点
        point_indexes = []
        for v in tokens[:3]:
            index = v.split('/')
            vertex_index = int(index[0])
            point_indexes.append(vertex_index)

            if v not in aux_vertex_map:
                # 当前点还没有纪录的话先纪录当前点
                self._vertex.append(temp_vertices[vertex_index])

                if len(index) == 2:
                    self._tex_coord.append(temp_tex_coords[int(index[1])])
                    self._normal.append([0, 0, 0, 0])
                else:
                    if index[1]:
                        self._tex_coord.append(temp_tex_coords[int(index[1])])
                    else:
                        self._tex_coord.append([0, 0])
                    self._normal.append(temp_normals[int(index[2])])

                aux_vertex_map[v] = len(aux_vertex_map)

            self._index.append(aux_vertex_map[v])
        self._adjacency.append([-1, -1, -1])

        current_triangle_index = int((len(self._index) - 3) / 3)
        # 建立邻接关系
        for i in range(len(point_indexes)):
            current_vertex_index = point_indexes[i]
            prev_vertex_index = point_indexes[i - 1]
            if current_vertex_index not in aux_point_map or prev_vertex_index not in aux_point_map:
                continue
            triangle_index_set = aux_point_map[current_vertex_index] & aux_point_map[prev_vertex_index]
            common_triangle_number = len(triangle_index_set)
            if common_triangle_number == 1:
                triangle_index = triangle_index_set.pop()
                temp = temp_vertices[prev_vertex_index]
                for j in range(3):
                    if self._vertex[self._index[triangle_index * 3 + j]] == temp:
                        self._adjacency[triangle_index][j] = current_triangle_index * 4 + i
                        self._adjacency[-1][i] = triangle_index * 4 + j
                        break
            elif common_triangle_number >= 2:
                raise Exception('3 or more triangle adjacency with the same edge')

        # 将当前三角形加入到aux_point_map中
        for vertex_index in point_indexes:
            # 判断当前位置（position）为顶点的三角形有没有纪录
            if vertex_index not in aux_point_map:
                aux_point_map[vertex_index] = set()
            aux_point_map[vertex_index].add(current_triangle_index)

    @staticmethod
    def find_max_min(max_x, min_x, new_x):
        return max(max_x, new_x), min(min_x, new_x)

    def get_length_xyz(self):
        return self.d_x, self.d_y, self.d_z

    @property
    def vertex(self):
        return np.array(self._vertex, dtype=np.float32)

    @property
    def normal(self):
        return np.array(self._normal, dtype=np.float32)

    @property
    def index(self):
        return np.array(self._index, dtype=np.uint32)

    @property
    def adjacency(self):
        return np.array(self._adjacency, dtype=np.int32)

    def split(self, bspline: BSplineBody):
        triangles = self.reorganize()
        data = []
        for t in triangles:
            data.append(t.as_element_for_shader(bspline))
            pass
        return self.original_triangle_number, np.array(data, ACTriangle.DATA_TYPE)

    def reorganize(self):
        res = []  # type: list[ACTriangle]
        for i, index in enumerate(zip(*([iter(self._index)] * 3))):
            print(index)
            t = ACTriangle(i)  # type: ACTriangle
            t.position, t.normal, t.tex_coord = [np.array([lst[x] for x in index], dtype='f4') for lst in
                                                 [self._vertex, self._normal, self._tex_coord]]
            res.append(t)
        for i, triangle in enumerate(res):
            triangle.neighbor = []
            for j in self._adjacency[i]:
                if j != -1:
                    triangle.neighbor.append((res[j // 4], j % 4))
                else:
                    triangle.neighbor.append((None, -1))
        for t in res:
            print(t)
        return res


class ACTriangle:
    DATA_TYPE = [('samplePoint', [('parameter', '4f4'),
                                  ('sample_point_original_normal', '4f4'),
                                  ('knot_left_index', '4u4')], 37),
                 ('normal_adj', '4f4', 3),
                 ('adjacency_normal', '4f4', 6),
                 ('original_normal', '4f4', 3),
                 ('original_position', '4f4', 3),
                 ('need_adj', '8i4'),
                 ]

    SAMPLE_PATTERN = np.array([
        [1.000000, 0.000000, 0.000000],

        [0.833333, 0.166667, 0.000000],
        [0.833333, 0.000000, 0.166667],

        [0.666667, 0.333333, 0.000000],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.000000, 0.333333],

        [0.500000, 0.500000, 0.000000],
        [0.500000, 0.333333, 0.166667],
        [0.500000, 0.166667, 0.333333],
        [0.500000, 0.000000, 0.500000],

        [0.333333, 0.666667, 0.000000],
        [0.333333, 0.500000, 0.166667],
        [0.333333, 0.333333, 0.333333],
        [0.333333, 0.166667, 0.500000],
        [0.333333, 0.000000, 0.666667],

        [0.166667, 0.833333, 0.000000],
        [0.166667, 0.666667, 0.166667],
        [0.166667, 0.500000, 0.333333],
        [0.166667, 0.333333, 0.500000],
        [0.166667, 0.166667, 0.666667],
        [0.166667, 0.000000, 0.833333],

        [0.000000, 1.000000, 0.000000],
        [0.000000, 0.833333, 0.166667],
        [0.000000, 0.666667, 0.333333],
        [0.000000, 0.500000, 0.500000],
        [0.000000, 0.333333, 0.666667],
        [0.000000, 0.166667, 0.833333],
        [0.000000, 0.000000, 1.000000],

        [1, 0, 0],
        [0.6667, 0.3333, 0], [0.6667, 0, 0.3333],
        [0.3333, 0.6667, 0], [0.3333, 0, 0.6667],
        [0, 1, 0], [0, 0.6667, 0.3333], [0, 0.3333, 0.6667], [0, 0, 1]], dtype='f4')

    def __init__(self, i):
        self._id = i
        self._position = None  # type: np.array
        self._normal = None  # type: np.array
        self._tex_coord = None  # type: np.array
        self._neighbor = None  # type: list[(ACTriangle, int)]

    def __str__(self):
        return ','.join([str(x.id if x else None) + '-' + str(y) for x, y in self._neighbor])

    def as_element_for_shader(self, b_spline_body: BSplineBody) -> list:
        data = []
        samplePoints = []
        for pattern in ACTriangle.SAMPLE_PATTERN:
            samplePoints.append(self.get_sample_point(pattern))

        return data

    def get_sample_point(self, pattern):
        return [self._position * pattern, self._normal * pattern, [0, 0, 0, 0]]

    @property
    def id(self):
        return self._id

    @property
    def position(self):
        return self._position

    @property
    def normal(self):
        return self._normal

    @property
    def tex_coord(self):
        return self._tex_coord

    @property
    def neighbor(self):
        return self._neighbor

    @position.setter
    def position(self, value):
        self._position = value

    @normal.setter
    def normal(self, value):
        self._normal = value

    @tex_coord.setter
    def tex_coord(self, value):
        self._tex_coord = value

    @neighbor.setter
    def neighbor(self, value):
        self._neighbor = value


if __name__ == '__main__':
    import numpy as np

    data = []
    for i in range(10):
        samplePoint = []
        for j in range(37):
            samplePoint.append((np.array([j + 1000 + .5] * 4, dtype='f4'), [j + .5] * 4, [j] * 4))
        data.append((samplePoint,
                     np.array([[i + .5] * 4] * 3, dtype='f4'),
                     [[i + .5] * 4] * 6,
                     [[i + .5] * 4] * 3,
                     [[i + .5] * 4] * 3,
                     [i] * 8
                     ))

    table = np.array(data, dtype=[('samplePoint', [('parameter', '4f4'),
                                                   ('sample_point_original_normal', '4f4'),
                                                   ('knot_left_index', '4u4')], 37),
                                  ('normal_adj', ('f4', (3, 4))),
                                  ('adjacency_normal', ('f4', (6, 4))),
                                  ('original_normal', ('f4', (3, 4))),
                                  ('original_position', ('f4', (3, 4))),
                                  ('need_adj', '8i4'),
                                  ])
    print(table[0])
    print(table[0][0][0])
    print(table.itemsize)
    SPLITED_TRIANGLE_SIZE = 48 * 37 + 15 * 16 + 32
    print(SPLITED_TRIANGLE_SIZE)

    model = OBJ('../res/3d_model/test_2_triangle.obj')
    model.reorganize()
