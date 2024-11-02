from pathlib import Path
import os
import shutil
import numpy
import math
import random
import easygui
import json
import png

UI_1 = """
<Panel id="ttstt_connect" visibility="Host" active="false" allowDragging="true" returnToOriginalPositionWhenReleased="false" width="350" height="40" color="white">
    <HorizontalLayout>
        <Text width="70">TTsTT</Text>
        <InputField id="ttstt_url">http://127.0.0.1:5000</InputField>
        <Button width="100" onClick="onConnect">Connect</Button>
    </HorizontalLayout>
</Panel>

<Panel id="ttstt_main" allowDragging="true" visibility="Host" returnToOriginalPositionWhenReleased="false" width="500" height="280" color="white">
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
            <Cell><Slider minValue="0.01" maxValue="1" value="{}" id="brushStrength" onValueChanged="onBrushStrength"/></Cell>
        </Row>
        <Row>
            <Cell><Text>Brush Fade</Text></Cell>
            <Cell><Slider minValue="0" maxValue="1" value="{}" id="brushFade" onValueChanged="onBrushFade"/></Cell>
        </Row>
        <Row>
            <Cell><Text>Tex Scale</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="1" width="330" maxValue="100" value="{}" id="textScale" onValueChanged="onTexScaleSlide" />
                    <Button onClick="onTexScale" width="70">Set</Button>
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row>
            <Cell><Text>Grid Scale</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="0.1" width="330" maxValue="2" value="{}" id="gridScale" onValueChanged="onGridScaleSlide" />
                    <Button onClick="onGridScale" width="70">Set</Button>
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row>
            <Cell></Cell>
            <Cell>
                <HorizontalLayout>
                    <Button onClick="onLoadButton">Load</Button>
                    <Button onClick="sendID" id="save">Save</Button>
                    <Button onClick="sendID" id="export">Export</Button>
                </HorizontalLayout>
            </Cell>
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
        self.texture_data = {}
        self.curr_operation_idx = 0
        self.counter = 0
        self.file_name = None
        self.brush_radius = 5
        self.brush_strength = 1
        self.grid_height = 3
        self.brush_fade_strength = 0.5
        self.brush_type = "Raise"
        self.grid_size = 0.5
        self.image_scale = 10
        tex_search_path = os.path.join(Path.cwd(), "textures")
        self.loaded_textures = [f for f in os.listdir(tex_search_path) if \
                                os.path.isfile(os.path.join(tex_search_path, f)) and \
                                (f.endswith(".png") or f.endswith(".jpg"))]
        self.tex_data = []
        for f in self.loaded_textures:
            print("loading", f)
            self.tex_data.append(png.Reader(filename=os.path.join(tex_search_path, f)).read_flat())
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
    
    def get_texture(self, x, z, op_idx=None):
        default_v = [1] + [0] * (len(self.loaded_textures) - 1)
        if not (x, z) in self.texture_data:
            return default_v
        else:
            if op_idx is None:
                op_idx = self.curr_operation_idx

            vals = self.texture_data[(x, z)]
            idx = len(vals) - 1
            while idx >= 0 and vals[idx][0] >= op_idx:
                idx -= 1
            if idx < 0 or vals[idx][1] is None:
                return default_v
            return vals[idx][1]

    def set_texture(self, x, z, v):
        if not (x, z) in self.texture_data:
            self.texture_data[(x, z)] = []
        self.texture_data[(x, z)].append([self.curr_operation_idx, v])

    def set_height(self, x, z, v):
        if not (x, z) in self.height_data:
            self.height_data[(x, z)] = []
        self.height_data[(x, z)].append([self.curr_operation_idx, v])

    def has_height(self, x, z):
        return (x, z) in self.height_data and not self.height_data[(x, z)][-1][1] is None

    def itr_pos(self):
        for x, z in self.height_data.keys():
            if not self.height_data[(x, z)][-1][1] is None:
                yield x, z

    def set_filename(self):
        self.file_name = str(os.path.join(Path.cwd(), "export", "tmp_export_" + str(self.counter)))
        self.counter += 1

    def export_tts(self):
        if not self.file_name is None and os.path.exists(self.file_name + ".obj"):
            os.remove(self.file_name + ".obj")
            os.remove(self.file_name + ".png")
        self.set_filename()
        self.write_mesh(self.file_name)

    def extract_color(self, x, z, img):
        x *= self.image_scale
        z *= self.image_scale
        x = int(x) % int(img[0])
        z = int(z) % int(img[1])

        idx = (x + z * img[0]) * 3
        return img[2][idx:idx+3]

    def get_color(self, x, z, xx, zz, op_idx=None):
        ts1 = [
            self.get_texture(int(math.floor(x)), int(math.floor(z)), op_idx),
            self.get_texture(int(math.floor(x)) + 1, int(math.floor(z)), op_idx),
            self.get_texture(int(math.floor(x)), int(math.floor(z)) + 1, op_idx),
            self.get_texture(int(math.floor(x)) + 1, int(math.floor(z)) + 1, op_idx)
        ]
        dist_ts = [
            (1**0.5)-self.dist((x, z), (int(math.floor(x)), int(math.floor(z)))),
            (1**0.5)-self.dist((x, z), (int(math.floor(x))+1, int(math.floor(z)))),
            (1**0.5)-self.dist((x, z), (int(math.floor(x)), int(math.floor(z))+1)),
            (1**0.5)-self.dist((x, z), (int(math.floor(x))+1, int(math.floor(z))+1)),
        ]
        tot_dist = sum(dist_ts)
        for i in range(len(dist_ts)):
            dist_ts[i] /= tot_dist

        ts = [
            sum(ts1[i][j] * dist_ts[i] for i in range(len(dist_ts))) for j in range(len(ts1[0]))
        ]

        colors = [
            self.extract_color(x, z, img) for img in self.tex_data
        ]

        return [
            max(0, min(255, int(sum(c[i] * t for c, t in zip(colors, ts)))))
            for i in range(3)
        ]



    def write_mesh(self, file_name, res=128*4):
        with open(file_name + ".obj", "w") as outfile:
            print("#Terrain made by ttstt - Tabletop Simulator Terraintool", file=outfile)
            print("o heightmap", file=outfile)

            idxs = {}
            for (x, z) in self.itr_pos():
                y = self.get_height(x, z) * self.grid_height
                print("v", x * self.grid_size, y, z * self.grid_size, file=outfile)
                idxs[(x, z)] = len(idxs) + 1
            min_x = min(x for x, z in self.itr_pos())
            min_z = min(z for x, z in self.itr_pos())
            max_x = max(x for x, z in self.itr_pos())
            max_z = max(z for x, z in self.itr_pos())
            for (x, z) in self.itr_pos():
                print("vt", (x - min_x) / (max_x - min_x), -(z - min_z) / (max_z - min_z), file=outfile)

            f_idxs = {}
            for x, z in self.itr_pos():
                if self.has_height(x+1, z) and \
                   self.has_height(x+1, z+1) and \
                   self.has_height(x, z+1):
                    a = [x * self.grid_size, self.get_height(x, z) * self.grid_height, z * self.grid_size]
                    b = [x * self.grid_size, self.get_height(x, z + 1) * self.grid_height, 
                         (z + 1) * self.grid_size]
                    c = [(x + 1) * self.grid_size, self.get_height(x + 1, z + 1) * self.grid_height, 
                         (z + 1) * self.grid_size]
                    d = [(x + 1) * self.grid_size, self.get_height(x + 1, z) * self.grid_height, 
                         z * self.grid_size]
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
        
        data = [
            [
                c
                for x in range(0, res)
                for c in self.get_color( (max_x-min_x) * (x / res) + min_x, (max_z - min_z) * (z / res) + min_z, x, z)
            ] for z in range(0, res)
        ]

        img = png.from_array(data, "RGB")
        img.save(file_name + ".png")


    def get_mesh_name(self):
        return "file:///" + self.file_name

    def onNewPlane(self):
        self.height_data = {}
        self.texture_data = {}
        for x in range(-10, 10):
            for y in range(-10, 10):
                self.set_height(x, y, 10)
                self.set_texture(x, y, [1] + [0] * (len(self.loaded_textures) - 1))
        self.export_tts()

    def dist(self, a, b):
        return math.sqrt(sum((i-j)**2 for i, j in zip(a, b)))

    def iter_circle(self, x, z, s):
        for xi in range(int(s*2) + 2):
            for zi in range(int(s*2) + 2):
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
            others = [self.get_height(x, z) for x, z in self.iter_circle(key[0] * self.grid_size, 
                                                                         key[1] * self.grid_size, 
                                                                         3 / self.grid_size) if (x, z) != key]
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
            t = self.get_texture(*key)
            for i, n in enumerate(self.loaded_textures):
                if n == self.brush_type:
                    t[i] = min(1, strength + t[i])
                else:
                    t[i] = max(0, t[i] - strength)
            self.set_texture(*key, t)
            return val

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
            for xx, zz in self.iter_circle(x, z, self.get_actual_brush_radius()/ self.grid_size):
                if (xx, zz) not in brush_strength:
                    brush_strength[(xx, zz)] = 0
                brush_strength[(xx, zz)] = max(brush_strength[(xx, zz)], 
                                          self.get_brush_strength(self.dist((x / self.grid_size, z / self.grid_size), 
                                                                            (xx, zz)) * self.grid_size))

        for key, strength in brush_strength.items():
            self.apply_brush(key, data, strength)
        self.curr_operation_idx += 1
        self.export_tts()

    def onSetBrush(self, data):
        self.brush_type = data[1][0].strip()

    def onSetTexScale(self, data):
        self.image_scale = float(data[1][0].strip())
        self.export_tts()

    def onSetGridScale(self, data):
        self.grid_size = float(data[1][0].strip())
        self.export_tts()

    def onSetBrushRadius(self, data):
        self.brush_radius = max(0, float(data[1][0].strip()))

    def onSetBrushStrength(self, data):
        self.brush_strength = max(0, float(data[1][0].strip()))

    def onSetBrushFadeStrength(self, data):
        self.brush_fade_strength = min(1, max(0, float(data[1][0].strip())))

    def onUndo(self, data):
        self.curr_operation_idx -= 1
        self.export_tts()
    
    def onRedo(self, data):
        self.curr_operation_idx += 1
        self.export_tts()

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
                                                          self.brush_fade_strength, self.image_scale, self.grid_size)

    def onLoad(self, data):
        print("on load")
        path = easygui.fileopenbox(default="*.json")
        if path is None:
            return
        with open(path) as f:
            j = json.load(f)
            self.curr_operation_idx = j["curr_operation_idx"]
            self.height_data = {(k0, k1): v for k0, k1, v in j["height_data"]}
            self.texture_data = {(k0, k1): v for k0, k1, v in j["texture_data"]}
        self.export_tts()

    def onSave(self, data):
        print("on save")
        path = easygui.filesavebox(default="*.json")
        if path is None:
            return
        with open(path, "w") as f:
            json.dump({
             "curr_operation_idx": self.curr_operation_idx,
             "height_data": [[k[0], k[1], v]for k, v in self.height_data.items()],
             "texture_data": [[k[0], k[1], v]for k, v in self.texture_data.items()]
            }, f)

    def onExport(self, data):
        print("on export")
        path = easygui.filesavebox()
        if path is None:
            return
        self.write_mesh(path.split(".")[0], 2048)

    def onRequest(self, request):
        data = [row.split() for row in request.decode().split("\n")]

        phonebook = {
            "get_plane": lambda x: None,
            "brush_stroke": self.onBrushStroke,
            "set_brush": self.onSetBrush,
            "set_brush_radius": self.onSetBrushRadius,
            "set_brush_strength": self.onSetBrushStrength,
            "set_brush_fade_strength": self.onSetBrushFadeStrength,
            "set_tex_scale": self.onSetTexScale,
            "set_grid_scale": self.onSetGridScale,
            "undo": self.onUndo,
            "redo": self.onRedo,
            "load": self.onLoad,
            "save": self.onSave,
            "export": self.onExport,
        }

        if len(data) > 0 and len(data[0]) > 0:
            if data[0][0] in phonebook:
                phonebook[data[0][0]](data)
            if data[0][0] == "get_ui":
                return self.get_ui()

        return self.get_mesh_name()
