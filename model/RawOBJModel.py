import logging
from enum import Enum


class ModelFileFormatType(Enum):
    obj = 1


class OBJ:
    # class Material: def __int__(self, filename):
    #         self.name = filename

    def __init__(self, file_path, format_type):
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.indexes = []

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
                        max_x, min_x = self.findMaxMin(max_x, min_x, temp_vertices[-1][0])
                        max_y, min_y = self.findMaxMin(max_y, min_y, temp_vertices[-1][1])
                        max_z, min_z = self.findMaxMin(max_z, min_z, temp_vertices[-1][2])

                    elif first_token == 'vn':
                        temp_normals.append(list(map(float, tokens)))
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

        # 归一化，事模型坐标从-1,1
        # mid_x = (max_x + min_x) / 2
        # d_x = (max_x - min_x) / 2
        #
        # mid_y = (max_y + min_y) / 2
        # d_y = (max_y - min_y) / 2
        #
        # mid_z = (max_z + min_z) / 2
        # d_z = (max_z - min_z) / 2

        temp_vertices.pop(0)
        for v in temp_vertices:
            # v[0] = (v[0] - mid_x) / d_x
            # v[1] = (v[1] - mid_y) / d_y
            # v[2] = (v[2] - mid_z) / d_z
            v[2] = 0
        logging.info('load obj finish, has vertices:' + str(len(self.vertices)))

    def parse_face(self, aux_map, temp_normals, temp_tex_coords, temp_vertices, tokens):
        for v in tokens[:3]:
            if v not in aux_map:
                index = v.split('/')

                self.vertices.append(temp_vertices[int(index[0])])
                if len(index) == 2:
                    self.tex_coords.append(temp_tex_coords[int(index[1])])
                else:
                    if index[1]:
                        self.tex_coords.append(temp_tex_coords[int(index[1])])
                    self.normals.append(temp_normals[int(index[2])])

                aux_map[v] = len(aux_map)
            self.indexes.append(aux_map[v])

    def findMaxMin(self, max_x, min_x, new_x):
        return max(max_x, new_x), min(min_x, new_x)
