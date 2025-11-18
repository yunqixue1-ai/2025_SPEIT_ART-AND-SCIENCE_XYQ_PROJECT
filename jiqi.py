import turtle
import math

class SO2LieGroup:
    """二维旋转群 SO(2)"""
    @staticmethod
    def rotation_matrix(theta):
        c, s = math.cos(theta), math.sin(theta)
        return [[c, -s],
                [s,  c]]
    
    @staticmethod
    def apply_rotation(theta, x, y):
        R = SO2LieGroup.rotation_matrix(theta)
        new_x = R[0][0] * x + R[0][1] * y
        new_y = R[1][0] * x + R[1][1] * y
        return new_x, new_y

class RobotArm:
    """机械臂结构，父臂和子臂链"""
    def __init__(self, base_pos=(0, 0)):
        self.base_x, self.base_y = base_pos
        # 定义臂段长度
        self.lengths = [150, 100, 70]
        # 当前主臂旋转角度
        self.theta = 0
        # 子臂相对角度：李代数小角度，模拟速度方向
        self.sub_angles = [0, 0]
    
    def update_angles(self, d_theta, d_subs):
        """更新角速度和子臂相对角度"""
        self.theta += d_theta
        # 限制子臂角度范围，模拟小变动（李代数微小旋转）
        for i in range(len(self.sub_angles)):
            self.sub_angles[i] += d_subs[i]
            self.sub_angles[i] = max(min(self.sub_angles[i], 0.5), -0.5)  # 限制范围
    
    def get_positions(self):
        """计算所有关节位置"""
        # 主臂端点
        x1, y1 = SO2LieGroup.apply_rotation(self.theta, self.lengths[0], 0)
        x1 += self.base_x
        y1 += self.base_y
        
        # 子臂1相对于主臂旋转：θ + sub1
        angle2 = self.theta + self.sub_angles[0]
        x2, y2 = SO2LieGroup.apply_rotation(angle2, self.lengths[1], 0)
        x2 += x1
        y2 += y1
        
        # 子臂2相对于子臂1旋转：θ + sub1 + sub2
        angle3 = angle2 + self.sub_angles[1]
        x3, y3 = SO2LieGroup.apply_rotation(angle3, self.lengths[2], 0)
        x3 += x2
        y3 += y2
        
        return [(self.base_x, self.base_y), (x1, y1), (x2, y2), (x3, y3)]

class LieGroupAnimation:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(900, 700)
        self.screen.bgcolor("black")
        self.screen.title("李群 SO(2) 与 机器人臂动态展示")
        self.screen.tracer(0)
        
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.width(4)

        self.arm = RobotArm()
        
        # 控制参数
        self.main_rot_speed = 0.03  # 主臂转速（弧度/帧）
        self.sub_rot_speeds = [0.01, -0.015]  # 子臂微角速度
        
        self.paused = False
        
        self.bind_keys()
        self.screen.ontimer(self.animate, 50)
        self.screen.mainloop()
    
    def draw_arm(self):
        positions = self.arm.get_positions()
        self.t.clear()

        # 画坐标轴
        self.t.penup()
        self.t.goto(-400, 0)
        self.t.pendown()
        self.t.color("gray")
        self.t.pensize(1)
        self.t.goto(400, 0)
        self.t.penup()
        self.t.goto(0, -350)
        self.t.pendown()
        self.t.goto(0, 350)

        # 画臂段
        self.t.pensize(6)
        base_color = "cyan"
        joint_color = "yellow"
        
        # 基点
        self.t.penup()
        self.t.goto(positions[0])
        self.t.pendown()
        self.t.dot(15, joint_color)
        
        # 逐节画臂段连接线和关节
        for i in range(1, len(positions)):
            self.t.color(base_color)
            self.t.penup()
            self.t.goto(positions[i-1])
            self.t.pendown()
            self.t.goto(positions[i])
            
            self.t.penup()
            self.t.goto(positions[i])
            self.t.pendown()
            self.t.dot(10, joint_color)
        
        # 画李代数速度向量展示(主臂和子臂的微小转动箭头)
        self.draw_lie_algebra_vectors(positions)
        
        # 说明文字
        self.draw_texts()
        self.screen.update()
    
    def draw_lie_algebra_vectors(self, positions):
        """画李代数微小旋转‘速度’向量"""
        self.t.width(3)
        scale = 80
        
        # 主臂旋转速度箭头（围绕基点)
        base_x, base_y = positions[0]
        self.t.color("magenta")
        self.t.penup()
        self.t.goto(base_x, base_y)
        self.t.setheading(math.degrees(self.arm.theta) + 90)  # 垂直主臂方向
        self.t.pendown()
        self.t.forward(self.main_rot_speed * scale * 20)
        self.t.penup()
        self.t.goto(base_x, base_y)
        
        # 子臂1相对旋转速度箭头（围绕第1关节）
        joint1 = positions[1]
        angle1 = math.degrees(self.arm.theta + 90)
        self.t.color("orange")
        self.t.goto(joint1)
        self.t.setheading(angle1)
        self.t.pendown()
        self.t.forward(self.sub_rot_speeds[0] * scale * 50)
        self.t.penup()
        self.t.goto(joint1)

        # 子臂2相对旋转速度箭头（围绕第2关节）
        joint2 = positions[2]
        angle2 = math.degrees(self.arm.theta + self.arm.sub_angles[0] + 90)
        self.t.color("lime")
        self.t.goto(joint2)
        self.t.setheading(angle2)
        self.t.pendown()
        self.t.forward(self.sub_rot_speeds[1] * scale * 50)
        self.t.penup()
        self.t.goto(joint2)
    
    def draw_texts(self):
        lines = [
            "李群 SO(2) 与机器人手臂动态展示",
            "主臂旋转○ 李代数（微小旋转速率）箭头 → 子臂旋转",
            "按空格暂停/继续，←→调主臂旋转速度，↑↓调子臂旋转速度",
            f"主臂转速: {self.main_rot_speed:.3f} rad/帧",
            f"子臂1速率: {self.sub_rot_speeds[0]:.3f} rad/帧",
            f"子臂2速率: {self.sub_rot_speeds[1]:.3f} rad/帧"
        ]
        
        self.t.penup()
        self.t.goto(-430, 320)
        self.t.color("white")
        self.t.pensize(1)
        for i, l in enumerate(lines):
            self.t.goto(-430, 320 - 20 * i)
            self.t.write(l, font=("Arial", 12, "normal"))

    def animate(self):
        if not self.paused:
            self.arm.update_angles(self.main_rot_speed, self.sub_rot_speeds)
            self.draw_arm()
        self.screen.ontimer(self.animate, 50)
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def increase_main_speed(self):
        self.main_rot_speed += 0.005
    
    def decrease_main_speed(self):
        self.main_rot_speed = max(0, self.main_rot_speed - 0.005)
    
    def increase_sub_speed1(self):
        self.sub_rot_speeds[0] += 0.001
    
    def decrease_sub_speed1(self):
        self.sub_rot_speeds[0] -= 0.001
    
    def increase_sub_speed2(self):
        self.sub_rot_speeds[1] += 0.001
    
    def decrease_sub_speed2(self):
        self.sub_rot_speeds[1] -= 0.001
    
    def bind_keys(self):
        self.screen.listen()
        self.screen.onkey(self.toggle_pause, "space")
        self.screen.onkey(self.increase_main_speed, "Right")
        self.screen.onkey(self.decrease_main_speed, "Left")
        self.screen.onkey(self.increase_sub_speed1, "Up")
        self.screen.onkey(self.decrease_sub_speed1, "Down")
        self.screen.onkey(self.increase_sub_speed2, "w")
        self.screen.onkey(self.decrease_sub_speed2, "s")

if __name__ == "__main__":
    LieGroupAnimation()
