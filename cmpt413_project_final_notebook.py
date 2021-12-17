# -*- coding: utf-8 -*-
"""cmpt413-project-final-notebook.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/143ymoI1134RvLXxKfFgEnB8tefyc1K1h

# Multinomial Logistic Regression
"""

from google.colab import drive
drive.mount('/content/drive')

"""Import the neccessary libraries:

1.   numpy and pandas for processing and transforming data
2.   From sklearn LogisticRegression for the model, TfidfVectorizer for turning input text to vector, cross_val_score for evaluating the model, and train_test_split for splitting the input data to train and test
3.   hstack from scipy to stack multiple vectors on top of each other


"""

import numpy as np
import pandas as pd
import pickle
import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split

"""Read the data, and then split it to train and test using train_test_split. The test split is 70-30 and random state is set to 999 to match the other two algorithms."""

class_names = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

data = pd.read_csv('comments-rated.csv').fillna(' ')
train_data, test_data = train_test_split(data, test_size=0.3, random_state=999)

train = train_data['comment_text']
test = test_data['comment_text']
all = pd.concat([train, test])

"""word_TfidfVectorizer turns each word in the input to a vector using the TF-IDF method. Description of each paramater:


*   strip_accents: remove accents and perform other character normalization during the preprocessing step based on 'unicode'
*   analyzer: set to word so it will apply TF-IDF on words and not characters
*   token_pattern: regular expression denoting what constitutes a “token” 
*   stop_words: remove stop words in the pre-processing stages. 'english' is the only supported value, and it will remove words that do not give any useful information to the model
*   ngram_range: covers how many words in each sentence to apply the TF-IDF method to vectorize. It set is (1, 1) meaning the vectorizer will go over the unigramsword_TfidfVectorizer
*   max_features: an upper limit on the number of features

"""

word_TfidfVectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='word',
    token_pattern=r'\w{1,}',
    stop_words='english',
    ngram_range=(1, 1),
    max_features=10000)
word_TfidfVectorizer.fit(all)
train_word_features = word_TfidfVectorizer.transform(train)
test_word_features = word_TfidfVectorizer.transform(test)

"""char_TfidfVectorizer applies the TF-IDF method to the character of each word in order to include more information regarding the input. Description of each paramter: 


*   strip_accents: remove accents and perform other character normalization during the preprocessing step based on 'unicode'

*   analyzer: set to char so it will apply TF-IDF on characters of each word and not the words themselves
*   ngram_range: covers how many characters in each word to apply the TF-IDF method to vectorize. It set is (2, 6) meaning the vectorizer will go over every two, three,... up to six characters in each word and embed their information in the input vector
*   max_features: an upper limit on the number of features
"""

char_TfidfVectorizer = TfidfVectorizer(
    sublinear_tf=True,
    strip_accents='unicode',
    analyzer='char',
    ngram_range=(2, 6),
    max_features=50000)
char_TfidfVectorizer.fit(all)
train_char_features = char_TfidfVectorizer.transform(train)
test_char_features = char_TfidfVectorizer.transform(test)

"""The train features to input to LR will include word embeddings calculated using TF-IDF and n-gram character representations (and so will the test features)"""

train_features = hstack([train_char_features, train_word_features])
test_features = hstack([test_char_features, test_word_features])

"""Create a logistic regression model for each class, train the model using the train data. Then, using cross_val_score validate the model on the test data over the evaluation metrics (Precision, Recall, F1, ROC_AUC)"""

for class_name in class_names:
    train_target = train_data[class_name]
    test_target = test_data[class_name]
    start = time.time()
    classifier = LogisticRegression(C=0.1, solver='sag')
    classifier.fit(train_features, train_target)
    end = time.time()
    print("{} took {} seconds".format(class_name, end - start))
    p_score = np.mean(cross_val_score(classifier, test_features, test_target, cv=3, scoring='precision'))
    r_score = np.mean(cross_val_score(classifier, test_features, test_target, cv=3, scoring='recall'))
    f1_score = np.mean(cross_val_score(classifier, test_features, test_target, cv=3, scoring='f1'))
    roc_auc_score = np.mean(cross_val_score(classifier, test_features, test_target, cv=3, scoring='roc_auc'))
    print("{} p_score {} r_score {} f1_score {} roc_auc_score {}".format(class_name, p_score, r_score, f1_score, roc_auc_score))

"""# 1-D Convolutional Neural Network"""

from google.colab import drive
drive.mount('/content/drive')

"""Import the necessary libraries. Pandas is used for processing and transforming data; TensorFlow and Keras provide the main ML functionality and model APIs."""

import pandas as pd
import keras
import tensorflow as tf

"""Read in data and prepare for processing by isolating X (comment text) and Y (binary classification by label)."""

df_comments = pd.read_csv('comments-rated.csv')
cols_to_drop = [0, 2, 3, 4, 5, 6, 7]
df_comments.drop(df_comments.columns[cols_to_drop],axis=1,inplace=True)
df_comments = df_comments

df_labels = pd.read_csv('comments-rated.csv')
cols_to_drop = [0,1]
df_labels.drop(df_labels.columns[cols_to_drop],axis=1,inplace=True)

"""Tokenize input text and transform into feature vectors to be machine readable format using Keras' text preprocessing API"""

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import MultiLabelBinarizer

maxlen = 250
max_words = 5000
tokenizer = Tokenizer(num_words=max_words, lower=True)
tokenizer.fit_on_texts(df_comments.comment_text)

def get_features(text_series):
    sequences = tokenizer.texts_to_sequences(text_series)
    return pad_sequences(sequences, maxlen=maxlen)

x = get_features(df_comments.comment_text)
y = tf.convert_to_tensor(df_labels)

"""Generate 70/30 train/test split of data using standardized random_state=999."""

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, df_labels, test_size=0.3, random_state=999)

"""Build and compile a 1-Dimensional CNN with 6 dense layers (one for each class). Filter length, embedding dimension, and dropout hyperparameters are specified (implemented levels shown resulting from experimentation and tuning on dataset). Evaluation metrics are also specified during model compilation.

A sequential model is used to stack layers in order. The input is represented in the form of a word embedding. The dropout layer helps prevent overfitting (regularization) by randomly setting input units to 0. The Conv1D layer is the temporal convolutional layer with the provided activation function. Max-over-time pooling reduces the data by downsampling the input by taking the maximum value over every window. And, Dense and Activation layers represent the final connected neural network layers.
"""

from keras.models import Sequential
from keras.layers import Dense, Activation, Embedding, Flatten, GlobalMaxPool1D, Dropout, Conv1D
from keras.callbacks import ReduceLROnPlateau, EarlyStopping, ModelCheckpoint
from keras.losses import binary_crossentropy
from tensorflow.keras.optimizers import Adam

filter_length = 300
embedding_dim = 20
dropout = 0.1

model = Sequential()
model.add(Embedding(max_words, embedding_dim))
model.add(Dropout(dropout))
model.add(Conv1D(filter_length, 3, padding='same', activation='relu', strides=1))
model.add(GlobalMaxPool1D())
model.add(Dense(6))
model.add(Activation('sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[
        tf.keras.metrics.AUC(curve="ROC", name="ROC_AUC"), 
        tf.keras.metrics.Precision(name="P"), 
        tf.keras.metrics.Recall(name="R")
    ])

"""Fit model on training data, evaluate on testing data, and output results to file. This code loads the model written from this iteration of training which is saved in the same directory as the code itself. An example, already trained, model is located in source.zip/CNN/output/model-conv1d.h5 for easy loading and evaluation."""

with open('output' + str(max_words) + '_' + str(dropout) + '_' + str(embedding_dim) + '.txt', 'w') as f:
    model.summary(print_fn=lambda x: f.write(x + '\n'))

    callbacks = [
        ReduceLROnPlateau(), 
        EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=50),
        ModelCheckpoint(filepath='model-conv1d.h5', save_best_only=True)
    ]

    history = model.fit(x_train, y_train,
                        epochs=20,
                        batch_size=32,
                        validation_split=0.1,
                        callbacks=callbacks)

    cnn_model = keras.models.load_model('model-conv1d.h5')
    metrics = cnn_model.evaluate(x_test, y_test, return_dict=True)
    f.writelines(str(metrics))
    fscore = 2 * (metrics['P'] * metrics['R']) / (metrics['P'] + metrics['R'])
    f.writelines('\n')
    f.writelines('F-Score: ' + str(fscore))

"""#LSTM RNN

## Importing Libraries
"""

import numpy as np, pandas as pd
import re
import spacy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
import string
from string import ascii_lowercase
from tqdm import tqdm_notebook
import itertools
import io
import matplotlib.pyplot as plt
from functools import reduce
from tensorflow import keras
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Dense, Input, LSTM, Embedding, Dropout, Activation
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.models import Model
from keras.models import Sequential
from keras.layers import Conv1D, MaxPooling1D
from keras.layers import BatchNormalization
from keras import initializers, regularizers, constraints, optimizers, layers
!pip install talos
import talos

"""## Importing Data"""

train=pd.read_csv('comments-rated.csv')

"""## Data Exploration"""

labels = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
y = train[labels].values

"""###Data Pre-processing

#### Text Normalization

* Removing Characters in between Text
* Removing Repeated Characters
* Converting data to lower-case
* Removing Numbers from the data
* Remove Punctuation
* Remove Whitespaces
* Removing spaces in between words
* Removing "\n"
* Remove Non-english characters
"""

RE_PATTERNS = {
    ' american ':
        [
            'amerikan'
        ],

    ' adolf ':
        [
            'adolf'
        ],


    ' hitler ':
        [
            'hitler'
        ],

    ' fuck':
        [
            '(f)(u|[^a-z0-9 ])(c|[^a-z0-9 ])(k|[^a-z0-9 ])([^ ])*',
            '(f)([^a-z]*)(u)([^a-z]*)(c)([^a-z]*)(k)',
            ' f[!@#\$%\^\&\*]*u[!@#\$%\^&\*]*k', 'f u u c',
            '(f)(c|[^a-z ])(u|[^a-z ])(k)', r'f\*',
            'feck ', ' fux ', 'f\*\*', 'f**k','fu*k',
            'f\-ing', 'f\.u\.', 'f###', ' fu ', 'f@ck', 'f u c k', 'f uck', 'f ck'
        ],

    ' ass ':
        [
            '[^a-z]ass ', '[^a-z]azz ', 'arrse', ' arse ', '@\$\$',
            '[^a-z]anus', ' a\*s\*s', '[^a-z]ass[^a-z ]',
            'a[@#\$%\^&\*][@#\$%\^&\*]', '[^a-z]anal ', 'a s s','a55', '@$$'
        ],

    ' ass hole ':
        [
            ' a[s|z]*wipe', 'a[s|z]*[w]*h[o|0]+[l]*e', '@\$\$hole', 'a**hole'
        ],

    ' bitch ':
        [
            'b[w]*i[t]*ch', 'b!tch',
            'bi\+ch', 'b!\+ch', '(b)([^a-z]*)(i)([^a-z]*)(t)([^a-z]*)(c)([^a-z]*)(h)',
            'biatch', 'bi\*\*h', 'bytch', 'b i t c h', 'b!tch', 'bi+ch', 'l3itch'
        ],

    ' bastard ':
        [
            'ba[s|z]+t[e|a]+rd'
        ],

    ' trans gender':
        [
            'transgender'
        ],

    ' gay ':
        [
            'gay'
        ],

    ' cock ':
        [
            '[^a-z]cock', 'c0ck', '[^a-z]cok ', 'c0k', '[^a-z]cok[^aeiou]', ' cawk',
            '(c)([^a-z ])(o)([^a-z ]*)(c)([^a-z ]*)(k)', 'c o c k'
        ],

    ' dick ':
        [
            ' dick[^aeiou]', 'deek', 'd i c k', 'dik'
        ],

    ' suck ':
        [
            'sucker', '(s)([^a-z ]*)(u)([^a-z ]*)(c)([^a-z ]*)(k)', 'sucks', '5uck', 's u c k'
        ],

    ' cunt ':
        [
            'cunt', 'c u n t'
        ],

    ' bull shit ':
        [
            'bullsh\*t', 'bull\$hit'
        ],

    ' homo sex ual':
        [
            'homosexual'
        ],

    ' jerk ':
        [
            'jerk'
        ],

    ' idiot ':
        [
            'i[d]+io[t]+', '(i)([^a-z ]*)(d)([^a-z ]*)(i)([^a-z ]*)(o)([^a-z ]*)(t)', 'idiots'
                                                                                      'i d i o t'
        ],

    ' dumb ':
        [
            '(d)([^a-z ]*)(u)([^a-z ]*)(m)([^a-z ]*)(b)'
        ],

    ' shit ':
        [
            'shitty', '(s)([^a-z ]*)(h)([^a-z ]*)(i)([^a-z ]*)(t)', 'shite', '\$hit', 's h i t', '$h1t'
        ],

    ' shit hole ':
        [
            'shythole'
        ],

    ' retard ':
        [
            'returd', 'retad', 'retard', 'wiktard', 'wikitud'
        ],

    ' rape ':
        [
            ' raped'
        ],

    ' dumb ass':
        [
            'dumbass', 'dubass'
        ],

    ' ass head':
        [
            'butthead'
        ],

    ' sex ':
        [
            'sexy', 's3x', 'sexuality'
        ],


    ' nigger ':
        [
            'nigger', 'ni[g]+a', ' nigr ', 'negrito', 'niguh', 'n3gr', 'n i g g e r'
        ],

    ' shut the fuck up':
        [
            'stfu', 'st*u'
        ],

    ' pussy ':
        [
            'pussy[^c]', 'pusy', 'pussi[^l]', 'pusses', 'p*ssy'
        ],

    ' faggot ':
        [
            'faggot', ' fa[g]+[s]*[^a-z ]', 'fagot', 'f a g g o t', 'faggit',
            '(f)([^a-z ]*)(a)([^a-z ]*)([g]+)([^a-z ]*)(o)([^a-z ]*)(t)', 'fau[g]+ot', 'fae[g]+ot',
        ],

    ' mother fucker':
        [
            ' motha ', ' motha f', ' mother f', 'motherucker',
        ],

    ' whore ':
        [
            'wh\*\*\*', 'w h o r e'
        ],
    ' fucking ':
        [
            'f*$%-ing'
        ],
}

def clean_text(text,remove_repeat_text=True, remove_patterns_text=True, is_lower=True):

  if is_lower:
    text=text.lower()
    
  if remove_patterns_text:
    for target, patterns in RE_PATTERNS.items():
      for pat in patterns:
        text=str(text).replace(pat, target)

  if remove_repeat_text:
    text = re.sub(r'(.)\1{2,}', r'\1', text) 

  text = str(text).replace("\n", " ")
  text = re.sub(r'[^\w\s]',' ',text)
  text = re.sub('[0-9]',"",text)
  text = re.sub(" +", " ", text)
  text = re.sub("([^\x00-\x7F])+"," ",text)
  return text

"""Cleaning Training Data"""

train['comment_text']=train['comment_text'].apply(lambda x: clean_text(x))

"""#### Lemmatization"""

comments_train=train['comment_text']

comments_train=list(comments_train)

wordnet_lemmatizer = WordNetLemmatizer()

def lemma(text, lemmatization=True):
  output=""
  if lemmatization:
    text=text.split(" ")
    for word in text:
       word1 = wordnet_lemmatizer.lemmatize(word, pos = "n")
       word2 = wordnet_lemmatizer.lemmatize(word1, pos = "v")
       word3 = wordnet_lemmatizer.lemmatize(word2, pos = "a")
       word4 = wordnet_lemmatizer.lemmatize(word3, pos = "r")
       output=output + " " + word4
  else:
    output=text
  
  return str(output.strip())

"""Lemmatizing Training Data"""

lemmatized_train_data = [] 

for line in tqdm_notebook(comments_train, total=159571): 
    lemmatized_train_data.append(lemma(line))

"""#### Stopwords Removal"""

stopword_list=STOP_WORDS

"""Adding Single and Dual to STOP_WORDS"""

def iter_all_strings():
    for size in itertools.count(1):
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)

dual_alpha_list=[]
for s in iter_all_strings():
    dual_alpha_list.append(s)
    if s == 'zz':
        break

dual_alpha_list.remove('i')
dual_alpha_list.remove('a')
dual_alpha_list.remove('am')
dual_alpha_list.remove('an')
dual_alpha_list.remove('as')
dual_alpha_list.remove('at')
dual_alpha_list.remove('be')
dual_alpha_list.remove('by')
dual_alpha_list.remove('do')
dual_alpha_list.remove('go')
dual_alpha_list.remove('he')
dual_alpha_list.remove('hi')
dual_alpha_list.remove('if')
dual_alpha_list.remove('is')
dual_alpha_list.remove('in')
dual_alpha_list.remove('me')
dual_alpha_list.remove('my')
dual_alpha_list.remove('no')
dual_alpha_list.remove('of')
dual_alpha_list.remove('on')
dual_alpha_list.remove('or')
dual_alpha_list.remove('ok')
dual_alpha_list.remove('so')
dual_alpha_list.remove('to')
dual_alpha_list.remove('up')
dual_alpha_list.remove('us')
dual_alpha_list.remove('we')

for letter in dual_alpha_list:
    stopword_list.add(letter)
print("Done!!")

"""Checking for other words that we may need in STOP_WORDS"""

def search_stopwords(data, search_stop=True):
  output=""
  if search_stop:
    data=data.split(" ")
    for word in data:
      if not word in stopword_list:
        output=output+" "+word 
  else:
    output=data

  return str(output.strip())

potential_stopwords = [] 

for line in tqdm_notebook(lemmatized_train_data, total=159571): 
    potential_stopwords.append(search_stopwords(line))

"""Combining all the sentences in the list into a single string"""

def string_combine_a(stopword):
  final_a=""
  for item in range(39893):
    final_a=final_a+" "+stopword[item]
  return final_a

def string_combine_b(stopword):
  final_b=""
  for item in range(39893,79785):
    final_b=final_b+" "+stopword[item]
  return final_b

def string_combine_c(stopword):
  final_c=""
  for item in range(79785,119678):
    final_c=final_c+" "+stopword[item]
  return final_c

def string_combine_d(stopword):
  final_d=""
  for item in range(119678,159571):
    final_d=final_d+" "+stopword[item]
  return final_d

total_string_potential_a=string_combine_a(potential_stopwords)
total_string_potential_b=string_combine_b(potential_stopwords)
total_string_potential_c=string_combine_c(potential_stopwords)
total_string_potential_d=string_combine_d(potential_stopwords)

"""Counting the number of words in each of the 4 strings"""

def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts

total_string_potential_a_dict=word_count(total_string_potential_a)
total_string_potential_b_dict=word_count(total_string_potential_b)
total_string_potential_c_dict=word_count(total_string_potential_c)
total_string_potential_d_dict=word_count(total_string_potential_d)

"""Converting Dictionaries to Dataframe"""

total_string_potential_a_df = pd.DataFrame(list(total_string_potential_a_dict.items()),columns = ['Word','Count'])
total_string_potential_b_df = pd.DataFrame(list(total_string_potential_b_dict.items()),columns = ['Word','Count'])
total_string_potential_c_df = pd.DataFrame(list(total_string_potential_c_dict.items()),columns = ['Word','Count'])
total_string_potential_d_df = pd.DataFrame(list(total_string_potential_d_dict.items()),columns = ['Word','Count'])

"""Getting Dataframe output in descending order"""

top50_potential_stopwords_a=total_string_potential_a_df.sort_values(by=['Count'],ascending=False).head(50)
top50_potential_stopwords_b=total_string_potential_b_df.sort_values(by=['Count'],ascending=False).head(50)
top50_potential_stopwords_c=total_string_potential_c_df.sort_values(by=['Count'],ascending=False).head(50)
top50_potential_stopwords_d=total_string_potential_d_df.sort_values(by=['Count'],ascending=False).head(50)

"""Looking for common terms in all top 50 dataframes"""

common_potential_stopwords=list(reduce(set.intersection,map(set,[top50_potential_stopwords_a.Word,top50_potential_stopwords_b.Word,top50_potential_stopwords_c.Word,top50_potential_stopwords_d.Word])))

"""Retaining certain words and removing others from the above list"""

potential_stopwords=['editor', 'reference', 'thank', 'work','find', 'good', 'know', 'like', 'look', 'thing', 'want', 'time', 'list', 'section','wikipedia', 'doe', 'add','new', 'try', 'think', 'write','use', 'user', 'way', 'page']

"""Adding above retrived words into the stopwords list"""

for word in potential_stopwords:
    stopword_list.add(word)

"""Removing Stopwords from Training Data"""

def remove_stopwords(text, remove_stop=True):
  output = ""
  if remove_stop:
    text=text.split(" ")
    for word in text:
      if word not in stopword_list:
        output=output + " " + word
  else :
    output=text

  return str(output.strip())

processed_train_data = [] 

for line in tqdm_notebook(lemmatized_train_data, total=159571): 
    processed_train_data.append(remove_stopwords(line))

processed_train_data[152458]

"""Removing Stopwords from Test Data

## Model Building
"""

max_features=100000      
maxpadlen = 200          
val_split = 0.3      
embedding_dim_fasttext = 300

"""Tokenization"""

tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(list(processed_train_data))
list_tokenized_train = tokenizer.texts_to_sequences(processed_train_data)
word_index=tokenizer.word_index

"""Padding"""

X_t=pad_sequences(list_tokenized_train, maxlen=maxpadlen, padding = 'post')

indices = np.arange(X_t.shape[0])
np.random.shuffle(indices)

X_t = X_t[indices]
labels = y[indices]

"""### Splitting data into Training and Validation Set"""

num_validation_samples = int(val_split*X_t.shape[0])
x_train = X_t[: -num_validation_samples]
y_train = labels[: -num_validation_samples]
x_val = X_t[-num_validation_samples: ]
y_val = labels[-num_validation_samples: ]

"""### Importing Fast Text"""

##PLEASE IMPORT THIS FROM https://fasttext.cc/docs/en/english-vectors.html in your working directory or from SFU Vault: https://vault.sfu.ca/index.php/s/AEvM2fabFwXTSZZ
embeddings_index_fasttext = {}
f = open('wiki-news-300d-1M.vec', encoding='utf8')
for line in f:
    values = line.split()
    word = values[0]
    embeddings_index_fasttext[word] = np.asarray(values[1:], dtype='float32')
f.close()

embedding_matrix_fasttext = np.random.random((len(word_index) + 1, embedding_dim_fasttext))
for word, i in word_index.items():
    embedding_vector = embeddings_index_fasttext.get(word)
    if embedding_vector is not None:
        embedding_matrix_fasttext[i] = embedding_vector

"""### Creating Model

#### Talos Grid Search  for LSTM Model
"""

def toxic_classifier(x_train,y_train,x_val,y_val,params):

  inp=Input(shape=(maxpadlen, ),dtype='int32')

  embedding_layer = Embedding(len(word_index) + 1,
                           embedding_dim_fasttext,
                           weights = [embedding_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
  embedded_sequences = embedding_layer(inp)

  x = LSTM(params['output_count_lstm'], return_sequences=True,name='lstm_layer')(embedded_sequences)
  x = GlobalMaxPool1D()(x)
  x = Dropout(params['dropout'])(x)
  x = Dense(params['output_count_dense'], activation=params['activation'], kernel_initializer='he_uniform')(x)
  x = Dropout(params['dropout'])(x)
  preds = Dense(6, activation=params['last_activation'], kernel_initializer='glorot_uniform')(x)
  model = Model(inputs=inp, outputs=preds)
  model.compile(loss=params['loss'], optimizer=params['optimizer'], metrics=['accuracy'])
  model_info=model.fit(x_train,y_train, epochs=params['epochs'], batch_size=params['batch_size'],  validation_data=(x_val, y_val))

  return model_info, model

p={
    'output_count_lstm': [40,50,60],
    'output_count_dense': [30,40,50],
    'batch_size': [32],
    'epochs':[2],
    'optimizer':['adam'],
    'activation':['relu'],
    'last_activation': ['sigmoid'],
    'dropout':[0.1,0.2],
    'loss': ['binary_crossentropy']   
}

scan_results = talos.Scan(x=x_train,
               y=y_train,
               x_val=x_val,
               y_val=y_val,
               model=toxic_classifier,
               params=p,
               experiment_name='tcc',
               print_params=True)

model_id = scan_results.data['val_accuracy'].astype('float').argmax()
model_id

analyze_object = talos.Analyze(scan_results)

analyze_object.best_params('val_accuracy', ['accuracy', 'loss', 'val_loss'])

"""#### Training Model with Best Parameters

LSTM
"""

inp=Input(shape=(maxpadlen, ),dtype='int32')

embedding_layer = Embedding(len(word_index) + 1,
                           embedding_dim_fasttext,
                           weights = [embedding_matrix_fasttext],
                           input_length = maxpadlen,
                           trainable=False,
                           name = 'embeddings')
embedded_sequences = embedding_layer(inp)

#Select Model with Best Parameters from above Talos.scan 
x = LSTM(50, return_sequences=True,name='lstm_layer')(embedded_sequences)
x = GlobalMaxPool1D()(x)
x = Dropout(0.1)(x)
x = Dense(60, activation="relu", kernel_initializer='he_uniform')(x)
x = Dropout(0.1)(x)
preds = Dense(6, activation="sigmoid", kernel_initializer='glorot_uniform')(x)

model_1 = Model(inputs=inp, outputs=preds)
model_1.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=[tf.keras.metrics.Precision(),tf.keras.metrics.AUC(),tf.keras.metrics.Recall()])

model_1.summary()

model_info_1=model_1.fit(x_train,y_train, epochs=2, batch_size=32,  validation_data=(x_val, y_val))

"""## Saving the Model"""

#Model file accesible from https://vault.sfu.ca/index.php/apps/files/?dir=/&fileid=110815034
model_1.save(filepath="Model_LSTM_RNN")

"""## Loading Saved Model and Print Metrics"""

loaded_model_1 = keras.models.load_model(filepath="Model_LSTM_RNN")
metrics =loaded_model_1.evaluate(x_val, y_val, return_dict=True)
print(str(metrics))
fscore = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
print('F-Score: ' + str(fscore))