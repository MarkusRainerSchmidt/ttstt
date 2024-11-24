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
<Panel id="ttstt_connect" visibility="Host" active="false" allowDragging="true" returnToOriginalPositionWhenReleased="false" width="350" height="40" color="white" rectAlignment="LowerLeft">
    <HorizontalLayout>
        <Text width="70">TTsTT</Text>
        <InputField id="ttstt_url">http://127.0.0.1:5000</InputField>
        <Button width="100" onClick="onConnect">Connect</Button>
    </HorizontalLayout>
</Panel>

<Panel id="ttstt_main" allowDragging="true" visibility="Host" returnToOriginalPositionWhenReleased="false" width="500" height="250" color="white" rectAlignment="LowerLeft">
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
            <Cell>
            </Cell>
            <Cell>
                <HorizontalLayout>
                    <Text id="numObjects">1 Object</Text>
                    <Button onClick="onUndo">Undo</Button>
                    <Button onClick="onAdvanced">Advanced</Button>
                </HorizontalLayout>
                </Cell>
        </Row>
    </TableLayout>
</Panel>


<Panel id="ttstt_advanced" allowDragging="true" visibility="Host" returnToOriginalPositionWhenReleased="false" width="500" height="250" color="white" active="false" rectAlignment="LowerLeft">
    <TableLayout columnWidths="100 400" cellSpacing="3">
        <Row>
            <Cell><Text></Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Text width="350">Advanced</Text>
                    <Button width="50" onClick="onSimple">Back</Button>
                </HorizontalLayout>
            </Cell>
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
            <Cell><Text>Grid Height</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="0.1" width="330" maxValue="10" value="{}" id="gridHeight" onValueChanged="onGridHeightSlide" />
                    <Button onClick="onGridHeight" width="70">Set</Button>
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row>
            <Cell><Text>Edit Tex Res</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="6" width="330" maxValue="14" wholeNumbers="true" value="{}" id="editTexRes" onValueChanged="onEditTexResSlide" />
                    <Button onClick="onEditTexRes" width="70">Set</Button>
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row>
            <Cell><Text>Export Tex Res</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="6" width="330" maxValue="14" wholeNumbers="true" value="{}" id="exportTexRes" onValueChanged="onExportTexResSlide" />
                </HorizontalLayout>
            </Cell>
        </Row>
        <Row>
            <Cell><Text>Brush Sample Dist</Text></Cell>
            <Cell>
                <HorizontalLayout>
                    <Slider minValue="0.01" maxValue="10" value="{}" id="brushSampleDist" onValueChanged="onBrushSampleDistSlide" />
                </HorizontalLayout>
            </Cell>
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

# COLS_AND_ROWS_PER_OBJ = 150
COLS_AND_ROWS_PER_OBJ = 80

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
        self.edit_tex_res = 7
        self.export_tex_res = 10
        self.brush_sample_dist = 0.5
        tex_search_path = os.path.join(Path.cwd(), "textures")
        self.written_meshes = []
        self.has_warned_cannot_delete_file = False
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
            return 0
        else:
            if op_idx is None:
                op_idx = self.curr_operation_idx

            vals = self.height_data[(x, z)]
            idx = len(vals) - 1
            while idx >= 0 and vals[idx][0] >= op_idx:
                idx -= 1
            if idx < 0 or vals[idx][1] is None:
                return 0
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
        self.counter = (self.counter + 1) % 10

    def export_tts(self):
        if not self.file_name is None and os.path.exists(self.file_name + ".obj"):
            os.remove(self.file_name + ".obj")
            os.remove(self.file_name + ".png")
        if not self.file_name is None:
            for sanitized_filename in self.get_mesh_name().split("|"):
                for s in " \\:_./-":
                    sanitized_filename = sanitized_filename.replace(s, "")
                prefix = os.path.join(Path.home(), "Documents", "My Games", "Tabletop Simulator", "Mods")
                for f in [
                    os.path.join(prefix, "Models Raw", sanitized_filename) + "obj.rawm",
                    os.path.join(prefix, "Images Raw", sanitized_filename) + "png.rawt"
                ]:
                    if os.path.exists(f):
                        os.remove(f)
                    else:
                        if not self.has_warned_cannot_delete_file:
                            print("WARNING: could not delete TTS temp file! Maybe you 'Mod Save Location' is not in your Document s folder?", f)
                            self.has_warned_cannot_delete_file = True
        self.set_filename()
        self.write_mesh(self.file_name, 2**self.edit_tex_res)

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



    def write_mesh(self, file_name, res=128):
        min_x = min(x for x, z in self.itr_pos())
        min_z = min(z for x, z in self.itr_pos())
        max_x = max(x for x, z in self.itr_pos())
        max_z = max(z for x, z in self.itr_pos())
        size_x = max_x - min_x
        size_z = max_z - min_z
        self.curr_x_objs = 1 + (size_x - 1) // COLS_AND_ROWS_PER_OBJ
        self.curr_z_objs = 1 + (size_z - 1) // COLS_AND_ROWS_PER_OBJ
        self.written_meshes = []
        for idx_x in range(self.curr_x_objs):
            from_x = min_x + (idx_x * COLS_AND_ROWS_PER_OBJ)
            to_x = from_x + COLS_AND_ROWS_PER_OBJ
            for idx_z in range(self.curr_z_objs):
                from_z = min_z + (idx_z * COLS_AND_ROWS_PER_OBJ)
                to_z = from_z + COLS_AND_ROWS_PER_OBJ
                curr_filename = file_name + "_" + str(idx_x) + "_" + str(idx_z) 
                wrote_sth = False
                with open(curr_filename + ".obj", "w") as outfile:
                    print("#Terrain made by ttstt - Tabletop Simulator Terraintool", file=outfile)
                    print("o heightmap", file=outfile)

                    idxs = {}
                    for x in range(from_x, to_x + 1):
                        for z in range(from_z, to_z + 1):
                            if self.has_height(x, z):
                                y = self.get_height(x, z) * self.grid_height + 10
                                print("v", x * self.grid_size, y, z * self.grid_size, file=outfile)
                                idxs[(x, z)] = len(idxs) + 1
                                wrote_sth = True
                    
                    for x in range(from_x, to_x + 1):
                        for z in range(from_z, to_z + 1):
                            if self.has_height(x, z):
                                print("vt", (x - from_x) / (COLS_AND_ROWS_PER_OBJ + 1),
                                           -(z - from_z) / (COLS_AND_ROWS_PER_OBJ + 1), file=outfile)

                    f_idxs = {}
                    for x in range(from_x, to_x):
                        for z in range(from_z, to_z):
                            if self.has_height(x, z) and \
                            self.has_height(x+1, z) and \
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
                if wrote_sth:
                    self.written_meshes.append(curr_filename)
                data = [
                    [
                        c
                        for x in range(0, res)
                        for c in self.get_color( (COLS_AND_ROWS_PER_OBJ) * (x / res) + from_x,
                                                 (COLS_AND_ROWS_PER_OBJ) * (z / res) + from_z,
                                                 x, z)
                    ] for z in range(0, res)
                ]

                img = png.from_array(data, "RGB")
                img.save(curr_filename + ".png")


    def get_mesh_name(self):
        return "|".join(["file:///" + m for m in self.written_meshes])

    def onNewPlane(self):
        self.height_data = {}
        self.texture_data = {}
        for x in range(-10, 10):
            for y in range(-10, 10):
                self.set_height(x, y, 0)
                self.set_texture(x, y, [1] + [0] * (len(self.loaded_textures) - 1))
        self.curr_operation_idx += 1
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

    def onSetGridHeight(self, data):
        self.grid_height = float(data[1][0].strip())
        self.export_tts()

    def onSetEditTexRes(self, data):
        self.edit_tex_res = int(data[1][0].strip())
        self.export_tts()

    def onSetExportTexRes(self, data):
        self.export_tex_res = int(data[1][0].strip())

    def onSetBrushSampleDist(self, data):
        self.brush_sample_dist = float(data[1][0].strip())

    def onSetBrushRadius(self, data):
        self.brush_radius = max(0, float(data[1][0].strip()))

    def onSetBrushStrength(self, data):
        self.brush_strength = max(0, float(data[1][0].strip()))

    def onSetBrushFadeStrength(self, data):
        self.brush_fade_strength = min(1, max(0, float(data[1][0].strip())))

    def onUndo(self, data):
        self.curr_operation_idx = max(1, self.curr_operation_idx - 1)

        keys = list(self.height_data.keys())
        for key in keys:
            val = self.height_data[key]
            self.height_data[key] = [[t, v] for t, v in val if t < self.curr_operation_idx]
            if len(self.height_data[key]) == 0:
                del self.height_data[key]
        keys = list(self.texture_data.keys())
        for key in keys:
            val = self.texture_data[key]
            self.texture_data[key] = [[t, v] for t, v in val if t < self.curr_operation_idx]
            if len(self.texture_data[key]) == 0:
                del self.texture_data[key]

        self.export_tts()
    
    # def onRedo(self, data):
    #     self.curr_operation_idx += 1
    #     self.export_tts()

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
                                                          self.brush_fade_strength, self.image_scale, self.grid_size,
                                                          self.grid_height, self.edit_tex_res, self.export_tex_res,
                                                          self.brush_sample_dist)

    def onLoad(self, data):
        print("on load")
        path = easygui.fileopenbox(default="*.json")
        if path is None:
            print("aborted")
            return
        with open(path) as f:
            j = json.load(f)
            self.curr_operation_idx = j["curr_operation_idx"]
            new_loaded_textures = j["loaded_textures"]
            self.height_data = {(k0, k1): v for k0, k1, v in j["height_data"]}
            self.texture_data = {(k0, k1): v for k0, k1, v in j["texture_data"]}

            loaded_tex_idx = {}
            for idx, f in enumerate(self.loaded_textures):
                loaded_tex_idx[f] = idx
            translate_format = {
                idx: loaded_tex_idx[f] for idx, f in enumerate(new_loaded_textures) if f in loaded_tex_idx
            }

            for key in self.texture_data.keys():
                for idx, (timepoint, vx) in enumerate(self.texture_data[key]):
                    new_data = [0] * len(self.loaded_textures)
                    for jdx, v in enumerate(vx):
                        if jdx in translate_format:
                            new_data[translate_format[jdx]] = v
                    self.texture_data[key][idx][1] = new_data

        self.export_tts()
        print("done")

    def onSave(self, data):
        print("on save")
        path = easygui.filesavebox(default="*.json")
        if path is None:
            print("aborted")
            return
        with open(path, "w") as f:
            json.dump({
             "curr_operation_idx": self.curr_operation_idx,
             "loaded_textures": self.loaded_textures,
             "height_data": [[k[0], k[1], v]for k, v in self.height_data.items()],
             "texture_data": [[k[0], k[1], v] for k, v in self.texture_data.items()]
            }, f)
        print("done")

    def onExport(self, data):
        print("on export")
        path = easygui.filesavebox()
        if path is None:
            print("aborted")
            return
        self.write_mesh(path.split(".")[0], 2**self.export_tex_res)
        print("done")

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
            "set_grid_height": self.onSetGridHeight,
            "set_edit_tex_res": self.onSetEditTexRes,
            "set_export_tex_res": self.onSetExportTexRes,
            "set_brush_sample_dist": self.onSetBrushSampleDist,
            "undo": self.onUndo,
            # "redo": self.onRedo,
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
