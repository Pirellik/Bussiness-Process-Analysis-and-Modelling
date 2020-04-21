from alpha_alg import AlphaAlgorithm
from heuristic_miner import HeuristicMiner


def use_alpha(log_path, graph_name):
   alpha = AlphaAlgorithm()
   alpha.read_log_file(log_path)
   alpha.build_model()
   alpha.create_graph(filename=graph_name)

def use_heuristic(log_path, graph_name, thresh_direct_followers, thresh_parallel, thresh_oneloop, thresh_twoloop):
   hminer = HeuristicMiner()
   hminer.read_log_file(log_path)
   hminer.build_model()
   hminer.create_graph(filename=graph_name)


if __name__ == '__main__':

   # ========================================

   # ALPHA parametry:
   log_path = 'logs/exercise5.xes'
   graph_name = 'alpha_graph_exercise5'

   # wywołanie ALPHA:
   use_alpha(log_path, graph_name)

   # ========================================

   # HEURISTIC parametry:
   log_path = 'logs/exercise5.xes'
   graph_name = 'heuristic_graph_exercise5'
   thresh_direct_followers = 0.9
   thresh_parallel = 0.7
   thresh_oneloop = 0.9
   thresh_twoloop = 0.9

   # wywołanie HEURISTIC:
   use_heuristic(log_path, graph_name, thresh_direct_followers, thresh_parallel, thresh_oneloop, thresh_twoloop)

   # ========================================