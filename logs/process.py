import csv
import sys
import tabulate
import matplotlib.pyplot as pyplot
import matplotlib
import numpy
import statistics

if(len(sys.argv) < 3):
    print("ERROR too few arguments.\nprocess.py {hello, ring, page} filenames ...\nThe first argument should be the type of log file followed by one or more file names of log files as input to this python script.")
    sys.exit(-1)

def getMeanAndDeviation(list):
    myMean = statistics.mean(list)
    deltaFromMax = max(list) - myMean
    deltaFromMin = myMean - min(list)
    if(deltaFromMax > deltaFromMin):
        return (myMean, deltaFromMax)
    return (myMean, deltaFromMin)


def percentify(matrix, total):
    percTupleList = []
    for i, l in enumerate(matrix):
        percList = [p*100.0/t for (p,t) in zip(l, total)]
        percTupleList.append(getMeanAndDeviation(percList))
    return percTupleList

#Definition of row numbers for hello benchmark:
hello_createEnclaveRow = 0
hello_preparePagesRow = 1
hello_createEnclaveRow_exclusive = 2
hello_driverRow = hello_createEnclaveRow + 5
hello_communicationSetupRow = hello_driverRow + 14
hello_firstSendingRow = hello_communicationSetupRow + 3

#Definition of row numbers for ring benchmark:
ring_firstSendingRow = 16

#Definition of row numbers for page benchmark:
page_sendPageRow = 16

#Definition of indeces within rows:
labelIndex = 0
totalInstructionIndex = 1
kernelInstructionIndex = 2

#Lists for sending and receiving performance in hello benchmark and for creating enclaves
hello_sendingInstructions = []
hello_receivingInstructions = []
hello_sendingAccesses = []
hello_receivingAccesses = []
hello_createEnclaveShimInstructionList = []
hello_setupLinuxDriverInstructionList = []
hello_createEnclaveShimAccessList = []
hello_setupLinuxDriverAccessList = []

#Dicts for sending and receiving performance in ring benchmark
ring_sendingInstructions = {}
ring_receivingInstructions = {}
ring_sendingAccesses = {}
ring_receivingAccesses = {}

#Lists for sending complete pages in page benchmark
page_sendInstructions = []
page_sendAccesses = []

#Matrices and lists used for final results
userInstructionMatrix = []
kernelInstructionMatrix = []
totalInstructionMatrix = []
l2CacheAccessMatrix = []

hello_status = False
ring_status = False
page_status = False
if sys.argv[1] == "hello":
  hello_status = True
elif sys.argv[1] == "ring":
  ring_status = True
elif sys.argv[1] == "page":
    page_status = True
else:
  print("First argument needs to be hello or ring.")
  sys.exit(-2)

for fileNumber, fileName in enumerate(sys.argv[2:]):
    print("Processing file name: "+fileName)
    #lists local to each iteration
    titles = []
    data = []
    labels = []
    processedRows = []

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

    if(hello_status):
      hello_createEnclaveShimAccessList.append(0)
      hello_createEnclaveShimInstructionList.append(0)
      hello_setupLinuxDriverAccessList.append(0)
      hello_setupLinuxDriverInstructionList.append(0)
      table = [] # only used for pretty printing
      for num, label in enumerate(labels):
          table.append([label, userInstructionMatrix[num][fileNumber], kernelInstructionMatrix[num][fileNumber], totalInstructionMatrix[num][fileNumber], l2CacheAccessMatrix[num][fileNumber]])
          if(label >= 100 and label < 200):
              if(kernelInstructionMatrix[num][fileNumber] != totalInstructionMatrix[num][fileNumber]):
                  print("ERROR: something went wrong when processing create enclave.")
                  sys.exit(-3)
              hello_createEnclaveShimInstructionList[fileNumber] += kernelInstructionMatrix[num][fileNumber]
              hello_createEnclaveShimAccessList[fileNumber] += l2CacheAccessMatrix[num][fileNumber]
          if(label >= 1000 and label < 1100):
              hello_setupLinuxDriverInstructionList[fileNumber] += totalInstructionMatrix[num][fileNumber]
              hello_setupLinuxDriverAccessList[fileNumber] += l2CacheAccessMatrix[num][fileNumber]

      print(tabulate.tabulate(table, headers=["label", "user inst.", "kernel inst.", "total inst.", "L2 accesses"]))

      if(int(labels[hello_driverRow]) != 201):
          print("Label mismatch on driver row")
          print(labels[hello_driverRow])
          sys.exit(-5)

      if(int(labels[hello_communicationSetupRow]) != 10):
          print("label mismatch on communication row")
          print(labels[hello_communicationSetupRow])
          sys.exit(-6)

      for idx in range(hello_firstSendingRow, len(userInstructionMatrix)):
          if((idx-hello_firstSendingRow) % 2 == 0):
              hello_sendingInstructions.append(totalInstructionMatrix[idx][fileNumber])
              hello_sendingAccesses.append(l2CacheAccessMatrix[idx][fileNumber])
          else:
              hello_receivingInstructions.append(totalInstructionMatrix[idx][fileNumber])
              hello_receivingAccesses.append(l2CacheAccessMatrix[idx][fileNumber])
    elif(ring_status):
      for idx in range(ring_firstSendingRow, len(userInstructionMatrix)):
        if( labels[idx] not in ring_sendingInstructions.keys() ):
          ring_sendingInstructions[labels[idx]] = []
          ring_receivingInstructions[labels[idx]] = []
          ring_sendingAccesses[labels[idx]] = []
          ring_receivingAccesses[labels[idx]] = []
        if((idx-ring_firstSendingRow) % 2 == 0):
          ring_sendingInstructions[labels[idx]].append(totalInstructionMatrix[idx][fileNumber])
          ring_sendingAccesses[labels[idx]].append(l2CacheAccessMatrix[idx][fileNumber])
        else:
          ring_receivingInstructions[labels[idx]].append(totalInstructionMatrix[idx][fileNumber])
          ring_receivingAccesses[labels[idx]].append(l2CacheAccessMatrix[idx][fileNumber])
    elif(page_status):
        for idx in range(page_sendPageRow, len(userInstructionMatrix)):
            if(labels[idx] != 0xBABE):
                print("Error: page send row has wrong label")
                sys.exit(-7)
            page_sendInstructions.append(totalInstructionMatrix[idx][fileNumber])
            page_sendAccesses.append(l2CacheAccessMatrix[idx][fileNumber])

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

if hello_status:
  print("Sending message:   {:>16d}±{:>5.2f} instructions {:>16.4f}±{:>5.2f} cache accesses".format(statistics.mean(hello_sendingInstructions), statistics.stdev(hello_sendingInstructions), statistics.mean(hello_sendingAccesses), statistics.stdev(hello_sendingAccesses)))
  print("Receiving message: {:>16d}±{:>5.2f} instructions {:>16.4f}±{:>5.2f} cache accesses".format(statistics.mean(hello_receivingInstructions), statistics.stdev(hello_receivingInstructions), statistics.mean(hello_receivingAccesses), statistics.stdev(hello_receivingAccesses)))

  createLabels        = ['Prepare Enclave Pages', 'Setup Driver', 'Setup Enclave'] # Setup enclave includes setting up communication.
  createInstructionsPercentages   = percentify([totalInstructionMatrix[hello_preparePagesRow], hello_setupLinuxDriverInstructionList, [total - setup + comm for (total, setup, comm) in zip (totalInstructionMatrix[hello_createEnclaveRow_exclusive], hello_setupLinuxDriverInstructionList, totalInstructionMatrix[hello_communicationSetupRow])]], totalInstructionMatrix[hello_createEnclaveRow])
  createAccessesPercentages   = percentify([l2CacheAccessMatrix[hello_preparePagesRow], hello_setupLinuxDriverAccessList, [total - setup + comm for (total, setup, comm) in zip (l2CacheAccessMatrix[hello_createEnclaveRow_exclusive], hello_setupLinuxDriverAccessList, l2CacheAccessMatrix[hello_communicationSetupRow])]], l2CacheAccessMatrix[hello_createEnclaveRow])
  print(createLabels)
  print(createInstructionsPercentages)
  print(createAccessesPercentages)

  # Making bar chart
  ticks = [0, 2]#[0,2,4]
  #TODO add standard deviations
  tickLabels = ['{:,}\nInstructions'.format(statistics.mean(totalInstructionMatrix[hello_createEnclaveRow])), '{:,}\nCache Accesses'.format(statistics.mean(l2CacheAccessMatrix[hello_createEnclaveRow]))]

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
elif ring_status:
    packetSizes = []
    txInstMeans = []
    rxInstMeans = []
    txInstDevs  = ([], [])
    rxInstDevs  = ([], [])
    txAccessMeans = []
    rxAccessMeans = []
    txAccessDevs = ([], [])
    rxAccessDevs = ([], [])
    for size in ring_sendingInstructions.keys():
        packetSizes.append(size)
        txInstQuantiles = numpy.percentile(ring_sendingInstructions[size], [25,50,75])
        rxInstQuantiles = numpy.percentile(ring_receivingInstructions[size], [25,50,75])
        txInstMeans.append( txInstQuantiles[1] )
        rxInstMeans.append( rxInstQuantiles[1] )
        txInstDevs[0].append( txInstQuantiles[1] - txInstQuantiles[0])
        txInstDevs[1].append( txInstQuantiles[2] - txInstQuantiles[1])
        rxInstDevs[0].append( rxInstQuantiles[1] - rxInstQuantiles[0])
        rxInstDevs[1].append( rxInstQuantiles[2] - rxInstQuantiles[1])

        txAccessQuantiles = numpy.percentile(ring_sendingAccesses[size], [25,50,75])
        rxAccessQuantiles = numpy.percentile(ring_receivingAccesses[size], [25,50,75])
        txAccessMeans.append(txAccessQuantiles[1])
        rxAccessMeans.append(rxAccessQuantiles[1])
        txAccessDevs[0].append( txAccessQuantiles[1] - txAccessQuantiles[0])
        txAccessDevs[1].append( txAccessQuantiles[2] - txAccessQuantiles[1])
        rxAccessDevs[0].append( rxAccessQuantiles[1] - rxAccessQuantiles[0])
        rxAccessDevs[1].append( rxAccessQuantiles[2] - rxAccessQuantiles[1])
    #print(packetSizes)
    #print(txInstMeans)
    #print(rxInstMeans)
    #print(txInstDevs)
    #print(rxInstDevs)
    #print(txAccessMeans)
    #print(rxAccessMeans)
    #print(txAccessDevs)
    #print(rxAccessDevs)
    fig = pyplot.figure(figsize=(5,7))

    capsize=0 #5
    markeredgewidth=0 #1
    linewidth=2
    ax1 = fig.add_subplot(2,1,1)
    #ax1.set_xscale('log', basex=2)
    #ax1.set_yscale('log')
    ax1.errorbar(x=packetSizes, y=txInstMeans, yerr=txInstDevs, capsize=capsize, markeredgewidth=markeredgewidth, linewidth=linewidth, elinewidth=linewidth)
    ax1.errorbar(x=packetSizes, y=rxInstMeans, yerr=rxInstDevs, capsize=capsize, markeredgewidth=markeredgewidth)
    ax1.set_ylabel("Thousands of Instructions")
    #ax1.set_title("Costs for sending and receiving messages.")
    ax1.legend(["Send", "Receive"])
    ax1.set_xlim((0,4096))
    ax1.set_xticks(range(0,4096+1,512))
    ax1.set_yticks(range(0,120000+1,20000))
    ax1.set_yticklabels(range(0, 120+1, 20))
    ax1.grid()

    ax2 = fig.add_subplot(2,1,2)
    #ax2.set_xscale('log', basex=2)
    ax2.errorbar(x=packetSizes, y=txAccessMeans, yerr=txAccessDevs, capsize=capsize, markeredgewidth=markeredgewidth, linewidth=linewidth, elinewidth=linewidth)
    ax2.errorbar(x=packetSizes, y=rxAccessMeans, yerr=rxAccessDevs, capsize=capsize, markeredgewidth=markeredgewidth)
    ax2.set_ylabel("Thousands of Last-Level Cache Accesses")
    ax2.set_xlabel("Packet Size in Bytes")
    ax2.legend(["Send", "Receive"], loc='upper left')
    ax2.set_xlim((0, 4096))
    ax2.set_xticks(range(0,4096+1,512))
    ax2.set_yticks(range(0,12000+1,2000))
    ax2.set_yticklabels(range(0, 12+1, 2))
    ax2.grid()

    pyplot.show()
elif page_status:
    print(page_sendInstructions)
    print(numpy.percentile(page_sendInstructions, [25,50,75]))
    print(page_sendAccesses)
    print(numpy.percentile(page_sendAccesses, [25,50,75]))
