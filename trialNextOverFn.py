def newover(endover):
    if endover[-2:]=='.6':
        newover = str(int(float(endover[:-2]))+1)
        newover = newover+'.1'
    else:
        newover = endover[:-1]+str(int(float(endover[-1:]))+1)
    return newover
   

print newover('134.5')
print newover('134.6')
print newover('1.1')
print newover('1.2')
print newover('1.3')
print newover('0.1')
print newover('0.6')