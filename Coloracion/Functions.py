import Sudoku as sk
import Graph as gp
from timeit import default_timer as timer
import math

colors = ["#FFFFFF", "#FF0000", "#00FF00", "#008FFF", "#FFFF00", "#FF00FF", "#00FFFF", "#FF8F00", "#FF008F", "#8F00FF"]

def S2G (sudo): # Sudoku to Graph
    n = sudo.lvl
    N = n * n
    G = gp.Graph()
    
    for square in sudo.squares:
        a = gp.Node("{0}{1}".format(square.x, square.y))
        a.set_color(colors[square.value])
        G.add_node(a)
    
    for node in G.nodes:
        i = int(node.name[0])
        j = int(node.name[1])
        
        for k in range(j+1, N):
            G.add_edge(node, G.nodes[i*N + k])
        
        for k in range(i+1, N):
            G.add_edge(node, G.nodes[k*N + j])
           
        a = list(range(-(i%n), n-(i%n)))
        b = list(range(-(j%n), n-(j%n)))
        for k in a:
            for l in b:
                edge = (node, G.nodes[(i+k)*N + j+l])
                if (k != 0 or l != 0) and (edge not in G.edges and (edge[1], edge[0]) not in G.edges):
                    G.add_edge(edge[0], edge[1])
    return G

def nd_w_sm_clr (graph): # nodes with same color
    l = []
    for color in colors:
        aux = []
        for node in graph.nodes:
            if node.color == color:
                aux.append(node.name)
        l.append(aux)
    return l

def chrom (graph, node): # return the namber of neighbors colored
    clr = colors[1:].copy()
    x = 0
    l = graph.neighbors(node)
    for n in l:
        if n.color in clr:
            clr.remove(n.color)
            x += 1
    return x
    
def coloring (graph):
    x = int(math.sqrt(len(graph.nodes)))
    
    node = graph.nodes[0]
    a = chrom(graph, node)
    
    while len(nd_w_sm_clr(graph)[0]) > 0:
        avail_clrs = colors[1:x+1].copy()
        
        for n in graph.nodes:
            b = chrom(graph, n)
            if n.color == "#FFFFFF" and b > a:
                a = b
                node = n
        
        neighbors = graph.neighbors(node)
        for n in neighbors:
            if n.color in avail_clrs:
                avail_clrs.remove(n.color)
        
        node.set_color(avail_clrs[0])
        a = 0
        

def G2S (graph):
    n = math.sqrt(math.sqrt(len(graph.nodes)))
    S = sk.Sudoku(int(n))
    
    for node in graph.nodes:
        S.set_in(colors.index(node.color), int(node.name[0]), int(node.name[1]))
    
    return S
    

if __name__ == "__main__":
    '''s = sk.Sudoku(2)
    
    s.set_in(3, 1, 0)
    s.set_in(2, 1, 2)
    s.set_in(1, 2, 1)
    s.set_in(4, 2, 3)
    
    print(s)
    
    g = S2G(s)
    start = timer()
    coloring(g)
    print("Time: ", timer() - start)
    
    
    z = G2S(g)
    print(z)
    print(z.solved())
    print(nd_w_sm_clr(g))
    '''
    s = sk.Sudoku(3)
    
    s.set_in(5, 0, 0)
    s.set_in(3, 0, 1)
    s.set_in(7, 0, 4)
    
    s.set_in(6, 1, 0)
    s.set_in(1, 1, 3)
    s.set_in(9, 1, 4)
    s.set_in(5, 1, 5)
    
    s.set_in(9, 2, 1)
    s.set_in(8, 2, 2)
    s.set_in(6, 2, 7)
    
    s.set_in(8, 3, 0)
    s.set_in(6, 3, 4)
    s.set_in(3, 3, 8)
    
    s.set_in(4, 4, 0)
    s.set_in(8, 4, 3)
    s.set_in(3, 4, 5)
    s.set_in(1, 4, 8)
    
    s.set_in(7, 5, 0)
    s.set_in(2, 5, 4)
    s.set_in(6, 5, 8)
    
    s.set_in(6, 6, 1)
    s.set_in(2, 6, 6)
    s.set_in(8, 6, 7)
    
    s.set_in(4, 7, 3)
    s.set_in(1, 7, 4)
    s.set_in(9, 7, 5)
    s.set_in(5, 7, 8)
    
    s.set_in(8, 8, 4)
    s.set_in(7, 8, 7)
    s.set_in(9, 8, 8)

    g = S2G(s)
    print(nd_w_sm_clr(g))
    print(s)
    
    start = timer()
    coloring(g)
    print("Time: ", timer() - start)
    
    z = G2S(g)
    print(z)
    print(z.solved())
    print(nd_w_sm_clr(g))