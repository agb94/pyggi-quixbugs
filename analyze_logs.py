import json
import os
import sys

def analyze_log(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
    #print(path)
    success = 0
    patches = []
    for epoch_data in data:
        if epoch_data['Success']:
            success += 1
            patches.append(epoch_data['BestPatch'])
        #print(epoch_data['Success'], epoch_data['BestFitness'] if 'BestFitness' in epoch_data else None)
    if success:
        unique_patches = list(set(patches))
        print(path, success, len(unique_patches))
        for patch in unique_patches:
            print(patch)

if __name__ == "__main__":
    log_dir = sys.argv[1]
    for log in os.listdir(log_dir):
        if log != '.keep':
            analyze_log(os.path.join(log_dir, log))
