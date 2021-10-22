import pandas as pd
import pickle
with open("resultados.bin",'rb') as file:
    resultados_dataframe=pickle.load(file)
for a in resultados_dataframe.columns:
    print(f'{a} - mean:{round(resultados_dataframe[a].mean(),2)} std:{round(resultados_dataframe[a].std(),2)} min:{round(resultados_dataframe[a].min(),2)} max:{round(resultados_dataframe[a].max(),2)}')
b = []
for a in resultados_dataframe.index:
    b.append(round(resultados_dataframe.loc[a].mean(),2))
    print(f'{a} - mean:{round(resultados_dataframe.loc[a].mean(),2)} std:{round(resultados_dataframe.loc[a].std(),2)} min:{round(resultados_dataframe.loc[a].min(),2)} max:{round(resultados_dataframe.loc[a].max(),2)}')
b = pd.Series(b)
print(f'mean {b.mean()} std:{b.std()} min:{b.min()} max:{b.max()}')