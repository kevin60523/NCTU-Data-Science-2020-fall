"""
CREDIT TO　３０９５５１０６２
"""
import pandas as pd
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from collections import Counter, defaultdict
from sklearn import preprocessing
from sklearn import svm
from tqdm import tqdm

training_data = pd.read_csv('./train.csv')
testing_data = pd.read_csv('./test.csv')

vectorizer = TfidfVectorizer()
vectorizer.fit(training_data['Headline'] + ' ' + training_data['Category'])
train_X = vectorizer.transform(training_data['Headline'] + ' ' + training_data['Category'])
train_y = [label for label in training_data['Label'].to_list()]
le = preprocessing.LabelEncoder()
le.fit(train_y)
train_y = le.transform(train_y)

clf = svm.SVC(probability=True, random_state=8964)
clf.fit(train_X.toarray(), train_y)
dev_X = vectorizer.transform(testing_data['Headline'] + ' ' + testing_data['Category'])
svm_probabilities = clf.predict_proba(dev_X.toarray())

total_predict = []
for row in svm_probabilities:
    result = np.where(row == np.amax(row))
    total_predict.append(le.inverse_transform(result[0])[0])
    

answer = pd.DataFrame(columns=['ID', 'Label'])
for i in range(len(testing_data)):
    df = pd.DataFrame({'ID':[testing_data['ID'][i]], 'Label':[total_predict[i]-0.4]})
    answer = answer.append(df, ignore_index = True)

answer.to_csv ('./answer.csv', index = False, header=True)

