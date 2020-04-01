import csv
import sys
import tabulate

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
    print(name + ": " + str(totalInst))
    print("{:>16.2f}% user API".format(userInst*100.0/totalInst))
    print("{:>16.2f}% kernel driver".format((kernelInst - shimInst)*100.0/totalInst))
    if(shimInst != 0):
        print("{:>16.2f}% management shim".format(shimInst*100.0/totalInst))

reportStats("Create enclave", totalInstructions[0], userInstructions[0], kernelInstructions[0], createEnclaveShimInstructions)
reportStats("Communication channel setup", totalInstructions[12] + totalInstructions[13], userInstructions[12] + userInstructions[13], kernelInstructions[12] + kernelInstructions[13], 0)

