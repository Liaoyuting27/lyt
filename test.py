# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 10:13:51 2019

@author: Administrator
"""

from PIL import Image


def imageprepare():
    file_name = '0.png'
    myimage = Image.open(file_name)
    myimage = myimage.resize((28, 28), Image.ANTIALIAS).convert('L')  
    tv = list(myimage.getdata())  
    tva = [(255-x)*1.0/255.0 for x in tv]  
    return tva

result = imageprepare()
init = tf.global_variables_initializer()
saver = tf.train.Saver 

with tf.Session() as sess:
    sess.run(init)
    saver = tf.train.import_meta_graph('data/model.ckpt.meta')  
    saver.restore(sess,  'data/model.ckpt')  

    graph = tf.get_default_graph()  
    x = graph.get_tensor_by_name("x:0")  
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    y_conv = graph.get_tensor_by_name("y_conv:0") 

    prediction = tf.argmax(y_conv, 1)
    predint = prediction.eval(feed_dict={x: [result], keep_prob: 1.0}, session=sess)  
    print(predint[0]) 