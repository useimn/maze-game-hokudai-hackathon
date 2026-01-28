from random import choice, randint
from math import sqrt, atan2
import textwrap

# === グローバル変数 ===
playerX, playerY = 0.0, 0.0
playerSpeed = 3
playerSize = 20
playerVX, playerVY = 0.0, 0.0
friction = 0.95
acceleration = 0.5

slip_areas = []

goalX, goalY = 0.0, 0.0
goalSize = 50

startTime = 0
timeLimit = 60000

obstacles, traffic_obstacles, onigiri_list, bicycle_list, child_obstacles, flashlight_list, bug_enemies = [], [], [], [], [], [], []

# ゲーム状態
is_speed_boosted, boost_timer, has_flashlight, isInverted = False, 0, False, False
BOOST_DURATION = 300
current_mode = ""
traffic_spawn_timer, cars_in_a_row, gap_duration, spawn_counter = 0, 14, 120, 0
gate_is_closed = True
gameState = "MENU"
backgroundColor = 100
apology_text = ""
result_message = ""
result_color = None

# 三限/夜モード専用変数
sunX, sunY, sunSize, sunSpeed = -100, -100, 60, 0
sun_is_active, player_is_frozen, distance_traveled, unfreeze_input = False, False, 0.0, ""

# BugEnemy関連の変数
frozen_by_bug = False
bug_freeze_counter = 0
required_k_count = 10

# メニューボタン
period1_button = {'x': 200, 'y': 250, 'w': 200, 'h': 100, 'label': '1st Period'}
period3_button = {'x': 500, 'y': 250, 'w': 200, 'h': 100, 'label': '3rd Period'}
night_button = {'x': 800, 'y': 250, 'w': 200, 'h': 100, 'label': 'Night'}

grid_spacing, path_width, path_area_start_x = 50, 15, 0
new_path_x, top_path_y = 100, 0
new_complex_path = [
    (50, 260), (220, 260), (270, 250), (340, 250),
    (380, 300), (380, 340), (460, 340), (480, 360)
]

# --- Class Definitions ---

class BugEnemy:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.speed = speed
        self.size = 25
        self.hit = False
        self.color = color(150, 50, 200)

    def move(self):
        if player_is_frozen: return
        dx, dy = playerX - self.x, playerY - self.y
        distance = sqrt(dx**2 + dy**2)
        if distance > 0:
            vx = (dx / distance) * self.speed
            vy = (dy / distance) * self.speed
            self.x += vx
            self.y += vy

    def draw(self):
        fill(self.color)
        ellipse(self.x, self.y, self.size, self.size)
        fill(255)
        ellipse(self.x - 5, self.y - 5, 5, 5)
        ellipse(self.x + 5, self.y - 5, 5, 5)

class Flashlight:
    def __init__(self, x, y):
        self.x, self.y, self.size, self.is_taken = x, y, 30, False
    def draw(self):
        if not self.is_taken:
            fill(180); rectMode(CENTER)
            rect(self.x, self.y, 15, self.size)
            fill(255, 255, 0)
            ellipse(self.x, self.y - self.size/2, 20, 20)

class Child:
    def __init__(self, gx, gy, speed):
        self.gx, self.gy = gx, gy
        self.x = path_area_start_x + gx * grid_spacing
        self.y = gy * grid_spacing
        self.size, self.speed = 25, speed
        self.targetX, self.targetY = self.x, self.y
        self.hit = False

    def findNewTarget(self):
        options = [(self.gx + 1, self.gy), (self.gx - 1, self.gy), (self.gx, self.gy + 1), (self.gx, self.gy - 1)]
        valid_options = []
        max_gx, max_gy = int((width - path_area_start_x) / grid_spacing), int(height / grid_spacing)
        for gx, gy in options:
            if 0 <= gx <= max_gx and 0 <= gy <= max_gy: valid_options.append((gx, gy))
        if valid_options:
            self.gx, self.gy = choice(valid_options)
            self.targetX, self.targetY = path_area_start_x + self.gx * grid_spacing, self.gy * grid_spacing

    def move(self):
        if abs(self.x - self.targetX) < self.speed and abs(self.y - self.targetY) < self.speed:
            self.x = self.targetX
            self.y = self.targetY
            self.findNewTarget()

        if abs(self.x - self.targetX) >= self.speed:
            if self.x < self.targetX: self.x += self.speed
            else: self.x -= self.speed
        elif abs(self.y - self.targetY) >= self.speed:
            if self.y < self.targetY: self.y += self.speed
            else: self.y -= self.speed

    def draw(self):
        if has_flashlight:
            fill(255, 180, 200); ellipse(self.x, self.y - 10, self.size-5, self.size-5)
            rectMode(CENTER); rect(self.x, self.y + 10, 15, 20)

class Bicycle:
    def __init__(self, x, y):
        self.x, self.y, self.size, self.is_taken = x, y, 30, False
    def draw(self):
        if not self.is_taken:
            fill(200); stroke(50); strokeWeight(2)
            ellipse(self.x-self.size/2, self.y, self.size/1.5, self.size/1.5); ellipse(self.x+self.size/2, self.y, self.size/1.5, self.size/1.5)
            line(self.x, self.y-self.size/2, self.x-self.size/2, self.y); line(self.x, self.y-self.size/2, self.x+self.size/2, self.y)
            noStroke()

class Onigiri:
    def __init__(self, x, y):
        self.x, self.y, self.size, self.is_collected = x, y, 30, False
    def draw(self):
        if not self.is_collected:
            fill(255); triangle(self.x, self.y-self.size/2, self.x-self.size/2, self.y+self.size/2, self.x+self.size/2, self.y+self.size/2)
            fill(0); rectMode(CENTER); rect(self.x, self.y+self.size/4, self.size/1.5, self.size/3)

class PathCar:
    def __init__(self, waypoints, speed, w, h, loops=False):
        self.waypoints, self.speed, self.w, self.h = waypoints, speed, w, h
        self.size, self.hit = max(w, h), False
        if self.waypoints:
            self.x, self.y = self.waypoints[0]
        else:
            self.x, self.y = 0, 0
        self.target_index, self.angle = 1, 0
        self.loops = loops

    def move(self):
        if not self.waypoints or self.target_index >= len(self.waypoints):
            if self.loops and self.waypoints:
                self.target_index = 0
            else:
                return
        
        target_x, target_y = self.waypoints[self.target_index]
        dx, dy = target_x - self.x, target_y - self.y
        distance = sqrt(dx**2 + dy**2)

        if distance < self.speed:
            self.x, self.y = target_x, target_y
            self.target_index += 1
        else:
            self.angle = atan2(dy, dx)
            vx = (dx / distance) * self.speed
            vy = (dy / distance) * self.speed
            self.x += vx
            self.y += vy
            
    def draw(self):
        pushMatrix(); translate(self.x, self.y); rotate(self.angle)
        rectMode(CENTER)
        fill(200, 50, 50); rect(0, 0, self.w, self.h)
        fill(50, 100, 200); rect(self.w * 0.1, 0, self.w * 0.4, self.h * 0.9)
        popMatrix()

def generate_random_grid_path(start_gx, start_gy, steps):
    path_points = []
    gx, gy = start_gx, start_gy
    max_gx, max_gy = int((width - path_area_start_x) / grid_spacing), int(height / grid_spacing)
    px, py = path_area_start_x + gx * grid_spacing, gy * grid_spacing
    path_points.append((px, py))
    last_move = None
    for _ in range(steps):
        if last_move and random(10) > 3:
            move_direction = last_move
        else:
            move_direction = choice(['x', 'y'])
        if move_direction == 'x':
            next_gx = gx + choice([-1, 1])
            if not (0 <= next_gx <= max_gx): next_gx = gx - (next_gx - gx)
            gx, last_move = next_gx, 'x'
        else:
            next_gy = gy + choice([-1, 1])
            if not (0 <= next_gy <= max_gy): next_gy = gy - (next_gy - gy)
            gy, last_move = next_gy, 'y'
        px, py = path_area_start_x + gx * grid_spacing, gy * grid_spacing
        path_points.append((px, py))
    if path_points and len(path_points) > 1:
        path_points.append(path_points[0])
    return path_points

def setup():
    global path_area_start_x, new_path_x, top_path_y
    size(1200, 600)
    noStroke(); textAlign(CENTER, CENTER); textSize(32)
    path_area_start_x = 2 * width / 5.0
    new_path_x, top_path_y = 100, 50

def get_random_grid_point():
    max_gx = int((width - path_area_start_x) / grid_spacing)
    max_gy = int(height / grid_spacing) -1
    return (int(random(max_gx)), int(random(max_gy)))

def startGame(mode):
    global playerX, playerY, goalX, goalY, startTime, obstacles, timeLimit, gameState, backgroundColor, current_mode
    global traffic_obstacles, onigiri_list, bicycle_list, gate_is_closed, traffic_spawn_timer, spawn_counter
    global sunX, sunY, sunSpeed, sun_is_active, player_is_frozen, distance_traveled, unfreeze_input, is_speed_boosted, boost_timer, child_obstacles, flashlight_list, has_flashlight, slip_areas, isInverted
    global bug_enemies, frozen_by_bug, bug_freeze_counter

    current_mode = mode
    obstacles, traffic_obstacles, onigiri_list, bicycle_list, child_obstacles, flashlight_list, slip_areas, bug_enemies = [], [], [], [], [], [], [], []
    playerX, playerY, goalX, goalY = width - 25, height - 25, 50, 50
    timeLimit = 60000; backgroundColor = 100
    
    sun_is_active, player_is_frozen, gate_is_closed = False, False, False
    is_speed_boosted, boost_timer, has_flashlight, isInverted = False, 0, False, False
    distance_traveled, unfreeze_input = 0.0, ""
    frozen_by_bug = False
    bug_freeze_counter = 0
    
    slip_areas.append({'x': path_area_start_x + grid_spacing * 1, 'y': grid_spacing * 4, 'w': grid_spacing * 3, 'h': grid_spacing * 3})
    slip_areas.append({'x': path_area_start_x + grid_spacing * 8, 'y': grid_spacing * 8, 'w': grid_spacing * 4, 'h': grid_spacing * 2})
    
    obstacles.append(PathCar(generate_random_grid_path(1, 1, 40), 2.0, 40, 25, loops=True))
    obstacles.append(PathCar(generate_random_grid_path(5, 8, 50), 2.5, 40, 25, loops=True))

    for _ in range(2):
        bug_x = randint(0, int(path_area_start_x))
        bug_y = randint(0, height)
        bug_speed = random(0.5, 1.5)
        bug_enemies.append(BugEnemy(bug_x, bug_y, bug_speed))

    for _ in range(3):
        gx, gy = get_random_grid_point()
        bicycle_list.append(Bicycle(path_area_start_x + gx * grid_spacing, gy * grid_spacing))

    if mode == "period1":
        traffic_spawn_timer, spawn_counter = 0, 0
        gate_is_closed = True
        for _ in range(3):
            gx, gy = get_random_grid_point()
            onigiri_list.append(Onigiri(path_area_start_x + gx * grid_spacing, gy * grid_spacing))
    elif mode == "period3":
        sunX, sunY = -100, -100
        sunSpeed = playerSpeed * 0.80
    elif mode == "night":
        backgroundColor = 30
        child_speed = playerSpeed * 0.5
        for i in range(10):
            gx, gy = get_random_grid_point()
            child_obstacles.append(Child(gx, gy, child_speed))
        
        gx_f, gy_f = get_random_grid_point()
        flashlight_list.append(Flashlight(path_area_start_x + gx_f * grid_spacing, gy_f * grid_spacing))

    startTime = millis()
    gameState = "PLAYING"
    loop()

def manageBugs():
    global player_is_frozen, frozen_by_bug
    for bug in bug_enemies:
        bug.move()
        bug.draw()
        if not bug.hit and not player_is_frozen and dist(playerX, playerY, bug.x, bug.y) < playerSize / 2 + bug.size / 2:
            player_is_frozen = True
            frozen_by_bug = True
            bug.hit = True

def manageTraffic():
    global traffic_spawn_timer, spawn_counter, traffic_obstacles
    traffic_spawn_timer -= 1
    if traffic_spawn_timer <= 0:
        if spawn_counter < cars_in_a_row:
            num_lanes = int((width - path_area_start_x) / grid_spacing)
            lane_index = int(random(num_lanes))
            spawn_x = path_area_start_x + lane_index * grid_spacing
            path = [(spawn_x, -50), (spawn_x, height + 50)]
            speed = random(2, 4)
            traffic_obstacles.append(PathCar(path, speed, 40, 25))
            spawn_counter += 1
            traffic_spawn_timer = 20
        else:
            spawn_counter, traffic_spawn_timer = 0, gap_duration
    
    traffic_obstacles = [car for car in traffic_obstacles if car.y <= height + 60]

def manageOnigiri():
    global gate_is_closed
    collected_count = 0
    for o in onigiri_list:
        o.draw()
        if not o.is_collected and dist(playerX, playerY, o.x, o.y) < playerSize/2 + o.size/2:
            o.is_collected = True
        if o.is_collected: collected_count += 1
    if len(onigiri_list) > 0 and collected_count == len(onigiri_list): gate_is_closed = False

def manageSun():
    global sunX, sunY, player_is_frozen, sun_is_active, frozen_by_bug
    if not sun_is_active or player_is_frozen: 
        return
        
    fill(255, 200, 0)
    ellipse(sunX, sunY, sunSize, sunSize)
    
    dx, dy = playerX - sunX, playerY - sunY
    distance = sqrt(dx**2 + dy**2)
    
    if distance > 0:
        vx = (dx / distance) * sunSpeed
        vy = (dy / distance) * sunSpeed
        sunX += vx
        sunY += vy
        
    if dist(playerX, playerY, sunX, sunY) < playerSize / 2 + sunSize / 2:
        player_is_frozen = True
        frozen_by_bug = False 

def manageBicycles():
    global is_speed_boosted, boost_timer
    for bike in bicycle_list:
        bike.draw()
        if not bike.is_taken and dist(playerX, playerY, bike.x, bike.y) < playerSize/2 + bike.size/2:
            bike.is_taken, is_speed_boosted, boost_timer = True, True, BOOST_DURATION

def manageChildren():
    global player_is_frozen, frozen_by_bug
    for child in child_obstacles:
        child.move(); child.draw()
        if not child.hit and not player_is_frozen and dist(playerX, playerY, child.x, child.y) < playerSize/2 + child.size/2:
            player_is_frozen = True
            frozen_by_bug = False
            child.hit = True

def manageFlashlight():
    global has_flashlight, isInverted
    for f in flashlight_list:
        f.draw()
        if not f.is_taken and dist(playerX, playerY, f.x, f.y) < playerSize/2 + f.size/2:
            f.is_taken, has_flashlight, isInverted = True, True, True

def is_on_complex_path(px, py):
    for i in range(len(new_complex_path) - 1):
        x1, y1 = new_complex_path[i]; x2, y2 = new_complex_path[i+1]
        A, B, C = y1 - y2, x2 - x1, x1 * y2 - x2 * y1
        denominator = sqrt(A**2 + B**2)
        if denominator == 0: continue
        distance = abs(A * px + B * py + C) / denominator
        on_segment = False
        if min(x1, x2) - path_width <= px <= max(x1, x2) + path_width and \
           min(y1, y2) - path_width <= py <= max(y1, y2) + path_width: on_segment = True
        if distance < path_width / 2.0 and on_segment: return True
    return False

def is_on_diagonal_path(px, py):
    x1, y1 = 480.0, 240.0; x2, y2 = 240.0, 0.0
    A, B, C = y1 - y2, x2 - x1, x1 * y2 - x2 * y1
    denominator = sqrt(A**2 + B**2)
    if denominator == 0: return False
    distance = abs(A * px + B * py + C) / denominator
    on_segment = False
    if min(x1, x2) - path_width <= px <= max(x1, x2) + path_width and \
       min(y1, y2) - path_width <= py <= max(y1, y2) + path_width: on_segment = True
    return distance < path_width / 2.0 and on_segment


def is_on_path(x, y):
    on_a_path = False
    if (is_on_complex_path(x, y) or is_on_diagonal_path(x, y) or
            (new_path_x - path_width / 2 < x < new_path_x + path_width / 2) or
            (top_path_y - path_width / 2 < y < top_path_y + path_width / 2) or
            (540 - path_width / 2 < y < 540 + path_width / 2 and 50 < x < 480)):
        on_a_path = True
    if x >= path_area_start_x:
        relative_x = x - path_area_start_x
        on_vertical_grid = (relative_x % grid_spacing < path_width / 2 or
                            relative_x % grid_spacing > grid_spacing - path_width / 2)
        on_horizontal_grid = (y % grid_spacing < path_width / 2 or
                              y % grid_spacing > grid_spacing - path_width / 2)
        if on_vertical_grid or on_horizontal_grid:
            on_a_path = True
    if current_mode == "period1" and gate_is_closed and x < path_area_start_x:
        return False
    return on_a_path

def is_on_slip_floor(px, py):
    for area in slip_areas:
        if (area['x'] < px < area['x'] + area['w'] and
            area['y'] < py < area['y'] + area['h']): return True
    return False

def drawMenu():
    background(50, 80, 150)
    pushStyle()
    textAlign(CENTER, CENTER)
    textSize(64); fill(255); text("Late For School", width / 2, 100)
    textSize(32); rectMode(CORNER)
    fill(100, 200, 100); rect(period1_button['x'], period1_button['y'], period1_button['w'], period1_button['h'])
    fill(0); text(period1_button['label'], period1_button['x'] + period1_button['w']/2, period1_button['y'] + period1_button['h']/2)
    fill(200, 200, 100); rect(period3_button['x'], period3_button['y'], period3_button['w'], period3_button['h'])
    fill(0); text(period3_button['label'], period3_button['x'] + period3_button['w']/2, period3_button['y'] + period3_button['h']/2)
    fill(100, 100, 200); rect(night_button['x'], night_button['y'], night_button['w'], night_button['h'])
    fill(255); text(night_button['label'], night_button['x'] + night_button['w']/2, night_button['y'] + night_button['h']/2)
    popStyle()

def drawCryingChildScreen():
    fill(0, 180); rect(0, 0, width, height)
    faceX, faceY, faceSize = width/2, height/2 - 50, 200
    fill(255, 220, 180); ellipse(faceX, faceY, faceSize, faceSize)
    fill(50, 150, 255); ellipse(faceX - 40, faceY + 20, 20, 30); ellipse(faceX + 40, faceY + 20, 20, 30)
    stroke(0); strokeWeight(5)
    line(faceX - 60, faceY, faceX - 20, faceY - 10); line(faceX + 60, faceY, faceX + 20, faceY - 10)
    noStroke(); fill(0); arc(faceX, faceY + 40, 80, 80, 0, PI)
    rescue_word = "rescue"
    pushStyle()
    textAlign(CENTER, CENTER)
    textSize(40); fill(255, 100, 0); text("Type '{}' to escape!".format(rescue_word), width/2, height/2 + 150)
    textSize(32); fill(255); text(unfreeze_input, width/2, height/2 + 200)
    popStyle()

def drawGame():
    global playerX, playerY, playerVX, playerVY, timeLimit, distance_traveled, sun_is_active, is_speed_boosted, boost_timer, isInverted
    global bug_freeze_counter, player_is_frozen, frozen_by_bug

    elapsedTime = millis() - startTime
    remainingTime = (timeLimit - elapsedTime) / 1000
    
    if remainingTime <= 0:
        showApology(current_mode)
        return 
    if dist(playerX, playerY, goalX, goalY) < playerSize/2 + goalSize/2:
        showResult("You're Safe!", color(0, 200, 0))
        return

    # --- Logic Updates ---
    if current_mode == "period1": manageTraffic()
    if is_speed_boosted:
        boost_timer -= 1
        if boost_timer <= 0: is_speed_boosted = False
    
    oldX, oldY = playerX, playerY
    current_speed = playerSpeed * 2 if is_speed_boosted else playerSpeed
    if not player_is_frozen:
        if is_on_slip_floor(playerX, playerY):
            if keyPressed:
                if keyCode == LEFT: playerVX -= acceleration
                elif keyCode == RIGHT: playerVX += acceleration
                elif keyCode == UP: playerVY -= acceleration
                elif keyCode == DOWN: playerVY += acceleration
            playerVX *= friction
            playerVY *= friction
        else:
            playerVX, playerVY = 0, 0
            if keyPressed:
                if keyCode == LEFT: playerX -= current_speed
                elif keyCode == RIGHT: playerX += current_speed
                elif keyCode == UP: playerY -= current_speed
                elif keyCode == DOWN: playerY += current_speed
        playerX += playerVX
        playerY += playerVY

    if current_mode == "period3" and not sun_is_active:
        distance_traveled += dist(oldX, oldY, playerX, playerY)
        if distance_traveled > 180: sun_is_active = True
        
    if current_mode == "period1" and gate_is_closed and playerX < path_area_start_x + playerSize / 2:
        playerX = path_area_start_x + playerSize / 2
    playerX = constrain(playerX, playerSize / 2, width - playerSize / 2)
    playerY = constrain(playerY, playerSize / 2, height - playerSize / 2)
    
    if not is_on_path(playerX, playerY):
        timeLimit -= 50

    # --- Drawing ---
    background(backgroundColor)
    fill(100, 200, 255, 100)
    rectMode(CORNER)
    for area in slip_areas: rect(area['x'], area['y'], area['w'], area['h'])
    fill(180)
    rectMode(CORNER)
    rect(new_path_x - path_width / 2, 0, path_width, height)
    rect(0, top_path_y - path_width / 2, width, path_width)
    rect(50, 540 - path_width / 2, 430, path_width)
    for x_offset in range(0, int(3 * width / 5.0) + grid_spacing, grid_spacing):
        rect(path_area_start_x + x_offset - path_width / 2, 0, path_width, height)
    for y in range(0, height, grid_spacing):
        rect(path_area_start_x, y - path_width / 2, 3 * width / 5.0, path_width)
    stroke(180)
    strokeWeight(path_width)
    line(480, 240, 240, 0)
    for i in range(len(new_complex_path) - 1):
        line(new_complex_path[i][0], new_complex_path[i][1], new_complex_path[i+1][0], new_complex_path[i+1][1])
    noStroke()

    fill(250, 100, 100)
    rectMode(CENTER)
    rect(goalX, goalY, goalSize, goalSize)
    
    if current_mode == "period3": manageSun()
    if current_mode == "night":
        manageChildren()
        manageFlashlight()

    manageBicycles()
    manageBugs()
    
    all_obstacles = obstacles + traffic_obstacles
    for ob in all_obstacles:
        ob.move()
        ob.draw()
        if not ob.hit and dist(playerX, playerY, ob.x, ob.y) < playerSize / 2 + ob.size / 2:
            timeLimit -= 5000
            ob.hit = True
            if is_speed_boosted: is_speed_boosted, boost_timer = False, 0
            
    if current_mode == "period1": manageOnigiri()
    
    if is_speed_boosted: fill(255, 255, 0)
    elif is_on_path(playerX, playerY): fill(50, 150, 250)
    else: fill(255, 0, 0)
    ellipse(playerX, playerY, playerSize, playerSize)

    if current_mode == "period1" and gate_is_closed:
        fill(255, 0, 0, 150)
        rectMode(CORNER)
        rect(path_area_start_x - path_width / 2, 0, path_width, height)

    if current_mode == "night" and isInverted:
        blendMode(DIFFERENCE)
        fill(255)
        rectMode(CORNER)
        rect(0, 0, width, height)
        blendMode(BLEND)
        
    if player_is_frozen:
        if frozen_by_bug:
            if frameCount % 20 < 10:
                pushStyle()
                rectMode(CORNER)
                fill(255, 0, 0, 100)
                rect(0, 0, width, height)
                popStyle()
            
            pushStyle()
            textAlign(CENTER, CENTER)
            textSize(50)
            fill(255, 0, 0)
            text("BUG FREEZE!", width/2, height/2 - 80)
            textSize(40)
            fill(255)
            text("Spam 'k' key to escape!", width/2, height/2)
            textSize(32)
            text("({}/{})".format(bug_freeze_counter, required_k_count), width/2, height/2 + 60)
            popStyle()

        elif current_mode == "night": drawCryingChildScreen()
        elif current_mode == "period3":
            pushStyle()
            textAlign(CENTER, CENTER)
            textSize(40); fill(255, 100, 0); text("Type 'water' to escape!", width/2, height/2)
            textSize(32); fill(255); text(unfreeze_input, width/2, height/2 + 50)
            popStyle()
    
    pushStyle()
    textAlign(CENTER, CENTER)
    textSize(32); fill(255); text("Time Left: {:.1f}".format(remainingTime), width/2, 50)
    popStyle()

def draw():
    if gameState == "MENU":
        drawMenu()
    elif gameState == "PLAYING":
        drawGame()
    elif gameState == "APOLOGY_SCREEN":
        drawApologyScreen()
        noLoop()
    elif gameState == "GAME_OVER":
        drawResultScreen(result_message, result_color)
        noLoop()

def generateApologyEmail(mode):
    recipient, period = "", ""
    if mode == "period1":
        recipient, period = "Prof. Rika Tomabechi", "1st period class"
    elif mode == "period3":
        recipient, period = "Prof. Yoshiharu Hirabayashi", "3rd period class"
    elif mode == "night":
        recipient, period = "Prof. Manabu Yoshida", "night session"
    
    email_body = """
To: {recipient}

Subject: Apology for Lateness

Dear {recipient},

I am writing to sincerely apologize for my tardiness for the {period} today.
There is no excuse for my being late, and I will ensure that it does not happen again.

I am very sorry for any disruption my tardiness may have caused.

Sincerely,

Yusei Mine
""".format(recipient=recipient, period=period)
    return textwrap.dedent(email_body).strip()

def drawApologyScreen():
    background(20, 20, 40)
    pushStyle() # スタイルを独立させる
    
    # 描画基準を完全に画面中央に設定
    textAlign(CENTER, CENTER)
    
    # メール本文
    fill(255)
    textSize(22)
    textLeading(32)
    # 座標 (width/2, height/2) を中心として描画
    # text(文字列, x, y) 形式は改行(\n)を考慮しつつ、指定した点を中心に配置する
    text(apology_text, width/2, height/2 - 40)
    
    # 戻るボタンの案内
    textSize(28)
    fill(200)
    text("Click to return to menu", width/2, height - 60)
    
    popStyle()


def drawResultScreen(message, c):
    background(50, 150)
    pushStyle()
    textAlign(CENTER, CENTER)
    textSize(64); fill(c); text(message, width/2, height/2 - 50)
    textSize(32); fill(255); text("Click to return to menu", width/2, height/2 + 50)
    popStyle()

def showApology(mode):
    global gameState, apology_text
    if gameState == "PLAYING":
        gameState = "APOLOGY_SCREEN"
        apology_text = generateApologyEmail(mode)

def showResult(message, c):
    global gameState, result_message, result_color
    if gameState == "PLAYING":
        gameState = "GAME_OVER"
        result_message = message
        result_color = c

def keyPressed():
    global unfreeze_input, player_is_frozen, sunX, sunY, sun_is_active, frozen_by_bug, bug_freeze_counter, distance_traveled
    
    if not player_is_frozen:
        return

    if frozen_by_bug:
        if key == 'k':
            bug_freeze_counter += 1
        if bug_freeze_counter >= required_k_count:
            player_is_frozen = False
            frozen_by_bug = False
            bug_freeze_counter = 0
    else: 
        if key == BACKSPACE:
            unfreeze_input = unfreeze_input[:-1]
        elif 'a' <= key <= 'z':
            unfreeze_input += str(key)
        
        unfreeze_word = ""
        if current_mode == "night":
            unfreeze_word = "rescue"
        elif current_mode == "period3":
            unfreeze_word = "water"

        if unfreeze_word and unfreeze_word in unfreeze_input:
            player_is_frozen = False
            unfreeze_input = ""
            if current_mode == "period3":
                sun_is_active = False
                sunX, sunY = -100, -100
                distance_traveled = 0.0

def mousePressed():
    global gameState
    if gameState == "MENU":
        if period1_button['x'] < mouseX < period1_button['x'] + period1_button['w'] and \
           period1_button['y'] < mouseY < period1_button['y'] + period1_button['h']: startGame("period1")
        if period3_button['x'] < mouseX < period3_button['x'] + period3_button['w'] and \
           period3_button['y'] < mouseY < period3_button['y'] + period3_button['h']: startGame("period3")
        if night_button['x'] < mouseX < night_button['x'] + night_button['w'] and \
           night_button['y'] < mouseY < night_button['y'] + night_button['h']: startGame("night")
    elif gameState == "GAME_OVER" or gameState == "APOLOGY_SCREEN":
        gameState = "MENU"
        loop()
