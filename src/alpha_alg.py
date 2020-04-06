import itertools
import copy
from graph import MyGraph
from pm4py.objects.log.importer.xes import factory as xes_import
from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.visualization.petrinet import factory as pn_vis_factory



class AlphaAlgorithm:
    def __init__(self):
        self.log = None
        self.TL_set = None
        self.TI_set = None
        self.TO_set = None
        self.direct_followers_set = None
        self.causalities_dict = None
        self.inv_causalities_dict = None
        self.parallel_tasks_set = None
    
    def read_log_file(self, filepath):
        self.log = set()

        if filepath.endswith('.txt'):
            with open(filepath, 'r') as infile:
                for trace in infile.readlines():
                    self.log.add(tuple(trace.split()))
        elif filepath.endswith('.xes'):
            xes_log = xes_import.apply(filepath)
            for trace in xes_log:
                events = [x['concept:name'] for x in trace]
                self.log.add(tuple(events))
    
    def build_model(self):
        if self.log is None:
            print("ERROR: Read log file before building model.")
            return
        self._construct_TL_set()
        self._construct_TI_set()
        self._construct_TO_set()
        self._construct_direct_followers_set()
        self._construct_causalities_dict()
        self._construct_inv_causalities_dict()
        self._construct_parallel_tasks_set()

    def create_graph(self, filename='graph'):
        if self.log is None:
            print("ERROR: Read log file and build model before creating graph.")
            return
        elif self.TL_set is None:
            print("ERROR: Build model before creating graph.")
            return
        causality = self.causalities_dict
        parallel_events = self.parallel_tasks_set
        inv_causality = self.inv_causalities_dict

        G = MyGraph()

        # adding split gateways based on causality
        for event in causality.keys():
            if len(causality[event]) > 1:
                print('LEN', len(causality[event]))
                if tuple(causality[event]) in parallel_events:
                    G.add_and_split_gateway(event,causality[event])
                else:
                    G.add_xor_split_gateway(event,causality[event])

        # adding merge gateways based on inverted causality
        for event in inv_causality.keys():
            if len(inv_causality[event]) > 1:
                print('LEN', len(inv_causality[event]))
                if tuple(inv_causality[event]) in parallel_events:
                    G.add_and_merge_gateway(inv_causality[event],event)
                else:
                    G.add_xor_merge_gateway(inv_causality[event],event)
            elif len(inv_causality[event]) == 1:
                source = list(inv_causality[event])[0]
                G.edge(source,event)

        # adding start event
        G.add_event("start")
        if len(self.TI_set) > 1:
            if tuple(self.TI_set) in parallel_events: 
                G.add_and_split_gateway("start",self.TI_set)
            else:
                G.add_xor_split_gateway("start",self.TI_set)
        else: 
            G.edge("start",list(self.TI_set)[0])

        # adding end event
        G.add_event("end")
        if len(self.TO_set) > 1:
            if tuple(self.TO_set) in parallel_events: 
                G.add_and_merge_gateway(self.TO_set,"end")
            else:
                G.add_xor_merge_gateway(self.TO_set,"end")    
        else: 
            G.edge(list(self.TO_set)[0],"end")

        # G.format = 'svg'
        G.render('graphs/' + filename)
        G.view('graphs/' + filename)

    def _construct_TL_set(self):
        self.TL_set = set()
        for sequence in self.log:
            for task in sequence:
                self.TL_set.add(task)
    
    def _construct_TI_set(self):
        self.TI_set = set()
        for sequence in self.log:
            self.TI_set.add(sequence[0])

    def _construct_TO_set(self):
        self.TO_set = set()
        for sequence in self.log:
            self.TO_set.add(sequence[-1])

    def _construct_direct_followers_set(self):
        self.direct_followers_set = set()
        for sequence in self.log:
            for task_a, task_b in zip(sequence, sequence[1:]):
                self.direct_followers_set.add((task_a, task_b))
            
    def _construct_causalities_dict(self):
        self.causalities_dict = {}
        for task_pair in self.direct_followers_set:
            if tuple(reversed(task_pair)) not in self.direct_followers_set:
                if task_pair[0] in self.causalities_dict.keys():
                    self.causalities_dict[task_pair[0]].append(task_pair[1])
                else:
                    self.causalities_dict[task_pair[0]] = [task_pair[1]]

    def _construct_inv_causalities_dict(self):
        self.inv_causalities_dict = {}
        for key, values in self.causalities_dict.items():
            if len(values) == 1:
                if values[0] in self.inv_causalities_dict.keys():
                  self.inv_causalities_dict[values[0]].append(key)
                else:
                  self.inv_causalities_dict[values[0]] = [key]

    def _construct_parallel_tasks_set(self):
        self.parallel_tasks_set = set()
        for task_pair in self.direct_followers_set:
            if tuple(reversed(task_pair)) in self.direct_followers_set:
                self.parallel_tasks_set.add(task_pair)
