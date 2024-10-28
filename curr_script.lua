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
        diffuse = filename .. ".png",
        material = 3
    })
    ttstt.plane_object.locked = true
end


function ttsttEnable()
    ttstt.brush_obj = spawnObject({
        type = "go_game_piece_white",
    })
    ttstt.brush_down = false
    ttstt.active = true

    ttstt.plane_object = nil

    WebRequest.put("http://127.0.0.1:5000", "new_plane", function(request)
        if request.is_error then
            log(request.error)
        else
            reloadPlane(request.text)
        end
    end)
    ttstt.brush_curr_pos_log_idx = -1
end

function ttsttDisable()
    ttstt.active = false
    endBrushStroke()
    destroyObject(ttstt.brush_obj)
    destroyObject(ttstt.plane_object)
end

function ttsttLoad()
    ttstt = {}
    for _, player in ipairs(Player.getPlayers()) do
        if player.host then
            ttstt.host = player
        end
    end
    ttstt.active = false
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
end

function ttsttUpdate()
    if ttstt.active then
        local p = ttstt.host.getPointerPosition()
        ttstt.brush_obj.setPosition(p)

        if ttstt.brush_down then
            -- printToAll(tostring(p.x) .. " " .. tostring(p.y) .. " " .. tostring(p.z))
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
        local data_to_send = {}
        data_to_send[1] = "brush_stroke"
        -- clean up markers
        for i=0, ttstt.brush_curr_pos_log_idx do
            local p = ttstt.brush_pos_log[i]
            destroyObject(ttstt.brush_pos_objs[i])
            data_to_send[#data_to_send + 1] = tostring(p.x) .. " " .. tostring(p.y) .. " " .. tostring(p.z)
        end

        -- contact server
        WebRequest.put("http://127.0.0.1:5000", table.concat(data_to_send, "\n"), function(request)
            if request.is_error then
                log(request.error)
            else
                reloadPlane(request.text)
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

function ttsttChat(message)
    if message == "ttstt" then
        if ttstt.active then
            ttsttDisable()
        else
            ttsttEnable()
        end
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