import csv
import numpy as np

class FrequencyData:
    def __init__(self, frequencyFolder='.', fileCount=250):
        self.data = {
            'recipeId': [],
            'frequency': [],
            'clusterId': [],
            'sampleCnt': 0
        }

        frequencyIdArr = []

        with open(f'{frequencyFolder}/frequencyId.csv', encoding='utf-8') as frequencyIdData:
            frequencyIdReader = csv.reader(frequencyIdData)
            for _frequencyIdArr in frequencyIdReader:
                frequencyIdArr = _frequencyIdArr


        id = 0
        for i in range(fileCount):
            with open(f'{frequencyFolder}/frequency_{i}.csv', encoding='utf-8') as frequencyData:
                frequencyReader = csv.reader(frequencyData)
                for frequency in frequencyReader:
                    self.data['recipeId'].append(frequencyIdArr[id])
                    self.data['frequency'].append(self.decomopress(frequency))
                    self.data['clusterId'].append(0)
                    id += 1
        
        self.data['frequency'] = np.array(self.data['frequency'])
        self.data['sampleCnt'] = id

    def decomopress(self, compressedVector):
        return list(map(int, list('1'.join(['0'*int(i) for i in compressedVector]))))

    def clean(self, lessThan=1, greaterThan=500):
        newIdArr = []

        maskArr = (self.data['frequency'].sum(axis=0) >= lessThan) & (self.data['frequency'].sum(axis=0) <= greaterThan)

        self.data['frequency']

        for i in range(len(maskArr)):
            if maskArr[i]:
                newIdArr.append(i)

        self.data['frequency'] = self.data['frequency'][:, maskArr]

        # remove rows that have only zeros.

        return newIdArr

if __name__ == '__main__':
    frequency= FrequencyData('../data-crawling/frequencyData', 250)

    print('Initialized')
    print(frequency.data['frequency'].sum(axis=0)[86])
    print(frequency.data['frequency'].sum(axis=0)[945])



