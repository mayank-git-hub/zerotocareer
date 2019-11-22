import sys
import json

output_file = sys.argv[1]

results = sys.argv[2:]

output_results = {}

for no, result_i in enumerate(results):

	output_results[no] = result_i

with open('/home/mayank/temporary_files/'+output_file, 'w') as f:
	json.dump(f, output_results)
