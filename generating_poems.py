


import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

#
simplified_batch_size = 1

rnn_units = 1024
embedding_dim = 256



#read_dataset
poems_df = pd.read_csv('./data/poems.csv')
#Filtering out large poems
poems_df['string'] = poems_df.apply(lambda row: f'\n{row["title"]}\n\n{row["author"]}\n\n{row["content"]}', axis=1)
poems_df['length'] = poems_df.string.map(len)


#We consider 1000 as the maximum length to filter
MAX_POEM_LENGTH=1000
poems_filtered = poems_df[poems_df.length<MAX_POEM_LENGTH]

print('There are ', len(poems_filtered), 'poems after filtering by length (considering poems with lenght less than 1000).')
poems_filtered = poems_df[poems_df.length<1000]
poems_string=poems_filtered.string
STOP_SIGN = '␣'

tokenizer = tf.keras.preprocessing.text.Tokenizer(
    char_level=True,
    filters='',
    lower=False,
    split=''
)

# Stop word is not a part of recipes, but tokenizer must know about it as well.
tokenizer.fit_on_texts([STOP_SIGN])

tokenizer.fit_on_texts(poems_string)

tokenizer.get_config()

tokenizer.get_config()
def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.models.Sequential()

    model.add(tf.keras.layers.Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        batch_input_shape=[batch_size, None]
    ))

    model.add(tf.keras.layers.LSTM(
        units=rnn_units,
        return_sequences=True,
        stateful=True,
        recurrent_initializer=tf.keras.initializers.GlorotNormal()
    ))

    model.add(tf.keras.layers.Dense(vocab_size))

    return model
VOCABULARY_SIZE=129

def generate_text(model, start_string, num_generate = 1000, temperature=1.0):
    # Evaluation step (generating text using the learned model)

    #padded_start_string = STOP_WORD_TITLE + start_string COMENTADO POR MIKE
    padded_start_string = start_string

    # Converting our start string to numbers (vectorizing).
    input_indices = np.array(tokenizer.texts_to_sequences([padded_start_string]))

    # Empty string to store our results.
    text_generated = []

    # Here batch size == 1.
    model.reset_states()
    for char_index in range(num_generate):
        predictions = model(input_indices)
        # remove the batch dimension
        predictions = tf.squeeze(predictions, 0)

        # Using a categorical distribution to predict the character returned by the model.
        predictions = predictions / float(temperature)
        predicted_id = tf.random.categorical(
            predictions,
            num_samples=1
        )[-1, 0].numpy()

        # We pass the predicted character as the next input to the model
        # along with the previous hidden state.
        input_indices = tf.expand_dims([predicted_id], 0)

        next_character = tokenizer.sequences_to_texts(input_indices.numpy())[0]

        text_generated.append(next_character)

    return (padded_start_string + ''.join(text_generated))


def generate_combinations(model, temperature, word):
    poem_length = 1000
    generated_text = generate_text(
        model,
        start_string=word,
        num_generate = poem_length,
        temperature=temperature
    )
    return generated_text.replace(STOP_SIGN, "")



st.sidebar.title('Poetry generator')


st.sidebar.markdown('Generating our poems in spanish')


option = st.sidebar.selectbox(
    'Task type',
    ('Generating poem','Other'),
    index=1
)


if option == 'Generating poem':
    model_simplified = build_model(VOCABULARY_SIZE, embedding_dim, rnn_units, simplified_batch_size)
    model_simplified.load_weights('./model/weights.h5')
    print("Loaded Model from disk")
    #model_simplified = load_model('./model/trained_model.h5', compile=False)
    model_simplified.build(tf.TensorShape([simplified_batch_size, None]))
    st.title('Start generating')

    word = st.text_input('Type the word you want to start the poem with', value = 'Corazón')
    temperature = st.text_input('Type the temperature', value = '0.8')
    generated_text  = generate_combinations(model_simplified, temperature, word)

    title = 'Resultant poem'
    st.text(str(generated_text))


    try:
        print('everything working')

    except Exception as e:
        print('Error  ')
