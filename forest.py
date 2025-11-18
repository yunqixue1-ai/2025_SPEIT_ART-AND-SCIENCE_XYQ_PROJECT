import turtle as t
import random

# 初始化设置
t.colormode(255)
t.speed(0)  # 最快速度
t.screensize(1000, 600, "#87CEEB")  # 天空蓝背景
t.setup(1000, 600)
t.title("稳定版树林场景")
t.hideturtle()

def move(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()

# 1. 绘制草地（底部矩形，稳定）
move(-500, -300)
t.fillcolor("#32CD32")
t.begin_fill()
t.setheading(0)
t.forward(1000)
t.setheading(90)
t.forward(100)
t.setheading(180)
t.forward(1000)
t.end_fill()

# 2. 绘制单棵树（封装函数，稳定复用）
def draw_tree(x, y, height, color):
    # 树干（矩形，稳定无偏差）
    move(x, y)
    t.fillcolor("#8B4513")
    t.begin_fill()
    t.setheading(90)
    t.forward(height * 0.2)  # 树干高度=树总高的20%
    t.setheading(0)
    t.forward(height * 0.05)
    t.setheading(-90)
    t.forward(height * 0.2)
    t.setheading(180)
    t.forward(height * 0.05)
    t.end_fill()
    
    # 树冠（三层三角形，稳定组合）
    crown_size = height * 0.4  # 树冠大小=树总高的40%
    # 上层树冠
    move(x - crown_size/2, y + height * 0.2)
    t.fillcolor(color)
    t.begin_fill()
    t.setheading(90)
    t.forward(crown_size)
    t.setheading(-30)
    t.forward(crown_size)
    t.setheading(210)
    t.forward(crown_size)
    t.end_fill()
    
    # 中层树冠
    move(x - crown_size*0.6/2, y + height * 0.2 + crown_size*0.3)
    t.begin_fill()
    t.setheading(90)
    t.forward(crown_size * 0.8)
    t.setheading(-30)
    t.forward(crown_size * 0.8)
    t.setheading(210)
    t.forward(crown_size * 0.8)
    t.end_fill()
    
    # 下层树冠
    move(x - crown_size*0.7/2, y + height * 0.2 + crown_size*0.3 + crown_size*0.8*0.3)
    t.begin_fill()
    t.setheading(90)
    t.forward(crown_size * 0.6)
    t.setheading(-30)
    t.forward(crown_size * 0.6)
    t.setheading(210)
    t.forward(crown_size * 0.6)
    t.end_fill()

# 3. 批量生成树林（随机位置+高度，稳定不重叠）
tree_colors = ["#228B22", "#006400", "#008000", "#2E8B57"]  # 多种绿色，自然
for _ in range(30):  # 生成30棵树
    x = random.randint(-450, 450)  # x轴范围
    y = random.randint(-300, -200)  # y轴在草地范围内
    height = random.randint(80, 200)  # 树高随机
    color = random.choice(tree_colors)
    draw_tree(x, y, height, color)

# 4. 绘制太阳（右上角，稳定点缀）
move(400, 200)
t.fillcolor("#FFD700")
t.begin_fill()
t.circle(30)
t.end_fill()
# 太阳光芒（直线，稳定）
for angle in range(0, 360, 30):
    move(400, 200)
    t.setheading(angle)
    t.forward(40)

t.done()