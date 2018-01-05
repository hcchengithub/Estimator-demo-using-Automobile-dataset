import pandas as pd
import numpy as np
import peforth
import tensorflow as tf
peforth.ok(cmd='''
    ." Please make sure that version >= 1.2" cr
    __main__ :> tf.__version__ . cr
    cr ." Type 'exit' to continue or 'bye' to abort " cr
    ''')

# Read CSV dataset
# The CSV file does not have a header, so we have to fill in column names.
names = ['symboling', 'normalized-losses', 'make', 'fuel-type', 'aspiration', 'num-of-doors', 'body-style', 'drive-wheels', 'engine-location', 'wheel-base', 'length', 'width', 'height', 'curb-weight', 'engine-type', 'num-of-cylinders', 'engine-size', 'fuel-system', 'bore', 'stroke', 'compression-ratio', 'horsepower', 'peak-rpm', 'city-mpg', 'highway-mpg', 'price',]
# We also have to specify dtypes.
dtypes = { 'symboling': np.int32, 'normalized-losses': np.float32, 'make': str, 'fuel-type': str, 'aspiration': str, 'num-of-doors': str, 'body-style': str, 'drive-wheels': str, 'engine-location': str, 'wheel-base': np.float32, 'length': np.float32, 'width': np.float32, 'height': np.float32, 'curb-weight': np.float32, 'engine-type': str, 'num-of-cylinders': str, 'engine-size': np.float32, 'fuel-system': str, 'bore': np.float32, 'stroke': np.float32, 'compression-ratio': np.float32, 'horsepower': np.float32, 'peak-rpm': np.float32, 'city-mpg': np.float32, 'highway-mpg': np.float32, 'price': np.float32, }
# Read the file.
df = pd.read_csv('imports-85.data', names=names, dtype=dtypes, na_values='?')

# Fix problems pre-existing in the dataset
# Some rows don't have price data, we can't use those.
df = df.dropna(axis='rows', how='any', subset=['price'])
# Fill missing values in continuous columns with zeros instead of NaN.
float_columns = [k for k,v in dtypes.items() if v == np.float32]
df[float_columns] = df[float_columns].fillna(value=0., axis='columns')
# Fill missing values in continuous columns with '' instead of NaN (NaN mixed with strings is very bad for us).
string_columns = [k for k,v in dtypes.items() if v == str]
df[string_columns] = df[string_columns].fillna(value='', axis='columns')

# Get X and y
# Split the data into a training set and an eval set.
training_data = df[:160]
eval_data = df[160:]
# Separate input features from labels
training_label = training_data.pop('price')
eval_label = eval_data.pop('price')

# Make input function for training: 
#   num_epochs=None -> will cycle through input data forever
#   shuffle=True -> randomize order of input data
training_input_fn = tf.estimator.inputs.pandas_input_fn(
    x=training_data, y=training_label, 
    batch_size=64, shuffle=True, num_epochs=None)

# Make input function for evaluation:
#   shuffle=False -> do not randomize input data
eval_input_fn = tf.estimator.inputs.pandas_input_fn(
    x=eval_data, y=eval_label, batch_size=64, shuffle=False)

# Describe how the model should interpret the inputs. 
# The names of the feature columns have to match the names
# of the series in the dataframe.
# 我覺得這一段可以自動化，因為前面 for dataFrame 已經講過一遍了

symboling = tf.feature_column.numeric_column('symboling')
normalized_losses = tf.feature_column.numeric_column('normalized-losses')
make = tf.feature_column.categorical_column_with_hash_bucket('make', 50)
fuel_type = tf.feature_column.categorical_column_with_vocabulary_list('fuel-type', vocabulary_list=['diesel', 'gas'])
aspiration = tf.feature_column.categorical_column_with_vocabulary_list('aspiration', vocabulary_list=['std', 'turbo'])
num_of_doors = tf.feature_column.categorical_column_with_vocabulary_list('num-of-doors', vocabulary_list=['two', 'four'])
body_style = tf.feature_column.categorical_column_with_vocabulary_list('body-style', vocabulary_list=['hardtop', 'wagon', 'sedan', 'hatchback', 'convertible'])
drive_wheels = tf.feature_column.categorical_column_with_vocabulary_list('drive-wheels', vocabulary_list=['4wd', 'rwd', 'fwd'])
engine_location = tf.feature_column.categorical_column_with_vocabulary_list('engine-location', vocabulary_list=['front', 'rear'])
wheel_base = tf.feature_column.numeric_column('wheel-base')
length = tf.feature_column.numeric_column('length')
width = tf.feature_column.numeric_column('width')
height = tf.feature_column.numeric_column('height')
curb_weight = tf.feature_column.numeric_column('curb-weight')
engine_type = tf.feature_column.categorical_column_with_vocabulary_list('engine-type', ['dohc', 'dohcv', 'l', 'ohc', 'ohcf', 'ohcv', 'rotor'])
num_of_cylinders = tf.feature_column.categorical_column_with_vocabulary_list('num-of-cylinders', ['eight', 'five', 'four', 'six', 'three', 'twelve', 'two'])
engine_size = tf.feature_column.numeric_column('engine-size')
fuel_system = tf.feature_column.categorical_column_with_vocabulary_list('fuel-system', ['1bbl', '2bbl', '4bbl', 'idi', 'mfi', 'mpfi', 'spdi', 'spfi'])
bore = tf.feature_column.numeric_column('bore')
stroke = tf.feature_column.numeric_column('stroke')
compression_ratio = tf.feature_column.numeric_column('compression-ratio')
horsepower = tf.feature_column.numeric_column('horsepower')
peak_rpm = tf.feature_column.numeric_column('peak-rpm')
city_mpg = tf.feature_column.numeric_column('city-mpg')
highway_mpg = tf.feature_column.numeric_column('highway-mpg')

linear_features = [symboling, normalized_losses, make, fuel_type, aspiration, num_of_doors,
                   body_style, drive_wheels, engine_location, wheel_base, length, width,
                   height, curb_weight, engine_type, num_of_cylinders, engine_size, fuel_system,
                   bore, stroke, compression_ratio, horsepower, peak_rpm, city_mpg, highway_mpg]

def experiment_fn(run_config, params):
  # This function makes an Experiment, containing an Estimator 
  # and inputs for training and evaluation.
  # You can use params and config here to customize the Estimator 
  # depending on the cluster or to use hyperparameter tuning.
  
  # 我要拿 estimator 來玩
  estimator=tf.contrib.learn.LinearRegressor(
        feature_columns=linear_features, config=run_config
        )
  peforth.vm.push(estimator)
  peforth.vm.dictate("constant estimator // ( -- obj ) tf.contrib.learn.LinearRegressor")
  
  # Collect information for training
  return tf.contrib.learn.Experiment(
    estimator=estimator,
    train_input_fn=training_input_fn,
    train_steps=10000,
    eval_input_fn=eval_input_fn
  )
# shutil http://www.cnblogs.com/CLTANG/archive/2011/11/15/2249257.html
import shutil
shutil.rmtree("/tmp/output_dir", ignore_errors=True)  # 刪除暫存目錄
result = tf.contrib.learn.learn_runner.run(
    experiment_fn, 
    run_config=tf.contrib.learn.RunConfig(model_dir="/tmp/output_dir")
    )
#regressor = tf.contrib.learn.LinearRegressor(feature_columns=linear_features,model_dir="/tmp/output_dir")
peforth.ok(cmd="cr .' Done, now up to you to play with the AI!' cr")

# __main__ :> eval_data py> dict(pop()) \ 轉成 dict 
# estimator :> predict(x=pop()) \ 餵進去給 estimator 得到結果在 generator 裡面
# <py> [i for i in tos()] </pyV> .s \ 把結果列出來
# 0: <generator object _as_iterable at 0x000001FC2C6D2C50> (<class 'generator'>)
# 1: [8913.3389, 8308.6182, 8540.8213, 14110.35, 14079.014, 14142.436, 15199.271, 15419.371, 17507.143, 13029.415, 13149.531, 13765.071, 13800.103, 14109.767, 17586.846, 17921.291, 20345.182, 21738.92, 9228.6484, 9701.5625, 9666.6533, 10139.566, 10633.109, 10866.222, 10878.761, 12020.095, 7642.5405, 16187.499, 14511.044, 14131.028, 16565.107, 17936.807, 16724.201, 17978.393, 19020.17, 20313.533, 16998.342, 18961.502, 18606.131, 19618.875, 17995.02] (<class 'list'>)
#
