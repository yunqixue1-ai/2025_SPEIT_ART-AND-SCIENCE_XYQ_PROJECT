import turtle as t
import math

t.bgcolor("black")
t.speed(0)
t.colormode(255)
t.pensize(2)
t.hideturtle()
t.tracer(0)

# 复数坐标类，用于矩阵与群作用模拟
class ComplexPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def rotate(self, angle_deg):
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        x_new = cos_a * self.x - sin_a * self.y
        y_new = sin_a * self.x + cos_a * self.y
        return ComplexPoint(x_new, y_new)
    
    def scale(self, factor):
        return ComplexPoint(self.x * factor, self.y * factor)
    
    def translate(self, dx, dy):
        return ComplexPoint(self.x + dx, self.y + dy)
    
    def to_tuple(self):
        return (self.x, self.y)

def smooth_color(step, total, offset=0):
    # 带偏移的HSV样式色环循环
    r = int((math.sin(2 * math.pi * (step/total) + offset) * 127) + 128)
    g = int((math.sin(2 * math.pi * (step/total) + offset + 2*math.pi/3) * 127) + 128)
    b = int((math.sin(2 * math.pi * (step/total) + offset + 4*math.pi/3) * 127) + 128)
    return r, g, b

def draw_point(p, color=(255,255,255), size=3):
    t.penup()
    t.goto(p.x, p.y)
    t.pendown()
    t.dot(size, color)

def group_action_demo():
    # 两个生成元旋转角度，模拟C_n x C_m 的直积群作用
    gen1_angle = 30  # 第一个生成元旋转角度
    gen2_angle = 60  # 第二个生成元旋转角度
    order_1 = 12
    order_2 = 6
    
    base_point = ComplexPoint(100, 0)
    
    size = 4
    total_steps = order_1 * order_2

    # 用二维嵌套循环模拟群的元素，由两个生成元组成
    for i in range(order_1):
        # 定义第一个生成元作用
        point_after_g1 = base_point.rotate(gen1_angle * i)

        # 置换颜色偏移体现群元素交换，colors随着i,j置换偏移
        color_offset = (2 * math.pi / order_1) * i
        
        for j in range(order_2):
            # 定义第二个生成元的作用，也就是组合群作用
            final_point = point_after_g1.rotate(gen2_angle * j)
            # 轻微缩放，制造层次感
            scaled_point = final_point.scale(1 - 0.03 * j)

            r, g, b = smooth_color(i * order_2 + j, total_steps, offset=color_offset)

            # 点大小维持基本尺寸，j越大点略小
            draw_point(scaled_point, (r, g, b), size=max(size - j*0.4, 1))

            # 动态更新绘制提高流畅度
            if (i*order_2 + j) % 6 == 0:
                t.update()

def main():
    group_action_demo()
    t.update()

if __name__ == '__main__':
    main()
    t.done()
