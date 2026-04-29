import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score,accuracy_score,auc,confusion_matrix
import pefile
from scanner.features import extract_features

# Load data from the absolute path it was originally located at
try:
    malData=pd.read_csv(r"C:\Users\vaval\Desktop\jup\MalwareData.csv",sep="|",low_memory=True)
except FileNotFoundError:
    print("Warning: MalwareData.csv not found at the expected location.")
    malData=pd.DataFrame()
print(malData.shape)
#malData.head()
malData['legitimate'].value_counts()[0]
#malData.columns
k = malData["ResourcesMaxEntropy"].mean()
print(k)

fig=plt.figure()
ax=fig.add_axes([0,0,1,1])
ax.hist(malData['legitimate'],20)
plt.show()

malData=malData.drop(['Name'],axis=1)
malData=malData.drop(['md5'],axis=1)
# Calculate the cou
#rrelation matrix
correlation_matrix = malData.corr()

# Create a heatmap of the correlation matrix
plt.figure(figsize=(50, 20))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()

y=malData['legitimate']
malData=malData.drop(['legitimate'],axis=1)

# Specify the columns to keep
columns_to_keep = ['Machine', 'SizeOfOptionalHeader', 'MajorSubsystemVersion','DllCharacteristics','SizeOfStackReserve','SectionsMeanEntropy','SectionsMaxEntropy','Subsystem','ResourcesMaxEntropy','VersionInformationSize']

# Keep only the specified columns
malData = malData[columns_to_keep]
x_train,x_test,y_train,y_test=train_test_split(malData,y,test_size=0.3,random_state=42)

print(x_train.shape)
# Removed max_depth=2 to prevent underfitting
clf=RandomForestClassifier(random_state=0)
# Use .values to strip feature names during training to prevent the UserWarning during prediction
randomModel=clf.fit(x_train.values, y_train.values)

# Save the trained model directly to the scanner directory
model_path = os.path.join('scanner', 'model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(randomModel, f)
print(f"Model successfully saved to {model_path}")

#accuracy of trained dataset
train_pred=randomModel.predict(x_train.values)
accuracy_score(y_train.values,train_pred)
print(train_pred)

#accuracy of test dataset
prediction=randomModel.predict(x_test.values)
print("accuracy:",accuracy_score(y_test,prediction))
print(prediction)

print(f1_score(y_test,prediction))

confusionmatrix=confusion_matrix(y_test,prediction)
print(confusionmatrix)

sns.heatmap(confusionmatrix,annot=True)

# Path to the executable file
file_path = 'boy.exe'

try:
    # Use the shared feature extraction logic
    lst = extract_features(file_path)
    print("Extracted Features:", lst)

    pred = randomModel.predict([lst])
    print("Prediction:", pred)

    if pred[0] == 0:
        print("File is safe")
    else:
        print("File contains ransomware")  
except Exception as e:
    print(f"Failed to analyze {file_path}: {e}")