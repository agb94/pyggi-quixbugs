import json
import os

epoch = 30

def analyze_log(path):
    with open(path, 'r') as f:
        data = json.loads(f.read())
   
    success = 0
    patches = []
    for i in range(epoch):
        epoch_data = data[str(i+1)]
        if epoch_data['Success']:
            success += 1
            patches.append(epoch_data['BestPatch'])
        # print(epoch_data['Success'], epoch_data['BestFitness'])
    if success:
        unique_patches = list(set(patches))
        print(path, success, len(unique_patches))
        for patch in unique_patches:
            print(patch)

if __name__ == "__main__":
    for log in os.listdir('logs'):
        if log != '.keep':
            analyze_log("logs/{}".format(log))
