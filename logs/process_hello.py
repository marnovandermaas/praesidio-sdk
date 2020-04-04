import csv
import sys
import tabulate
import matplotlib.pyplot as pyplot
import numpy
import statistics

#TODO put output stats around the whole create enclave driver thing to see how many instructions are lost in the context switch
#TODO put output stats around dma_alloc_coherent in create enclave
#TODO put output stats around copy_from_user in create enclave
#TODO put output stats around opening file, mallocing and copying in hello/user.c

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
    if(label > 100):
        if(kernelInstructions[num] != totalInstructions[num]):
            print("ERROR: something went wrong when processing create enclave.")
            sys.exit(-3)
        createEnclaveShimInstructions += kernelInstructions[num]

print(tabulate.tabulate(table, headers=["label", "delta user inst.", "delta kernel inst.", "delta total inst."]))

def reportStats(name, totalInst, userInst, kernelInst, shimInst):
    x_vals = [userInst*100.0/totalInst, (kernelInst - shimInst)*100.0/totalInst, shimInst*100.0/totalInst]
    print(name + ": " + str(totalInst))
    print("{:>16.2f}% user API".format(x_vals[0]))
    print("{:>16.2f}% kernel driver".format(x_vals[1]))
    if(shimInst != 0):
        print("{:>16.2f}% management shim".format(x_vals[2]))
    for idx, x in enumerate(x_vals):
        if x == 0:
            x_vals[idx] = 0.001
    objects = ('User API', 'Kernel Driver', 'Management Shim')
    y_pos = numpy.arange(len(objects))
    pyplot.barh(y_pos, x_vals, align='center')
    pyplot.yticks(y_pos, objects)
    pyplot.xlabel("Percentage of total instructions")
    pyplot.title(name)
    pyplot.show()



#reportStats("Create enclave", totalInstructions[0], userInstructions[0], kernelInstructions[0], createEnclaveShimInstructions)
#reportStats("Communication channel setup", totalInstructions[12] + totalInstructions[13], userInstructions[12] + userInstructions[13], kernelInstructions[12] + kernelInstructions[13], 0)

sendingInstructions = []
receivingInstructions = []
for idx, inst in enumerate(userInstructions[14:]):
    if(idx%2 == 0):
        sendingInstructions.append(inst)
    else:
        receivingInstructions.append(inst)
print("Sending message:    " + str(int(statistics.median(sendingInstructions))) + " instructions")
print("Receiving message: " + str(int(statistics.median(receivingInstructions))) + " instructions")

def makeStackBar(ax, percentages, labels, colors, textRotation, tickLabel):
    if(len(percentages) != len(labels) or  len(percentages) != len(colors) or len(percentages) != len(textRotation)):
        print("Lengths must correspond for makeStackBar")
    cumm = 0
    newLabels = []
    for idx, label in enumerate(labels):
        newLabels[idx] = label + " " + str(percentage) + "%"
    for idx, p in enumerate(percentages):
        ax.barh([0], [p], left=cumm, align='center', color=colors[idx])
        r, g, b, _ = colors[idx]
        textColor = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.text(cumm+p/2, 0, labels[idx], ha='center', va='center', color=textColor, rotation=textRotation)
        cum += p
    ax.set_yticks([0])
    ax.set_yticklabels([tickLabel])

pyplot.figure()
ax1 = pyplot.subplot(411)
ax1.barh([0], [9.78], align='center', color='r')
ax1.barh([0], [90.22], left=9.78, align='center', color='b')
ax1.text(9.78/2, 0, 'API + Shim\n9.78%', ha='center', va='center', color='k', rotation='90')
ax1.text(9.78+90.22/2, 0, 'Kernel Driver\n90.22%', ha='center', va='center', color='w')
ax1.set_yticks([0])
ax1.set_yticklabels(['Total'])

ax2 = pyplot.subplot(412)
ax2.barh([0], [95.30], align='center', color='r')
ax2.barh([0], [4.60], left=95.30, align='center', color='orange')
ax2.text(95.30/2, 0, 'User API\n95.3%', ha='center', va='center', color='k')
ax2.text(95.30 + 4.60/2, 0, 'Shim 4.6%', ha='center', va='center', color='k', rotation='90')
ax2.set_yticks([0])
ax2.set_yticklabels(['API+Shim'])

ax3 = pyplot.subplot(413)
makeStackBar(ax3, [9.78, 90.22], ['API + Shim\n9.78%', ])
ax3.barh([1,2,3], [1,2,3], align='center')

ax4 = pyplot.subplot(414)

pyplot.show()
#context switch, dma_alloc_coherent, copy_from_user
