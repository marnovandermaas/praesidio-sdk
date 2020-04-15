import csv
import sys
import tabulate
import matplotlib.pyplot as pyplot
import matplotlib
import numpy
import statistics

titles = []
data = []

if(len(sys.argv) != 2):
    print("ERROR: Please give the file name of the log as input to this python script.")
    sys.exit(-1)

with open(sys.argv[1]) as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for num, row in enumerate(csvReader):
        if(num is 0):
            titles = row
        elif(num is not 1):
            data.append(row)

labelIndex = 0
totalInstructionIndex = 1
kernelInstructionIndex = 2

labels = []
userInstructions = []
kernelInstructions = []
totalInstructions = []

processedRows = []

for num, row in enumerate(data):
    if num not in processedRows:
        processedRows.append(num)
        currentLabel = int(row[labelIndex])
        labels.append(currentLabel)
        found = False
        for idx in range(num+1, len(data)):
            if int(data[idx][labelIndex]) == currentLabel:
                found = True
                processedRows.append(idx)
                #Instructions
                tmpKernelInstructions = int(data[idx][kernelInstructionIndex]) - int(row[kernelInstructionIndex])
                tmpTotalInstructions = int(data[idx][totalInstructionIndex]) - int(row[totalInstructionIndex])
                userInstructions.append(tmpTotalInstructions - tmpKernelInstructions)
                kernelInstructions.append(tmpKernelInstructions)
                totalInstructions.append(tmpTotalInstructions)
                break
        if not found:
            print("Failed to find pair.")
            print(num)
            print(currentLabel)
            sys.exit(-4)

if((len(labels) != len(userInstructions)) or (len(labels) != len(kernelInstructions)) or (len(labels) != len(data)/2) or (len(processedRows) != len(data))):
    print("ERROR: Something went wrong when processing the data.")
    print(len(labels))
    print(len(userInstructions))
    print(len(kernelInstructions))
    print(len(data))
    print(len(processedRows))
    print(labels)
    sys.exit(-2)

table = []
createEnclaveShimInstructions = 0
setupLinuxDriverInstructions = 0

for num, label in enumerate(labels):
    table.append([label, userInstructions[num], kernelInstructions[num], totalInstructions[num]])
    if(label >= 100 and label < 200):
        if(kernelInstructions[num] != totalInstructions[num]):
            print("ERROR: something went wrong when processing create enclave.")
            sys.exit(-3)
        createEnclaveShimInstructions += kernelInstructions[num]
    if(label >= 1000 and label < 1100):
        setupLinuxDriverInstructions += totalInstructions[num]

print(setupLinuxDriverInstructions)
print(tabulate.tabulate(table, headers=["label", "delta user inst.", "delta kernel inst.", "delta total inst."]))

def percentify(list, total):
    percList = []
    tmpTotal = 0
    for i in list:
        percList.append(i*100.0/total)
        tmpTotal += i
    if(tmpTotal != total):
        if(tmpTotal > total):
            print("Error: total given smaller than sum of list")
            sys.exit(-6)
        delta = (total - tmpTotal)*100.0/total
        percList[0] += delta
        print("Warning: adding "+str(delta)+" to first element, because of mismatch of totals")
    return percList

def reportStats(name, totalInst, userInst, kernelInst, setupInst, shimInst):
    xVals = percentify([userInst, (kernelInst-shimInst-setupInst), setupInst, shimInst], totalInst)
    print(name + ": " + str(totalInst))
    print("{:>16.4f}% user API".format(xVals[0]))
    print("{:>16.4f}% kernel driver".format(xVals[1]))
    print("{:>16.4f}% driver setup".format(xVals[2]))
    if(shimInst != 0):
        print("{:>16.4f}% management shim".format(xVals[3]))
    return xVals
    # for idx, x in enumerate(x_vals):
    #     if x == 0:
    #         x_vals[idx] = 0.001
    # objects = ('User API', 'Kernel Driver', 'Management Shim')
    # y_pos = numpy.arange(len(objects))
    # pyplot.barh(y_pos, x_vals, align='center')
    # pyplot.yticks(y_pos, objects)
    # pyplot.xlabel("Percentage of total instructions")
    # pyplot.title(name)
    # pyplot.show()

createEnclaveRow = 0
preparePagesRow = 1
createEnclaveRow_exclusive = 2
driverRow = createEnclaveRow + 5
if(int(labels[driverRow]) != 201):
    print("Label mismatch on driver row")
    sys.exit(-5)
sendingRow = driverRow + 14
receivingRow = sendingRow + 1

createStats = reportStats(name="Create enclave", totalInst=totalInstructions[createEnclaveRow], userInst=userInstructions[createEnclaveRow], kernelInst=kernelInstructions[createEnclaveRow], setupInst=setupLinuxDriverInstructions, shimInst=createEnclaveShimInstructions)
#altCreateStats = reportStats("Alternative create enclave", totalInstructions[createEnclaveRow], userInstructions[createEnclaveRow], kernelInstructions[createEnclaveRow], totalInstructions[driverRow])
reportStats("Communication channel setup", totalInstructions[sendingRow] + totalInstructions[receivingRow], userInstructions[sendingRow] + userInstructions[receivingRow], kernelInstructions[sendingRow] + kernelInstructions[receivingRow], 0, 0)

# createLabels        = ['Setup\nEnclave\nPages', 'Create Enclave', 'Setup Driver', 'Management Shim']
# createPercentages   = percentify([totalInstructions[preparePagesRow], (totalInstructions[createEnclaveRow_exclusive] - setupLinuxDriverInstructions - createEnclaveShimInstructions), setupLinuxDriverInstructions, createEnclaveShimInstructions], totalInstructions[createEnclaveRow])
createLabels        = ['Setup\nEnclave\nPages', 'Setup Driver', 'Management Shim']
createPercentages   = percentify([totalInstructions[preparePagesRow], setupLinuxDriverInstructions, (totalInstructions[createEnclaveRow_exclusive] - setupLinuxDriverInstructions)], totalInstructions[createEnclaveRow])
print(createLabels)
print(createPercentages)

sendingInstructions = []
receivingInstructions = []
for idx, inst in enumerate(userInstructions[sendingRow:]):
    if(idx%2 == 0):
        sendingInstructions.append(inst)
    else:
        receivingInstructions.append(inst)
print("Sending message:    " + str(int(statistics.median(sendingInstructions))) + " instructions")
print("Receiving message: " + str(int(statistics.median(receivingInstructions))) + " instructions")

def makeStackBar(level, percentages, labels):
    if(len(percentages) != len(labels)):
        print("Lengths must correspond for makeStackBar")
    cumm = 0
    height = 1
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
        pyplot.barh(y=[level], width=[p], height=height, left=cumm, align='center', color=barColor)
        verticalAlignment = 'center'
        xCoord = cumm+p/2
        tmpLevel = level
        if(p < 5):
            textColor = 'k'
            pyplot.arrow(xCoord, level+height*3./4., 0, -height/4., color=textColor, head_width=1., head_length=.05, length_includes_head=True)
            tmpLevel += height*3./4.
            verticalAlignment = 'bottom'
        pyplot.text(xCoord, tmpLevel, newLabel, ha='center', va=verticalAlignment, color=textColor)
        cumm += p

ticks = [0]#[0,2,4]
tickLabels = ['{:,}\nInstructions'.format(totalInstructions[createEnclaveRow])]#('Driver', 'Total', 'API + shim')

fig = pyplot.figure(figsize=(10,5))
#makeStackBar(level=ticks[0], percentages=[20, 20, 20, 40], labels=['Context Switch', 'DMA Alloc', 'Copy from user', 'Other'], colors=['g', 'c', 'darkturquoise', 'b'], textRotation=['0', '0', '0', '0'])
#makeStackBar(level=ticks[0], percentages=createStats, labels=['User API', 'Kernel Driver', 'Driver Setup' 'Management Shim'])
makeStackBar(level = ticks[0], percentages=createPercentages, labels=createLabels)
#makeStackBar(level=ticks[1], percentages=altCreateStats, labels=['User API', 'Kernel', 'Praesidio Driver +\nManagement Shim'])
#makeStackBar(level=ticks[2], percentages=[95.30, 4.60], labels=['User API', 'Shim'], colors=['r', 'orange'], textRotation=['0', '90'])

pyplot.grid(b=True, which='major', axis='x')
pyplot.yticks(ticks, tickLabels)
pyplot.ylim(min(ticks)-1, max(ticks) + 1.5)
pyplot.xlabel("Percentage of total")
pyplot.xlim(-10, 110)
pyplot.title("Cost to Create Enclave")

pyplot.show()
