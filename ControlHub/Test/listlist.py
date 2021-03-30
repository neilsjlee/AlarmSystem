

test = []

print(test)
test.append([1,2,3,4])

print(test)
print(test[0])

test[0].pop(3)

print(test)
print(test[0])

test[0].pop(0)

print(test)
print(test[0])

test[0].pop(0)

print(test)
print(test[0])

test[0].pop(0)

print(test)
print(test[0])

if test[0] is None:
    print("\"test\"is " + "None")
elif test[0] == []:
    print("\"test\"is " + "[]")
elif not test[0]:
    print("\"test\" " + "not test[0]")
elif len(test[0]) == 0:
    print("\"test\"is " + "not test[0]")

