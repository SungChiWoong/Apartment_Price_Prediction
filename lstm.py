# -*- coding: utf-8 -*-

from keras.backend import dropout
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


Gung=pd.read_csv("/content/sample_data/OO시.csv")

Gung = Gung.drop(['5년이하 전세가격지수'], axis = 1)

Gung['date'] = pd.to_datetime(Gung['날짜'])

Gung = Gung.drop(['날짜'], axis = 1)

ts_train = Gung[:54].iloc[:,0:1].values
ts_test = Gung[54:].iloc[:,0:1].values
ts_train_len = len(ts_train)
ts_test_len = len(ts_test)

# scale the data
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0,1))
ts_train_scaled = sc.fit_transform(ts_train)

# create training data of s samples and t time steps
X_train = []
y_train = []
for i in range(3, ts_train_len-1):
    X_train.append(ts_train_scaled[i-3:i, 0])
    y_train.append(ts_train_scaled[i:i+1, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1 ))

inputs = pd.concat((Gung["5년이하 매매가격지수"][:54], Gung["5년이하 매매가격지수"][54:]), axis=0).values
inputs = inputs[len(inputs)-len(ts_test)-3:]

inputs = inputs.reshape(-1,1)
inputs = sc.fit_transform(inputs)
inputs

X_train.shape

from keras.backend import dropout
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.optimizers import gradient_descent_v2
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.optimizers import SGD
from keras.metrics import MeanSquaredError
from tensorflow import keras
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error, r2_score

Gung=pd.read_csv("/content/sample_data/OO시.csv")

tf.random.set_seed(14)
np.random.seed(seed=14)
train = Gung[:103].iloc[:,0:1].values
def ts_train_test_normalize(all_data, time_steps, for_periods):
    ts_train = all_data[:103].iloc[:,0:1].values
    ts_test = all_data[103:].iloc[:,0:1].values
    ts_train_len = len(ts_train)
    ts_test_len = len(ts_test)

    sc = MinMaxScaler(feature_range=(0,1))
    ts_train_scaled = sc.fit_transform(ts_train)

    X_train = []
    y_train = []
    for i in range(time_steps, ts_train_len-1):
        X_train.append(ts_train_scaled[i-time_steps:i, 0])
        y_train.append(ts_train_scaled[i:i+for_periods, 0])
    X_train, y_train = np.array(X_train), np.array(y_train)

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1 ))

    inputs = pd.concat((all_data["epu"][:103], all_data["epu"][103:]), axis=0).values
    inputs = inputs[len(inputs)-len(ts_test)-time_steps:]
    inputs = inputs.reshape(-1,1)
    inputs = sc.transform(inputs)
    X_test = []
    for i in range(time_steps, ts_test_len + time_steps - for_periods):
        X_test.append(inputs[i-time_steps:i,0])
    X_test = np.array(X_test)
    print(X_test.shape)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    return X_train, y_train, X_test, sc

X_train, y_train, X_test, sc = ts_train_test_normalize(Gung,3,1)
X_train.shape[0], X_train.shape[1]

X_train_see = pd.DataFrame(np.reshape(X_train, (X_train.shape[0], X_train.shape[1])))
y_train_see = pd.DataFrame(y_train)
pd.concat([X_train_see, y_train_see], axis = 1)

X_test_see = pd.DataFrame(np.reshape(X_test, (X_test.shape[0], X_test.shape[1])))
pd.DataFrame(X_test_see)

print("There are " + str(X_train.shape[0]) + " samples in the training data")
print("There are " + str(X_test.shape[0]) + " samples in the test data")

def actual_pred_plot(preds):
    actual_pred = pd.DataFrame(columns = ['epu', 'prediction'])
    actual_pred['epu'] = Gung.loc[103:,'epu'][0:len(preds)]
    actual_pred['prediction'] = preds[:,0]


    m = MeanSquaredError()
    m.update_state(np.array(actual_pred['epu']), np.array(actual_pred['epu']))

    return (m.result().numpy(), actual_pred.plot())

my_LSTM_model = Sequential()
my_LSTM_model.add(LSTM(units = 50,
                      return_sequences = True,
                      input_shape = (X_train.shape[1],1),
                      activation = 'relu'))
my_LSTM_model.add(LSTM(units = 50, activation = 'relu'))
my_LSTM_model.add(Dense(units=1))

my_LSTM_model.compile(optimizer = SGD(lr = 0.01, decay = 1e-7,
                                    momentum = 0.9, nesterov = False),
                    loss = 'mean_squared_error')

my_LSTM_model.fit(X_train, y_train, epochs = 20000, batch_size =len(X_train), verbose = 0, shuffle=False)

A = X_test[65:]
B=[]
print(A.shape)
for i in range(0,24,1):
  K = my_LSTM_model.predict(A)
  A = np.append(A, np.array(K))
  B=np.append(B,np.array(K))
  A = A[1:]
  A = A.reshape(-1,3,1)

B=B.reshape(-1,1)
B=sc.inverse_transform(B)
# print(B.dtype)
plt.plot(B)
plt.show()

C=pd.DataFrame(B)
C.to_csv('OO시.csv',index=False)

LSTM_prediction = my_LSTM_model.predict(X_test)
LSTM_prediction[1:10]
LSTM_prediction = sc.inverse_transform(LSTM_prediction)

print(LSTM_prediction[1:10])
print(LSTM_prediction.shape)
LSTM_prediction[1:10]
actual_pred_plot(LSTM_prediction)

y_pred = pd.DataFrame(LSTM_prediction[:, 0])

R = np.append(LSTM_prediction,B)
R2=np.append(train,R)
plt.plot(R2)
plt.show()
y_test=Gung.loc[103:,'epu'][0:len(LSTM_prediction)]
y_test.reset_index(drop=True, inplace=True)

def confirm_result(y_test, y_pred):
    MAE = mean_absolute_error(y_test, y_pred)
    MSE = mean_squared_error(y_test, y_pred)
    RMSE = np.sqrt(mean_squared_error(y_test, y_pred))
    MSLE = mean_squared_log_error(y_test, y_pred)
    RMSLE = np.sqrt(mean_squared_log_error(y_test, y_pred))
    R2 = r2_score(y_test, y_pred)

    pd.options.display.float_format = '{:.5f}'.format
    Result = pd.DataFrame(data=[MAE,MSE,RMSE, RMSLE, R2],
                        index = ['MAE','MSE','RMSE', 'RMSLE', 'R2'],
                        columns=['Results'])
    return Result
print(confirm_result(y_test, y_pred))

def fix_font():
  import os
  import matplotlib as mpl
  import matplotlib.pyplot as plt
  os.system("apt-get install -y fonts-nanum")
  os.system("fc-cache -fv")
  mpl.font_manager._rebuild()
  findfont=mpl.font_manager.fontManager.findfont
  mpl.font_manager.findfont=findfont
  mpl.backends.backend_agg.findfont=findfont
  plt.rcParams['font.family']="NanumBarunGothic"
  plt.rcParams['axes.unicode_minus']=False

fix_font()

