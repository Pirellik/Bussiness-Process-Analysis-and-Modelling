from alpha_alg import AlphaAlgorithm


if __name__ == '__main__':
   alpha = AlphaAlgorithm()
   alpha.read_log_file('logs/org_log.xes')
   alpha.build_model()
   alpha.create_graph()