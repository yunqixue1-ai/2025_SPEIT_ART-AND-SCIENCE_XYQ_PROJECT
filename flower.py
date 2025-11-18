import turtle
import random

def petal(t, radius, angle):
    for i in range(2):
        t.circle(radius, angle)
        t.left(180 - angle)
        
def flower(t, n, radius, angle):
    for i in range(n):
        petal(t, radius, angle)
        t.left(360.0 / n)

def move(t, x, y):
    t.penup()
    t.goto(x, y)
    t.pendown()

def random_flower(t):
    # 随机颜色
    colors = ["red", "blue", "purple", "pink", "orange", "violet", "maroon", "magenta", "cyan", "crimson"]
    t.color(random.choice(colors))
    
    # 随机花瓣数、角度半径参数
    petals = random.randint(5, 12)          # 花瓣数 5~12
    radius = random.uniform(20, 80)         # 花瓣半径 20~80
    angle = random.uniform(30, 80)          # 花瓣弧度 30~80
    
    t.begin_fill()
    flower(t, petals, radius, angle)
    t.end_fill()

def draw_flower_cluster(t, count=30, width=600, height=400):
    # 在指定区域内绘制count朵花
    for _ in range(count):
        x = random.randint(-width//2, width//2)
        y = random.randint(-height//2, height//2 - 50)  # 留点上方空白
        move(t, x, y)
        random_flower(t)

def main():
    screen = turtle.Screen()
    screen.bgcolor("lightyellow")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.width(2)

    draw_flower_cluster(t, count=40, width=800, height=600)

    screen.mainloop()

if __name__ == "__main__":
    main()
