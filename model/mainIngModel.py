import csv
import numpy as np
from sklearn.decomposition import PCA, KernelPCA
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.model_selection import KFold, cross_validate, train_test_split

def oneHotEncoding(vector):
    ingCnt = 700 
    encodedVector = [0 for _ in range(ingCnt)]

    for ing in vector:
        encodedVector[int(ing)] = 1

    return encodedVector 

def oneHotDecoding(vector):
    result = []
    for i, value in enumerate(vector):
        if value == 1:
            result.append(i)
    return '/'.join(list(map(str, result)))

def loadLabelledData(fileRef='./labelledData/mainIngredients.csv', testSize=0.33):
    sampleIdArr = []
    allIngData = []
    mainIngData =[]

    with open(fileRef, encoding='utf-8') as f:
        r = csv.reader(f)
        for i, recipe in enumerate(r):
            if i == 0:
                continue
            sampleIdArr.append(recipe[1])
            allIngData.append(oneHotEncoding(recipe[2].split('/')))
            mainIngData.append(list(map(int, (recipe[3].split('/')))))
    
    train_pure_all, test_pure_all, train_pure_main, test_pure_main = train_test_split(allIngData, mainIngData, test_size=testSize, shuffle=True)

    train_all = []
    test_all = []
    train_main = []
    test_main = []

    for i, mainIngArr in enumerate(train_pure_main):
        for mainIng in mainIngArr:
            train_all.append(train_pure_all[i])
            train_main.append(mainIng)

    for i, mainIngArr in enumerate(test_pure_main):
        for mainIng in mainIngArr:
            test_all.append(test_pure_all[i])
            test_main.append(mainIng)

    return {
        'pure': {
            'train': (train_pure_all, train_pure_main),
            'test': (test_pure_all, test_pure_main),
        },
        'separated': {
            'train': (train_all, train_main),
            'test': (test_all, test_main),
        }
    }

def loadIngNameData(fileRef='../ingredient/newIngredients2.csv'):
    ingNameArr = []
    with open(fileRef, encoding='utf-8') as f:
        r = csv.reader(f)
        for ing in r:
            if ing[0] == 'id':
                continue
            ingNameArr.append(ing[1])
    return ingNameArr

def createPipeline(drType='pca', modelType='rf', n=100):
    if drType == 'pca':
        pca = PCA(n_components=0.9)
    elif drType == 'kpca':
        pca = KernelPCA(n_components=150)
    elif drType == 'rpc':
        pca = PCA(n_components=150, svd_solver='randomized')

    
    if modelType == 'rf':
        model = RandomForestClassifier(n_estimators=n, min_samples_leaf=10, n_jobs=-1)
    elif modelType == 'svm':
        model = SVC(probability=True)
    elif modelType == 'bagging':
        model = BaggingClassifier(SVC(probability=True), n_estimators=10, n_jobs=-1)

    pipeline = Pipeline([('pca', pca), ('model', model)])

    return pipeline

def crossValidate(allIngData, mainIngData, pipeline, k=10):

    scorer = {
        "accuracy": "accuracy",
        # "precision": "precision",
        # "recall": "recall",
        "r2": "r2"
    }

    return cross_validate(
        pipeline, allIngData, mainIngData, cv=KFold(n_splits=k), scoring=scorer, return_estimator=True, return_train_score=True, n_jobs=-1
    )

def analyzeResult(indexedData, result, mainIngData, ingNameArr):
    parsed_mainIngData = sorted(list(set(mainIngData)))

    probDict = {} 

    indexedDataArr = list(map(int, indexedData.split('/')))
    indexedDataArr.sort()

    for ing in indexedDataArr:
        try:
            probDict[ingNameArr[ing]] = result[0][parsed_mainIngData.index(ing)]
        except:
            probDict[ingNameArr[ing]] = 0
    
    return probDict

def createIndexedData(rawData, ingNameArr):
    indexedDataArr = []
    for ingName in rawData:
        try:
            indexedDataArr.append(ingNameArr.index(ingName))
        except:
            print(f'There is no ingredient named "{ingName}"!')
    return '/'.join(map(str, indexedDataArr))


def createSample(indexedData):
    return oneHotEncoding(list(map(int, indexedData.split('/'))))

# pipeline should be already fitted.
def calcAccuracy(pipeline, train_main, test_pure_all, test_pure_main, k=0.2):

    result = pipeline.predict_proba(test_pure_all)

    parsed_train_main = sorted(list(set(train_main)))

    realMainIngArr = []

    for idxArr in test_pure_main:
        realMainIngArr.append(idxArr)

    predictedMainIngArr = []
    for i, idx in enumerate(np.argmax(result, axis=1)):
        mainIngs = []
        # mainIngs.append(ingNameArr[parsed_train_main[idx]])
        mainIngs.append(parsed_train_main[idx])
        for subMainIdArr in np.where(result[i] > k*result[i][idx]):
            for subMainId in subMainIdArr:
                if subMainId != idx:
                    # mainIngs.append(ingNameArr[parsed_train_main[subMainId]])
                    mainIngs.append(parsed_train_main[subMainId])
        predictedMainIngArr.append(mainIngs)

    f1Arr = []
    precisionArr = []
    recallArr = []

    for sampleIdx in range(len((test_pure_all))):
        precision = 10e-10
        for idx in predictedMainIngArr[sampleIdx]:
            if idx in realMainIngArr[sampleIdx]:
                precision += 1
        precision /= len(predictedMainIngArr[sampleIdx])

        recall = 10e-10
        for idx in realMainIngArr[sampleIdx]:
            if idx in predictedMainIngArr[sampleIdx]:
                recall += 1
        recall /= len(realMainIngArr[sampleIdx])

        f1 = 2/(1/precision + 1/recall)

        f1Arr.append(f1)
        precisionArr.append(precision)
        recallArr.append(recall)

    return f1Arr, precisionArr, recallArr


if __name__ == '__main__':
    indexedData = '533/31/357/393/332/545/13/173/7'
    data = loadLabelledData()
    allIngData = data['separated']['train'][0]
    mainIngData = data['separated']['train'][1]
    ingNameArr = loadIngNameData()
    pipeline = createPipeline()
    # pipeline.fit(allIngData, mainIngData)
    # result = pipeline.predict_proba([createSample(indexedData)])
    # probDict = analyzeResult(indexedData, result, mainIngData, ingNameArr)
    # print(probDict)
    print(crossValidate(allIngData, mainIngData, pipeline, 10))