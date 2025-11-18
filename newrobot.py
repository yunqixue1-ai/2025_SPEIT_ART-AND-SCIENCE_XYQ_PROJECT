import turtle
import math

def rgb_to_hex(r, g, b):
    r = max(0, min(int(r), 255))
    g = max(0, min(int(g), 255))
    b = max(0, min(int(b), 255))
    return "#%02x%02x%02x" % (r, g, b)

def hsv_to_rgb(h, s, v):
    """HSV to RGB conversion for rainbow colors"""
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

class SO2LieGroup:
    @staticmethod
    def rotation_matrix(theta):
        c, s = math.cos(theta), math.sin(theta)
        return [[c, -s],[s, c]]
    
    @staticmethod
    def apply_rotation(theta, x, y):
        R = SO2LieGroup.rotation_matrix(theta)
        return R[0][0]*x + R[0][1]*y, R[1][0]*x + R[1][1]*y

class RobotArmMultiDOF:
    def __init__(self, base_pos=(0,0), control_type="closed_loop", color_scheme="cyan"):
        self.base_x, self.base_y = base_pos
        self.lengths = [130, 90, 60]
        self.joint_angles = [0, 0, 0]
        self.control_type = control_type
        self.color_scheme = color_scheme
        
        self.t = 0
        
        # Closed-loop controller parameters (Lie algebra based)
        self.kp = 0.18 if control_type == "closed_loop" else 0.05
        
        # SO(3) rotation angle
        self.SO3_theta = 0
        
        # End effector trajectory history
        self.end_effector_path = []
        self.max_path_length = 200
        
        # Performance metrics
        self.error_history = []
        self.max_error_history = 100

    def generate_target_angles(self, t):
        """Multi-DOF trajectory planning with combined periodic motion"""
        a1 = math.sin(t * 0.6) * math.pi / 3
        a2 = math.sin(t * 0.9 + 1) * math.pi / 5
        a3 = math.sin(t * 1.2 + 2) * math.pi / 7
        return [a1, a2, a3]

    def get_joint_positions(self):
        positions = [(self.base_x, self.base_y, 0)]
        x, y = self.base_x, self.base_y
        total_theta = 0
        z = 0
        for i, (length, angle) in enumerate(zip(self.lengths, self.joint_angles)):
            total_theta += angle
            nx, ny = SO2LieGroup.apply_rotation(total_theta, length, 0)
            x += nx
            y += ny
            if i == len(self.lengths) - 1:
                z = 45 * math.sin(self.SO3_theta + x * 0.05)
            else:
                z = 0
            positions.append((x, y, z))
        return positions
    
    def step_control(self):
        target_angles = self.generate_target_angles(self.t)
        diffs = [target - curr for target, curr in zip(target_angles, self.joint_angles)]
        
        # Calculate tracking error
        error = math.sqrt(sum(d*d for d in diffs))
        self.error_history.append(error)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        # Lie algebra based angular velocity control
        angular_velocities = [self.kp * diff for diff in diffs]
        
        for i in range(len(self.joint_angles)):
            self.joint_angles[i] += angular_velocities[i]
            self.joint_angles[i] = math.atan2(math.sin(self.joint_angles[i]), 
                                             math.cos(self.joint_angles[i]))
        
        self.SO3_theta += 0.06
        self.t += 0.1
    
    def get_avg_error(self):
        if not self.error_history:
            return 0
        return sum(self.error_history) / len(self.error_history)

class DualArmAnimation:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(1200, 850)
        self.screen.bgcolor("#0a0a0a")
        self.screen.title("Dual Robot Arms: Lie Algebra Controller vs Open-Loop Control")

        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)

        # Left arm: Lie algebra closed-loop controller
        self.robot_left = RobotArmMultiDOF(
            base_pos=(-250, -200), 
            control_type="closed_loop",
            color_scheme="cyan"
        )
        
        # Right arm: Simple open-loop controller
        self.robot_right = RobotArmMultiDOF(
            base_pos=(250, -200), 
            control_type="open_loop",
            color_scheme="orange"
        )
        
        self.paused = False
        self.frame_count = 0

        self.bind_keys()
        self.screen.tracer(0, 0)
        self.animate()
        self.screen.mainloop()

    def draw_background_grid(self):
        """Draw decorative background grid"""
        self.t.pensize(1)
        self.t.color("#1a1a1a")
        
        # Vertical lines
        for x in range(-550, 600, 50):
            self.t.penup()
            self.t.goto(x, -400)
            self.t.pendown()
            self.t.goto(x, 400)
        
        # Horizontal lines
        for y in range(-400, 450, 50):
            self.t.penup()
            self.t.goto(-550, y)
            self.t.pendown()
            self.t.goto(550, y)

    def draw_arm(self, robot, rainbow_offset=0):
        positions = robot.get_joint_positions()
        
        # Determine color scheme
        if robot.color_scheme == "cyan":
            arm_color = "#00d4ff"
            joint_color = "#ffff00"
            glow_color = "#00ffff"
        else:
            arm_color = "#ff8800"
            joint_color = "#ff00ff"
            glow_color = "#ffaa00"
        
        # Draw arm segments with glow effect
        self.t.pensize(10)
        self.t.color("#222222")
        self.t.penup()
        self.t.goto(positions[0][0], positions[0][1])
        self.t.pendown()
        for pos in positions[1:]:
            self.t.goto(pos[0], pos[1])
        
        self.t.pensize(6)
        self.t.color(arm_color)
        self.t.penup()
        self.t.goto(positions[0][0], positions[0][1])
        self.t.pendown()
        for pos in positions[1:]:
            self.t.goto(pos[0], pos[1])

        # Draw joints
        for i, pos in enumerate(positions):
            self.t.penup()
            self.t.goto(pos[0], pos[1])
            # Outer glow
            self.t.dot(24, "#444444")
            # Inner joint
            self.t.dot(18, joint_color)

        # Record and draw end effector trajectory with rainbow gradient
        end_pos = positions[-1]
        robot.end_effector_path.append(end_pos)
        if len(robot.end_effector_path) > robot.max_path_length:
            robot.end_effector_path.pop(0)
        
        path_len = len(robot.end_effector_path)
        for i, pt in enumerate(robot.end_effector_path):
            # Rainbow gradient based on position in path
            hue = ((i / path_len) * 360 + rainbow_offset) % 360
            r, g, b = hsv_to_rgb(hue, 0.8, 0.9)
            col = rgb_to_hex(r, g, b)
            self.t.penup()
            self.t.goto(pt[0], pt[1])
            self.t.pendown()
            alpha = (i / path_len)
            size = 4 + int(4 * alpha)
            self.t.dot(size, col)

        # Z-axis height visualization
        for i, pos in enumerate(positions):
            intensity = 127 + int(128 * math.sin(robot.SO3_theta + i + pos[0]*0.02))
            col = rgb_to_hex(intensity, intensity, 255 - intensity)
            self.t.penup()
            self.t.goto(pos[0], pos[1] - 30)
            self.t.pendown()
            self.t.dot(10, col)

    def draw_info_panel(self):
        """Draw information panel with performance metrics"""
        # Title
        self.t.penup()
        self.t.goto(-580, 380)
        self.t.color("#00ffff")
        self.t.write("Multi-DOF Robot Arms: Lie Algebra Control & SO(3) Demonstration", 
                    font=("Arial", 16, "bold"))
        
        # Left arm info
        self.t.goto(-580, 340)
        self.t.color("#00d4ff")
        self.t.write("LEFT ARM: Lie Algebra Closed-Loop Controller", 
                    font=("Arial", 13, "bold"))
        
        self.t.goto(-580, 315)
        self.t.color("#aaaaaa")
        self.t.write(f"• Kp gain: {self.robot_left.kp:.2f}", 
                    font=("Arial", 11, "normal"))
        
        self.t.goto(-580, 295)
        self.t.write(f"• Avg tracking error: {self.robot_left.get_avg_error():.4f} rad", 
                    font=("Arial", 11, "normal"))
        
        # Right arm info
        self.t.goto(50, 340)
        self.t.color("#ff8800")
        self.t.write("RIGHT ARM: Open-Loop Controller", 
                    font=("Arial", 13, "bold"))
        
        self.t.goto(50, 315)
        self.t.color("#aaaaaa")
        self.t.write(f"• Kp gain: {self.robot_right.kp:.2f}", 
                    font=("Arial", 11, "normal"))
        
        self.t.goto(50, 295)
        self.t.write(f"• Avg tracking error: {self.robot_right.get_avg_error():.4f} rad", 
                    font=("Arial", 11, "normal"))
        
        # Instructions
        self.t.goto(-580, 260)
        self.t.color("#ffff00")
        self.t.write("Controls: [SPACE] Pause/Resume", 
                    font=("Arial", 12, "normal"))
        
        # Footer info
        self.t.goto(-580, 230)
        self.t.color("#888888")
        self.t.write("Rainbow trails show end-effector paths | Color depth shows SO(3) Z-axis rotation", 
                    font=("Arial", 10, "italic"))

    def animate(self):
        if not self.paused:
            self.robot_left.step_control()
            self.robot_right.step_control()
            
            self.t.clear()
            self.draw_background_grid()
            
            # Draw center divider
            self.t.pensize(2)
            self.t.color("#333333")
            self.t.penup()
            self.t.goto(0, -400)
            self.t.pendown()
            self.t.goto(0, 400)
            
            self.draw_arm(self.robot_left, rainbow_offset=0)
            self.draw_arm(self.robot_right, rainbow_offset=180)
            self.draw_info_panel()
            
            self.screen.update()
            self.frame_count += 1
        
        self.screen.ontimer(self.animate, 20)

    def toggle_pause(self):
        self.paused = not self.paused

    def bind_keys(self):
        self.screen.listen()
        self.screen.onkey(self.toggle_pause, "space")

if __name__ == "__main__":
    DualArmAnimation()
