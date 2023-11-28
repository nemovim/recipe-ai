import csv
import numpy as np

class FrequencyData:
    def __init__(self, fileName):
        self.data = {
            'recipeId': [],
            'frequency': [],
            'clusterId': [],
            'sampleCnt': 0
        }

        with open(fileName, encoding='utf-8') as f:
            r = csv.reader(f)
            for line in r:
                if line[0] == 'id':
                    continue
                self.data['recipeId'].append(line[0])
                self.data['frequency'].append(self.decomopress(line[1].split('/')))
                self.data['clusterId'].append(0)
    
        self.data['frequency'] = np.array(self.data['frequency'])

    def decomopress(self, compressedVector):
        return list(map(int, list('1'.join(['0'*int(i) for i in compressedVector]))))

    # def clean(self, lessThan=1):
    #     newIdArr = []

    #     # maskArr = (self.data['frequency'].sum(axis=0) >= lessThan) & (self.data['frequency'].sum(axis=0) <= greaterThan)
    #     maskArr = (self.data['frequency'].sum(axis=0) >= lessThan)

    #     self.data['frequency']

    #     for i in range(len(maskArr)):
    #         if maskArr[i]:
    #             newIdArr.append(i)

    #     self.data['frequency'] = self.data['frequency'][:, maskArr]

    #     # remove rows that have only zeros.

    #     return newIdArr

if __name__ == '__main__':
    frequency= FrequencyData('../data-crawling/frequencyData/allFrequency_cleaned.csv')
    

    print('Initialized')

    print(frequency.data['frequency'][0])
    # print(frequency.data['frequency'].sum(axis=0)[86])
    # print(frequency.data['frequency'].sum(axis=0)[945])



