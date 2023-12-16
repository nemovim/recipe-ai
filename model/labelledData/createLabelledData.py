import csv
import json

def loadRawData(fileRef='labeling.labels.json'):
    recipeArr = []

    with open(fileRef, encoding='utf-8') as recipeFile:
        recipeJSON = json.load(recipeFile)
        for i, recipe in enumerate(recipeJSON):

            allArr = recipe['ingredientArr']
            mainArr = list(filter(lambda ing: True if ing != None else False, recipe['mainArr']))

            if mainArr == [-1] or mainArr == []:
                continue

            recipeArr.append([i, recipe['recipeId'], allArr, mainArr])

    return recipeArr 

def loadMappingDict(fileRef='../../ingredient/idMappings2.csv'):
    mappingDict = {}
    with open(fileRef, encoding='utf-8') as f:
        r = csv.reader(f)
        for mapping in r:
            if mapping[0] == 'old':
                continue
            mappingDict[int(mapping[0])] = mapping[1]
    return mappingDict

def saveLabelledData(recipeArr, fileRef='mainIngredients.csv'):
    with open(fileRef, '+w', encoding='utf-8', newline='') as mainFile:
        writer = csv.writer(mainFile)
        writer.writerow(['id', 'recipe', 'all', 'main'])
        writer.writerows(recipeArr)

def parseData(recipeArr, mappingDict):
    for recipe in recipeArr:
        allIng = '/'.join(updateIng(mappingDict, recipe[2]))
        mainIng = '/'.join(updateIng(mappingDict, recipe[3]))
        recipe[2] = allIng
        recipe[3] = mainIng
    return recipeArr

def updateIng(mappingDict, ingArr):
    ingSet = set()
    for ing in ingArr:
        try:
            ingSet.add(mappingDict[ing])
        except:
            continue
    return sorted(list(ingSet))

if __name__ == '__main__':
    saveLabelledData(parseData(loadRawData(), loadMappingDict()))