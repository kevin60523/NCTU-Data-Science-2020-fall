from random import randint
import random
classification = []
for i in range(100):
    k = 1
    classification.append(k)
with open('./classification.txt', 'w') as f:
    f.write("%s" % ''.join(str(x) for x in classification))
    
