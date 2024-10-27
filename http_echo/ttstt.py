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
    #Calculate the normal for all the triangles, by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle
    # n is now an array of normals per triangle. The length of each normal is dependent the vertices, 
    # we need to normalize these, so that our next step weights each normal equally.
    return normalize_v3(numpy.cross( b - a , c - a ))

class TTSTT:
    def __init__(self):
        self.height_data = {}
        self.counter = 0
        self.file_name = None

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
                print("v", x, y, z, file=outfile)
                idxs[(x, z)] = len(idxs) + 1
            for (x, z), y in self.height_data.items():
                print("vt", x * 0.1, z * 0.1, file=outfile)

            f_idxs = {}
            for (x, z), y in self.height_data.items():
                if (x+1, z) in self.height_data and \
                   (x+1, z+1) in self.height_data and \
                   (x+1, z+1) in self.height_data:
                    f_idxs[(x, z)] = len(f_idxs) + 1
            for x, z in f_idxs.keys():
                a = [x, self.height_data[(x, z)], z]
                b = [x, self.height_data[(x, z + 1)], z + 1]
                c = [x + 1, self.height_data[(x + 1, z + 1)], z + 1]
                d = [x + 1, self.height_data[(x + 1, z)], z]
                print("vn", *get_normals(a, b, c), file=outfile)
                print("vn", *get_normals(c, d, a), file=outfile)
            for x, z in f_idxs.keys():
                idx_a = str(idxs[(x, z)]) + "/" + str(idxs[(x, z)]) + "/"
                idx_b = str(idxs[(x, z + 1)]) + "/" + str(idxs[(x, z + 1)]) + "/"
                idx_c = str(idxs[(x + 1, z + 1)]) + "/" + str(idxs[(x + 1, z + 1)]) + "/"
                idx_d = str(idxs[(x + 1, z)]) + "/" + str(idxs[(x + 1, z)]) + "/"
                print("f", idx_a + str(f_idxs[(x, z)] * 2 - 1), 
                        idx_b + str(f_idxs[(x, z)] * 2 - 1), idx_c + str(f_idxs[(x, z)] * 2 - 1), file=outfile)
                print("f", idx_c + str(f_idxs[(x, z)] * 2), 
                        idx_d + str(f_idxs[(x, z)] * 2), idx_a + str(f_idxs[(x, z)] * 2), file=outfile)
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
        for x, y, z in data[1:]:
            xi = -int(float(x))
            zi = int(float(z))
            if (xi, zi) in self.height_data:
                self.height_data[(xi, zi)] = self.height_data[(xi, zi)] + 1
        self.write_mesh()

    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "new_plane": self.onNewPlane,
            "brush_stroke": self.onBrushStroke
        }

        if len(data) > 0 and len(data[0]) > 0 and data[0][0] in phonebook:
            phonebook[data[0][0]](data)
