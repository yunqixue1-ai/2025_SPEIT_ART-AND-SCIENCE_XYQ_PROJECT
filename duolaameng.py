import turtle as t

# 初始化设置（保证绘制稳定）
t.colormode(255)
t.speed(10)
t.screensize(600, 600, "white")
t.setup(600, 600)
t.title("稳定版Q版哆啦A梦")
t.hideturtle()

# 工具函数：移动画笔
def move(x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()

# 1. 头部（正圆，稳定核心）
move(0, -150)
t.pencolor("black")
t.fillcolor("#1E90FF")  # 哆啦A梦蓝
t.begin_fill()
t.circle(150)
t.end_fill()

# 2. 脸部（白色椭圆，简单几何）
move(0, -50)
t.fillcolor("white")
t.begin_fill()
t.circle(100)
t.end_fill()

# 3. 眼睛（两个正圆，对称稳定）
# 左眼
move(-40, 60)
t.fillcolor("white")
t.begin_fill()
t.circle(25)
t.end_fill()
move(-40, 70)
t.fillcolor("black")
t.begin_fill()
t.circle(10)
t.end_fill()
move(-35, 80)
t.fillcolor("white")
t.begin_fill()
t.circle(5)
t.end_fill()

# 右眼
move(40, 60)
t.fillcolor("white")
t.begin_fill()
t.circle(25)
t.end_fill()
move(40, 70)
t.fillcolor("black")
t.begin_fill()
t.circle(10)
t.end_fill()
move(35, 80)
t.fillcolor("white")
t.begin_fill()
t.circle(5)
t.end_fill()

# 4. 鼻子（红色正圆+短线）
move(0, 30)
t.fillcolor("#FF0000")
t.begin_fill()
t.circle(15)
t.end_fill()
move(0, 15)
t.pensize(3)
t.goto(0, -20)

# 5. 嘴巴（简单圆弧，不易出错）
move(-50, -20)
t.pensize(2)
t.setheading(-60)
t.circle(60, 120)

# 6. 胡须（直线，稳定无偏差）
move(-50, 20)
t.setheading(0)
t.forward(40)
move(-50, 0)
t.forward(45)
move(-50, -20)
t.forward(40)

move(50, 20)
t.setheading(180)
t.forward(40)
move(50, 0)
t.forward(45)
move(50, -20)
t.forward(40)

# 7. 铃铛（黄色正圆+细节）
move(0, -150)
t.fillcolor("#FFD700")
t.begin_fill()
t.circle(20)
t.end_fill()
move(0, -150)
t.pencolor("black")
t.pensize(2)
t.goto(0, -170)
move(-10, -160)
t.setheading(0)
t.forward(20)

t.done()