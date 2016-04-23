import logging
from mvc_model.ACTriangle import ACTriangle, ACPoly
from mvc_model.aux import BSplineBody
from util.util import normalize, equal_vec
from itertools import product
from math import factorial
import numpy as np


class BSplinePatch:
    def __init__(self, control_points):
        self._control_points = np.array(control_points).reshape((4, 4, 3))

    def sample(self, u, v):
        result = np.zeros((3,))
        control_point_number = self._control_points.shape[:2]
        for i, j in product(*[range(x) for x in control_point_number]):
            result += self.b(u, control_point_number[0] - 1, i) \
                      * self.b(v, control_point_number[1] - 1, j) \
                      * self._control_points[i, j]

        result_u = np.zeros((3,))
        for j in range(4):
            temp = np.zeros((3,))
            for i in range(3):
                temp += self.b(u, 2, i) * (self._control_points[i, j] - self._control_points[i + 1, j])
            result_u += self.b(v, 3, j) * temp

        result_v = np.zeros((3,))
        for i in range(4):
            temp = np.zeros((3,))
            for j in range(3):
                temp += self.b(v, 2, j) * (self._control_points[i, j] - self._control_points[i, j + 1])
            result_v += self.b(u, 3, i) * temp

        cross = np.cross(result_v, result_u)

        return result.tolist() + [1], normalize(cross).tolist() + [0]

    def c(self, n, r):
        return factorial(n) / factorial(r) / factorial(n - r)

    def b(self, t, n, i):
        return self.c(n, i) * pow(t, i) * pow(1 - t, n - i)

    @property
    def control_points(self):
        return np.hstack((self._control_points.reshape(16, 3), np.ones((16, 1))))
        # return self._control_points.reshape(16, 3)


class BPT:
    def __init__(self, file_path):
        self._b_spline_patch = []

        with open(file_path, 'r') as file:
            patch_number = int(file.readline())
            for _ in range(patch_number):
                control_points = []
                u, v = map(lambda s: int(s) + 1, file.readline().split())
                for _ in range(u * v):
                    control_points.append([float(x) for x in file.readline().split()])
                self._b_spline_patch.append(BSplinePatch(control_points))

    @property
    def b_spline_patch(self):
        return self._b_spline_patch


class OBJ:
    def __init__(self, file_path: str = None, bpt=None):
        self._bezier_control_points = []
        self._vertex = []
        self._normal = []
        self._tex_coord = []
        self._bezier_uv = []
        self._has_texture = False
        self._index = []
        self._adjacency = []
        self._original_index_number = 0
        self._original_triangle_number = 0
        self._original_vertex_number = 0
        self._original_normal_number = 0
        self._triangles = None  # type: list[ACTriangle]
        self._length = []
        self._from_bezier = False

        if file_path:
            if file_path.endswith('.obj') or file_path.endswith('.OBJ'):
                self.parse_from_obj(file_path)
            else:
                self.parse_from_bpt(BPT(file_path))
        elif bpt:
            self.parse_from_bpt(bpt)
        else:
            raise Exception()

    def parse_from_obj(self, file_path):
        temp_vertices = [[0, 0, 0]]
        temp_normals = [[0, 0, 0]]
        temp_tex_coords = [[0, 0]]
        f_store = set()
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
                elif first_token == 'vn':
                    temp_normals.append(list(map(float, tokens)))
                    temp_normals[-1] = normalize(temp_normals[-1])
                    temp_normals[-1].append(0)
                elif first_token == 'vt':
                    temp_tex_coords.append(list(map(float, tokens)))
                elif first_token == 'f':
                    f_store.add(' '.join(tokens))
                elif first_token == 'vp':
                    pass
                    # logging.warning("this feature(vp) in wavefront .obj is not implement, ignore")
                    # raise Exception()
                elif first_token in ('usemtl', 'usemat'):
                    pass
                    # logging.warning("this feature(usemtl, usemat) in wavefront .obj is not implement, ignore")
                    # raise Exception()
                    # material = tokens[0]
                elif first_token == 'mtllib':
                    pass
                    # logging.warning("this feature(mtllib) in wavefront .obj is not implement, ignore")
                    # raise Exception()
                    # self.mtl = self.Material(tokens[0])
        self.handle_face(f_store, temp_normals, temp_tex_coords, temp_vertices)

    def parse_from_bpt(self, bpt: BPT):
        self._from_bezier = True
        temp_vertices = []
        temp_normals = []
        temp_uv = []
        f_store = set()
        parse_factor = 5
        one_patch_point = (parse_factor + 1) ** 2
        temp_index = []
        for i, j in product(range(parse_factor), range(parse_factor)):
            i1 = i * (parse_factor + 1) + j
            i2 = i1 + 1
            i3 = i1 + parse_factor + 1
            i4 = i3 + 1
            temp_index.append((i1, i2, i3))
            temp_index.append((i3, i2, i4))

        for i, b in enumerate(bpt.b_spline_patch):
            self._bezier_control_points.append(b.control_points)
            for u, v in product(np.linspace(0, 1, parse_factor + 1), np.linspace(0, 1, parse_factor + 1)):
                p, n = (b.sample(u, v))
                p[3] = i

                ##以下代码是特地给犹它茶壶用的
                if i < 4 and u == 0:
                    n = [0, 0, 1, 0]
                elif i < 8 and u == 0:
                    n = [0, 0, -1, 0]

                temp_vertices.append(p)
                temp_normals.append(n)
                temp_uv.append([u, v])
            for index in temp_index:
                real_index = [ii + i * one_patch_point for ii in index]
                # p1, p2, p3 = [np.array(temp_vertices[ii], dtype='f4') for ii in real_index]
                # if equal_vec(p1, p2) or equal_vec(p1, p3) or equal_vec(p3, p2):
                #     continue
                f_store.add("{0}//{0} {1}//{1} {2}//{2}".format(*real_index))

        self.handle_face(f_store, temp_normals, None, temp_vertices, temp_uv)

    def handle_face(self, f_store, temp_normals, temp_tex_coords, temp_vertices, temp_uv=None):
        model_range = [(-999999, 999999)] * 3
        for v in temp_vertices:
            for i in range(3):
                model_range[i] = self.find_max_min(model_range[i], v[i])

        # 归一化，使模型坐标从-1,1
        mid = []
        self._length = []
        for r in model_range:
            mid.append((r[0] + r[1]) / 2)
            self._length.append(r[0] - r[1])
        # d 为 xyz三个维度中，模型跨度最大值
        d = max(*self._length) / 2

        # 归一化 self._length
        self._length = [x / d for x in self._length]

        # 归一化 temp_vertices
        temp_vertices = [[(e - m) / d for e, m in zip(v[:3], mid)] + v[3:] for v in temp_vertices]

        # 归一化 bezier_control_points
        for c in self._bezier_control_points:
            for i in range(3):
                c[:, i] = (c[:, i] - mid[i]) / d

        # vertex 到 vertex_index map
        aux_vertex_map = {}
        # point 到 由该point构成的三角形index map, 这里的三角形index由该三角形的第一个顶点的self.index中的位置决定。
        aux_point_map = {}
        for l in f_store:
            tokens = l.split()
            if len(tokens) in (3, 4):
                self.parse_face(aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords, temp_vertices,
                                tokens[:3], temp_uv)
                if len(tokens) == 4:
                    self.parse_face(aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords,
                                    temp_vertices, [tokens[0], tokens[2], tokens[3]], temp_uv)
            else:
                logging.error("this feature(face vertices = " + str(
                    len(tokens)) + ") in wavefront .obj is not implement")
                raise Exception()
        logging.info('load obj finish, has vertices:' + str(len(self._vertex)))
        self._original_index_number = len(self._index)
        self._original_triangle_number = self._original_index_number / 3
        self._original_vertex_number = len(self._vertex)
        self._original_normal_number = len(self._normal)
        self._triangles = None  # type: list[ACTriangle]
        self.reorganize()
        print('OBJ:', 'original triangle number: %d' % self._original_triangle_number)

    def parse_face(self, aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords, temp_vertices, tokens, temp_uv):
        # 纪录该三角形的三个顶点
        point_indexes = []
        for v in tokens[:3]:
            index = v.split('/')
            vertex_index = int(index[0])
            point_indexes.append(vertex_index)

            if v not in aux_vertex_map:
                # 当前点还没有纪录的话先纪录当前点
                self._vertex.append(temp_vertices[vertex_index])
                if temp_uv:
                    self._bezier_uv.append(temp_uv[vertex_index])
                else:
                    self._bezier_uv.append([0, 0])

                if len(index) == 2:
                    self._tex_coord.append(temp_tex_coords[int(index[1])])
                    self._normal.append([0, 0, 0, 0])
                else:
                    if index[1]:
                        self._tex_coord.append(temp_tex_coords[int(index[1])])
                    else:
                        self._has_texture = False
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
                triangle_index = triangle_index_set.pop()[0]
                temp = temp_vertices[prev_vertex_index]
                for j in range(3):
                    if self._vertex[self._index[triangle_index * 3 + j]] == temp:
                        self._adjacency[triangle_index][j] = current_triangle_index * 4 + i
                        self._adjacency[-1][i] = triangle_index * 4 + j
                        break
            elif common_triangle_number >= 2:
                # print(triangle_index_set, tokens)
                raise Exception('3 or more triangle adjacency with the same edge, number is', common_triangle_number)

        # 将当前三角形加入到aux_point_map中
        for vertex_index in point_indexes:
            # 判断当前位置（position）为顶点的三角形有没有纪录
            if vertex_index not in aux_point_map:
                aux_point_map[vertex_index] = set()
            aux_point_map[vertex_index].add((current_triangle_index, ' '.join(tokens)))

    @staticmethod
    def find_max_min(max_min, new_x):
        return max(max_min[0], new_x), min(max_min[1], new_x)

    def get_length_xyz(self):
        return self._length

    @property
    def vertex(self):
        return np.array(self._vertex, dtype=np.float32)

    @property
    def normal(self):
        return np.array(self._normal, dtype=np.float32)

    @property
    def tex_coord(self):
        return np.array(self._tex_coord, dtype=np.float32)

    @property
    def index(self):
        return np.array(self._index, dtype=np.uint32)

    @property
    def adjacency(self):
        return np.array(self._adjacency, dtype=np.int32)

    def split(self, bspline: BSplineBody):
        pnp_data = []
        pnn_data = []
        for t in self._triangles:
            pnp, pnn = t.gen_pn_triangle()
            pnp_data.append(np.hstack((pnp, [[0]] * 10)))
            pnn_data.append(np.hstack((pnn, [[0]] * 6)))

        polygons = []
        for t in self._triangles:
            polygons.append(ACPoly(t))

        split_line = bspline.get_split_line()
        for i in range(3):
            up = []
            down = polygons
            for j in split_line[i][::-1]:
                down_temp = []
                for p in down:  # type: ACPoly
                    upp, downp = p.split(i, j)
                    if upp:
                        up.append(upp)
                    if downp:
                        down_temp.append(downp)
                down = down_temp
            polygons = up + down

        triangles = []
        for p in polygons:  # type: ACPoly
            triangles += p.to_triangle()

        triangle_data = []
        for t in triangles:
            triangle = t.as_element_for_shader()
            triangle_data.append(triangle)
        return len(triangle_data), \
               np.array(triangle_data, ACTriangle.DATA_TYPE), \
               np.array(pnp_data, dtype='f4'), \
               np.array(pnn_data, dtype='f4')

    def reorganize(self):
        self._triangles = []  # type: list[ACTriangle]
        for i, index in enumerate(zip(*([iter(self._index)] * 3))):
            t = ACTriangle(i)  # type: ACTriangle
            t.positionv4, t.normalv4, t.tex_coord, t.bezier_uv = [np.array([lst[x] for x in index], dtype='f4') for lst
                                                                  in
                                                                  [self._vertex, self._normal, self._tex_coord,
                                                                   self._bezier_uv]]
            t.bezier_id = int(t.positionv4[0][3])
            self._triangles.append(t)
        for i, triangle in enumerate(self._triangles):
            triangle.neighbor = []
            for j in self._adjacency[i]:
                if j != -1:
                    triangle.neighbor.append((self._triangles[j // 4], j % 4))
                else:
                    triangle.neighbor.append((None, -1))

    def intersect(self, start_point, direction):
        mint = 99999
        res = None
        for triangle in self._triangles:
            t, p = triangle.intersect(start_point, direction)
            if p is not None and t < mint:
                if t < mint:
                    mint = t
                    res = p
        return res

    @property
    def has_texture(self):
        return self._has_texture

    @property
    def from_bezier(self):
        return self._from_bezier

    @property
    def bezier_control_points(self):
        return np.array(self._bezier_control_points, dtype='f4')

    @property
    def bezier_uv(self):
        return np.array(self._bezier_uv, dtype='f4')


from matplotlib.pylab import plot, show

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
                     [i] * 4))

    table = np.array(data, dtype=[('samplePoint', [('parameter', '4f4'),
                                                   ('sample_point_original_normal', '4f4'),
                                                   ('knot_left_index', '4u4')], 37),
                                  ('normal_adj', ('f4', (3, 4))),
                                  ('adjacency_normal', ('f4', (6, 4))),
                                  ('original_normal', ('f4', (3, 4))),
                                  ('original_position', ('f4', (3, 4))),
                                  ('need_adj', '4i4'),
                                  ])
    # print(table[0])
    # print(table[0][0][0])
    # print(table.itemsize)
    # SPLITED_TRIANGLE_SIZE = 48 * 37 + 15 * 16 + 32
    # print(SPLITED_TRIANGLE_SIZE)

    model = BPT(file_path='../res/3d_model/t.bpt')
    bsp = model.b_spline_patch[0]
    x = np.linspace(0, 1, 100)
    y1 = [bsp.b(xx, 3, 0) for xx in x]
    y2 = [bsp.b(xx, 3, 1) for xx in x]
    y3 = [bsp.b(xx, 3, 2) for xx in x]
    y4 = [bsp.b(xx, 3, 3) for xx in x]
    plot(x, y1)
    plot(x, y2)
    plot(x, y3)
    plot(x, y4)
    show()
    model = OBJ(file_path='../res/3d_model/cube2.obj')
    bsb = BSplineBody(2, 2, 2)
    model.split(bsb)
