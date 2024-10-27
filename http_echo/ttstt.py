from pathlib import Path
import os
import shutil
import numpy

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
        self.counter = 0
        self.file_name = None
        self.brush_size = 3
        self.brush_strength = 1
        self.brush_type = "raise"
        self.grid_size = 1

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
            for (x, z), y in self.height_data.items():
                print("v", x * self.grid_size, y, z * self.grid_size, file=outfile)
                idxs[(x, z)] = len(idxs) + 1
            for (x, z), y in self.height_data.items():
                print("vt", x * 0.1, z * 0.1, file=outfile)

            f_idxs = {}
            for (x, z), y in self.height_data.items():
                if (x+1, z) in self.height_data and \
                   (x+1, z+1) in self.height_data and \
                   (x, z+1) in self.height_data:
                    f_idxs[(x, z)] = len(f_idxs) + 1
            for x, z in f_idxs.keys():
                a = [x * self.grid_size, self.height_data[(x, z)], z * self.grid_size]
                b = [x * self.grid_size, self.height_data[(x, z + 1)], (z + 1) * self.grid_size]
                c = [(x + 1) * self.grid_size, self.height_data[(x + 1, z + 1)], (z + 1) * self.grid_size]
                d = [(x + 1) * self.grid_size, self.height_data[(x + 1, z)], z * self.grid_size]
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

    def onBrushStroke(self, data):
        brush_area = set()
        for x, _, z in data[1:]:
            for xi in range(int(self.brush_size / self.grid_size) + 2):
                for zi in range(int(self.brush_size / self.grid_size) + 2):
                    xx = int(-float(x) / self.grid_size - self.brush_size/2 + xi)
                    zz = int(float(z) / self.grid_size - self.brush_size/2 + zi)
                    brush_area.add((xx, zz))

        for key in brush_area:
            if not key in self.height_data:
                self.height_data[key] = 10
            self.height_data[key] = self.height_data[key] + self.brush_strength
        self.write_mesh()

    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "new_plane": self.onNewPlane,
            "brush_stroke": self.onBrushStroke
        }

        if len(data) > 0 and len(data[0]) > 0 and data[0][0] in phonebook:
            phonebook[data[0][0]](data)
