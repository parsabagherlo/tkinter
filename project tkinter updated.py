import tkinter as tk
from PIL import Image, ImageTk

window = tk.Tk()
window.title("Volleyball Game")

# ----------------------
#  Global Variables
# ----------------------

score = [0, 0]        
last_scorer = 1       

# Movement / physics
player_speed = 10
jump_speed = -15
gravity = 1
initial_ball_dx = 5
initial_ball_dy = -5
ball_speed_multiplier = 1.5

ball_dx = initial_ball_dx
ball_dy = initial_ball_dy

bufon_dy = 0
peter_dy = 0

# Track pressed keys
keys_pressed = set()

# NEW: Track if the ball has already caused a score
floor_scored = False

# NEW: Track if the ball is currently overlapping each player (to avoid repeated hits)
bufon_hit_cooldown = False
peter_hit_cooldown = False

# ----------------------
#  Create Canvas
# ----------------------

canvas = tk.Canvas(window, width=800, height=400, bg="lightblue")
canvas.pack()

# ----------------------
#  Load Images
# ----------------------

pil_image_1 = Image.open("C:/Users/Mhmd-MKh/Desktop/tkinter photo.jpg")
pil_image_1 = pil_image_1.resize((60, 110), Image.LANCZOS)
my_image1 = ImageTk.PhotoImage(pil_image_1)

pil_image_2 = Image.open("C:/Users/Mhmd-MKh/Desktop/tkinter photo2.jpg")
pil_image_2 = pil_image_2.resize((60, 110), Image.LANCZOS)
my_image2 = ImageTk.PhotoImage(pil_image_2)

# ----------------------
#  Create Objects
# ----------------------

# Draw net (from x=400, y=300 to x=400, y=400)
canvas.create_line(400, 250, 400, 400, width=4)

# Score display
score_text = canvas.create_text(400, 20, 
    text="bufon: 0    peter check: 0", font=("Arial", 16))

# bufon rectangle
bufon = canvas.create_rectangle(50, 340, 80, 400, fill="green")
# image for bufon
image_bufon_id = canvas.create_image(50, 290, anchor="nw", image=my_image1)

# peter_check rectangle
peter_check = canvas.create_rectangle(720, 340, 750, 400, fill="blue")
# image for peter_check
image_peter_id = canvas.create_image(720, 290, anchor="nw", image=my_image2)

# Ball
ball = canvas.create_oval(0, 0, 30, 30, fill="white")

# ----------------------
#  Key Handlers
# ----------------------

def key_pressed(event):
    keys_pressed.add(event.keysym.lower())

def key_released(event):
    keys_pressed.discard(event.keysym.lower())

window.bind("<KeyPress>", key_pressed)
window.bind("<KeyRelease>", key_released)

# ----------------------
#  Movement & Collisions
# ----------------------

def move_players():
    """ Moves both players (bufon, peter_check) + their images, applies gravity, and checks boundaries. """
    global bufon_dy, peter_dy

    # -- bufon controls (a/d/w) --
    if 'a' in keys_pressed:
        move_player(bufon, image_bufon_id, dx=-player_speed)
    if 'd' in keys_pressed:
        move_player(bufon, image_bufon_id, dx=player_speed)
    if 'w' in keys_pressed and on_ground(bufon):
        bufon_dy = jump_speed

    # -- peter_check controls (j/l/i) --
    if 'j' in keys_pressed:
        move_player(peter_check, image_peter_id, dx=-player_speed)
    if 'l' in keys_pressed:
        move_player(peter_check, image_peter_id, dx=player_speed)
    if 'i' in keys_pressed and on_ground(peter_check):
        peter_dy = jump_speed

    # Apply gravity
    bufon_dy += gravity
    peter_dy += gravity

    # Move both rectangles vertically
    canvas.move(bufon, 0, bufon_dy)
    canvas.move(peter_check, 0, peter_dy)
    # Move images vertically to match
    canvas.move(image_bufon_id, 0, bufon_dy)
    canvas.move(image_peter_id, 0, peter_dy)

    # Limit each player
    limit_player_position(bufon, image_bufon_id, is_bufon=True)
    limit_player_position(peter_check, image_peter_id, is_bufon=False)

def move_player(rect_id, img_id, dx=0):
    """ Moves a player rectangle + its image horizontally by dx. """
    canvas.move(rect_id, dx, 0)
    canvas.move(img_id, dx, 0)

def on_ground(player):
    """ Returns True if bottom of the player is at or below y=400 (the floor). """
    x1, y1, x2, y2 = canvas.coords(player)
    return y2 >= 400

def limit_player_position(player_rect, player_img_id, is_bufon):
    """ Keeps the player within the court and above the floor. """
    global bufon_dy, peter_dy
    x1, y1, x2, y2 = canvas.coords(player_rect)
    
    # Floor collision
    if y2 >= 400:
        # Snap to floor
        canvas.coords(player_rect, x1, 340, x2, 400)
        canvas.coords(player_img_id, x1, 290)  # image is 50 px taller than rectangle (110 vs 60)
        if is_bufon:
            bufon_dy = 0
        else:
            peter_dy = 0

    # Left boundary
    if x1 < 0:
        offset = -x1
        canvas.move(player_rect, offset, 0)
        canvas.move(player_img_id, offset, 0)

    # Right boundary
    if x2 > 800:
        offset = 800 - x2
        canvas.move(player_rect, offset, 0)
        canvas.move(player_img_id, offset, 0)

    # Net boundary at x=400
    if is_bufon and x2 > 400:
        offset = 400 - x2
        canvas.move(player_rect, offset, 0)
        canvas.move(player_img_id, offset, 0)
    if (not is_bufon) and x1 < 400:
        offset = 400 - x1
        canvas.move(player_rect, offset, 0)
        canvas.move(player_img_id, offset, 0)

def move_ball():
    """ Moves the ball, handles collisions with walls, floor, net, and players. """
    global ball_dx, ball_dy, score, last_scorer
    global floor_scored, bufon_hit_cooldown, peter_hit_cooldown

    # Move the ball
    canvas.move(ball, ball_dx, ball_dy)
    x1, y1, x2, y2 = canvas.coords(ball)
    px1, py1, px2, py2 = canvas.coords(bufon)
    p2x1, p2y1, p2x2, p2y2 = canvas.coords(peter_check)

    # ----------------------
    #  Floor / Scoring Fix
    # ----------------------
    if y2 >= 400:
        # Only score once until the ball is moved up again
        if not floor_scored:
            floor_scored = True
            if x1 < 400:
                score_point(1)  # peter_check scores
            else:
                score_point(0)  # bufon scores
        return
    else:
        # Once the ball is above the floor, allow scoring again next time
        floor_scored = False

    # Ball collision with walls (left/right)
    if x1 <= 0 or x2 >= 800:
        ball_dx *= -1

    # Ball collision with ceiling
    if y1 <= 0:
        ball_dy *= -1

    # Ball collision with net (x=400 from y=300..400)
    net_left = 398
    net_right = 402
    if x2 >= net_left and x1 <= net_right and y2 >= 300:
        ball_dx *= -1

    # ----------------------
    #  Player Collisions Fix
    # ----------------------
    # If ball overlaps bufon:
    if check_collision(ball, bufon):
        if not bufon_hit_cooldown:
            bufon_hit_cooldown = True
            bounce_ball_off_player(x1, x2, px1, px2)
    else:
        bufon_hit_cooldown = False

    # If ball overlaps peter_check:
    if check_collision(ball, peter_check):
        if not peter_hit_cooldown:
            peter_hit_cooldown = True
            bounce_ball_off_player(x1, x2, p2x1, p2x2)
    else:
        peter_hit_cooldown = False

def bounce_ball_off_player(ball_left, ball_right, player_left, player_right):
    """ Bounces the ball off a player (only once per overlap). """
    global ball_dx, ball_dy
    x1, y1, x2, y2 = canvas.coords(ball)
    px1, py1, px2, py2 = canvas.coords(bufon)
    p2x1, p2y1, p2x2, p2y2 = canvas.coords(peter_check)

    if check_collision(ball, bufon):
        ball_center = (x1 + x2) / 2
        player_center = (px1 + px2) / 2
        if ball_center < player_center:  # Hit left side
            ball_dx = -abs(ball_dx)  # Move left
        else:  # Hit right side
            ball_dx = abs(ball_dx)  # Move right
        ball_dy = -abs(ball_dy)
        ball_dx *= ball_speed_multiplier  # Slightly increase speed
        ball_dy *= ball_speed_multiplier

    # Ball collision with peter_check
    if check_collision(ball, peter_check):
        ball_center = (x1 + x2) / 2
        player_center = (p2x1 + p2x2) / 2
        if ball_center < player_center:  # Hit left side
            ball_dx = -abs(ball_dx)  # Move left
        else:  # Hit right side
            ball_dx = abs(ball_dx)  # Move right
        ball_dy = -abs(ball_dy)
        ball_dx *= ball_speed_multiplier  # Slightly increase speed
        ball_dy *= ball_speed_multiplier

def check_collision(obj1, obj2):
    """ Returns True if obj1 and obj2 overlap on the canvas. """
    x1, y1, x2, y2 = canvas.coords(obj1)
    x3, y3, x4, y4 = canvas.coords(obj2)
    return (x1 < x4 and x3 < x2 and y1 < y4 and y3 < y2)

def bounce_off_player(player):
    """ (Unused in your final code, leaving as-is.) """
    global ball_dx, ball_dy
    ball_dy = -abs(ball_dy)
    ball_dx *= 1.05
    ball_dy *= 1.05

def score_point(player_index):
    """ player_index = 0 => bufon, 1 => peter_check. """
    global score, last_scorer
    score[player_index] += 1
    last_scorer = player_index
    canvas.itemconfig(score_text, text=f"bufon: {score[0]}    peter check: {score[1]}")
    # Show "Goal!" temporarily
    canvas.create_text(400, 200, text="Goal!", fill="gold")
    # Reset after a short delay
    window.after(1000, reset_after_goal)

def reset_after_goal():
    """ Clears & redraws all objects, placing the ball on the side of whoever *didn’t* score. """
    canvas.delete("all")

    # Redraw net
    canvas.create_line(400, 250, 400, 400, width=4)

    # Redraw score
    global score_text
    score_text = canvas.create_text(
        400, 20, 
        text=f"bufon: {score[0]}    peter check: {score[1]}", 
        font=("Arial", 16)
    )

    # Redraw players (rectangles) & images
    global bufon, peter_check, image_bufon_id, image_peter_id
    bufon = canvas.create_rectangle(50, 340, 80, 400, fill="green")
    peter_check = canvas.create_rectangle(720, 340, 750, 400, fill="blue")

    # Recreate images
    image_bufon_id = canvas.create_image(50, 290, anchor="nw", image=my_image1)
    image_peter_id = canvas.create_image(720, 290, anchor="nw", image=my_image2)

    # Reset movement variables for players
    global bufon_dy, peter_dy
    bufon_dy = 0
    peter_dy = 0

    # Redraw ball
    global ball
    ball = canvas.create_oval(0, 0, 30, 30, fill="white")

    # Put ball on the side of the *opposite* player who scored
    reset_ball_position()

def reset_ball_position():
    """ Places the ball near the losing player. """
    global ball_dx, ball_dy
    if last_scorer == 1:
        x = 720
    else:
        x = 50
    y = 400 - 60 - 30 - 10
    canvas.coords(ball, x, y, x + 30, y + 30)

    # Reverse horizontal direction relative to who scored
    ball_dx = initial_ball_dx * (-1 if last_scorer == 1 else 1)
    ball_dy = initial_ball_dy

def game_loop():
    move_players()
    move_ball()
    window.after(20, game_loop)

# Initialize ball position once at start
reset_ball_position()

# Start the loop
game_loop()

# Start Tkinter event loop
window.mainloop()
