file1 = open("min", "r")
file2 = open("max", "r")
file1 = file1.readlines()
file2 = file2.readlines()
mini = float('inf') 
t1 = 0
t2 = 0

for index in range(0,len(file1)):
    diff = float(file2[index]) - float(file1[index])
    if diff < mini:
        mini = diff
        t1= file1[index]
        t2=file2[index]

print mini,t1,t2

