#-*- coding=utf-8 -*-

import os,sys
from os import listdir,getcwd
from os.path import join
import subprocess
import random


#
sets=[('VOCCaltechPed', 'train'), ('VOCCaltechPed', 'test')]  #modify 
#
file_ext_name = 'jpg'

#VOCdevkit所在的目录
VOC_root_path = '/home/hik/workspace/justin/darknet/darknet-master/train/VOCdevkit' 
#caffe root path
caffe_root_path = '/home/hik/workspace/justin/SSD/caffe'

wd =  sys.path[0]

for dataset_name, image_set in sets:

	fn = '%s/%s/ImageSets/Main/%s.txt'%(VOC_root_path,dataset_name, image_set)
	print fn
	image_ids = open( fn ).read().strip().split()
	#随机打乱,在create_data.sh中打散
	#random.shuffle( image_ids )
	
	list_fn = '%s/%s.txt'%(wd,image_set)
	print list_fn
	list_file = open(list_fn,'w')
	
	for image_id in image_ids:
		list_file.write( '%s/JPEGImages/%s.%s %s/Annotations/%s.xml\n'%(dataset_name,image_id,file_ext_name,dataset_name, image_id) )
	list_file.close()
	

#执行外部程序,获取训练图像的尺寸
list_file= os.path.join( wd,'test.txt')
dst_file= os.path.join( wd,'test_name_size.txt')
tools_path = os.path.join(caffe_root_path,'build/tools/get_image_size')
cmd_str = tools_path + ' ' + VOC_root_path + ' ' + list_file + ' ' + dst_file

print 'command:',cmd_str

subprocess.call(cmd_str, shell=True)

