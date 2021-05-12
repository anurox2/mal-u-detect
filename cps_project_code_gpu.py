# -*- coding: utf-8 -*-
"""CPS_Project_Code_GPU.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DE2UB75hnj6uQ4bZFy1qwh44rY2zml7s
"""

"""
Cyberphysical Systems Project - DGA Detection code optimized for GPU
Created By: Aman Kumar Gupta
WSU ID: X397J446
"""

# Import libraries here
## Data manipulation libraries
import pandas as pd
import numpy as np
from numpy import savetxt

## Machine learning libraries
# Tensorflow
from tensorflow.python.keras.preprocessing import sequence
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers.core import Dense, Dropout, Activation
from tensorflow.python.keras.layers.embeddings import Embedding
from tensorflow.python.keras.layers.recurrent import LSTM
from tensorflow.python.keras.callbacks import Callback
# Sklearn
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from matplotlib import pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.metrics import auc

import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Activation, Conv1D, Input, Dense, concatenate
from keras.optimizers import SGD
from keras.layers.embeddings import Embedding
from keras.layers.pooling import GlobalMaxPooling1D

# Downloading the data files
!wget https://github.com/anurox2/cps_project/raw/master/dga_text.csv
!wget https://github.com/anurox2/cps_project/raw/master/top_1m_small.csv

# Fetch time and generate filename
import time
timestr = str(time.strftime("%Y-%m-%d_%H-%M"))
filename = "Run_"+timestr
print(filename)

"""## Data Prep"""

# Read the benign dataset and add a classification column ------------------------------------------------
df1_benign = pd.read_csv('top_1m_small.csv', index_col=False, header=None, low_memory=False)

try:
    print('Trying to drop column 0 ------')
    df1_benign.drop(columns={0}, inplace=True)
    df1_benign.drop(df1_benign.index[0], inplace=True)
except Exception:
    print(Exception.with_traceback())
    print("Dropping column 0 in the benign dataset failed")

try:
    print('Trying to rename column 1 ------')
    df1_benign.rename(columns={1:'URLs', 2:'classify'}, inplace=True)
except Exception:
    print(Exception)
    print("Renaming column 1 to URLs in the benign dataset failed")

# Benign URLs are set to 0 (zero)
df1_benign['classify'] = 0

# --------------------------------------------------------------------------------------------------------

# Read the malicious dataset and add a classification column ----------------------------------------------------------------------
df2_mal = pd.read_csv('dga_text.csv', header=None, low_memory=False)
df2_mal.rename(columns={0: 'URLs'}, inplace=True)

# Malicious URLs are set to 1 (one)
df2_mal['classify'] = 1
print("Both datasets have the same length", (df1_benign.shape == df2_mal.shape), "\n\t", df1_benign.shape, "\t", df2_mal.shape)
# ---------------------------------------------------------------------------------------------------------------------------------

if(df1_benign.shape == df2_mal.shape):
    # Forming the dataset
    df3_final = pd.concat([df1_benign, df2_mal], axis=0)
    df3_final = df3_final.sample(frac=1).reset_index(drop=True)

    ## Writing the final dataset back
    df3_final.to_csv('final_dataset.csv', index=False)

    # Use the full data set
    df4_test = df3_final.copy(deep=True)

    X = df4_test['URLs'].tolist()

    valid_chars = {x:idx+1 for idx, x in enumerate(set(''.join(X)))}
    max_features = len(valid_chars)+1
    maxlen = np.max([len(x) for x in X])
    print("The longest url is", maxlen, "characters long")

    X = [[valid_chars[y] for y in x] for x in X]
    X = sequence.pad_sequences(X, maxlen=maxlen)

    y = df4_test['classify'].values
    labels = ['URLs', 'classify']
    print(df4_test.head())

else:
    print("Stopping code!! Datasets aren't of the same size!!")

X_full = X
y_full = y

# Shorten dataset?
shorten = False
subset_value = 10000

if(shorten):
    print("Using subset for training!!! -----------------------------------------------------------")
    X = X_full[:subset_value]
    y = y_full[:subset_value]
else:
    print("Using full dataset for training!!! -----------------------------------------------------------")

"""## Machine Learning"""

## The following class is used to generate a set of metrics such as precision, recall, and F1 score, since the new Keras library doesn't support it.
class ModelMetrics(Callback):
  
  def on_train_begin(self,logs={}):
    self.precisions=[]
    self.recalls=[]
    self.f1_scores=[]
  def on_epoch_end(self, batch, logs={}):
    
    y_val_pred=self.model.predict(X_test)
   
    _precision,_recall,_f1,_sample=precision_recall_fscore_support(y_test,y_val_pred)
    
    
    self.precisions.append(_precision)
    self.recalls.append(_recall)
    self.f1_scores.append(_f1)

metrics = ModelMetrics()

# ML model ----------------------------------------------

epochs = 50

### CNN Code
text_input = Input(shape = (maxlen,), name='text_input')
x = Embedding(input_dim=max_features, input_length=maxlen, output_dim=128)(text_input)

conv_a = Conv1D(15,2, activation='relu')(x)
conv_b = Conv1D(15,3, activation='relu')(x)
conv_c = Conv1D(15,4, activation='relu')(x)
conv_d = Conv1D(15,5, activation='relu')(x)
conv_e = Conv1D(15,6, activation='relu')(x)

pool_a = GlobalMaxPooling1D()(conv_a)
pool_b = GlobalMaxPooling1D()(conv_b)
pool_c = GlobalMaxPooling1D()(conv_c)
pool_d = GlobalMaxPooling1D()(conv_d)
pool_e = GlobalMaxPooling1D()(conv_e)

flattened = concatenate([pool_a, pool_b, pool_c, pool_d, pool_e])

drop = Dropout(.2)(flattened)

outputs = []
for name in range(0,1):
  dense = Dense(1)(drop)
  out = Activation("sigmoid")(dense)
  outputs.append(out)
ml_model1 = Model(inputs=text_input, outputs=outputs)

ml_model1.compile(loss='binary_crossentropy',
    optimizer='rmsprop',
    metrics=['accuracy', 'mae']
    )

## Splitting the test and train dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, )

## Fitting data to the model
history = ml_model1.fit(X_train, y_train, 
                        batch_size=128,
                        epochs=epochs,
                        validation_data=(X_test, y_test),
                        verbose=1)

y_pred = ml_model1.predict(X_test)
out_data = {'y':y_test, 'pred':y_pred, 'confusion_matrix': sklearn.metrics.confusion_matrix(y_test, y_pred>0.5)}

print(out_data)

print("\n\nConfusion Matrix",sklearn.metrics.confusion_matrix(y_test, y_pred>0.5))
print("\n\nAccuracy of the model", accuracy_score(y_test, y_pred>0.5)*100)

## PRINTING GRAPHS -----------------------------------------------------------

# ## Get training and testing accuracy values
# training_accuracy = history.history['accuracy']
# test_accuracy = history.history['val_accuracy']

# ## Get training and testing loss values
# training_loss = history.history['loss']
# test_loss = history.history['val_loss']

# ## Get training and testing MAE values
# training_mae = history.history['mae']
# test_mae = history.history['val_mae']

# ## Visualize loss history
# # Plot training & validation accuracy values
# plt.plot(training_accuracy)
# plt.plot(test_accuracy)
# plt.title('Model accuracy')
# plt.ylabel('Accuracy')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')

# filename_acc = filename + "_Accuracy.pdf"

# plt.savefig(filename_acc, bbox_inches='tight')
# # plt.show()
# plt.close()

# # Plot training & validation loss values
# plt.plot(training_loss)
# plt.plot(test_loss)
# plt.title('Model loss')
# plt.ylabel('Loss')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')
# # plt.show()
# filename_loss = filename + "_Loss.pdf"
# plt.savefig(filename_loss, bbox_inches='tight')
# # plt.show()
# plt.close()

# # Plot training & validation MAE values
# plt.plot(training_mae)
# plt.plot(test_mae)
# plt.title('Model MAE')
# plt.ylabel('MAE')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')
# # plt.show()
# filename_mae = filename + "_MAE.pdf"
# plt.savefig(filename_mae, bbox_inches='tight')
# # plt.show()
# plt.close()

!pip install h5py

ml_model1.save("ml_model1.h5")
print("Saved model to disk")

# Import keras dependencies
from keras.models import load_model

# Load model from file
model_loaded_from_file = load_model('ml_model1.h5')

# Print model summary
model_loaded_from_file.summary()

url_test = ['facebook.com', 'google.com', 'wdwdbwudbiwu234234378.we', 'f104ea51c3.net', 'f13a20fe91.biz', 'f150ca94e5.in', 'f15ee0f88c.biz', 'f16e947827.biz', 'f18f11f8c6.org', 'f1f94c94ce.in', 'f26587fa7d.in', 'f31e13083a.info', 'f3894fffd7.com', 'f3abc4206d.com', 'f43fc75d58.info', 'f468a98bec.org', 'f49524f1f1.in', 'f49c90beb9.com', 'f4f4c59a12.in', 'f53e582bb5.net', 'f5a5f41b76.net', 'f5f14065ff.com', 'f65a67f2b0.org', 'f6b9261356.in', 'f6fb725d56.org', 'f806a43bdf.com']
pred_data = pd.DataFrame(url_test, columns = ['URLs'])



X_pred = pred_data['URLs'].tolist()
X_pred = [[valid_chars[y] for y in x] for x in X_pred]
X_pred = sequence.pad_sequences(X_pred, maxlen=maxlen)

y_pred = model_loaded_from_file.predict(X_pred)

combined_data = list(zip(url_test, y_pred))

results = pd.DataFrame(combined_data, columns=['URLs', 'Malicious Probability'])
print(results)