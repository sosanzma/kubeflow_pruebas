import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
df['sepal_area'] = df['sepal_length'] * df['sepal_width']
df.to_csv('/output/processed.csv', index=False)
