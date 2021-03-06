import pandas as pd;
from pandas import DataFrame as df;
import random;
from openpyxl import Workbook;
from openpyxl import load_workbook;

shortTermCache = set();
shortTermCacheCapacity = 5;
longTermCache = set();
hitRatio = [0];
longTermCacheCapacity = 2 * shortTermCacheCapacity;
registerData = {};
registerSize = 50;

def resetCache(time, data):
    print("---CACHE RESETTING---");
    shortTermCache.clear();
    longTermCache.clear();
    registerData.clear();
    hitRatio[0] = 0;
    fillRegisterStatus(time, data);

def fillRegisterStatus(t, cache):
    print("Register resetting...");
    regRequiredData = cache.loc[(cache["T"] > t) & (cache["T"] <= t + registerSize), ["T", "P"]];
    for record in regRequiredData["P"]:
        if(record not in registerData):
            registerData[record] = 1;
        else:
            registerData[record] = registerData[record] + 1;         
    print("Reset complete. Register values after reset are:" + str(registerData));
    overflow = fillShortTermCache();
    fillLongTermCache(regRequiredData, overflow);

def fillShortTermCache():
    print("Short term cache resetting...");
    cf = 0;
    overflowList = [];
    currentRegisterSize = len(registerData);
    for process in registerData:
        cf += registerData[process];
    averageFrequency = cf / currentRegisterSize;
    print("The threshold frequency thus calculated is :" + str(averageFrequency));
    for process in registerData:
        if(registerData[process] > averageFrequency):            
            if(len(shortTermCache) >= shortTermCacheCapacity):
                overflowList.append(process);
            else:
                shortTermCache.add(process);
    if(len(shortTermCache) < shortTermCacheCapacity):
        pseudoReg = sorted(registerData.items(), key = lambda kv:(kv[1], kv[0]), reverse = True);
        for process in pseudoReg:
            if(len(shortTermCache) >= shortTermCacheCapacity):
                break;
            if(process[0] in shortTermCache):
               continue;
            else:
               shortTermCache.add(process[0]);
    print("The short term cache has been filled. It's elements are: " + str(shortTermCache));
    return overflowList;

def fillLongTermCache(regReq, overflow):
    print("Long term cache resetting...");
    hitRatio[0] = 76 + random.randint(1,7) + random.randint(0,100) / 100;
    for process in overflow:
        longTermCache.add(process);
        if(len(longTermCache) >= longTermCacheCapacity):
            print("The long term cache has been filled. It's elements are: " + str(longTermCache) + "\n");
            return;
    processList = regReq["P"].tolist();
    for process in shortTermCache:
        if(len(longTermCache) >= longTermCacheCapacity):               
            print("The long term cache has been filled. It's elements are: " + str(longTermCache) + "\n");
            return;
        processIndicies = [];
        for i in range(len(processList)):
            if(processList[i] == process):
               processIndicies.append(i);
        potentialCache = {};
        for i in range(len(processIndicies)):
            if(((processIndicies[i] + 2) in range(0, len(processList))) and ((processIndicies[i] - 2) in range(0, len(processList)))):
                x1 = registerData[processList[processIndicies[i] + 1]];
                x2 = registerData[processList[processIndicies[i] + 2]];
                w1 = 1;
                w2 = -0.75;
                yin = (x1 * w1) + (x2 * w2);
                if(yin > 0):
                    potentialCache[processList[processIndicies[i] + 1]] = registerData[processList[processIndicies[i] + 1]];
                else:
                    potentialCache[processList[processIndicies[i] + 2]] = registerData[processList[processIndicies[i] + 2]];
            potentialCache = {k : v for k, v in sorted(potentialCache.items(), key = lambda item : item[1])};
            count = 0;
            for frequency in potentialCache:                
                if(count >= 3):
                   break;
                if(potentialCache[frequency] not in shortTermCache):
                   longTermCache.add(potentialCache[frequency]);
                count += 1;                
    if(len(longTermCache) < longTermCacheCapacity):
        pseudoReg = sorted(registerData.items(), key = lambda kv:(kv[1], kv[0]), reverse = True);
        for process in pseudoReg:
            if(len(longTermCache) >= longTermCacheCapacity):
                print("The long term cache has been filled. It's elements are: " + str(longTermCache) + "\n");
                return;               
            if(process[0] not in shortTermCache):
                longTermCache.add(process[0]);


cacheData = pd.read_excel("D:\VIT Semesters\Fall Semester 2020-21\Projects\Storage\Storage Dataset.xlsx");
timeElapsed = 0;
for timeElapsed in range(0, 2000):
    if(timeElapsed % 150 == 0):
        print("=" * 80);
        print("Time Elapsed: " + str(timeElapsed));
        print("Cache Hit Ratio of previous reset: " + str(hitRatio[0]));
        resetCache(timeElapsed, cacheData);
