import csv
import sys
import tabulate
import matplotlib.pyplot as pyplot
import matplotlib
import numpy
import statistics

if(len(sys.argv) < 2):
    print("ERROR: Please give one or more file names of log files as input to this python script.")
    sys.exit(-1)

def percentify(matrix, total):
    percTupleList = []
    for i, l in enumerate(matrix):
        percList = [p*100.0/t for (p,t) in zip(l, total)]
        percTupleList.append((statistics.mean(perList), statistics.stdev(percList)))
    return percTupleList

#Definition of row numbers:
createEnclaveRow = 0
preparePagesRow = 1
createEnclaveRow_exclusive = 2
driverRow = createEnclaveRow + 5
communicationSetupRow = driverRow + 14
firstSendingRow = communicationSetupRow + 3

#Definition of indeces within rows:
labelIndex = 0
totalInstructionIndex = 1
kernelInstructionIndex = 2

sendingInstructions = []
receivingInstructions = []
sendingAccesses = []
receivingAccesses = []

#Matrices and lists used for final results
userInstructionMatrix = []
kernelInstructionMatrix = []
totalInstructionMatrix = []
l2CacheAccessMatrix = []
createEnclaveShimInstructionList = []
setupLinuxDriverInstructionList = []
createEnclaveShimAccessList = []
setupLinuxDriverAccessList = []

for fileNumber, fileName in enumerate(sys.argv[1:]):
    print("Processing file name: "+fileName)
    #lists local to each iteration
    titles = []
    data = []
    labels = []
    processedRows = []
    table = [] # only used for pretty printing

    with open(fileName) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for num, row in enumerate(csvReader):
            if(num is 0):
                titles = row
            elif(num is not 1):
                data.append(row)

    l2Index = -1
    for idx, n in enumerate(data[0]):
        if n == " L2$":
            l2Index = idx
    if l2Index < 0:
        print("l2Index may not be negative")
        sys.exit(-7)
    l2ReadsIndex = l2Index + 3
    l2WritesIndex = l2Index + 4

    processedIndex = 0
    for num, row in enumerate(data):
        if num not in processedRows:
            processedRows.append(num)
            currentLabel = int(row[labelIndex])
            labels.append(currentLabel)
            found = False
            for idx in range(num+1, len(data)):
                if int(data[idx][labelIndex]) == currentLabel:
                    found = True
                    if(fileNumber == 0):
                        userInstructionMatrix.append([])
                        kernelInstructionMatrix.append([])
                        totalInstructionMatrix.append([])
                        l2CacheAccessMatrix.append([])
                    processedRows.append(idx)
                    #Instructions
                    tmpKernelInstructions = int(data[idx][kernelInstructionIndex]) - int(row[kernelInstructionIndex])
                    tmpTotalInstructions = int(data[idx][totalInstructionIndex]) - int(row[totalInstructionIndex])
                    userInstructionMatrix[processedIndex].append(tmpTotalInstructions - tmpKernelInstructions)
                    kernelInstructionMatrix[processedIndex].append(tmpKernelInstructions)
                    totalInstructionMatrix[processedIndex].append(tmpTotalInstructions)
                    l2CacheAccessMatrix[processedIndex].append(int(data[idx][l2ReadsIndex]) + int(data[idx][l2WritesIndex]) - int(row[l2ReadsIndex]) - int(row[l2WritesIndex]))
                    processedIndex += 1
                    break
            if not found:
                print("Failed to find pair.")
                print(num)
                print(currentLabel)
                sys.exit(-4)

    if((len(labels) != len(userInstructionMatrix)) or (len(labels) != len(kernelInstructionMatrix)) or (len(labels) != len(l2CacheAccessMatrix)) or (len(labels) != len(data)/2) or (len(processedRows) != len(data))):
        print("ERROR: Something went wrong when processing the data.")
        print(len(labels))
        print(len(userInstructionMatrix))
        print(len(kernelInstructionMatrix))
        print(len(l2CacheAccessMatrix))
        print(len(data))
        print(len(processedRows))
        print(labels)
        sys.exit(-2)

    createEnclaveShimAccessList.append(0)
    createEnclaveShimInstructionList.append(0)
    setupLinuxDriverAccessList.append(0)
    setupLinuxDriverInstructionList.append(0)
    for num, label in enumerate(labels):
        table.append([label, userInstructionMatrix[num][fileNumber], kernelInstructionMatrix[num][fileNumber], totalInstructionMatrix[num][fileNumber], l2CacheAccessMatrix[num][fileNumber]])
        if(label >= 100 and label < 200):
            if(kernelInstructionMatrix[num][fileNumber] != totalInstructionMatrix[num][fileNumber]):
                print("ERROR: something went wrong when processing create enclave.")
                sys.exit(-3)
            createEnclaveShimInstructionList[fileNumber] += kernelInstructionMatrix[num][fileNumber]
            createEnclaveShimAccessList[fileNumber] += l2CacheAccessMatrix[num][fileNumber]
        if(label >= 1000 and label < 1100):
            setupLinuxDriverInstructionList[fileNumber] += totalInstructionMatrix[num][fileNumber]
            setupLinuxDriverAccessList[fileNumber] += l2CacheAccessMatrix[num][fileNumber]

    print(tabulate.tabulate(table, headers=["label", "user inst.", "kernel inst.", "total inst.", "L2 accesses"]))

    if(int(labels[driverRow]) != 201):
        print("Label mismatch on driver row")
        print(labels[driverRow])
        sys.exit(-5)

    if(int(labels[communicationSetupRow]) != 10):
        print("label mismatch on communication row")
        print(labels[communicationSetupRow])
        sys.exit(-6)

    for idx in range(firstSendingRow, len(userInstructionMatrix)):
        if((idx-firstSendingRow)%2 == 0):
            sendingInstructions.append(userInstructionMatrix[idx][fileNumber])
            sendingAccesses.append(l2CacheAccessMatrix[idx][fileNumber])
        else:
            receivingInstructions.append(userInstructionMatrix[idx][fileNumber])
            receivingAccesses.append(l2CacheAccessMatrix[idx][fileNumber])

print("Sending message:   {:>16d}±{:>5.2f} instructions {:>16.4f}±{:>5.2f} cache accesses".format(statistics.mean(sendingInstructions), statistics.stdev(sendingInstructions), statistics.mean(sendingAccesses), statistics.stdev(sendingAccesses)))
print("Receiving message: {:>16d}±{:>5.2f} instructions {:>16.4f}±{:>5.2f} cache accesses".format(statistics.mean(receivingInstructions), statistics.stdev(receivingInstructions), statistics.mean(receivingAccesses), statistics.stdev(receivingAccesses)))

def makeStackBar(level, percentages, labels):
    if(len(percentages) != len(labels)):
        print("Lengths must correspond for makeStackBar")
    cumm = 0
    fatness = 1
    for idx, p in enumerate(percentages):
        if p < 20:
            newLabel = labels[idx] + '\n'
        else:
            newLabel = labels[idx] + ' '
        newLabel += "{:>2.2f}%".format(p)
        if idx%2 != 0:
            barColor = 'lightgray'
            textColor = 'k'
        else:
            barColor = 'k'
            textColor = 'w'
        pyplot.bar(x=[level], height=[p], width=fatness, bottom=cumm, align='center', color=barColor)
        textAlignment = 'center'
        textSecondaryAlignment = 'center'
        textPos = cumm+p/2
        tmpLevel = level
        if(p < 5):
            textColor = 'k'
            pyplot.arrow(level+fatness*3./4., textPos, -fatness/4., 0, color=textColor, head_width=1., head_length=.05, length_includes_head=True)
            tmpLevel += fatness*3./4.
            textAlignment = 'left'
        pyplot.text(tmpLevel, textPos, newLabel, ha=textAlignment, va=textSecondaryAlignment, color=textColor)
        cumm += p

#createStats = reportStats(name="Create enclave", totalInst=totalInstructions[createEnclaveRow], userInst=userInstructions[createEnclaveRow], kernelInst=kernelInstructions[createEnclaveRow], setupInst=0, shimInst=createEnclaveShimInstructions)
#altCreateStats = reportStats("Alternative create enclave", totalInstructions[createEnclaveRow], userInstructions[createEnclaveRow], kernelInstructions[createEnclaveRow], totalInstructions[driverRow])
#reportStats("Communication channel setup", totalInstructions[sendingRow] + totalInstructions[receivingRow], userInstructions[sendingRow] + userInstructions[receivingRow], kernelInstructions[sendingRow] + kernelInstructions[receivingRow], 0, 0)

# createLabels        = ['Setup\nEnclave\nPages', 'Create Enclave', 'Setup Driver', 'Management Shim']
# createPercentages   = percentify([totalInstructions[preparePagesRow], (totalInstructions[createEnclaveRow_exclusive] - setupLinuxDriverInstructions - createEnclaveShimInstructions), setupLinuxDriverInstructions, createEnclaveShimInstructions], totalInstructions[createEnclaveRow])
createLabels        = ['Prepare Enclave Pages', 'Setup Driver', 'Setup Enclave'] # Setup enclave includes setting up communication.
createInstructionsPercentages   = percentify([totalInstructionMatrix[preparePagesRow], setupLinuxDriverInstructionList, [total - setup + comm for (total, setup, comm) in zip (totalInstructionMatrix[createEnclaveRow_exclusive], setupLinuxDriverInstructionList, totalInstructionMatrix[communicationSetupRow])]], totalInstructionList[createEnclaveRow])
createAccessesPercentages   = percentify([l2CacheAccessMatrix[preparePagesRow], setupLinuxDriverAccessList, [total - setup + comm for (total, setup, comm) in zip (l2CacheAccessMatrix[createEnclaveRow_exclusive], setupLinuxDriverAccessList, l2CacheAccessMatrix[communicationSetupRow])]], l2CacheAccessList[createEnclaveRow])
print(createLabels)
print(createInstructionsPercentages)
print(createAccessesPercentages)

# Making bar chart
ticks = [0, 2]#[0,2,4]
#TODO add standard deviations
tickLabels = ['{:,}\nInstructions'.format(statistics.mean(totalInstructionMatrix[createEnclaveRow])), '{:,}\nCache Accesses'.format(statistics.mean(l2CacheAccessMatrix[createEnclaveRow]))]

fig = pyplot.figure(figsize=(11,7))
#makeStackBar(level=ticks[0], percentages=[20, 20, 20, 40], labels=['Context Switch', 'DMA Alloc', 'Copy from user', 'Other'], colors=['g', 'c', 'darkturquoise', 'b'], textRotation=['0', '0', '0', '0'])
#makeStackBar(level=ticks[0], percentages=createStats, labels=['User API', 'Kernel Driver', 'Driver Setup' 'Management Shim'])
#makeStackBar(level=ticks[1], percentages=altCreateStats, labels=['User API', 'Kernel', 'Praesidio Driver +\nManagement Shim'])
#makeStackBar(level=ticks[2], percentages=[95.30, 4.60], labels=['User API', 'Shim'], colors=['r', 'orange'], textRotation=['0', '90'])

#makeStackBar(level=ticks[0], percentages=createInstructionsPercentages, labels=createLabels)
#makeStackBar(level=ticks[1], percentages=createAccessesPercentages, labels=createLabels)

pyplot.grid(b=True, which='major', axis='y', c='lightgray')
pyplot.xticks(ticks, tickLabels)
pyplot.xlim(min(ticks)-1, max(ticks) + 2)
pyplot.ylabel("Percentage of total")
pyplot.ylim(-10, 110)
pyplot.title("Cost to Create Enclave")

pyplot.show()
