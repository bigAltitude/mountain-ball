# -*- coding: utf-8 -*-
#  ╭─────────────────────────────────╮
#  │                                 │
#  │ Program: Ball Simulation Game   │
#  │ Date: 2025-03-17                │
#  │ Author: S Perkins               │
#  │ Company: Geo Consulting Limited │
#  │ Work: Geo-Science Engineering   │
#  │                                 │
#  ╰─────────────────────────────────╯

import tkinter as tk
import random
import math
import time

class BallSimulation:
    def __init__(self, master):
        self.master = master
        #  ╭──────────────────────────╮
        #  │ Define canvas dimensions │
        #  ╰──────────────────────────╯
        self.width = 800
        self.height = 300
        #  ╭──────────────────────────────────╮
        #  │ Create canvas widget for drawing │
        #  ╰──────────────────────────────────╯
        self.canvas = tk.Canvas(master, width=self.width, height=self.height)
        self.canvas.pack()

        #  ╭─────────────────────────────────────────────────────────────╮
        #  │ Flag to control simulation updates (active until game over) │
        #  ╰─────────────────────────────────────────────────────────────╯
        self.simulation_active = True

        #  ╭───────────────────────────────────────────────────────────╮
        #  │ Initialize hit counter (starts at -1 to offset first hit) │
        #  ╰───────────────────────────────────────────────────────────╯
        self.counter = -1
        #  ╭─────────────────────────────────────────────╮
        #  │ Create text item on canvas to display stats │
        #  ╰─────────────────────────────────────────────╯
        self.counter_text = self.canvas.create_text(
            10, 10, anchor='nw',
            text=f"Hits: {self.counter}", font=('Arial', 14)
        )

        #  ╭───────────────────────────────────────────────────────╮
        #  │ Bind ESC key and middle mouse button to quit the game │
        #  ╰───────────────────────────────────────────────────────╯
        self.master.bind('<Escape>', self.close_program)
        self.master.bind('<Button-2>', self.close_program)

        #  ╭────────────────────────────────────────────────╮
        #  │ Create the terrain at the bottom of the canvas │
        #  ╰────────────────────────────────────────────────╯
        self.create_terrain()

        #  ╭────────────────────────────────────────╮
        #  │ Create the ball (5 pixels in diameter) │
        #  ╰────────────────────────────────────────╯
        self.ball_radius = 4
        #  ╭────────────────────────────────────╮
        #  │ 4 pixel radius = 8 pixels diameter │
        #  ╰────────────────────────────────────╯
        self.ball = self.canvas.create_oval(
            self.width/2 - self.ball_radius, 0 - self.ball_radius,
            self.width/2 + self.ball_radius, 0 + self.ball_radius,
            fill=self.get_random_color(),
            outline=''
        )

        #  ╭─────────────────────────────────────────────────────────────────╮
        #  │ Set up physics parameters: position, velocity, and acceleration │
        #  ╰─────────────────────────────────────────────────────────────────╯
        self.ball_pos = [self.width/2, 0]
        self.ball_vel = [0.0, 0.0]
        self.ball_acc = [0.0, 300.0]
        #  ╭────────────────╮
        #  │ Gravity effect │
        #  ╰────────────────╯

        #  ╭───────────────────────────────────────────────╮
        #  │ Time step for physics simulation (in seconds) │
        #  ╰───────────────────────────────────────────────╯
        self.time_step = 0.001

        #  ╭────────────────────────────────────────────────╮
        #  │ Remember last dot position to space trail dots │
        #  ╰────────────────────────────────────────────────╯
        self.last_dot_pos = self.ball_pos[:]
        #  ╭───────────────────────────────────────────────────────────────────╮
        #  │ List to hold trail dots (each as a tuple of dot id and timestamp) │
        #  ╰───────────────────────────────────────────────────────────────────╯
        self.dots = []

        #  ╭─────────────────────────────────────────────────────╮
        #  │ Record start time to calculate elapsed time and HPM │
        #  ╰─────────────────────────────────────────────────────╯
        self.start_time = time.time()
        #  ╭─────────────────────────────────────╮
        #  │ Start updating the on-screen status │
        #  ╰─────────────────────────────────────╯
        self.update_status()
        #  ╭──────────────────────────╮
        #  │ Start the animation loop │
        #  ╰──────────────────────────╯
        self.animate()
        #  ╭───────────────────────────────────────────────╮
        #  │ Start cleanup for trail dots older than 5 sec │
        #  ╰───────────────────────────────────────────────╯
        self.cleanup_trail()

    def create_terrain(self):
        #  ╭────────────────────────────────────────────────────────────────╮
        #  │                                                                │
        #  │ Generate random terrain points along the bottom of the canvas, │
        #  │ then create a polygon to represent the terrain.                │
        #  │                                                                │
        #  ╰────────────────────────────────────────────────────────────────╯
        self.terrain_points = []
        x = 0
        while x <= self.width:
            #  ╭───────────────────────────────────────────────────╮
            #  │ Generate a random y-coordinate for terrain height │
            #  ╰───────────────────────────────────────────────────╯
            y = random.randint(self.height - 120, self.height)
            self.terrain_points.append((x, y))
            x += random.randint(15, 28)
        #  ╭───────────────────────────────────────────╮
        #  │ Ensure the terrain reaches the right edge │
        #  ╰───────────────────────────────────────────╯
        if self.terrain_points[-1][0] < self.width:
            self.terrain_points.append((self.width, self.terrain_points[-1][1]))
        #  ╭───────────────────────────────────────╮
        #  │ Close the polygon at the bottom edges │
        #  ╰───────────────────────────────────────╯
        self.terrain_points.append((self.width, self.height))
        self.terrain_points.append((0, self.height))
        #  ╭────────────────────────────────────────╮
        #  │ Draw the terrain polygon on the canvas │
        #  ╰────────────────────────────────────────╯
        self.canvas.create_polygon(self.terrain_points, fill='#76eec6')

    def animate(self):
        #  ╭───────────────────────────────────────────────────╮
        #  │                                                   │
        #  │ Update the ball's position, detect collisions,    │
        #  │ and schedule the next frame.                      │
        #  │                                                   │
        #  │ If simulation is no longer active, stop animation │
        #  ╰───────────────────────────────────────────────────╯
        if not self.simulation_active:
            return

        #  ╭───────────────────────────────────────────────╮
        #  │ Update velocity and position based on physics │
        #  ╰───────────────────────────────────────────────╯
        self.ball_vel[1] += self.ball_acc[1] * self.time_step
        self.ball_pos[0] += self.ball_vel[0] * self.time_step
        self.ball_pos[1] += self.ball_vel[1] * self.time_step

        #  ╭────────────────────────────────────────────╮
        #  │ Check for collisions with the window walls │
        #  ╰────────────────────────────────────────────╯
        self.check_wall_collision()
        #  ╭──────────────────────────────────╮
        #  │ Check for collision with terrain │
        #  ╰──────────────────────────────────╯
        if self.check_collision():
            self.resolve_collision()

        #  ╭───────────────────────────────────╮
        #  │ Leave a dot trail behind the ball │
        #  ╰───────────────────────────────────╯
        self.leave_trail()

        #  ╭─────────────────────────────────────────────╮
        #  │ Update the ball's coordinates on the canvas │
        #  ╰─────────────────────────────────────────────╯
        x, y = self.ball_pos
        self.canvas.coords(self.ball,
                           x - self.ball_radius, y - self.ball_radius,
                           x + self.ball_radius, y + self.ball_radius)

        #  ╭────────────────────────────────╮
        #  │ Schedule the next frame update │
        #  ╰────────────────────────────────╯
        self.master.after(int(self.time_step * 1000), self.animate)

    def leave_trail(self):
        #  ╭──────────────────────────────────────────────────╮
        #  │                                                  │
        #  │ Create a small dot on the canvas every 10 pixels │
        #  │ to leave a visible trail.                        │
        #  │                                                  │
        #  ╰──────────────────────────────────────────────────╯
        last_x, last_y = self.last_dot_pos
        current_x, current_y = self.ball_pos
        #  ╭─────────────────────────────────────────╮
        #  │ Calculate distance moved since last dot │
        #  ╰─────────────────────────────────────────╯
        distance = math.hypot(current_x - last_x, current_y - last_y)
        if distance >= 10:
            #  ╭──────────────────╮
            #  │ Draw a small dot │
            #  ╰──────────────────╯
            dot = self.canvas.create_oval(
                current_x - 1, current_y - 1,
                current_x + 1, current_y + 1,
                fill='black',
                outline=''
            )
            #  ╭───────────────────────────────────────╮
            #  │ Store dot with its creation timestamp │
            #  ╰───────────────────────────────────────╯
            self.dots.append((dot, time.time()))
            self.last_dot_pos = self.ball_pos[:]

    def check_wall_collision(self):
        #  ╭────────────────────────────────────────────────────────╮
        #  │                                                        │
        #  │ Detect collisions with the left, right, and top walls. │
        #  │ If the ball hits the top wall, update the hit counter. │
        #  │                                                        │
        #  │ Left wall collision                                    │
        #  ╰────────────────────────────────────────────────────────╯
        if self.ball_pos[0] - self.ball_radius <= 0:
            self.ball_pos[0] = self.ball_radius
            self.ball_vel[0] = -self.ball_vel[0] * 0.8
        #  ╭──────────────────────╮
        #  │ Right wall collision │
        #  ╰──────────────────────╯
        elif self.ball_pos[0] + self.ball_radius >= self.width:
            self.ball_pos[0] = self.width - self.ball_radius
            self.ball_vel[0] = -self.ball_vel[0] * 0.8

        #  ╭───────────────────────────────────────────────────╮
        #  │ Top wall collision: change color and count as hit │
        #  ╰───────────────────────────────────────────────────╯
        if self.ball_pos[1] - self.ball_radius <= 0:
            self.ball_pos[1] = self.ball_radius
            self.ball_vel[1] = -self.ball_vel[1] * 0.8
            #  ╭──────────────────────────────────────╮
            #  │ Change the ball's color on collision │
            #  ╰──────────────────────────────────────╯
            self.canvas.itemconfig(self.ball, fill=self.get_random_color())
            #  ╭───────────────────────╮
            #  │ Increment hit counter │
            #  ╰───────────────────────╯
            self.increment_counter()

    def increment_counter(self):
        #  ╭───────────────────────────────────╮
        #  │ Increment the hit counter by one. │
        #  ╰───────────────────────────────────╯
        self.counter += 1

    def close_program(self, event=None):
        #  ╭────────────────────────╮
        #  │ Shut down the program. │
        #  ╰────────────────────────╯
        self.master.destroy()

    def check_collision(self):
        #  ╭──────────────────────────────────────────────╮
        #  │                                              │
        #  │ Check if the ball collides with the terrain. │
        #  │ Returns True if collision occurs.            │
        #  │                                              │
        #  ╰──────────────────────────────────────────────╯
        x, y = self.ball_pos
        #  ╭──────────────────────────────────────────────────────╮
        #  │ Loop through terrain segments (ignore closing edges) │
        #  ╰──────────────────────────────────────────────────────╯
        for i in range(len(self.terrain_points) - 4):
            x1, y1 = self.terrain_points[i]
            x2, y2 = self.terrain_points[i+1]
            if x1 <= x <= x2 or x2 <= x <= x1:
                #  ╭────────────────────────────────────────────╮
                #  │ Calculate terrain y-coordinate at ball's x │
                #  ╰────────────────────────────────────────────╯
                if x2 != x1:
                    m = (y2 - y1) / (x2 - x1)
                    y_terrain = m * (x - x1) + y1
                else:
                    y_terrain = y1
                #  ╭─────────────────────────────────────╮
                #  │ Check if ball overlaps with terrain │
                #  ╰─────────────────────────────────────╯
                if y + self.ball_radius >= y_terrain:
                    self.collision_segment = (x1, y1, x2, y2)
                    return True
        return False

    def resolve_collision(self):
        #  ╭────────────────────────────────────────────────────╮
        #  │                                                    │
        #  │ Reflect the ball's velocity based on the terrain's │
        #  │ normal vector and adjust for slight energy loss.   │
        #  │                                                    │
        #  ╰────────────────────────────────────────────────────╯
        x1, y1, x2, y2 = self.collision_segment
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        #  ╭──────────────────────────────────────────────────╮
        #  │ Compute the normal vector to the terrain segment │
        #  ╰──────────────────────────────────────────────────╯
        nx = -dy / length
        ny = dx / length
        #  ╭───────────────────────────────────────────────────╮
        #  │ Compute dot product of velocity and normal vector │
        #  ╰───────────────────────────────────────────────────╯
        v_dot_n = self.ball_vel[0] * nx + self.ball_vel[1] * ny
        #  ╭─────────────────────────────╮
        #  │ Reflect the velocity vector │
        #  ╰─────────────────────────────╯
        self.ball_vel[0] -= 2 * v_dot_n * nx
        self.ball_vel[1] -= 2 * v_dot_n * ny
        #  ╭─────────────────────────────────╮
        #  │ Apply slight energy adjustments │
        #  ╰─────────────────────────────────╯
        self.ball_vel[0] *= 1.1
        self.ball_vel[1] *= 0.95

        #  ╭──────────────────────────────────────────────────────╮
        #  │ Adjust ball position to prevent sinking into terrain │
        #  ╰──────────────────────────────────────────────────────╯
        x, y = self.ball_pos
        if x2 != x1:
            m = (y2 - y1) / (x2 - x1)
            y_terrain = m * (x - x1) + y1
        else:
            y_terrain = y1
        overlap = (y + self.ball_radius) - y_terrain
        if overlap > 0:
            self.ball_pos[1] -= overlap

    def get_random_color(self):
        #  ╭───────────────────────────────────╮
        #  │ Return a random hex color string. │
        #  ╰───────────────────────────────────╯
        return f'#{random.randint(0, 255):02x}' + \
               f'{random.randint(0, 255):02x}' + \
               f'{random.randint(0, 255):02x}'

    def cleanup_trail(self):
        #  ╭────────────────────────────────────────────────────────────╮
        #  │                                                            │
        #  │ Remove dots from the canvas that are older than 5 seconds. │
        #  │ This helps keep the canvas from cluttering up.             │
        #  │                                                            │
        #  ╰────────────────────────────────────────────────────────────╯
        current_time = time.time()
        for dot, timestamp in self.dots[:]:
            if current_time - timestamp > 5:
                self.canvas.delete(dot)
                self.dots.remove((dot, timestamp))
        self.master.after(100, self.cleanup_trail)

    def update_status(self):
        #  ╭───────────────────────────────────────────────────────────╮
        #  │                                                           │
        #  │ Update the on-screen status text with current hit count,  │
        #  │ elapsed run time, and hits per minute (HPM). If 2 minutes │
        #  │ have passed, stop the simulation and display GAME OVER.   │
        #  │                                                           │
        #  ╰───────────────────────────────────────────────────────────╯
        run_time = time.time() - self.start_time
        #  ╭───────────────────────────────────────────────╮
        #  │ Check if 2 minutes (120 seconds) have elapsed │
        #  ╰───────────────────────────────────────────────╯
        if run_time >= 120 and self.simulation_active:
            self.simulation_active = False
            #  ╭─────────────────────╮
            #  │ Stop the simulation │
            #  ╰─────────────────────╯
            run_time = 120
            #  ╭─────────────────────────────────────╮
            #  │ Cap the displayed time at 2 minutes │
            #  ╰─────────────────────────────────────╯
            hpm = (self.counter / run_time * 60) if run_time > 0 else 0
            #  ╭─────────────────────────────────────────────╮
            #  │ Update the status text to include GAME OVER │
            #  ╰─────────────────────────────────────────────╯
            self.canvas.itemconfig(
                self.counter_text,
                text=f"Hits: {self.counter}  Time: {run_time:.1f} s  "
                     f"HPM: {hpm:.1f}  GAME OVER"
            )
            #  ╭─────────────────────────────────────────────────╮
            #  │ Simulation stops here; user must exit manually. │
            #  ╰─────────────────────────────────────────────────╯
            return
        else:
            hpm = (self.counter / run_time * 60) if run_time > 0 else 0
            self.canvas.itemconfig(
                self.counter_text,
                text=f"Hits: {self.counter}  Time: {run_time:.1f} s  "
                     f"HPM: {hpm:.1f}"
            )
            #  ╭────────────────────────────────────────────╮
            #  │ Continue updating the status every 100 ms. │
            #  ╰────────────────────────────────────────────╯
            self.master.after(100, self.update_status)

if __name__ == '__main__':
    #  ╭──────────────────────────────────────────╮
    #  │ Create main window and remove its border │
    #  ╰──────────────────────────────────────────╯
    root = tk.Tk()
    root.overrideredirect(True)
    #  ╭───────────────────────────────────╮
    #  │ Set window position to (100, 200) │
    #  ╰───────────────────────────────────╯
    root.geometry("+100+200")
    #  ╭────────────────────────────╮
    #  │ Instantiate the simulation │
    #  ╰────────────────────────────╯
    sim = BallSimulation(root)
    #  ╭─────────────────────────────╮
    #  │ Start the Tkinter main loop │
    #  ╰─────────────────────────────╯
    root.mainloop()
