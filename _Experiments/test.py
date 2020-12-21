import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots(1, 2)
ax[0].set_xlim(0, 10)
ax[0].set_ylim(0, 10)

def update_points(frame, points, data):
    points.set_offsets(data[..., frame])
    return [points]

class food():

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"{self.x}, {self.y}"

    def __repr__(self):
        return f"{self.x}, {self.y}"

    def loc(self):
        return self.x, self.y

data = np.array([np.arange(0, 10, 0.1), np.arange(0, 10, 0.1)])
foods = [food(5, 5)]
s = ax[0].scatter([], [])
# f = ax[0].scatter(*foods[0].loc()) #this won't work with food list greater than 1, it's just a test.
# b = ax[1].bar([0], [len[foods]])
point_ani = animation.FuncAnimation(fig, update_points, 100, fargs=(s, data),
                                   interval=50, blit=True)
plt.show()
