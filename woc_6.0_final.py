# -*- coding: utf-8 -*-

import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense

#reading the dataset from the file
with open('/datafile/dataset.txt', 'r') as f:
    content = f.read()
    names = content.split('\n')
    names = [name.strip() for name in names if name.strip()]

#converting characters to numerical values
chars = sorted(list(set(''.join(names))))
char_to_index = {char: i for i, char in enumerate(chars)}
index_to_char = {i: char for i, char in enumerate(chars)}

#preparing input and target data
max_len = max([len(name) for name in names])
X = np.zeros((len(names), max_len, len(chars)), dtype=bool)
y = np.zeros((len(names), len(chars)), dtype=bool)

for i, name in enumerate(names):
    for t, char in enumerate(name):
        X[i, t, char_to_index[char]] = 1
    y[i, char_to_index[name[-1]]] = 1

#building the model
model = Sequential()
model.add(LSTM(128, input_shape=(max_len, len(chars))))
model.add(Dense(len(chars), activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam')

#training the model
model.fit(X, y, epochs=1, batch_size=128)

#generating names
generated_names = []

def generate_name(seed, max_len, temperature=1.0):
    generated_name = seed
    for _ in range(max_len):  # Adjust the length as needed
        x = np.zeros((1, len(generated_name), len(chars)))
        for t, char in enumerate(generated_name):
            x[0, t, char_to_index[char]] = 1
        preds = model.predict(x, verbose=0)[0]
        next_index = sample(preds, temperature)
        next_char = index_to_char[next_index]
        generated_name += next_char
        if next_char == '\n':
            break
    return generated_name


def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


max_len = 7
for _ in range(200):
    new_name = generate_name(seed='A', max_len=max_len, temperature=0.5)
    if new_name not in generated_names:
        generated_names.append(new_name)

#analyzing uniqueness of generated names
unique_names = set(generated_names)
percent_unique = len(unique_names) / len(generated_names) * 100

print(f"Percentage of unique names: {percent_unique}%")

from google.colab import drive
drive.mount('/content/drive')

