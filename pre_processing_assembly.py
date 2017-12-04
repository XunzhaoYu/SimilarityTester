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

# Step 1: pre-processing:

readPath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/submissions/"
writePath = "/Users/xunzhaoyu/Documents/PhD/Documents of Study/TA/submissions/submissions_pre/"

fileList = os.listdir(readPath)
fileList = fileList[1:len(fileList)]  # remove the hidden file ".DS_Store"

comment = "#"
for f in fileList:
    fileReadPath = os.path.join(readPath, f)
    fw = f[0:len(f)-1] + "txt"
    fileWritePath = os.path.join(writePath, fw)

    if os.path.isfile(fileReadPath):
        srcFile = open(fileReadPath)
        objFile = open(fileWritePath, "w")

        # start pre-processing: ---------------------------------------------------------------------
        srcData = ""
        afterMain = False
        labels = []
        colonPos = 0

        fileLines = srcFile.readlines()
        for line in fileLines:
            # detect data section:
            if not afterMain:
                # detect global main:
                if line.find("main") != -1:
                    afterMain = True
                # detect data string, and record them in labels
                elif line.find(":") != -1:
                    temp = line.strip()
                    colonPos = temp.find(":")
                    labels.append(temp[0:colonPos])
            # start process main code
            else:
                # delete comments
                commentPos = line.find(comment)
                if commentPos != -1:
                    line = line[0:commentPos] + "\n"

                # record labels
                if line.find(":") != -1:
                        temp = line.strip()
                        colonPos = temp.find(":")
                        labels.append(temp[0:colonPos])
                        line = temp[colonPos:len(line)]

                # add lines into data
                srcData = srcData + line

        # sort labels by length
        labelNum = len(labels)
###        print labelNum

        swap = True
        for i in range(1, labelNum):
            if not swap:
                break
            else:
                swap = False
                for j in range(0, labelNum - i):
                    if len(labels[j]) < len(labels[j + 1]):
                        temp = labels[j]
                        labels[j] = labels[j + 1]
                        labels[j + 1] = temp
                        swap = True
        # delete labels
        for label in labels:
###            print label
            srcData = srcData.replace(label, "")

        # abbreviate special instruction: syscall
        srcData = srcData.replace("syscall", "sy")
        srcData = srcData.replace("move", "mo")
        srcData = srcData.replace("zero", "ze")

        # delete all space, comma
        srcData = srcData.replace(",", "").replace(";", "")
        objData = "".join(srcData.split())

        # end of pre-processing: ---------------------------------------------------------------------
        objFile.write(objData)

        srcFile.close()
        objFile.close()
