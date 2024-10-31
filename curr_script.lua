function reloadPlane(filename)
    if not (ttstt.plane_object == nil) then
        destroyObject(ttstt.plane_object)
    end

    ttstt.plane_object = spawnObject({
        type = "Custom_Model",
        -- position          = {x=20, y=0, z=0},
        -- rotation          = {x=0, y=180, z=0},
        -- scale             = {x=1, y=1, z=1},
        sound = false
    })
    ttstt.plane_object.setCustomObject({
        mesh = filename .. ".obj",
        collider = filename .. ".obj",
        diffuse = filename .. ".png",
        convex=false,
        material = 3
    })
    ttstt.plane_object.locked = true
end

function actualBrushRadius()
    if ttstt.brush_fade == 0 then
        return ttstt.brush_radius
    else
        return ttstt.brush_radius - math.log((ttstt.brush_strength * 1.01 - 0.01) / 0.01) / math.log(ttstt.brush_fade / 2)
    end
end

function setBrushSize()
    ttstt.brush_obj.setColorTint({r=1, g=1 - ttstt.brush_strength/10, b=1 - ttstt.brush_strength/10, a=0.3})
    ttstt.brush_obj.setScale({x=actualBrushRadius(), y=1, z=actualBrushRadius()})
    ttstt.inner_brush_obj.setScale({x=ttstt.brush_radius, y=1, z=ttstt.brush_radius})
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



function ttsttEnable()
    ttstt.brush_obj = spawnObject({
        type = "go_game_piece_white"
    })
    ttstt.inner_brush_obj = spawnObject({
        type = "go_game_piece_white"
    })
    ttstt.inner_brush_obj.setColorTint({r=1, g=1, b=1, a=0.3})
    ttstt.url = UI.getValue("ttstt_url")
    ttstt.brush_down = false
    ttstt.active = true

    if not (ttstt.plane_object == nil) then
        destroyObject(ttstt.plane_object)
    end

    ttstt.brush_radius = 1
    ttstt.brush_fade = 1
    ttstt.brush_strength = 1

    ttstt.plane_object = nil
    
    WebRequest.put(ttstt.url, "get_ui", function(request)
        if request.is_error then
            log(request.error)
        else
            UI.setXml(request.text)
            Wait.condition(
                function()
                    ttstt.brush_radius = UI.getAttribute("brushSize", "value")
                    ttstt.brush_fade = UI.getAttribute("brushFade", "value")
                    ttstt.brush_strength = UI.getAttribute("brushStrength", "value")
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
    ttstt.plane_object = nil
    ttstt.brush_radius = 1
    ttstt.brush_fade = 1
    ttstt.brush_strength = 1
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

    local log_obj = spawnObject({
        type = "go_game_piece_black",
    })
    ttstt.brush_pos_objs[ttstt.brush_curr_pos_log_idx] = log_obj
    log_obj.locked = true
    log_obj.setPosition(p)
    log_obj.setColorTint({r=0, g=0, b=0, a=0.3})
    log_obj.setScale({x=actualBrushRadius(), y=1, z=actualBrushRadius()})
    log_obj.interactable = false
end

function ttsttUpdate()
    if ttstt.active then
        local p = ttstt.host.getPointerPosition()
        ttstt.brush_obj.setPosition({x=p.x, y=p.y+0.3, z=p.z})
        ttstt.brush_obj.setRotation({x=0, y=0, z=0})
        ttstt.brush_obj.setAngularVelocity({x=0, y=0, z=0})
        ttstt.inner_brush_obj.setPosition(p)
        ttstt.inner_brush_obj.setRotation({x=0, y=0, z=0})
        ttstt.inner_brush_obj.setAngularVelocity({x=0, y=0, z=0})

        if ttstt.brush_down then
            if dist(ttstt.brush_pos_log[ttstt.brush_curr_pos_log_idx], p) >= 1.0 then
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
            destroyObject(ttstt.brush_pos_objs[i])
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