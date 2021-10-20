```

from random import random,choice,choices


def get_random_modify(goal,value,step =5):
    return round(((goal-value)*random())+(choice([-1,1]))*(step*random()),2)

preção = 120
oxigenação = 100
tempertura = 36
freq_respiratoria = 10
fre_card = 100
print('P O T fr fc : R')
print(f'{preção} {oxigenação} {tempertura} {freq_respiratoria} {fre_card} : {(100-preção)*3+(96-oxigenação)*4+(freq_respiratoria-20)*3+(tempertura-38)*4+(fre_card-100)*3}')   
_preção =[120,5]
_oxigenação = [98,.5]
_freq_respiratoria=[10,1]
_tempertura= [36,0.5]
_fre_card = [110,3]

print("pacientes bons")

for _ in range (10):
    preção = round( preção+get_random_modify(_preção[0],preção,_preção[1]),2)
    oxigenação = round( oxigenação+get_random_modify(_oxigenação[0],oxigenação,_oxigenação[1]),2)
    tempertura = round( tempertura+get_random_modify(_tempertura[0],tempertura,_tempertura[1]),2)
    freq_respiratoria =round( freq_respiratoria+get_random_modify(_freq_respiratoria[0],freq_respiratoria,_freq_respiratoria[1]),2)
    fre_card = round( fre_card+get_random_modify(_fre_card[0],fre_card,_fre_card[1]),2)
    print(f'{preção} | {oxigenação} | {tempertura} | {freq_respiratoria} | {fre_card} : {(100-preção)*3+(96-oxigenação)*4+(freq_respiratoria-20)*3+(tempertura-38)*4+(fre_card-100)*3}')  

_preção =[70,5]
_oxigenação = [25,5]
_freq_respiratoria=[25,1]
_tempertura= [40,0.5]
_fre_card = [115,3]

print("pacientes ruim")

for _ in range (10):
    preção = round( preção+get_random_modify(_preção[0],preção,_preção[1]),2)
    oxigenação = round( oxigenação+get_random_modify(_oxigenação[0],oxigenação,_oxigenação[1]),2)
    tempertura = round( tempertura+get_random_modify(_tempertura[0],tempertura,_tempertura[1]),2)
    freq_respiratoria =round( freq_respiratoria+get_random_modify(_freq_respiratoria[0],freq_respiratoria,_freq_respiratoria[1]),2)
    fre_card = round( fre_card+get_random_modify(_fre_card[0],fre_card,_fre_card[1]),2)
    print(f'{preção} | {oxigenação} | {tempertura} | {freq_respiratoria} | {fre_card} : {(100-preção)*3+(96-oxigenação)*4+(freq_respiratoria-20)*3+(tempertura-38)*4+(fre_card-100)*3}')   
```