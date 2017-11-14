#-*- coding:utf-8 -*-
import cv2
import os 
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

#解析xml文件,返回目标set
def parse_pascal_xml(xml_filename,filter_diff=False):
	tree = ET.parse(xml_filename)
	root = tree.getroot()
		
	obj_set = []
	#
	for obj in root.iter('object'):
		difficult = obj.find('difficult').text
		cls = obj.find('name').text
			
		#筛选掉困难样本
		if ( filter_diff is True and int(difficult) == 1):
			continue
				
		#cls_id = classes.index(cls)
		xmlbox = obj.find('bndbox')
		bd = (float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymax').text))
		obj_set.append( {'cls':cls,'bd':bd,'diff':int(difficult)} )
	
	return obj_set
	
#显示
#root_path 数据集根目录
#list_file 清单文件
#label_strs 标签名字列表
#colors 颜色表,不同的标签显示不同的颜色
def show_data( root_path,list_file,label_strs,colors ):
	wait_sec = 0
	cv2.namedWindow('ORG',0)
	
	label_lines = open(list_file).readlines()
	
	for a_label in label_lines:
		xml_file = os.path.join( root_path,'Annotations/%s.xml'%(a_label.strip()) )
		obj_set = parse_pascal_xml(xml_file)
		
		file_nm = a_label.strip()
		img_fn = os.path.join( root_path,'JPEGImages/'+file_nm+'.jpg')
				
		#print img_fn
		img = cv2.imread( img_fn )
				
		for idx,data in enumerate(obj_set):
			
			#类别默认id
			cls_id = 0
			#如果类别名称在标签序列中获取对应的类别id
			if( data['cls'] in label_strs ):
				cls_id = label_strs.index(data['cls'])
			
			#困难样本显示为灰色
			if( data['diff'] ):
				color = (128,128,128)
			else:
				color = ( 255*colors[cls_id][0],255*colors[cls_id][1],255*colors[cls_id][2] )
			
			#显示矩形框和类别名
			rect = data['bd']
			cv2.rectangle( img,(int(rect[0]),int(rect[1])),(int(rect[2]),int(rect[3])),color,2 )
			cv2.putText( img,data['cls'],(int(rect[0]),int(rect[1])), cv2.FONT_HERSHEY_SIMPLEX,0.5,color )
			#显示文件名
			cv2.putText( img,file_nm,(15,15), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0) )
			
		
		#显示图像
		cv2.imshow('ORG',img)
		#键盘操作
		key = cv2.waitKey(wait_sec)
		if(key==32):
			wait_sec = 1-wait_sec
		elif(key==ord('q') or key==ord('Q') ):
			return 0
		
	return 0
		
	
def main():

	#标签名称,可填可不填写
	labels = ['back_ground','person']
	#颜色表
	colors = plt.cm.hsv(np.linspace(0, 1, 1+len(labels))).tolist()
	
	#数据集的根目录
	root_path ='F:/data/Pedestrian/VOCCaltechPed'
	
	#图片清单文件
	list_file = os.path.join( root_path ,'ImageSets/Main/train.txt')
	
	show_data(root_path,list_file,labels,colors)

if __name__ == '__main__':
	main()