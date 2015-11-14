import logging
from enum import Enum
from copy import deepcopy


class ModelFileFormatType(Enum):
    obj = 1


class OBJ:
    # class Material: def __int__(self, filename):
    #         self.name = filename

    def __init__(self, file_path, format_type):
        self.vertex = []
        self.normal = []
        self.tex_coord = []
        self.index = []

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
            aux_map = {}
            with open(file_path, 'r') as file:
                for l in file:
                    if l is None or len(l) == 0 or l.startswith('#'):
                        continue

                    tokens = l.split()
                    first_token = tokens.pop(0)
                    if first_token == 'v':
                        temp_vertices.append(list(map(float, tokens)))
                        temp_vertices[-1].append(1.0)
                        max_x, min_x = self.find_max_min(max_x, min_x, temp_vertices[-1][0])
                        max_y, min_y = self.find_max_min(max_y, min_y, temp_vertices[-1][1])
                        max_z, min_z = self.find_max_min(max_z, min_z, temp_vertices[-1][2])

                    elif first_token == 'vn':
                        temp_normals.append(list(map(float, tokens)))
                        temp_normals[-1].append(1.0)
                    elif first_token == 'vt':
                        temp_tex_coords.append(list(map(float, tokens)))
                    elif first_token == 'f':
                        if len(tokens) in (3, 4):
                            self.parse_face(aux_map, temp_normals, temp_tex_coords, temp_vertices, tokens[:3])
                            if len(tokens) == 4:
                                self.parse_face(aux_map, temp_normals, temp_tex_coords, temp_vertices,
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

        # 归一化，使模型坐标从-1,1
        mid_x = (max_x + min_x) / 2
        self.d_x = (max_x - min_x)

        mid_y = (max_y + min_y) / 2
        self.d_y = (max_y - min_y)

        mid_z = (max_z + min_z) / 2
        self.d_z = (max_z - min_z)

        # xyz三个维度中，模型跨度最大值
        d = max(self.d_x, self.d_y, self.d_z)

        # 首先深拷贝各个顶点的坐标, 用于计算各个顶点在b样条体中的参数
        # self.parameters = deepcopy(self.vertices)

        temp_vertices.pop(0)
        for v in temp_vertices:
            v[0] = (v[0] - mid_x) / d
            v[1] = (v[1] - mid_y) / d
            v[2] = (v[2] - mid_z) / d


        # 计算模型在b样条体中的参数
        # 将parameters归一化到0～1
        # for v in self.parameters:
        #     v[0] = (v[0] - mid_x) / self.d_x
        #     v[1] = (v[1] - mid_y) / self.d_y
        #     v[2] = (v[2] - mid_z) / self.d_z

        self.d_x /= d
        self.d_y /= d
        self.d_z /= d

        logging.info('load obj finish, has vertices:' + str(len(self.vertex)))

    def parse_face(self, aux_map, temp_normals, temp_tex_coords, temp_vertices, tokens):
        for v in tokens[:3]:
            if v not in aux_map:
                index = v.split('/')

                self.vertex.append(temp_vertices[int(index[0])])
                if len(index) == 2:
                    self.tex_coord.append(temp_tex_coords[int(index[1])])
                else:
                    if index[1]:
                        self.tex_coord.append(temp_tex_coords[int(index[1])])
                    self.normal.append(temp_normals[int(index[2])])

                aux_map[v] = len(aux_map)
            self.index.append(aux_map[v])
        self.index.append(0)

    @staticmethod
    def find_max_min(max_x, min_x, new_x):
        return max(max_x, new_x), min(min_x, new_x)

    def get_length_xyz(self):
        return self.d_x, self.d_y, self.d_z
