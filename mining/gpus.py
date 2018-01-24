
def process(self, coin):
	# nvidia-smi|grep '[|]\s\{2,3\}[0-9]\{1,2\} ' -A 1|grep '[0-9]\{1,3\}[%]'
	# nvidia-smi|grep '[0-9]\{1,5\}MiB'|grep -v '%'
	# gpuStat.json = gpustat --no-color --show-cmd --show-power --json
	return None

def finalize(self, coin):
	return 0
