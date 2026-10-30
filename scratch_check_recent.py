import pandas as pd
import numpy as np

pca_df = pd.read_csv("d:/SAHAM/chart/macro_ml_pca.csv", index_col=0, parse_dates=True)
print("Last 12 months in PCA and Labels:")
print(pca_df.tail(12))
