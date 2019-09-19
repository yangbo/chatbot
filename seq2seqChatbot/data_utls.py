﻿# coding=utf-8

import math
import os
import random
import getConfig
import jieba

from db import FaqFindlaw

gConfig = {}

gConfig = getConfig.get_config()
conv_path = gConfig['resource_data']


def process_file(dialog_file):
    if not os.path.exists(conv_path):
        exit()

    convs = []  # 用于存储对话集合
    with open(conv_path, encoding='utf-8') as f:
        one_conv = []  # 存储一次完整对话
        for line in f:
            line = line.strip('\n').replace('/',
                                            '')  # 去除换行符，并在字符间添加空格符，原因是用于区分 123 与1 2 3. 【代码和注释不符，后面去掉M的时候认为没有空格，需要注意】
            if line == '':
                continue
            if line[0] == gConfig['e']:
                if one_conv:
                    convs.append(one_conv)
                one_conv = []
            elif line[0] == gConfig['m']:
                one_conv.append(line.split(' ')[1])  # 将一次完整的对话存储下来

    # 把对话分成问与答两个部分
    ask = []  # 问
    response = []  # 答
    for conv in convs:
        if len(conv) == 1:
            continue
        if len(conv) % 2 != 0:  # 因为默认是一问一答的，所以需要进行数据的粗裁剪，对话行数要是偶数的
            conv = conv[:-1]
        for i in range(len(conv)):
            if i % 2 == 0:
                conv[i] = " ".join(jieba.cut(conv[i]))  # 使用jieba分词器进行分词
                ask.append(conv[i])  # 因为i是从0开始的，因此偶数行为发问的语句，奇数行为回答的语句
            else:
                conv[i] = " ".join(jieba.cut(conv[i]))
                response.append(conv[i])
    return ask, response


def convert_seq2seq_files(questions, answers, TESTSET_SIZE):
    # 创建文件
    train_enc = open(gConfig['train_enc'], 'w', encoding='utf8')  # 问
    train_dec = open(gConfig['train_dec'], 'w', encoding='utf8')  # 答
    test_enc = open(gConfig['test_enc'], 'w', encoding='utf8')  # 问
    test_dec = open(gConfig['test_dec'], 'w', encoding='utf8')  # 答

    test_index = random.sample([i for i in range(len(questions))], TESTSET_SIZE)

    question_len = len(questions)
    for i in range(len(questions)):
        if i in test_index:
            test_enc.write(questions[i] + '\n')
            test_dec.write(answers[i] + '\n')
        else:
            train_enc.write(questions[i] + '\n')
            train_dec.write(answers[i] + '\n')
        if i % 1000 == 0:
            print(question_len, '处理进度：', i)

    train_enc.close()
    train_dec.close()
    test_enc.close()
    test_dec.close()


# 从文件读取问答数据
# ask, response = process_file(conv_path)

# 从数据库读取问答数据
def read_from_db():
    questions = []  # 问
    answers = []  # 答
    for chunk in FaqFindlaw.chunk(100):
        for faq in chunk:
            q = faq.question.replace('\n', '').replace('\r', '')
            a = faq.best_answer.replace('\n', '').replace('\r', '')
            questions.append(" ".join(jieba.cut(q)))
            answers.append(" ".join(jieba.cut(a)))
            if len(questions) % 1000 == 0:
                print("导出了%d条记录" % len(questions))
    return questions, answers


ask, response = read_from_db()

# 生成的*.enc文件保存了问题
# 生成的*.dec文件保存了回答
convert_seq2seq_files(ask, response, 10000)
