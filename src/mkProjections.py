#! /bin/python

from __future__ import print_function

########################################
print('processing cmd line args')
import argparse

parser=argparse.ArgumentParser('generate layer projections')

g1=parser.add_argument_group('computation options')
g1.add_argument('--batchsize',type=int,default=64)

g2=parser.add_argument_group('output options')
g2.add_argument('--output_dir',type=str,default='projections')
g2.add_argument('--model',type=str,default='ResNet50',choices=['ResNet50'])
g2.add_argument('--data',type=str,default='cifar10',choices=['cifar10'])

args = parser.parse_args()

########################################
print('creating tf graph')

import tensorflow as tf
import tensornets as nets
import cv2
import numpy as np

(Xtrain,Ytrain),(Xtest,Ytest)=tf.keras.datasets.cifar10.load_data()

inputs = tf.placeholder(tf.float32, [None, 224, 224, 3])
model = nets.ResNet50(inputs,is_training=False)
load_model_weights=model.pretrained()

########################################
print('creating output files')

import tables

filename = args.output_dir+'/'+args.model+'-'+args.data+'.h5'
f = tables.open_file(filename, mode='w')
atom = tables.Float64Atom()

def sanitize_tensor_name(t):
    return t.replace('/','_').split(':')[0]

arrays = [ f.create_earray(
            f.root, 
            sanitize_tensor_name(t.name), 
            atom, 
            [0]+t.get_shape().as_list()[1:]
            )
           for t in model.get_middles()
         ]

########################################
print('computing projections')

import datetime

tf.get_default_graph().finalize()
with tf.Session() as sess:
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    print('  loading weights')
    sess.run(load_model_weights)

    print('  loop')

    max_data=Xtrain.shape[0]
    #while stop<max_data:
    for i in range(0,max_data/args.batchsize+1):
        print(''+str(datetime.datetime.now())+': i=',i)
        start=i*args.batchsize
        stop=min((i+1)*args.batchsize,max_data)
        img = Xtrain[start:stop,:,:,:]

        img_resize = np.zeros([args.batchsize,224,224,3])
        for j in range(start,stop):
            j-=start
            img_resize[j,:,:,0] = cv2.resize(img[j,:,:,0],(224,224))
            img_resize[j,:,:,1] = cv2.resize(img[j,:,:,1],(224,224))
            img_resize[j,:,:,2] = cv2.resize(img[j,:,:,2],(224,224))
        img_resize = model.preprocess(img_resize) #,is_training=False)
        middles=sess.run(model.get_middles(), {inputs: img_resize})

        for arr,mid in zip(arrays,middles):
            arr.append(mid)

    #print('middles=',middles)
