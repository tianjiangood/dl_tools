#-*- coding:utf-8 -*-
import os 
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import cPickle as pk

#bonuding box的格式为(xmin,ymin,xmax,ymax)
#GT(Ground True)数据解析,以文件名为字典的key,字典的值为obj的set集合,每个obj信息形式为{'cls':...,'bd':...}
def voc_parse_gt( voc_root_path,file_list,classes,filter_diff ):

	gt_dat= {}
	counter = 0
	
	label_lines = open(file_list).readlines()
	for a_label in label_lines:
		xml_file = os.path.join( voc_root_path,'Annotations/%s.xml'%(a_label.strip()) )
		tree = ET.parse(xml_file)
		root = tree.getroot()
		
		obj_set = []
		#
		for obj in root.iter('object'):
			difficult = obj.find('difficult').text
			cls = obj.find('name').text
			
			#筛选掉困难样本
			if cls in classes and ( filter_diff is True and int(difficult) == 1):
				continue
				
			#cls_id = classes.index(cls)
			xmlbox = obj.find('bndbox')
			bd = (float(xmlbox.find('xmin').text), float(xmlbox.find('ymin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymax').text))
			obj_set.append( {'cls':cls,'bd':bd} )
			counter+=1
			
		gt_dat[a_label.strip()] = obj_set	
	
	return gt_dat,counter
	
#结果数据解析,检测结果保存为set集合的方式,每个检测结果的保存形式为{'img_id':..,'confidence':..,'bd':..}
def voc_parse_ret( ret_filename ):
	
	ret_set_list =[]
	ret_list = open(ret_filename).readlines()
	
	for a_ret in ret_list:
		ret_set = a_ret.strip().split()
		
		img_id = ret_set[0]
		confidence = float(ret_set[1])
		
		xmin = float(ret_set[2])
		ymin = float(ret_set[3])
		xmax = float(ret_set[4])
		ymax = float(ret_set[5])
		rect = (xmin,ymin,xmax,ymax)
		
		ret_set_list.append({'img_id':img_id,'confidence':confidence,'bd':rect})
		
	return ret_set_list

	
#降序排序比较函数
def sort_comp_desc(a,b):
	if a['confidence']>b['confidence']:
		return -1
	elif a['confidence']<b['confidence']:
		return 1
	else:
		return 0


#计算检测精度
def calc_rect_area( rect ):
	return (rect[2]-rect[0]+1)*(rect[3]-rect[1]+1)

#计算iou rect(xmin,ymin,xmax,ymax)
def calc_IOU(rect1,rect2):

	#交集
	bd_i= ( max(rect1[0],rect2[0]),max(rect1[1],rect2[1]),\
	        min(rect1[2],rect2[2]),min(rect1[3],rect2[3]) )
	iw = bd_i[2]-bd_i[0]+1
	ih = bd_i[3]-bd_i[1]+1
	iou=0
	if( iw>0 and ih>0 ):
		#area of union
		ua = calc_rect_area( rect1 ) + calc_rect_area( rect2 ) - iw*ih
		iou = iw*ih/ua
		
	return iou

	
#采用VOC2012 or ILSVRC style for computing AP
def cal_ap_voc2012( recall,precision ):
	ap_val = 0.0
	eps = 1e-6
	assert len(recall)==len(precision)
	lenght = len(recall)
	cur_prec = precision[lenght-1]
	cur_rec = recall[lenght-1]
	
	#倒序 
	for i in range(0,lenght-1)[::-1]:
		#当前最大的prec值
		cur_prec = max( precision[i],cur_prec)
		if( abs(recall[i]-cur_rec)>eps ):
			ap_val+=cur_prec*abs(recall[i]-cur_rec)
			
		cur_rec = recall[i]
		
	#传统方法
	#for i in range(1,len(recall)):
	#	ap_val += max( precision[i],precision[i-1] )*( recall[i]-recall[i-1] )
	
	return ap_val

	
#计算ap 采用11point模式
def cal_ap_11point( recall,precision ):
	ap_val = 0.0
	eps = 1e-6
	assert len(recall)==len(precision)
	num = len(recall)
	max_precs = np.zeros( num+1 )
	
	start_idx = num - 1
	for j in range(0,11)[::-1]:
		for i in range(0,start_idx+1)[::-1]:
			if recall[i] < (j/10.0):
				start_idx = i
				if j>0:
					max_precs[j-1] = max_precs[j]
				break
			else:
				if max_precs[j]<precision[i]:
					max_precs[j] = precision[i]
	
	for j in range(0,11):
		ap_val += max_precs[j]/11.0
		
	return ap_val
	
#统计gt_hashmap中类型名字包含在classes中的数量
def counter_gt_hashmap_by_cls( gt_hashmap,classes ):

	counter = 0
	for key_v in gt_hashmap.keys():
		for a_gt in gt_hashmap[key_v]:
			if( a_gt['cls'] in classes ):
				counter+=1
	return counter
	

#cls:待统计的class的名字
def voc_calc_precision( gt_hashmap,ret_list,cls,iou_thr ):

	#bin_nr = 10000
	#step_v = 1.0/bin_nr
	#置信度排序,按照将序号排列
	ret_list.sort(sort_comp_desc)
	tp = np.zeros( len(ret_list) )
	fp = np.zeros( len(ret_list) )
	conf_list = np.zeros( len(ret_list) )
	#tp = np.zeros( bin_nr )
	#fp = np.zeros( bin_nr )
	
	npos = counter_gt_hashmap_by_cls( gt_hashmap,[cls] )
	
	print 'npos = %d'%npos
	print 'ret_list len = %d'%len(ret_list)
	print 'gt_hashmap len = %d'%len(gt_hashmap)
	
	repeat_dat = {}
	
	for ret_idx,a_ret in enumerate( ret_list ):
		img_id = a_ret['img_id']
		conf =  a_ret['confidence']
		
		conf_list[ret_idx] = conf
		
		assert gt_hashmap.has_key(img_id)
		
		gt_set = gt_hashmap[img_id]
		
		iou_max = 0
		max_idx = -1
		max_gt = 0
		
		#找到最大的
		for idx,a_gt in enumerate(gt_set):
			if( not a_gt['cls']==cls ):
				continue
				
			if( a_gt.has_key('used')):
				continue
					
			#计算IOU
			iou = calc_IOU( a_ret['bd'], a_gt['bd'] )
			if(iou>iou_max):
				iou_max = iou
				max_idx = idx
				
		#IOU 大于阈值,认为是tp,否则是fp
		#另外对于重复的检测结果，认为是fp
		
		#idx_update = int( (1.0-conf)*(bin_nr-1) + 0.5 )
		if iou_max>iou_thr:
			if(gt_set[max_idx].has_key('used')):
				fp[ret_idx] = 1
				#fp[idx_update] += 1	
			else:
				tp[ret_idx] = 1
				#tp[idx_update] += 1
				gt_set[max_idx]['used'] = 1
		else:
			fp[ret_idx] = 1
			#fp[idx_update] += 1
			
	
	#删除字典的 used key,防止gt_hashmap多次使用
	print 'del used key!'
	del_nr = 0
	for a_key in gt_hashmap.keys():
		for idx,a_gt in enumerate(gt_hashmap[a_key]):
			if(a_gt.has_key('used')):
				gt_hashmap[a_key][idx].pop('used')
				del_nr +=1
				
	print 'del key nr=%d'%del_nr
	
	#计算统计结果
	tp = tp.cumsum()
	fp = fp.cumsum()
	
	recall = tp/npos
	precision = tp/(tp+fp) #range(1,len(tp)+1)
	
	ap = cal_ap_voc2012( recall,precision)
	
	return recall,precision,ap,conf_list
	
def main():

	#类别
	classes = ['person']
	#voc根目录
	voc_root_path = 'F:/data/Pedestrian/VOCCaltechPed'
	#文件列表
	gt_list_fn = os.path.join(voc_root_path,'ImageSets/Main/val.txt')
	#结果文件
	ret_fn = 'F:/data/Pedestrian/VOCCaltechPed/yolo_ret_person.txt'
	ret_fn2 = 'F:/data/Pedestrian/VOCCaltechPed/comp4_det_train_test_person.txt'
	#
	iou_thr = 0.5
	
	# 添加其他的测试结果对照
	
	#gt数据解析
	print 'start voc_parse_gt...'
	(gt_hashmap,total_npos ) = voc_parse_gt(voc_root_path,gt_list_fn,classes,True )
	print 'voc_parse_gt total_npos=%d ok !'%(total_npos)
	
	#结果文件解析
	print 'start voc_parse_ret...'
	ret_list = voc_parse_ret(ret_fn)
	print 'voc_parse_ret pk!!'
	
	print 'start voc_parse_ret...'
	ret_list2 = voc_parse_ret(ret_fn2)
	print 'voc_parse_ret pk!!'
	
	
	# 由于解析文件比较慢,因此在调试的时候可以将数据序列化到文件
	# if 0:
		# fp=open('d:/data_bk.ar','w')
		# total_dat = [ gt_hashmap,total_npos,ret_list ]
		# pk.dump(total_dat,fp)
		# fp.close()
	# else:
		# fp=open('d:/data_bk.ar','r')
		# total_dat = pk.load(fp)
		# gt_hashmap=total_dat[0]
		# total_npos = total_dat[1]
		# ret_list =total_dat[2] 
		# fp.close()
	
	#计算
	( recall,precision,ap,conf_list )     = voc_calc_precision( gt_hashmap,ret_list,classes[0],iou_thr )
	( recall2,precision2,ap2,conf_list2 ) = voc_calc_precision( gt_hashmap,ret_list2,classes[0],iou_thr )
	
	#show 
	plt.figure(1)
	per_line, = plt.plot(recall,precision,'b-')
	per_line.set_label('yolo_%s:AP=%.3f'%(classes[0],ap))
	
	per_line2, = plt.plot(recall2,precision2,'r-')
	per_line2.set_label('ssd_%s:AP=%.3f'%(classes[0],ap2))
	
	plt.plot([i/1000.0 for i in range(1,1001)],[i/1000.0 for i in range(1,1001)],'y--')
	
	plt.axis([0,1.2,0,1.2])
	plt.xlabel('recall')
	plt.ylabel('precision')
	plt.grid()
	
	plt.legend()
	plt.title('ROC')
	
	#单独绘制recall,precision和阈值的关系图
	plt.figure(2)
	ax221 = plt.subplot(121)
	ax222 = plt.subplot(122)
	per_line, = plt.plot(conf_list,precision,'b-')
	plt.xlabel('thr')
	plt.ylabel('precision')
	plt.grid()
	plt.sca(ax221)
	
	per_line, = plt.plot(conf_list,recall,'b-')
	plt.xlabel('thr')
	plt.ylabel('recall')
	plt.grid()
	plt.sca(ax222)
	
	plt.show()
	
	
if __name__ == '__main__':
	main()

