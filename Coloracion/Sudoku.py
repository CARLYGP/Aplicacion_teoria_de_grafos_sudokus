class Square:
    
    def __init__ (self, x, y):
        self.x = x
        self.y = y
        self.value = 0
        
    def set (self, val):
        self.value = val
        
    def __str__ (self):
        return str(self.value)
        
class Sudoku:
    
    def __init__ (self, n):
        self.lvl = n
        self.squares = [Square(i, j) for i in range(n*n) for j in range(n*n)]
    
    def set_in (self, val, x, y):
        n = self.lvl * self.lvl
        self.squares[x*n + y].set(val)
    
    def solved (self): #check if the Sudoku is solved
        n = self.lvl
        N = n*n
        for i in range(N):
            for j in range(N):
                val = self.squares[i*N + j].value
                if val == 0: return False
                
                # check in a row
                for k in range(j+1, n):
                    if self.squares[i*n + k] == val:
                        return False
                
                # check in a block
                a = list(range(-(i%n), n-(i%n)))
                b = list(range(-(j%n), n-(j%n)))
                for k in a:
                    for l in b:
                        if (k != 0 or l != 0) and self.squares[(i+k)*n + j+l] == val:
                            return False
                
                # check in a column
                val = self.squares[j*n + i].value
                for k in range(j+1, n):
                    if self.squares[i*n + k] == val:
                        return False
                
        return True
    
    def __str__ (self):
        n = self.lvl
        N = n*n
        r = ""
        for i in range(N):
            if i%n == 0 and i != 0:
                r += "-"*(n*N) + "\n"
            for j in range(N):
                r += str(self.squares[i*N + j]) + " "
                if (j+1)%n == 0 and j != N-1:
                    r += "| "
            r += "\n"
        return r
        
        
if __name__ == "__main__":
    s = Sudoku(2)
    
    s.set_in(4, 0, 1)
    s.set_in(2, 1, 2)
    s.set_in(2, 2, 1)
    s.set_in(1, 3, 2)
    
    print(str(s))
    print(s.solved())
    
    s.set_in(3, 0, 2)
    s.set_in(1, 0, 3)
    s.set_in(2, 0, 0)
    
    print(str(s))
    print(s.solved())
    
    s.set_in(4, 1, 3)
    s.set_in(1, 1, 1)
    s.set_in(3, 1, 0)
    
    print(str(s))
    print(s.solved())
    
    s.set_in(4, 2, 2)
    s.set_in(1, 2, 0)
    s.set_in(3, 2, 3)
    
    print(str(s))
    print(s.solved())
    
    s.set_in(4, 3, 0)
    s.set_in(3, 3, 1)
    s.set_in(2, 3, 3)
    
    print(str(s))
    print(s.solved())