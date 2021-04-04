
MAX_SIZE = 256

testlist = []

i = 0

while i < MAX_SIZE:
    testlist.append([])
    i = i + 1

print("1:\n\t", testlist)

testlist[5].append("task_a")
testlist[5].append("task_b")

print("2:\n\t", testlist)

testlist[5].remove("task_b")

print("3:\n\t", testlist)

testlist[6] = ["task_c", "task_d"]

print("3:\n\t", testlist)

j = 0
while testlist[j] == []:
    j = j + 1

print("index number: ", j, ", ", testlist[j])

