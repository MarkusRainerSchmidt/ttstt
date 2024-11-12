function splitStr(inputstr, sep)
    if sep == nil then
      sep = "%s"
    end
    local t = {}
    for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
      table.insert(t, str)
    end
    return t
end

function reloadPlane(model_paths)
    for _, plane_object in ipairs(ttstt.plane_objects) do
        destroyObject(plane_object)
    end
    ttstt.plane_objects = {}

    for idx, model_path in ipairs(splitStr(model_paths, "|")) do
        ttstt.plane_objects[idx] = spawnObject({
            type = "Custom_Model",
            -- position          = {x=20, y=0, z=0},
            -- rotation          = {x=0, y=180, z=0},
            -- scale             = {x=1, y=1, z=1},
            sound = false
        })
        ttstt.plane_objects[idx].setCustomObject({
            mesh = model_path .. ".obj",
            collider = model_path .. ".obj",
            diffuse = model_path .. ".png",
            convex=false,
            material = 3
        })
        ttstt.plane_objects[idx].locked = true
    end
end

function onSimple()
    UI.show("ttstt_main")
    UI.hide("ttstt_advanced")
end

function onAdvanced()
    UI.hide("ttstt_main")
    UI.show("ttstt_advanced")
end

function actualBrushRadius()
    if ttstt.brush_fade == 0 then
        return ttstt.brush_radius
    else
        return ttstt.brush_radius - math.log((ttstt.brush_strength * 1.01 - 0.01) / 0.01) / math.log(ttstt.brush_fade / 2)
    end
end

function setBrushSize()
    ttstt.inner_brush_obj.setColorTint({r=1, g=1 - ttstt.brush_strength/10, b=1 - ttstt.brush_strength/10, a=0.3})
    ttstt.brush_obj.setScale({x=actualBrushRadius() * 2, y=1, z=actualBrushRadius() * 2})
    ttstt.inner_brush_obj.setScale({x=ttstt.brush_radius * 2, y=1, z=ttstt.brush_radius * 2})
end

function onBrushRadius(player, value, id)
    WebRequest.put(ttstt.url, "set_brush_radius\n" .. tostring(value))
    ttstt.brush_radius = value
    setBrushSize()
end

function onBrushStrength(player, value, id)
    WebRequest.put(ttstt.url, "set_brush_strength\n" .. tostring(value))
    ttstt.brush_strength = value
    setBrushSize()
end

function onBrushFade(player, value, id)
    WebRequest.put(ttstt.url, "set_brush_fade_strength\n" .. tostring(value))
    ttstt.brush_fade = value
    setBrushSize()
end

function onBrushType(player, option, id)
    if option then
        WebRequest.put(ttstt.url, "set_brush\n" .. id)
    end
end

function onTexScaleSlide(player, value, id)
    ttstt.tex_scale_slie = value
end

function onTexScale(player, option, id)
    WebRequest.put(ttstt.url, "set_tex_scale\n" .. tostring(ttstt.tex_scale_slie), function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function onGridScaleSlide(player, value, id)
    ttstt.grid_Scale_slide = value
end

function onGridScale(player, option, id)
    WebRequest.put(ttstt.url, "set_grid_scale\n" .. tostring(ttstt.grid_Scale_slide), function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function onGridHeightSlide(player, value, id)
    ttstt.grid_height_slide = value
end

function onGridHeight(player, option, id)
    WebRequest.put(ttstt.url, "set_grid_height\n" .. tostring(ttstt.grid_height_slide), function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function onEditTexResSlide(player, value, id)
    ttstt.grid_edit_tex_res = value
end

function onEditTexRes(player, option, id)
    WebRequest.put(ttstt.url, "set_edit_tex_res\n" .. tostring(ttstt.grid_edit_tex_res), function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function onExportTexResSlide(player, value, id)
    ttstt.export_tex_res = value
    WebRequest.put(ttstt.url, "set_export_tex_res\n" .. tostring(ttstt.export_tex_res))
end

function onBrushSampleDistSlide(player, value, id)
    ttstt.brush_sample_dist = tonumber(value)
    WebRequest.put(ttstt.url, "set_brush_sample_dist\n" .. tostring(ttstt.brush_sample_dist))
end

function onUndo(player, option, id)
    WebRequest.put(ttstt.url, "undo", function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function onRedo(player, option, id)
    WebRequest.put(ttstt.url, "redo", function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function sendID(player, option, id)
    printToAll(id)
    WebRequest.put(ttstt.url, id)
end

function onLoadButton(player, option, id)
    WebRequest.put(ttstt.url, "load", function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
end

function spawnBrush()
    if not ttstt.brush_obj == nil then
        destroyObject(ttstt.brush_obj)
    end
    if not ttstt.inner_brush_obj == nil then
        destroyObject(ttstt.inner_brush_obj)
    end

    ttstt.brush_obj = spawnObject({
        type = "go_game_piece_white"
    })
    ttstt.inner_brush_obj = spawnObject({
        type = "go_game_piece_white"
    })
    ttstt.brush_obj.setColorTint({r=1, g=1, b=1, a=0.1})
    ttstt.brush_down = false
    setBrushSize()
end


function ttsttEnable()
    ttstt.brush_radius = 1
    ttstt.brush_fade = 1
    ttstt.brush_strength = 1
    spawnBrush()
    ttstt.url = UI.getValue("ttstt_url")
    ttstt.active = true
    ttstt.fetching_tex_scale = false

    for _, plane_object in ipairs(ttstt.plane_objects) do
        destroyObject(plane_object)
    end
    ttstt.plane_objects = {}
    
    WebRequest.put(ttstt.url, "get_ui", function(request)
        if request.is_error then
            log(request.error)
            ttsttDisable()
        else
            UI.setXml(request.text)
            Wait.condition(
                function()
                    ttstt.brush_radius = tonumber(UI.getAttribute("brushSize", "value"))
                    ttstt.brush_fade = tonumber(UI.getAttribute("brushFade", "value"))
                    ttstt.brush_strength = tonumber(UI.getAttribute("brushStrength", "value"))
                    ttstt.tex_scale_slie = tonumber(UI.getAttribute("textScale", "value"))
                    ttstt.grid_Scale_slide = tonumber(UI.getAttribute("gridScale", "value"))
                    ttstt.grid_height_slide = tonumber(UI.getAttribute("gridHeight", "value"))
                    ttstt.grid_edit_tex_res = tonumber(UI.getAttribute("editTexRes", "value"))
                    ttstt.export_tex_res = tonumber(UI.getAttribute("exportTexRes", "value"))
                    ttstt.brush_sample_dist = tonumber(UI.getAttribute("brushSampleDist", "value"))
                    setBrushSize()
                end,
                function()
                    return not UI.loading
                end
            )
        end
    end)
    WebRequest.put(ttstt.url, "get_plane", function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
    ttstt.brush_curr_pos_log_idx = -1

    UI.hide("ttstt_connect")
end

function ttsttDisable()
    ttstt.active = false
    endBrushStroke()
    destroyObject(ttstt.brush_obj)
    destroyObject(ttstt.inner_brush_obj)
    UI.hide("ttstt_main")
    UI.show("ttstt_connect")
end

function ttsttLoad()
    ttstt = {}
    for _, player in ipairs(Player.getPlayers()) do
        if player.host then
            ttstt.host = player
        end
    end
    ttstt.active = false
    ttstt.plane_objects = {}
    ttstt.brush_radius = 1
    ttstt.brush_fade = 1
    ttstt.brush_strength = 1
    ttstt.tex_scale_slie = 1
    ttstt.grid_Scale_slide = 1
    ttstt.grid_height_slide = 1
    ttstt.grid_edit_tex_res = 1
    ttstt.export_tex_res = 1
    ttstt.brush_sample_dist = 1
end

function dist(pos1, pos2)
    return math.sqrt(
        (pos1.x - pos2.x) * (pos1.x - pos2.x) +
        (pos1.y - pos2.y) * (pos1.y - pos2.y) +
        (pos1.z - pos2.z) * (pos1.z - pos2.z)
    )
end

function brushLogPos()
    local p = ttstt.host.getPointerPosition()
    ttstt.brush_curr_pos_log_idx = ttstt.brush_curr_pos_log_idx + 1
    ttstt.brush_pos_log[ttstt.brush_curr_pos_log_idx] = p

    if ttstt.brush_curr_pos_log_idx % 10 == 0 then
        local log_obj = spawnObject({
            type = "go_game_piece_black",
        })
        ttstt.brush_pos_objs[ttstt.brush_curr_pos_log_idx] = log_obj
        log_obj.locked = true
        log_obj.setPosition(p)
        log_obj.setColorTint({r=0, g=0, b=0, a=0.3})
        log_obj.setScale({x=ttstt.brush_radius * 2, y=1, z=ttstt.brush_radius * 2})
        log_obj.interactable = false
    end
end

function ttsttUpdate()
    if ttstt.active then
        if ttstt.brush_obj == nil or ttstt.inner_brush_obj == nil then
            spawnBrush()
        end

        local p = ttstt.host.getPointerPosition()
        ttstt.brush_obj.setPosition({x=p.x, y=p.y+0.3, z=p.z})
        ttstt.brush_obj.setRotation({x=0, y=0, z=0})
        ttstt.brush_obj.setAngularVelocity({x=0, y=0, z=0})
        ttstt.inner_brush_obj.setPosition(p)
        ttstt.inner_brush_obj.setRotation({x=0, y=0, z=0})
        ttstt.inner_brush_obj.setAngularVelocity({x=0, y=0, z=0})

        if ttstt.brush_down then
            if dist(ttstt.brush_pos_log[ttstt.brush_curr_pos_log_idx], p) >= ttstt.brush_sample_dist then
                brushLogPos()
            end
        end
    end
end

function newBrushStroke()
    ttstt.brush_pos_log = {}
    ttstt.brush_pos_objs = {}
    brushLogPos()
end

function endBrushStroke()
    if ttstt.brush_curr_pos_log_idx > -1 then
        ttstt.brush_obj.interactable = false
        ttstt.inner_brush_obj.interactable = false
        local data_to_send = {}
        data_to_send[1] = "brush_stroke"
        -- clean up markers
        for i=0, ttstt.brush_curr_pos_log_idx do
            local p = ttstt.brush_pos_log[i]
            if i % 10 == 0 then
                destroyObject(ttstt.brush_pos_objs[i])
            end
            data_to_send[#data_to_send + 1] = tostring(p.x) .. " " .. tostring(p.y) .. " " .. tostring(p.z)
        end

        -- contact server
        WebRequest.put(ttstt.url, table.concat(data_to_send, "\n"), function(request)
            if request.is_error then
                log(request.error)
                ttstt.brush_obj.interactable = true
                ttstt.inner_brush_obj.interactable = true
            else
                reloadPlane(request.text)
                ttstt.brush_obj.interactable = true
                ttstt.inner_brush_obj.interactable = true
            end
        end)
        ttstt.brush_curr_pos_log_idx = -1
    end
end

function ttsttMouse(object, down)
    if ttstt.active then
        if object == ttstt.brush_obj then
            ttstt.brush_down = down
            if down then
                newBrushStroke()
            else
                endBrushStroke()
            end
        end
    end
end

function onConnect()
    ttsttEnable()
end

function onDisconnect()
    ttsttDisable()
end

function ttsttChat(message)
    if message == "ttstt" then
        if ttstt.active then
            ttsttDisable()
        else
            ttsttEnable()
        end
    end
    if message == "brush raise" then
        WebRequest.put(ttstt.url, "set_brush\nRaise")
    end
    if message == "brush lower" then
        WebRequest.put(ttstt.url, "set_brush\nLower")
    end
    if message == "brush smooth" then
        WebRequest.put(ttstt.url, "set_brush\nSmooth")
    end
    if message == "brush flatten" then
        WebRequest.put(ttstt.url, "set_brush\nFlatten")
    end
    if message == "brush jitter" then
        WebRequest.put(ttstt.url, "set_brush\nJitter")
    end
end


-------------------------------


function onUpdate()
    ttsttUpdate()
end

function onLoad()
    ttsttLoad()
end

function onChat(message, player)
    ttsttChat(message)
end

function onObjectPickUp(colorName, object)
    ttsttMouse(object, true)
end

function onObjectDrop(colorName, object)
    ttsttMouse(object, false)
end