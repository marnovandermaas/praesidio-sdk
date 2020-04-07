import csv
import sys
import tabulate
import matplotlib.pyplot as pyplot
import matplotlib
import numpy
import statistics

#TODO put output stats around the whole create enclave driver thing to see how many instructions are lost in the context switch

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

print(titles)
# print(data)

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
        for idx in range(num+1, len(data)):
            if int(data[idx][labelIndex]) is currentLabel:
                processedRows.append(idx)
                #Instructions
                tmpKernelInstructions = int(data[idx][kernelInstructionIndex]) - int(row[kernelInstructionIndex])
                tmpTotalInstructions = int(data[idx][totalInstructionIndex]) - int(row[totalInstructionIndex])
                userInstructions.append(tmpTotalInstructions - tmpKernelInstructions)
                kernelInstructions.append(tmpKernelInstructions)
                totalInstructions.append(tmpTotalInstructions)
                break

#print(labels)
#print(userInstructions)
#print(kernelInstructions)
#print(processedRows)

if((len(labels) != len(userInstructions)) or (len(labels) != len(kernelInstructions)) or (len(labels) != len(data)/2) or (len(processedRows) != len(data))):
    print("ERROR: Something went wrong when processing the data.")
    sys.exit(-2)

table = []
createEnclaveShimInstructions = 0

for num, label in enumerate(labels):
    table.append([label, userInstructions[num], kernelInstructions[num], totalInstructions[num]])
    if(label >= 100 and label < 200):
        if(kernelInstructions[num] != totalInstructions[num]):
            print("ERROR: something went wrong when processing create enclave.")
            sys.exit(-3)
        createEnclaveShimInstructions += kernelInstructions[num]

print(tabulate.tabulate(table, headers=["label", "delta user inst.", "delta kernel inst.", "delta total inst."]))

def reportStats(name, totalInst, userInst, kernelInst, shimInst):
    xVals = [userInst*100.0/totalInst, (kernelInst - shimInst)*100.0/totalInst, shimInst*100.0/totalInst]
    print(name + ": " + str(totalInst))
    print("{:>16.4f}% user API".format(xVals[0]))
    print("{:>16.4f}% kernel driver".format(xVals[1]))
    if(shimInst != 0):
        print("{:>16.4f}% management shim".format(xVals[2]))
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

createEnclaveRow = 1
sendingRow = createEnclaveRow+14
receivingRow = sendingRow + 1

createStats = reportStats("Create enclave", totalInstructions[createEnclaveRow]+totalInstructions[0], userInstructions[createEnclaveRow]+totalInstructions[0], kernelInstructions[createEnclaveRow], createEnclaveShimInstructions)
reportStats("Communication channel setup", totalInstructions[sendingRow] + totalInstructions[receivingRow], userInstructions[sendingRow] + userInstructions[receivingRow], kernelInstructions[sendingRow] + kernelInstructions[receivingRow], 0)

sendingInstructions = []
receivingInstructions = []
for idx, inst in enumerate(userInstructions[sendingRow:]):
    if(idx%2 == 0):
        sendingInstructions.append(inst)
    else:
        receivingInstructions.append(inst)
print("Sending message:    " + str(int(statistics.median(sendingInstructions))) + " instructions")
print("Receiving message: " + str(int(statistics.median(receivingInstructions))) + " instructions")

def makeStackBar(level, percentages, labels, colors):
    if(len(percentages) != len(labels) or  len(percentages) != len(colors)):
        print("Lengths must correspond for makeStackBar")
    cumm = 0
    newLabels = []
    height = 1
    for idx, label in enumerate(labels):
        newLabels.append(label + "{:>2.2f}%".format(percentages[idx]))
    for idx, p in enumerate(percentages):
        pyplot.barh(y=[level], width=[p], height=height, left=cumm, align='center', color=colors[idx])
        r, g, b = matplotlib.colors.to_rgb(colors[idx])
        textColor = 'white' if r * g * b < 0.5 else 'darkgrey'
        verticalAlignment = 'center'
        xCoord = cumm+p/2
        if(p < 5):
            textColor = colors[idx]
            #pyplot.plot([xCoord, xCoord], [level+height/2, level+height], color=textColor, linestyle='-')
            pyplot.arrow(xCoord, level+height, 0, -height/2, color=textColor, head_width=1., head_length=.05, length_includes_head=True)
            level += height
            verticalAlignment = 'bottom'
        pyplot.text(xCoord, level, newLabels[idx], ha='center', va=verticalAlignment, color=textColor)
        cumm += p

ticks = [0]#[0,2,4]
tickLabels = ['Instructions']#('Driver', 'Total', 'API + shim')

fig = pyplot.figure(figsize=(10,5))
#makeStackBar(level=ticks[0], percentages=[20, 20, 20, 40], labels=['Context Switch', 'DMA Alloc', 'Copy from user', 'Other'], colors=['g', 'c', 'darkturquoise', 'b'], textRotation=['0', '0', '0', '0'])
makeStackBar(level=ticks[0], percentages=createStats, labels=['User API\n', 'Kernel Driver ', 'Management Shim\n'], colors=['r', 'g', 'b'])
#makeStackBar(level=ticks[2], percentages=[95.30, 4.60], labels=['User API', 'Shim'], colors=['r', 'orange'], textRotation=['0', '90'])

pyplot.grid(b=True, which='major', axis='x')
pyplot.yticks(ticks, tickLabels)
pyplot.ylim(-1, 2)
pyplot.xlabel("Percentage of total")
pyplot.xlim(-10, 110)

pyplot.show()
