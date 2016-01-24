


x = {1:'a', 2:'b', 3:'c'}
print x

for i in x:
    if i == 2:
        del x[i]
    if i in x:
        print i