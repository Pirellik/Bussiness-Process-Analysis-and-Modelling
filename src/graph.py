import graphviz
 
class MyGraph(graphviz.Digraph):
 
    def __init__(self, *args):
        super(MyGraph, self).__init__(*args)
        self.graph_attr['rankdir'] = 'LR'
        self.node_attr['shape'] = 'Mrecord'
        self.graph_attr['splines'] = 'ortho'
        self.graph_attr['nodesep'] = '0.8'
        self.edge_attr.update(penwidth='2')
 
    def add_event(self, name):
        super(MyGraph, self).node(name, shape="circle", label="")
 
    def add_and_gateway(self, *args):
        super(MyGraph, self).node(*args, shape="diamond",
                                  width=".6",height=".6",
                                  fixedsize="true",
                                  fontsize="40",label="+")
 
    def add_xor_gateway(self, *args, **kwargs):
        super(MyGraph, self).node(*args, shape="diamond",
                                  width=".6",height=".6",
                                  fixedsize="true",
                                  fontsize="35",label="×")
 
    def add_and_split_gateway(self, source, targets, *args):
        gateway = 'ANDs '+str(source)+'->'+str(targets)        
        self.add_and_gateway(gateway,*args)
        super(MyGraph, self).edge(source, gateway)
        for target in targets:
            super(MyGraph, self).edge(gateway, target)
 
    def add_xor_split_gateway(self, source, targets, *args):
        gateway = 'XORs '+str(source)+'->'+str(targets) 
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).edge(source, gateway)
        for target in targets:
            super(MyGraph, self).edge(gateway, target)
 
    def add_and_merge_gateway(self, sources, target, *args):
        gateway = 'ANDm '+str(sources)+'->'+str(target)
        self.add_and_gateway(gateway,*args)
        super(MyGraph, self).edge(gateway,target)
        for source in sources:
            super(MyGraph, self).edge(source, gateway)
 
    def add_xor_merge_gateway(self, sources, target, *args):
        gateway = 'XORm '+str(sources)+'->'+str(target)
        self.add_xor_gateway(gateway, *args)
        super(MyGraph, self).edge(gateway,target)
        for source in sources:
            super(MyGraph, self).edge(source, gateway)

    def add_one_loop(self, event, matrix, *args):
        inAdded = False
        outAdded = False 
        outname = "1loop "+str(event)+" out"
        inname = "1loop "+str(event)+" in"
        if matrix['IN'][event] == event:
            self.add_xor_gateway(inname, *args)
            matrix['IN'][event] = inname
            inAdded = True
        if matrix['OUT'][event] == event:            
            self.add_xor_gateway(outname, *args)
            matrix['OUT'][event] = outname
            outAdded = True
        super(MyGraph, self).edge(matrix['OUT'][event], matrix['IN'][event])
        if inAdded == True:
            super(MyGraph, self).edge(matrix['IN'][event],event)
        if outAdded == True:
            super(MyGraph, self).edge(event, matrix['OUT'][event])
        
    def add_two_loop(self, outevent, inevent, matrix, *args):
        inAdded = False
        outAdded = False
        outname = "2loop "+str(outevent)+str(inevent)+str(outevent)+" out"
        inname = "2loop "+str(outevent)+str(inevent)+str(outevent)+" in"   
        if matrix['IN'][outevent] == outevent:
            self.add_xor_gateway(inname, *args)
            matrix['IN'][outevent] = inname
            matrix['OUT'][inevent] = inname
            inAdded = True
        if matrix['OUT'][outevent] == outevent:
            self.add_xor_gateway(outname, *args) 
            matrix['OUT'][outevent] = outname
            matrix['IN'][inevent] = outname
            outAdded = True
        super(MyGraph, self).edge(matrix['OUT'][outevent], inevent)
        super(MyGraph, self).edge(inevent, matrix['IN'][outevent])
        if inAdded  == True:
            super(MyGraph, self).edge(matrix['IN'][outevent], outevent)
        if outAdded == True:
            super(MyGraph, self).edge(outevent,matrix['OUT'][outevent])