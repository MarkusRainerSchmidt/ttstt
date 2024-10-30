from pathlib import Path
import os
import shutil
import numpy
import math
import random

UI_1 = """
<Panel id="ttstt_connect" visibility="Host" active="false" allowDragging="true" returnToOriginalPositionWhenReleased="false" width="300" height="40" color="white">
    <HorizontalLayout>
        <Text width="70">TTsTT</Text>
        <InputField id="ttstt_url">http://127.0.0.1:5000</InputField>
        <Button width="70" onClick="onConnect">Conect</Button>
    </HorizontalLayout>
</Panel>

<Panel id="ttstt_main" allowDragging="true" visibility="Host" returnToOriginalPositionWhenReleased="false" width="500" height="250" color="white">
    <TableLayout columnWidths="100 400" cellSpacing="3">
        <Row>
            <Cell><Text></Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Text width="350">TTsTT</Text>
                    <Button width="50" onClick="onDisconnect">Disconnect</Button>
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row preferredHeight="60">
            <Cell>
                <VerticalLayout>
                    <Text>Brush Type</Text>
                    <Text>Texture Brush</Text>
                </VerticalLayout>
            </Cell>
            <Cell>
                <ToggleGroup>
                    <VerticalLayout>
                        <HorizontalLayout>
                            <ToggleButton id="Raise" onValueChanged="onBrushType" isOn="{}">Raise</ToggleButton>
                            <ToggleButton id="Lower" onValueChanged="onBrushType" isOn="{}">Lower</ToggleButton>
                            <ToggleButton id="Flatten" onValueChanged="onBrushType" isOn="{}">Flatten</ToggleButton>
                            <ToggleButton id="Smooth" onValueChanged="onBrushType" isOn="{}">Smooth</ToggleButton>
                            <ToggleButton id="Jitter" onValueChanged="onBrushType" isOn="{}">Jitter</ToggleButton>
                            <ToggleButton id="Delete" onValueChanged="onBrushType" isOn="{}">Delete</ToggleButton>
                        </HorizontalLayout>
                        <HorizontalLayout>
"""
UI_2 = """
                        </HorizontalLayout>
                    </VerticalLayout>
                </ToggleGroup>
            </Cell>
        </Row>
        <Row>
            <Cell><Text>Brush Radius</Text></Cell>
            <Cell><Slider minValue="0" maxValue="10" value="{}" id="brushSize" onValueChanged="onBrushRadius"/></Cell>
        </Row>
        <Row>
            <Cell><Text>Brush Strength</Text></Cell>
            <Cell><Slider minValue="0.01" maxValue="10" value="{}" id="brushStrength" onValueChanged="onBrushStrength"/></Cell>
        </Row>
        <Row>
            <Cell><Text>Brush Fade</Text></Cell>
            <Cell><Slider minValue="0" maxValue="1" value="{}" id="brushFade" onValueChanged="onBrushFade"/></Cell>
        </Row>
        <Row>
            <Cell></Cell>
            <Cell><HorizontalLayout><Button onClick="onLoad">Load</Button><Button onClick="onSave">Save</Button></HorizontalLayout></Cell>
        </Row>
        <Row>
            <Cell></Cell>
            <Cell><HorizontalLayout><Button onClick="onUndo">Undo</Button><Button onClick="onRedo">Redo</Button></HorizontalLayout></Cell>
        </Row>
    </TableLayout>
</Panel>
"""
TEXTURE_BUTTONS = """
    <ToggleButton onClick="onBrushType" id="{}" isOn="{}">{}</ToggleButton>
"""
# color="#C8C8C8|#FFFFFF|#C8C8C8|rgba(0.78,0.78,0.78,0.5)"

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
        self.brush_radius = 10
        self.brush_strength = 3
        self.brush_fade_strength = 0.5
        self.brush_type = "Raise"
        self.grid_size = 0.5
        tex_search_path = os.path.join(Path.cwd(), "textures")
        self.loaded_textures = [f for f in os.listdir(tex_search_path) if \
                                os.path.isfile(os.path.join(tex_search_path, f)) and \
                                (f.endswith(".png") or f.endswith(".jpg"))]
        self.onNewPlane()


    def get_height(self, x, z, op_idx=None):
        if not (x, z) in self.height_data:
            return 10
        else:
            if op_idx is None:
                op_idx = self.curr_operation_idx

            vals = self.height_data[(x, z)]
            idx = len(vals) - 1
            while idx >= 0 and vals[idx][0] >= op_idx:
                idx -= 1
            if idx < 0 or vals[idx][1] is None:
                return 10
            return vals[idx][1]
    
    def set_height(self, x, z, v):
        if not (x, z) in self.height_data:
            self.height_data[(x, z)] = []
        self.height_data[(x, z)].append((self.curr_operation_idx, v))

    def has_height(self, x, z):
        return (x, z) in self.height_data and not self.height_data[(x, z)][-1][1] is None

    def itr_pos(self):
        for x, z in self.height_data.keys():
            if not self.height_data[(x, z)][-1][1] is None:
                yield x, z

    def set_filename(self):
        self.file_name = str(os.path.join(Path.cwd(), "export", "test_" + str(self.counter)))
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
            for x, z in self.itr_pos():
                if self.has_height(x+1, z) and \
                   self.has_height(x+1, z+1) and \
                   self.has_height(x, z+1):
                    a = [x * self.grid_size, self.get_height(x, z), z * self.grid_size]
                    b = [x * self.grid_size, self.get_height(x, z + 1), (z + 1) * self.grid_size]
                    c = [(x + 1) * self.grid_size, self.get_height(x + 1, z + 1), (z + 1) * self.grid_size]
                    d = [(x + 1) * self.grid_size, self.get_height(x + 1, z), z * self.grid_size]
                    n1 = get_normals(a, b, c)
                    n2 = get_normals(c, d, a)
                    # n1[0] = -n1[0]
                    # n2[0] = -n2[0]
                    print("vn", *n1, file=outfile)
                    print("vn", *n2, file=outfile)
                    f_idxs[(x, z)] = len(f_idxs) + 1
            for x, z in f_idxs.keys():
                idx_a = str(idxs[(x, z)]) + "/" + str(idxs[(x, z)]) + "/"
                idx_b = str(idxs[(x, z + 1)]) + "/" + str(idxs[(x, z + 1)]) + "/"
                idx_c = str(idxs[(x + 1, z + 1)]) + "/" + str(idxs[(x + 1, z + 1)]) + "/"
                idx_d = str(idxs[(x + 1, z)]) + "/" + str(idxs[(x + 1, z)]) + "/"
                f_idx_1 = str(f_idxs[(x, z)] * 2 - 1)
                f_idx_2 = str(f_idxs[(x, z)] * 2)
                print("f", idx_a + f_idx_1, idx_b + f_idx_1, idx_c + f_idx_1, file=outfile)
                print("f", idx_c + f_idx_2, idx_d + f_idx_2, idx_a + f_idx_2, file=outfile)
        shutil.copyfile("textures/grass.png", self.file_name + ".png")


    def get_mesh_name(self):
        return "file:///" + self.file_name

    def onNewPlane(self):
        self.height_data = {}
        for x in range(-10, 10):
            for y in range(-10, 10):
                self.set_height(x, y, 10)
        self.write_mesh()

    def dist(self, a, b):
        return math.sqrt(sum((i-j)**2 for i, j in zip(a, b)))

    def iter_circle(self, x, z, s):
        for xi in range(int(s*2 / self.grid_size) + 2):
            for zi in range(int(s*2 / self.grid_size) + 2):
                xx = int(x / self.grid_size - s + xi)
                zz = int(z / self.grid_size - s + zi)
                if self.dist([xx, zz], [x / self.grid_size, z / self.grid_size]) <= s:
                    yield xx, zz

    def get_brush_strength(self, dist_from_center):
        if self.brush_fade_strength == 0:
            return self.brush_strength if dist_from_center < self.brush_radius else 0
        return (self.brush_strength * 1.01) / ( 1 + (self.brush_fade_strength / 2) ** ( self.brush_radius - dist_from_center ) ) - 0.01

    def get_actual_brush_radius(self):
        if self.brush_fade_strength == 0:
            return self.brush_radius
        return self.brush_radius - math.log( (self.brush_strength * 1.01 - 0.01 ) / 0.01, self.brush_fade_strength / 2)

    def mix(self, a, b, p):
        p = max(0, min(1, p))
        return a * (1 - p) + b * p

    def apply_brush(self, key, data, strength):
        def smooth(key, val):
            others = [self.get_height(x, z) for x, z in self.iter_circle(key[0] * self.grid_size, key[1] * self.grid_size, self.grid_size * 3) if (x, z) != key]
            if len(others) == 0:
                return val
            return self.mix(val, sum(others) / len(others), strength)
        def flatten(key, val):
            start_val = self.get_height(int(-float(data[1][0]) / self.grid_size), 
                                        int(float(data[1][2]) / self.grid_size))
            return self.mix(val, start_val, strength)
        def jitter(key, val):
            return val + (random.random() * 2 - 1) * strength

        def delete(key, val):
            return None
        
        def on_texture(key, val):
            pass

        brushes = {
            "Raise": lambda key, val: val + strength,
            "Lower": lambda key, val: val - strength,
            "Smooth": smooth,
            "Flatten": flatten,
            "Jitter": jitter,
            "Delete": delete,
        }
        for tex in self.loaded_textures:
            brushes[tex] = on_texture
        self.set_height(*key, brushes[self.brush_type](key, self.get_height(*key)))

    def onBrushStroke(self, data):
        brush_strength = {}
        for x, _, z in data[1:]:
            x = -float(x)
            z = float(z)
            for xx, zz in self.iter_circle(x, z, self.get_actual_brush_radius()):
                if (xx, zz) not in brush_strength:
                    brush_strength[(xx, zz)] = 0
                brush_strength[(xx, zz)] = max(brush_strength[(xx, zz)], 
                                               self.get_brush_strength(self.dist((x / self.grid_size, 
                                                                                  z / self.grid_size), (xx, zz))))

        for key, strength in brush_strength.items():
            self.apply_brush(key, data, strength)
        self.curr_operation_idx += 1
        self.write_mesh()

    def onSetBrush(self, data):
        self.brush_type = data[1][0].strip()

    def onSetBrushRadius(self, data):
        self.brush_radius = max(0, float(data[1][0].strip()))

    def onSetBrushStrength(self, data):
        self.brush_strength = max(0, float(data[1][0].strip()))

    def onSetBrushFadeStrength(self, data):
        self.brush_fade_strength = min(1, max(0, float(data[1][0].strip())))

    def onUndo(self, data):
        self.curr_operation_idx -= 1
        self.write_mesh()
    
    def onRedo(self, data):
        self.curr_operation_idx += 1
        self.write_mesh()

    def get_ui(self):
        print("get UI")
        texture_button_layout = ""
        for tex_filename in self.loaded_textures:
            texture_button_layout += TEXTURE_BUTTONS.format(tex_filename, self.brush_type == tex_filename, 
                                                            tex_filename.split(".")[0])
        brush_types = []
        for brush_type in ["Raise", "Lower", "Flatten", "Smooth", "Jitter", "Delete"]:
            brush_types.append(self.brush_type == brush_type)
        return UI_1.format(*brush_types) + texture_button_layout + UI_2.format(self.brush_radius, self.brush_strength, 
                                                          self.brush_fade_strength)


    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "get_plane": lambda x: None,
            "brush_stroke": self.onBrushStroke,
            "set_brush": self.onSetBrush,
            "set_brush_radius": self.onSetBrushRadius,
            "set_brush_strength": self.onSetBrushStrength,
            "set_brush_fade_strength": self.onSetBrushFadeStrength,
            "undo": self.onUndo,
            "redo": self.onRedo,
        }

        if len(data) > 0 and len(data[0]) > 0:
            if data[0][0] in phonebook:
                phonebook[data[0][0]](data)
            if data[0][0] == "get_ui":
                return self.get_ui()

        return self.get_mesh_name()
