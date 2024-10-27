from pathlib import Path
import os

class TTSTT:
    def __init__(self):
        self.height_data = {}
        self.counter = 0
        self.file_name = None

    def set_filename(self):
        self.file_name = str(os.path.join(Path.cwd(), "http_echo", "test_" + str(self.counter) +".obj"))
        self.counter += 1

    def write_mesh(self):
        if not self.file_name is None and os.path.exists(self.file_name):
            os.remove(self.file_name)
        self.set_filename()
        with open(self.file_name, "w") as outfile:
            print("#Terrain made by ttstt - Tabletop Simulator Terraintool", file=outfile)
            print("o heightmap", file=outfile)

            idxs = {}
            for (x, z), y in self.height_data.items():
                print("v", x, y, z, file=outfile)
                idxs[(x, z)] = len(idxs) + 1
            for (x, z), y in self.height_data.items():
                print("vt 0 0", file=outfile)
            for (x, z), y in self.height_data.items():
                print("vn 0 1 0", file=outfile)
            for (x, z), y in self.height_data.items():
                if (x+1, z) in self.height_data and \
                   (x+1, z+1) in self.height_data and \
                   (x+1, z+1) in self.height_data:
                    idx_a = str(idxs[(x, z)]) + "/1/1"
                    idx_b = str(idxs[(x, z + 1)]) + "/1/1"
                    idx_c = str(idxs[(x + 1, z + 1)]) + "/1/1"
                    idx_d = str(idxs[(x + 1, z)]) + "/1/1"
                    print("f", idx_a, idx_b, idx_c, file=outfile)
                    print("f", idx_c, idx_d, idx_a, file=outfile)


    def get_mesh_name(self, ):
        return "file:///" + self.file_name

    def onNewPlane(self, data):
        self.height_data = {}
        for x in range(0, 20):
            for y in range(0, 20):
                self.height_data[(x, y)] = 10
        self.write_mesh()

    def onBrushStroke(self, data):
        for x, y, z in data[1:]:
            xi = -int(float(x))
            zi = int(float(z))
            if (xi, zi) in self.height_data:
                self.height_data[(xi, zi)] = self.height_data[(xi, zi)] + 10
        self.write_mesh()

    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "new_plane": self.onNewPlane,
            "brush_stroke": self.onBrushStroke
        }

        if len(data) > 0 and len(data[0]) > 0 and data[0][0] in phonebook:
            phonebook[data[0][0]](data)
