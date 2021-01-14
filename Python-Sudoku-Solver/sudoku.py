import numpy as np
# Creates a list containing 5 lists, each of 8 items, all set to 0
grid = np.loadtxt("output.txt").reshape(9, 9)

grid = grid.astype(int)
print(grid)

def possible(y,x,n):
    global grid
    for i in range(0,9):
        if grid[y][i] == n :
            return False
    for i in range(0,9):
        if grid[i][x] == n :
            return False
    x0 = (x//3)*3
    y0 = (y//3)*3
    for i in range(0,3) :
        for j in range(0,3) : 
            if grid[y0+i][x0+j] == n :
                return False
    return True


print("before change\n", grid)

numberOfUnknown = 30
rand = np.random.randint(1,9,numberOfUnknown) 
for i in range(numberOfUnknown):
    rand2 = np.random.randint(1,9)
    #print(grid[rand[i]][rand2])
    grid[rand[i]][rand2] = 0

print("after change\n", grid)

def solve():
    global grid
    for y in range(9):
        for x in range(9):
            if grid[y][x] == 0:
                for n in range(1,10):
                    if possible(y,x,n):
                        grid[y][x] = n
                        solve()
                        grid[y][x] = 0
                return
    print(np.matrix(grid))
    input("More?")

solve()
