from pm4py.objects.log.importer.xes import factory as xes_import
from graph import MyGraph
import pandas as pd


class HeuristicMiner:
    def __init__(self, thresh_direct_followers=0.9, thresh_parallel=0.7, thresh_oneloop=0.9, thresh_twoloop=0.9):
        self.log = None
        self.all_events_set = None
        self.event_to_index = None
        self.index_to_event = None
        self.prob_matrix = None
        self.parallel_matrix = None
        self.oneloop_vector = None
        self.twoloop_matrix = None

        self.direct_followers_set = None
        self.causalities_dict = None
        self.inv_causalities_dict = None
        self.parallel_tasks_set = None
        self.oneloop_set = None
        self.twoloop_set = None

        self.direct_followers_threshold = thresh_direct_followers
        self.parallel_threshold = thresh_parallel
        self.oneloop_threshold = thresh_oneloop
        self.twoloop_threshold = thresh_twoloop
    
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
        
        self.all_events_set = set()
        for sequence in self.log:
            for event in sequence:
                self.all_events_set.add(event)
        
        self.event_to_index = {event: ind for ind, event in enumerate(self.all_events_set)}
        self.index_to_event = {ind: event for ind, event in enumerate(self.all_events_set)}
    
    def build_model(self):
        if self.log is None:
            print("ERROR: Read log file before building model.")
            return
        self._construct_matrices()
        self._construct_direct_followers_set()
        self._construct_causalities_dict()
        self._construct_inv_causalities_dict()
        self._construct_parallel_tasks_set()
        self._construct_TI_set()
        self._construct_TO_set()
        self._construct_oneloop_set()
        self._construct_twoloop_set()

    def create_graph(self, filename='graph'):
        if self.log is None:
            print("ERROR: Read log file and build model before creating graph.")
            return
        causality = self.causalities_dict
        parallel_events = self.parallel_tasks_set
        inv_causality = self.inv_causalities_dict


        #prepare in/out matrix
        inout_df = pd.DataFrame(index = list(self.all_events_set), columns = ['IN','OUT'])
        for col in inout_df.columns:
            for row in inout_df.index:
                inout_df[col][row] = row

        '''
        Code below is copied from this site: https://ai.ia.agh.edu.pl/pl:dydaktyka:dss:lab03
        However some modifications were made.
        '''

        G = MyGraph()

        #adding 1loops to graph
        for event in self.oneloop_set:
            G.add_one_loop(event, inout_df)

        #adding 2loops to graph
        for twoloop in self.twoloop_set:
            G.add_two_loop(twoloop[0], twoloop[1], inout_df)  

        # adding split gateways based on causality
        for event in causality.keys():
            if len(causality[event]) > 1:
                if tuple(causality[event]) in parallel_events:
                    G.add_and_split_gateway(inout_df['OUT'][event], [inout_df['IN'][elem] for elem in causality[event]])
                else:
                    G.add_xor_split_gateway(inout_df['OUT'][event], [inout_df['IN'][elem] for elem in causality[event]])

        # adding merge gateways based on inverted causality
        for event in inv_causality.keys():
            if len(inv_causality[event]) > 1:
                if tuple(inv_causality[event]) in parallel_events:
                    G.add_and_merge_gateway([inout_df['OUT'][elem] for elem in inv_causality[event]], inout_df['IN'][event])
                else:
                    G.add_xor_merge_gateway([inout_df['OUT'][elem] for elem in inv_causality[event]], inout_df['IN'][event])
            elif len(inv_causality[event]) == 1:
                source = list(inv_causality[event])[0]
                G.edge(inout_df['OUT'][source], inout_df['IN'][event])

        # adding start event
        G.add_event("start")
        if len(self.TI_set) > 1:
            if tuple(self.TI_set) in parallel_events: 
                G.add_and_split_gateway("start", [inout_df['IN'][event] for event in self.TI_set])
            else:
                G.add_xor_split_gateway("start", [inout_df['IN'][event] for event in self.TI_set])
        else: 
            G.edge("start", inout_df['IN'][list(self.TI_set)[0]])

        # adding end event
        G.add_event("end")
        if len(self.TO_set) > 1:
            if tuple(self.TO_set) in parallel_events: 
                G.add_and_merge_gateway([inout_df['OUT'][event] for event in self.TO_set], "end")
            else:
                G.add_xor_merge_gateway([inout_df['OUT'][event] for event in self.TO_set], "end")    
        else: 
            G.edge(inout_df['OUT'][list(self.TO_set)[0]], "end")

        # G.format = 'svg'
        G.render('graphs/' + filename)
        G.view('graphs/' + filename)

    def _construct_matrices(self):
        freq_matrix = [[0 for _ in range(len(self.all_events_set))] for _ in range(len(self.all_events_set))]
        for sequence in self.log:
            for task_a, task_b in zip(sequence, sequence[1:]):
                freq_matrix[self.event_to_index[task_a]][self.event_to_index[task_b]] += 1

        self.prob_matrix = [[0 for _ in range(len(self.all_events_set))] for _ in range(len(self.all_events_set))]
        for row_index, row in enumerate(self.prob_matrix):
            for col_index, elem in enumerate(row):
                t1t2 = freq_matrix[row_index][col_index]
                t2t1 = freq_matrix[col_index][row_index]
                self.prob_matrix[row_index][col_index] = (abs(t1t2) - abs(t2t1)) / (abs(t1t2) + abs(t2t1) + 1)

        self.parallel_matrix = [[0 for _ in range(len(self.all_events_set))] for _ in range(len(self.all_events_set))]
        for row_index, row in enumerate(self.parallel_matrix):
            for col_index, elem in enumerate(row):
                t1t2 = freq_matrix[row_index][col_index]
                t2t1 = freq_matrix[col_index][row_index]
                if t1t2 > 0 and t2t1 > 0:
                    self.parallel_matrix[row_index][col_index] = 1 - abs(t1t2 - t2t1) / max(t1t2, t2t1)

        self.oneloop_vector = [0 for _ in range(len(self.all_events_set))]
        for index in range(len(self.all_events_set)):
            self.oneloop_vector[index] = freq_matrix[index][index] / (freq_matrix[index][index] + 1)

        twoloop_freq = [[0 for _ in range(len(self.all_events_set))] for _ in range(len(self.all_events_set))]
        for sequence in self.log:
            for task_a, task_b, task_c in zip(sequence, sequence[1:], sequence[2:]):
                if task_a == task_c:
                    twoloop_freq[self.event_to_index[task_a]][self.event_to_index[task_b]] += 1
        
        self.twoloop_matrix = [[0 for _ in range(len(self.all_events_set))] for _ in range(len(self.all_events_set))]
        for row_index, row in enumerate(self.prob_matrix):
            for col_index, elem in enumerate(row):
                t1t2 = twoloop_freq[row_index][col_index]
                t2t1 = twoloop_freq[col_index][row_index]
                if t1t2 > t2t1:
                    self.twoloop_matrix[row_index][col_index] = (t1t2 + t2t1) / (t1t2 + t2t1 + 1)

    def _construct_direct_followers_set(self):
        self.direct_followers_set = set()
        for row_index, row in enumerate(self.prob_matrix):
            for col_index, elem in enumerate(row):
                if elem > self.direct_followers_threshold:
                    self.direct_followers_set.add((self.index_to_event[row_index], self.index_to_event[col_index]))

    def _construct_causalities_dict(self):
        self.causalities_dict = {}
        for task_pair in self.direct_followers_set:
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
        for row_index, row in enumerate(self.parallel_matrix):
            for col_index, elem in enumerate(row):
                if row_index == col_index:
                    continue
                if elem > self.parallel_threshold:
                    task_pair = (self.index_to_event[row_index], self.index_to_event[col_index])
                    self.parallel_tasks_set.add(task_pair)

    def _construct_TI_set(self):
        self.TI_set = set()
        next_events = [task_pair[1] for task_pair in self.direct_followers_set]
        for event in self.all_events_set:
            if event not in next_events:
                self.TI_set.add(event)

    def _construct_TO_set(self):
        self.TO_set = set()
        first_events = [task_pair[0] for task_pair in self.direct_followers_set]
        for event in self.all_events_set:
            if event not in first_events:
                self.TO_set.add(event)

    def _construct_oneloop_set(self):
        self.oneloop_set = set()
        for index, prob in enumerate(self.oneloop_vector):
            if prob > self.oneloop_threshold:
                self.oneloop_set.add(self.index_to_event[index])
    
    def _construct_twoloop_set(self):
        self.twoloop_set = set()
        for row_index, row in enumerate(self.twoloop_matrix):
            for col_index, elem in enumerate(row):
                if elem > self.twoloop_threshold:
                    self.twoloop_set.add((self.index_to_event[row_index], self.index_to_event[col_index]))
