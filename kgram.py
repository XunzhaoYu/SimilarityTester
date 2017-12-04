#!/usr/bin/env python
# coding=utf-8

# The steps of calculate hash for similarity check:
# 1. pre-processing
# 2. dividing the files by K-gram. List kGram.
# 3. calculating the hash value of kGram. List hashList.
# 4. shrinking the size of list by winnowing algorithm. Dictionary winHash.

import os
import time
import datetime
import timeit

import numpy as np

K = 12
data = ""
winHashList = []

readPath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/submissions_pre/"
writePath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/submissions_hash/"

fileList = os.listdir(readPath)
fileList = fileList[1:len(fileList)]  # remove the hidden file ".DS_Store"
print fileList

count = 0;

for f in fileList:
    print f
    count += 1
    print count
    fileReadPath = os.path.join(readPath, f)
    fileWritePath = os.path.join(writePath, f)

    if os.path.isfile(fileReadPath):
        srcFile = open(fileReadPath)
        objFile = open(fileWritePath, "w")

        data = srcFile.read()

# Step2: k-gram division -- kGram
        kGram = []

        shingleNum = len(data)-K
        for i in range(0, shingleNum):
            shingle = data[i:i+K]
            kGram.append(shingle)

        print kGram
        print "the number of k-gram:" + str(len(kGram)) + ", " + str(shingleNum)

# Step3: rolling hash -- hashList
        Base = 3
        first_hash = 0
        pre_hash = 0
        hash = 0
        hashList = []
        firstShingle = kGram[0]

#        start = time.time()
#        stTime = datetime.datetime.now()

        for i in range(K):
            hash += ord(firstShingle[i])*(Base**(K-1-i))

        hashList.append(hash)

        for i in range(1, len(kGram)):
            preshingle = kGram[i-1]
            shingle = kGram[i]

            hash = hash * Base - ord(preshingle[0])*Base**K + ord(shingle[K-1])
            hashList.append(hash)

        print hashList

#        end = time.time()
#        endTime = datetime.datetime.now()

#        print "rolling Hash running time :" + str((end-start))

# Step4: winnowing hash -- winHash

        WINSIZE = 4
        winCnt= len(kGram)-WINSIZE+1

        minHash = 0
        minPos = 0

        """"
        winHash = {}

        for i in range(winCnt):
            templist = hashList[i:WINSIZE+i]

            minHash= templist[WINSIZE-1]
            minPos = WINSIZE+i-1

            for j in range(WINSIZE):

                if templist[j] < minHash:
                    minHash = templist[j]
                    minPos = i+j

            if not winHash.has_key(minPos):
                winHash[minPos] = minHash
                
        print winHash
        """

        element = 0
        preMinPos = 0
        winHash = set()

        for i in range(winCnt):
            templist = hashList[i:WINSIZE+i]

            # calculate the minHash in a window
            minHash = templist[WINSIZE-1]
            minPos = WINSIZE+i-1

            for j in range(WINSIZE):
                if templist[j] < minHash:
                    minHash = templist[j]
                    minPos = i+j

            if minPos != preMinPos:
                # calculate the token of a new minHash
                element = minHash * 100
                # while winHash.count(element) != 0:
                while element in winHash:
                    element = element + 1

                winHash.add(element)
                preMinPos = minPos


        print winHash
        winHashList.append(winHash)
        objFile.write(str(winHash))

        srcFile.close()
        objFile.close()

# get results
resemblance = np.eye(count+1)
for i in xrange(count):
    resemblance[0, i+1] = i+1
    for j in xrange(i + 1, count):
        n = len(set(winHashList[i]).intersection(set(winHashList[j])))
        u = len(set(winHashList[i]).union(set(winHashList[j])))
        resemblance[i+1, j+1] = int( 100 * (float(n)/float(u)) )
resemblance = resemblance + resemblance.T - 2*np.eye(count+1)
print resemblance

resultPath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/result.csv"
resultFile = open(resultPath, "w")
np.savetxt(resultPath, resemblance, delimiter = ',')
resultFile.close()

# analyze the results
statistic = np.zeros((count, 2))
for i in xrange(count):
    temp = resemblance[i+1, :]
    temp = temp[1:(count+1)]
    statistic[i, 0] = sum(temp * temp.T)/count
    statistic[i, 1] = int(i+1)

swap = True
for i in range(1, count):
    if not swap:
        break
    else:
        swap = False
        for j in range(0, count - i):
            if statistic[j, 0] < statistic[j+1, 0]:
                temp = statistic[j, 0]
                temp2 = statistic[j, 1]
                statistic[j, 0] = statistic[j + 1, 0]
                statistic[j, 1] = statistic[j + 1, 1]
                statistic[j + 1, 0] = temp
                statistic[j + 1, 1] = temp2
                swap = True

print statistic

analysisPath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/analysis.csv"
analysisFile = open(analysisPath, "w")
np.savetxt(analysisPath, statistic, delimiter = ',')
analysisFile.close()