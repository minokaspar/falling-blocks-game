from tkinter import *
import random
import time

# ----- Config -----

GRAVITY = 0.5
MAX_FALL_SPEED = 25
HIGHSCORES = {"auto level-up": 0, "manual level-up": 0}
GADGET_DURATION = 300
GADGET_COLORS = {"slower": "red", "faster": "lightgreen", "shield": "cyan", "bomb": "orange",
                 "trigger": "yellow", "random": "pink", "normal": "black", "levelup": "lightblue",
                 "slower_p": "darkred", "faster_p": "green"}
P_SIZE = 40
E_SIZE = 20
CW = 1000
CH = 700
root = Tk()
root.title("Falling elements")
root.geometry(f"{CW}x{CH}+270+20")
canvas = Canvas(root, width = CW, height = CH, bg = "white")
canvas.pack()

# ----- Classes -----

class Player:
    def __init__(self):
        d = P_SIZE/2
        self.acceleration = 1
        self.accel_timer = 0
        self.shield = 0
        self.x = CW/2
        self.y = CH - 50 - d
        self.xv = 0
        self.id = canvas.create_rectangle(self.x - d, self.y - d, self.x + d, self.y + d, outline = "", fill = GADGET_COLORS["normal"], tags = "player")
        self.shield_id = None
    
    def create_shield(self):
        if self.shield < 1:
            d = P_SIZE
            self.shield_id = canvas.create_oval(self.x - d, self.y - d, self.x + d, self.y + d, outline = "", fill = GADGET_COLORS["shield"], tags = "player")
            canvas.tag_lower(self.shield_id)
            for e in elements:
                canvas.tag_lower(e.id)
        self.shield = GADGET_DURATION
    
    def remove_shield(self):
        canvas.delete(self.shield_id)
        self.shield_id = None
    
    def move_step(self):
        self.xv *= 0.9
        self.x += self.xv
        canvas.move("player", self.xv, 0)
        if self.x > CW - P_SIZE/2:
            self.xv = 0
            canvas.move("player", CW - P_SIZE/2 - self.x, 0)
            self.x = CW - P_SIZE/2
        elif self.x < P_SIZE/2:
            self.xv = 0
            canvas.move("player", P_SIZE/2 - self.x, 0)
            self.x = 0 + P_SIZE/2

class Element:
    def __init__(self):
        self.type = "normal"
        if game_mode == "manual level-up" and random.randint(0,6) < 1:
            self.type = "levelup"
        options = ["shield", "slower", "faster", "bomb", "trigger"]
        r = random.randint(0, 50)
        for i in range(len(options)):
            if i == r:
                self.type = options[i]
        
        d = E_SIZE/2
        self.x = random.randint(E_SIZE/2, CW - E_SIZE/2)
        self.y = -d
        self.yv = 0
        color = GADGET_COLORS[self.type]
        if self.type != "normal" and random.randint(0, 7) < 1:
            color = GADGET_COLORS["random"]
        self.id = canvas.create_rectangle(self.x - d, self.y - d, self.x + d, self.y + d, outline = "", fill = color)
        canvas.tag_lower(self.id)
    
    def fall_step(self):
        if self.yv < MAX_FALL_SPEED:
            self.yv += GRAVITY
        self.y += self.yv
        canvas.move(self.id, 0, self.yv)
        if self.y > CH - 50 + E_SIZE/2:
            canvas.delete(self.id)
            elements.remove(self)
            if self.type == "trigger":
                for _ in range(10):
                    elements.append(Element())

# ----- Mouse and Key bindings -----

keys = {"Right": False, "Left": False, "a": False, "d": False}
mouse_x = 0
dragging = False

def on_keypress(event):
    if event.keysym in keys:
        keys[event.keysym] = True

def on_keyrelease(event):
    if event.keysym in keys:
        keys[event.keysym] = False

root.bind("<KeyPress>", on_keypress)
root.bind("<KeyRelease>", on_keyrelease)

def on_click(event):
    global mouse_x, dragging
    dragging = True
    mouse_x = event.x

def on_release(event):
    global dragging
    dragging = False

def on_drag(event):
    global mouse_x
    if dragging:
        mouse_x = event.x

root.bind("<ButtonPress-1>", on_click)
root.bind("<B1-Motion>", on_drag)
root.bind("<ButtonRelease-1>", on_release)

# ----- Game loop -----

def accelerate_player():
    if keys["Right"] or keys["d"] or dragging and mouse_x > player.x and abs(mouse_x - player.x) > P_SIZE/2:
        player.xv += player.acceleration
    if keys["Left"] or keys["a"] or dragging and mouse_x < player.x and abs(mouse_x - player.x) > P_SIZE/2:
        player.xv -= player.acceleration

def create_elements():
    if random.randint(0, 100) < level*2 + 3:
        elements.append(Element())

def touching_element(elem):
    dpos = P_SIZE/2 + E_SIZE/2
    dneg = - P_SIZE/2 - E_SIZE/2
    return player.x + dneg < elem.x < player.x + dpos and player.y + dneg < elem.y < player.y + dpos

def gameover():
    global buttons
    canvas.delete("all")
    hiscore_text = "highscore"
    if level > HIGHSCORES[game_mode]:
        HIGHSCORES[game_mode] = level
        hiscore_text = "new highscore"
        
    canvas.create_text(CW/2, CH/2 - 75, text = "Game Over", font = ("Consolas", 20, "bold"))
    canvas.create_text(CW/2, CH/2 - 25, text = f"You died at level {level} | {hiscore_text}: level {HIGHSCORES[game_mode]}", font = ("Consolas", 20, "bold"))
    canvas.create_text(CW/2, CH/2 + 20, text = f"Game mode: {game_mode}", font = ("Consolas", 15, "bold"))
    restart_button = Button(root, text = "try again", font = ("Consolas", 20, "bold"), width = 15, height = 1, command = start_UI)
    buttons = [canvas.create_window(CW/2, CH/2 + 100, window = restart_button)]

def gameloop():
    global level
    accelerate_player()
    player.move_step()
    if player.shield > 0:
        player.shield -= 1
        if player.shield == 0:
            player.remove_shield()
    if player.accel_timer > 0:
        player.accel_timer -= 1
        if player.accel_timer == 0:
            player.acceleration = 1
            canvas.itemconfigure(player.id, fill = GADGET_COLORS["normal"])
    
    create_elements()
    bomb_trigger = False
    for e in elements[:]:
        e.fall_step()
        if touching_element(e):
            if e.type == "normal":
                if not player.shield > 0:
                    root.after(500, gameover)
                    return
            elif e.type == "shield":
                player.create_shield()
            elif e.type == "slower":
                player.acceleration = 0.5
                player.accel_timer = GADGET_DURATION
                canvas.itemconfigure(player.id, fill = GADGET_COLORS["slower_p"])
            elif e.type == "faster":
                player.acceleration = 2
                player.accel_timer = GADGET_DURATION
                canvas.itemconfigure(player.id, fill = GADGET_COLORS["faster_p"])
            elif e.type == "bomb":
                bomb_trigger = True
            elif e.type == "levelup":
                level += 1
                canvas.itemconfigure(level_index, text = f"Level {level}")
            
            canvas.delete(e.id)
            elements.remove(e)
    
    if bomb_trigger:
        for e in elements[:]:
            canvas.delete(e.id)
            elements.remove(e)
    
    if game_mode == "auto level-up":
        d = round((time.perf_counter() - timer)/5) + 1
        if d > level:
            level = d
            canvas.itemconfigure(level_index, text = f"Level {level}")
    
    root.after(16, gameloop)


# ----- UI -----

def set_game_mode(mode):
    global game_mode, buttons
    game_mode = mode
    buttons = []
    start_game()

def start_UI():
    global buttons
    canvas.delete("all")
    buttons = []
    auto_mode_button = Button(root, text = "auto level-up", font = ("Consolas", 20, "bold"), width = 20, height = 2, command = lambda: set_game_mode("auto level-up"))
    manual_mode_button = Button(root, text = "manual level-up", font = ("Consolas", 20, "bold"), width = 20, height = 2, command = lambda: set_game_mode("manual level-up"))
    canvas.create_text(CW/2, CH/2 - 75, text = "Choose game mode:", font = ("Consolas", 20, "bold"))
    buttons = [
        canvas.create_window(CW/2, CH/2, window = auto_mode_button),
        canvas.create_window(CW/2, CH/2 + 100, window = manual_mode_button)]

def start_game():
    global player, elements, level, level_index, timer
    canvas.delete("all")
    canvas.create_rectangle(0, CH - 50, CW, CH, fill = "black")
    player = Player()
    elements = []
    level = 1
    level_index = canvas.create_text(CW/2, CH - 25, text = f"Level {level}", font = ("Consolas", 15, "bold"), fill = "white")
    timer = time.perf_counter()
    gameloop()


game_mode = "no mode"
buttons = []
player = 0
elements = []
level = 1
level_index = 0
timer = 0
start_UI()

root.mainloop()