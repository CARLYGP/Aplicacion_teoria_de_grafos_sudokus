class Node:
    
    def __init__ (self, name):
        self.name = name
        self.color = ""
        
    def set_color (self, color):
        self.color = color
        
    def __str__ (self):
        r = "Node: " + self.name + "    " + "Color: " + self.color
        return r

class Graph:
    
    def __init__ (self):
        self.nodes = []
        self.edges = []
        
    def add_node (self, node):
        self.nodes.append(node)
        
    def add_edge (self, node1, node2):
        if node1 in self.nodes and node2 in self.nodes:
            self.edges.append((node1, node2))
        
    def neighbors (self, node):
        nbs = []
        if node in self.nodes:
            for edge in self.edges:
                if node in edge:
                    for n in edge:
                        if n != node:
                            nbs.append(n)
        else: print("no existe")
        return nbs
        
    def __str__ (self):
        r = "----------Nodes-----------\n"
        for node in self.nodes:
            r += str(node) + "\n"
        r += "---------Edges-----------\n"
        for edge in self.edges:
            r += "(" + edge[0].name + ", " + edge[1].name + ")" + "\n"
        return r

if __name__ == "__main__":
    a = Node("00")
    b = Node("01")
    c = Node("02")
    d = Node("03")
    e = Node("04")
    
    a.set_color("#000000")
    
    g = Graph()
    
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_node(d)
    g.add_node(e)
    
    g.add_edge(a, b)
    
    print(g)
    
    print(type(g.neighbors(g.nodes[0])))