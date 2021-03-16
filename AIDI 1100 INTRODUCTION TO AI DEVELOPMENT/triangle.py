from turtle import *
import queue
color('red', 'yellow')
begin_fill()

def triangle(position, dd):
    q = queue.Queue()
    q.put((position, dd))
    d = dd
    while not q.empty() and d > 5:
        front =q.get()
        position = front[0]
        up()
        setpos(position)
        down()
        print(position)
        seth(180)
        d = front[1]
        left(60)
        forward(d)
        
        left(120)
        forward(d)
        left(120)
        forward(d)
        q.put((position, d/2))
        q.put((position + Vec2D(-d/4, -d* 3 ** 0.5 / 4), d/2))
        q.put((position + Vec2D(d/4, -d* 3 ** 0.5 / 4 ), d/2))

triangle(Vec2D(0, 0) ,400)

end_fill()
done()
