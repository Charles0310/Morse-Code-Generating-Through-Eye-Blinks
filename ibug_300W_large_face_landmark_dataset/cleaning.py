
file = open('./')
#file = open('./labels_ibug_300W_train_eyes.xml', 'r')
file2 = open('./new.xml','a')
lines = file.readlines()
n= len(lines)
print(n)
i = 0
ans = []
while i < n:
    if lines[i].startswith("  <image file='helen"):
        ans.append(lines[i:i+16])
        for j in range(i,i+16):
            file2.write(lines[j])
        i += 16
    else:
        i += 1            
    

    
    

    