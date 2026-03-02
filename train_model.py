import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load data WITHOUT assuming header
data = pd.read_csv("asl_data.csv", header=None)

# First column = labels
y = data.iloc[:,0]

# Remaining columns = features
X = data.iloc[:,1:]

model = RandomForestClassifier()

model.fit(X,y)

pickle.dump(model,open("asl_model.pkl","wb"))

print("Model Saved Successfully")