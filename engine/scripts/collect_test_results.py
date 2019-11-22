import sys
import json

output_file = sys.argv[1]
suffix = sys.argv[2]

results = sys.argv[3:]

output_results = {}

for no, result_i in enumerate(results):

	output_results[no] = result_i
print('Debug: ', output_results)
with open('/home/mayank/temporary_files/'+output_file + '_' + suffix, 'w') as f:
	json.dump(output_results, f)
