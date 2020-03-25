#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 19:46:49 2020

@author: prince

Building Chatbot
"""

# importing the libraries
import numpy as np;
import tensorflow as tf;
import re;
import time;

""" PART 1 - DATA PREPROCESSING"""
# importing the dataset
lines = open('cornell-movie-dialogs-corpus/movie_lines.txt',
             encoding = 'utf-8', errors='ignore').read().split('\n')
conversations = open('cornell-movie-dialogs-corpus/movie_conversations.txt',
             encoding = 'utf-8', errors='ignore').read().split('\n')

# creating a dictionary that maps each line and its id
id2line = {}
for line in lines:
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        id2line[_line[0]] = _line[4]
        
# creating list of all conversations
conversations_ids = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'",
                                                    '').replace(" ", "")
    conversations_ids.append(_conversation.split(','))
    
# Getting separately questions and answers
questions = []
answers = []
for conversation in conversations_ids:
    for i in range(len(conversation) - 1):
        questions.append(id2line[conversation[i]])
        answers.append(id2line[conversation[i+1]])

# Doing a first cleaning of the texts
def clean_text(text):
    text = text.lower()
    text = re.sub(r"i'm", "i am", text)
    text = re.sub(r"he's", "he is", text)
    text = re.sub(r"she's", "she is", text)
    text = re.sub(r"that's", "that is", text)
    text = re.sub(r"what's", "what is", text)
    text = re.sub(r"where's", "where is", text)
    text = re.sub(r"\'ll", " will", text)
    text = re.sub(r"\'ve", " have", text)
    text = re.sub(r"\'re", " are", text)
    text = re.sub(r"\'d", " would", text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "can not", text)
    text = re.sub(r"[-()\"%/@;:<>{}+=~|.?,]", "", text)
    return text

# clean questions
clean_questions = []
for question in questions:
    clean_questions.append(clean_text(question))

#clean answers
clean_answers = []
for answer in answers:
    clean_answers.append(clean_text(answer))
    
# Creating a dictionary that maps each word to its number of occurences
word2count = {}

for answer in clean_answers:
    for word in answer.split():
        if word not in word2count:
            word2count[word] = {}
            word2count[word]['count'] = 1
            word2count[word]['group'] = 'a'
        else:
            word2count[word]['count'] += 1

for question in clean_questions:
    for word in question.split():
        if word not in word2count:
            word2count[word] = {}
            word2count[word]['count'] = 1
            word2count[word]['group'] = 'q'
        else:
            word2count[word]['count'] += 1


# Creating two dictionaries that maps the questions words and the answers words to a unique integer
threshold = 20
words2int = {}
word_number = 0
for word, value in word2count.items():
    if value['count'] > 20: # and value['group'] == 'q':
        words2int[word] = word_number
        word_number += 1

"""
answerswords2int = {}
word_number = 0
for word, value in word2count.items():
    if value['count'] > 20 and value['group'] == 'a':
        answerswords2int[word] = word_number
        word_number += 1
"""

# Adding the last tokens to this dictionary
tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']
for token in tokens:
    words2int[token] = len(words2int) + 1

# Creating the inverse dictionary of the words2int
words_int2words = {w_i: w for w, w_i in words2int.items()}

# Adding the End of String token to the end of every answer
for i in range(len(clean_answers)):
    clean_answers[i] += ' <EOS>'
    
# Translating all the questions and answers into integers
# and replacing all the words that were filtered out by <OUT>

questions_to_int = []
for question in clean_questions:
    ques_ints = []
    for word in question.split():
        if word not in words2int:
            ques_ints.append(words2int['<OUT>'])
        else:
            ques_ints.append(words2int[word])
    questions_to_int.append(ques_ints)
    
answers_to_int = []
for answer in clean_answers:
    ans_ints = []
    for word in answer.split():
        if word not in words2int:
            ans_ints.append(words2int['<OUT>'])
        else:
            ans_ints.append(words2int[word])
    answers_to_int.append(ques_ints)
    
# Sorting questions and answers by the length of questions
sorted_clean_questions = []
sorted_clean_answers = []
for length in range(1, 25):
    for question_enum in enumerate(questions_to_int):
        if len(question_enum[1]) == length:
            sorted_clean_questions.append(question_enum[1])
            sorted_clean_answers.append(answers_to_int[question_enum[0]])
