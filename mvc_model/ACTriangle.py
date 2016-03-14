class OriginalTriangle:
    def __init__(self, tid, positions, normals, adj_triangle_id):
        self.id = tid
        self.positions = positions
        self.normals = normals
        self.adj_triangle_id = adj_triangle_id

    def to_bytes(self):
        pass

# class OriginalTriangle:
#     def __init__(self, tid, positions, normals, adj_triangle_id):
#         self.id = tid
#         self.positions = positions
#         self.normals = normals
#         self.adj_triangle_id = adj_triangle_id
