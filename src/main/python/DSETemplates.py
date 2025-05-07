from ArchTemplates import GeneralArch

class GridSearchDSE:
	#todo

class BaysianDSE:
	#todo

class RL_DSE:
	#todo

class HierarchicalDSE:
	#todos

class GeneralDSE:
	def evaluate_result(self, result):
		return 0

	def run_dse(self, nn, initial_mapping, initial_hardware_config):
		hc = initial_hardware_config
		mp = initial_mapping
		ga = GeneralArch(mp, hc, nn)
		simulation_params = {
			"SIM_CYCLES": -1,
			"NEED_RAW_NET_DATA": False,
		}
		result = {}

		while(self.not_end_dse()):
			ga.gen_perf_trace(simulation_params)
			result = ga.estimate_our_pwr()
		
			self.save_estimate(result)
			
			hc, mp, result = self.evaluate_result(hc, mp, result))

		

		self.plot_dse_search()
