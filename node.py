# -*- coding: utf-8 -*-
from keras.models import load_model
import numpy as np
import argparse
import tensorflow as tf
import socket  
import time  
import threading  

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--ip", required=True,
    help="ip of server")
ap.add_argument("-m", "--model", required=True,
    help="name of trained model")
ap.add_argument("-c", "--child", required=True,
    help="list of child")
args = vars(ap.parse_args())

child = args["child"].split(',')
model_Name = args["model"]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.connect((args['ip'], 12345))  
sock.send(b'1')  
leaf = False
if child[0] == 'null':
    leaf = True
sock.send(model_Name.encode())  

idx = [] 
idx_len = 0

def recvThreadFunc():
    global idx
    global idx_len
    while True:  
        otherword = sock.recv(1024).decode() 
        if otherword:  
            splitword = otherword.split(';')
            for s in splitword:
                if s != '':
                    idx.append(int(s))
                    idx_len += 1
        else:
            continue     


def classifyThreadFunc():
    global idx
    global idx_len
    global model
    global tstX
    global graph
    global leaf
    idx_now = 0
    with graph.as_default():
        while True:  
            if idx_now < idx_len:
                i = idx[idx_now]
                X =  np.reshape(tstX[i],(1, 32, 32, 3))
                prob_out = model.predict(X)[0]
                if leaf == False:
                    label_out = child[np.argmax(prob_out)]
                    myword = '{}:{};'.format(label_out, i)
                    sock.send(myword.encode()) 
                    idx_now += 1
                    print '{} - {}'.format(str(datetime.now()), myword)
                else:
                    label_out = np.argmax(prob_out)
                    myword = '{}:{};'.format(label_out, i)
                    idx_now += 1
                    print '{} - {}'.format(str(datetime.now()), myword)


path_to_model = "./keras_model/" + model_Name + ".model"
path_to_data = "./cifar-100-python/"
path_to_meta = path_to_data + "meta"
path_to_test = path_to_data + "test"

cate_reptiles = ['crocodile', 'dinosaur', 'lizard', 'snake', 'turtle']
cate_fish = ['aquarium_fish', 'flatfish', 'ray', 'shark', 'trout']
cate_aquatic = ['beaver', 'dolphin', 'otter', 'seal', 'whale']
cate_medium = ['fox', 'porcupine', 'possum', 'raccoon', 'skunk']
cate_small = ['hamster', 'mouse', 'rabbit', 'shrew', 'squirrel']
cate_insects = ['bee', 'beetle', 'butterfly', 'caterpillar', 'cockroach']
cate_otherinv = ['crab', 'lobster', 'snail', 'spider', 'worm']
# cate_male = ['boy', 'man']
# cate_female = ['girl', 'woman']
cate_flowers = ['orchid', 'poppy', 'rose', 'sunflower', 'tulip']
cate_trees = ['maple_tree', 'oak_tree', 'palm_tree', 'pine_tree', 'willow_tree']
cate_fruitveg = ['apple', 'mushroom', 'orange', 'pear', 'sweet_pepper']
cate_all = []
cate_all.extend(cate_reptiles)
cate_all.extend(cate_fish)
cate_all.extend(cate_aquatic)
cate_all.extend(cate_medium)
cate_all.extend(cate_small)
cate_all.extend(cate_insects)
cate_all.extend(cate_otherinv)
# cate_all.extend(cate_male)
# cate_all.extend(cate_female)
cate_all.extend(cate_flowers)
cate_all.extend(cate_trees)
cate_all.extend(cate_fruitveg)



def prepare_test_data(limit):
    tstX = []
    tstY = []
    for i in range(0, 10000):
        cate = get_cate_tst(i)
        if cate in cate_all:
            tstX.append(tst['data'][i])
            tstY.append(cate)
            limit -= 1
            if limit <= 0:
                return tstX, tstY


def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        dict = pickle.load(fo)
    return dict


def get_cate_tst(index):
    return meta['fine_label_names'][tst['fine_labels'][index]]

meta = unpickle(path_to_meta)   # Keys: fine_label_names, coarse_label_names
tst = unpickle(path_to_test)    # Keys: data, batch_label, fine_labels, coarse_labels, filenames
n_test = 100
model = load_model(path_to_model)
graph = tf.get_default_graph()
tstX, tstY = prepare_test_data(n_test)

th1 = threading.Thread(target=classifyThreadFunc) 
th2 = threading.Thread(target=recvThreadFunc) 
threads = [th1, th2]  
for t in threads :  
    t.setDaemon(True)  
    t.start()  
t.join()