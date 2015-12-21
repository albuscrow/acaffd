import logging
from enum import Enum
import numpy as np

class ModelFileFormatType(Enum):
    obj = 1


class OBJ:
    def __init__(self, file_path, format_type):
        self.vertex = []
        self.normal = []
        self.tex_coord = []
        self.index = []
        self.adjacency = []

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
            with open(file_path, 'r') as file:
                for l in file:
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
                        temp_normals[-1].append(1)
                    elif first_token == 'vt':
                        temp_tex_coords.append(list(map(float, tokens)))
                    elif first_token == 'f':
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

        logging.info('load obj finish, has vertices:' + str(len(self.vertex)))
        self.original_index_number = len(self.index)
        self.original_triangle_number = self.original_index_number / 3
        self.original_vertex_number = len(self.vertex)
        self.original_normal_number = len(self.normal)

    def parse_face(self, aux_vertex_map, aux_point_map, temp_normals, temp_tex_coords, temp_vertices, tokens):
        # 纪录该三角形的三个顶点
        point_indexes = []
        for v in tokens[:3]:
            index = v.split('/')
            vertex_index = int(index[0])
            point_indexes.append(vertex_index)

            if v not in aux_vertex_map:
                # 当前点还没有纪录的话先纪录当前点
                self.vertex.append(temp_vertices[vertex_index])

                if len(index) == 2:
                    self.tex_coord.append(temp_tex_coords[int(index[1])])
                else:
                    if index[1]:
                        self.tex_coord.append(temp_tex_coords[int(index[1])])
                    self.normal.append(temp_normals[int(index[2])])

                aux_vertex_map[v] = len(aux_vertex_map)

            self.index.append(aux_vertex_map[v])
        self.adjacency.append([-1, -1, -1])

        current_triangle_index = int((len(self.index) - 3) / 3)
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
                    if self.vertex[self.index[triangle_index * 3 + j]] == temp:
                        self.adjacency[triangle_index][j] = current_triangle_index * 4 + i
                        self.adjacency[-1][i] = triangle_index * 4 + j
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
