from pathlib import Path
import os
import shutil
import numpy
import math

def normalize_v3(arr):
    ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
    lens = numpy.sqrt( arr[0]**2 + arr[1]**2 + arr[2]**2 )
    arr[0] /= lens
    arr[1] /= lens
    arr[2] /= lens
    return [arr[0], arr[1], arr[2]]

def get_normals(a, b, c):
    a = numpy.array([float(i) for i in a])
    b = numpy.array([float(i) for i in b])
    c = numpy.array([float(i) for i in c])
    return normalize_v3(numpy.cross( b - a , c - a ))

class TTSTT:
    def __init__(self):
        self.height_data = {}
        self.curr_operation_idx = 0
        self.counter = 0
        self.file_name = None
        self.brush_size = 5
        self.brush_strength = 0.5
        self.brush_type = "raise"
        self.grid_size = 0.5

    def get_height(self, x, z, op_idx=None):
        if not (x, z) in self.height_data:
            return 10
        else:
            if op_idx is None:
                op_idx = self.curr_operation_idx

            vals = self.height_data[(x, z)]
            idx = len(vals) - 1
            while vals[idx][0] > op_idx:
                idx -= 1
            if idx < 0:
                return 10
            return vals[idx][1]
    
    def set_heigt(self, x, z, v):
        if not (x, z) in self.height_data:
            self.height_data[(x, z)] = []
        self.height_data[(x, z)].append((self.curr_operation_idx, v))

    def itr_pos(self):
        for x, z in self.height_data.keys():
            yield x, z

    def set_filename(self):
        self.file_name = str(os.path.join(Path.cwd(), "http_echo", "test_" + str(self.counter)))
        self.counter += 1

    def write_mesh(self):
        if not self.file_name is None and os.path.exists(self.file_name + ".obj"):
            os.remove(self.file_name + ".obj")
            os.remove(self.file_name + ".png")
        self.set_filename()
        with open(self.file_name + ".obj", "w") as outfile:
            print("#Terrain made by ttstt - Tabletop Simulator Terraintool", file=outfile)
            print("o heightmap", file=outfile)

            idxs = {}
            for (x, z) in self.itr_pos():
                y = self.get_height(x, z)
                print("v", x * self.grid_size, y, z * self.grid_size, file=outfile)
                idxs[(x, z)] = len(idxs) + 1
            for (x, z) in self.itr_pos():
                print("vt", x * 0.1, z * 0.1, file=outfile)

            f_idxs = {}
            for (x, z), y in self.itr_pos():
                y = self.get_height(x, z)
                # @todo continue removing hight_data
                if (x+1, z) in self.height_data and \
                   (x+1, z+1) in self.height_data and \
                   (x, z+1) in self.height_data:
                    f_idxs[(x, z)] = len(f_idxs) + 1
            for x, z in f_idxs.keys():
                a = [x * self.grid_size, self.get_height(x, z), z * self.grid_size]
                b = [x * self.grid_size, self.get_height(x, z + 1), (z + 1) * self.grid_size]
                c = [(x + 1) * self.grid_size, self.get_height(x + 1, z + 1), (z + 1) * self.grid_size]
                d = [(x + 1) * self.grid_size, self.get_height(x + 1, z), z * self.grid_size]
                print("vn", *get_normals(a, b, c), file=outfile)
                print("vn", *get_normals(c, d, a), file=outfile)
            for x, z in f_idxs.keys():
                idx_a = str(idxs[(x, z)]) + "/" + str(idxs[(x, z)]) + "/"
                idx_b = str(idxs[(x, z + 1)]) + "/" + str(idxs[(x, z + 1)]) + "/"
                idx_c = str(idxs[(x + 1, z + 1)]) + "/" + str(idxs[(x + 1, z + 1)]) + "/"
                idx_d = str(idxs[(x + 1, z)]) + "/" + str(idxs[(x + 1, z)]) + "/"
                f_idx_1 = str(f_idxs[(x, z)] * 2 - 1)
                f_idx_2 = str(f_idxs[(x, z)] * 2)
                print("f", idx_a + f_idx_1, idx_b + f_idx_1, idx_c + f_idx_1, file=outfile)
                print("f", idx_c + f_idx_2, idx_d + f_idx_2, idx_a + f_idx_2, file=outfile)
        shutil.copyfile("http_echo/grass.png", self.file_name + ".png")


    def get_mesh_name(self, ):
        return "file:///" + self.file_name

    def onNewPlane(self, data):
        self.height_data = {}
        for x in range(-10, 10):
            for y in range(-10, 10):
                self.height_data[(x, y)] = 10
        self.write_mesh()

    def dist(self, a, b):
        return math.sqrt(sum((i-j)**2 for i, j in zip(a, b)))

    def iter_circle(self, x, z, s):
        for xi in range(int(s / self.grid_size) + 2):
            for zi in range(int(s / self.grid_size) + 2):
                xx = int(x / self.grid_size - s/2 + xi)
                zz = int(z / self.grid_size - s/2 + zi)
                if self.dist([xx, zz], [x / self.grid_size, z / self.grid_size]) <= s:
                    yield xx, zz


    def apply_brush(self, key):
        def smooth(key, val):
            others = [self.height_data[(x, z)] for x, z in self.iter_circle(*key, self.grid_size * 5) if (x, z) in self.height_data and (x, z) != key]
            if len(others) == 0:
                return val
            return val * max(0, 1 - self.brush_strength) + (sum(others) / len(others)) * min(1, self.brush_strength)
        brushes = {
            "raise": lambda key, val: val + self.brush_strength,
            "lower": lambda key, val: val - self.brush_strength,
            "smooth": smooth,
        }
        self.height_data[key] = brushes[self.brush_type](key, self.height_data[key])

    def onBrushStroke(self, data):
        brush_area = set()
        for x, _, z in data[1:]:
            for xx, zz in self.iter_circle(-float(x), float(z), self.brush_size):
                brush_area.add((xx, zz))

        for key in brush_area:
            if not key in self.height_data:
                self.height_data[key] = 10
            self.apply_brush(key)
        self.write_mesh()

    def onSetBrush(self, data):
        self.brush_type = data[1][0].strip()

    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "new_plane": self.onNewPlane,
            "brush_stroke": self.onBrushStroke,
            "set_brush": self.onSetBrush
        }

        if len(data) > 0 and len(data[0]) > 0 and data[0][0] in phonebook:
            phonebook[data[0][0]](data)
