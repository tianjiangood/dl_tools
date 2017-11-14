import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
#matplotlib inline

plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'

# Make sure that caffe is on the python path:
caffe_root = './'  # this file is expected to be in {caffe_root}/examples
import os
os.chdir(caffe_root)
import sys
sys.path.insert(0, 'python')

import caffe
caffe.set_device(0)
caffe.set_mode_gpu()


from google.protobuf import text_format
from caffe.proto import caffe_pb2

root_path = '/home/hik/workspace/justin/SSD/caffe/'
dataset_name = 'VOCCaltechPed'
# load PASCAL VOC labels
#labelmap_file = '/home/hik/workspace/justin/SSD/caffe/data/VOC0712/labelmap_voc.prototxt' #justin
labelmap_file = root_path + '/data/VOCdevkit/{}/labelmap_voc.prototxt'.format(dataset_name) #justin

file = open(labelmap_file, 'r')
labelmap = caffe_pb2.LabelMap()
text_format.Merge(str(file.read()), labelmap)

def get_labelname(labelmap, labels):
    num_labels = len(labelmap.item)
    labelnames = []
    if type(labels) is not list:
        labels = [labels]
    for label in labels:
        found = False
        for i in xrange(0, num_labels):
            if label == labelmap.item[i].label:
                found = True
                labelnames.append(labelmap.item[i].display_name)
                break
        assert found == True
    return labelnames
    
    
#model_def     = '/home/hik/ssd/caffe/models/VGGNet/VOC0712/SSD_300x300/deploy.prototxt'
#model_weights = '/home/hik/ssd/caffe/models/VGGNet/VOC0712/SSD_300x300/VGG_VOC0712_SSD_300x300_iter_5000.caffemodel'
model_def     = root_path + '/models/VGGNet/{}/SSD_500x500/deploy.prototxt'.format(dataset_name)						                #justin 
model_weights = root_path + '/models/VGGNet/{}/SSD_500x500/VGG_{}_SSD_500x500_iter_30000.caffemodel'.format(dataset_name,dataset_name) #justin 


net = caffe.Net(model_def,      # defines the structure of the model
                model_weights,  # contains the trained weights
                caffe.TEST)     # use test mode (e.g., don't perform dropout)

# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2, 0, 1))
transformer.set_mean('data', np.array([104,117,123])) # mean pixel
transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

# set net to batch size of 1
image_resize = 500
net.blobs['data'].reshape(1,3,image_resize,image_resize)

def proc_fun(filename,k,conf_thr):

	image = caffe.io.load_image(filename)
	plt.imshow(image)
	
	#st_time = time.clock()
	transformed_image = transformer.preprocess('data', image)
	net.blobs['data'].data[...] = transformed_image
	#print 'Preprocess cost is %.3fs'%( time.clock()-st_time)
	
	# Forward pass.
	st_time = time.clock()
	detections = net.forward()['detection_out']
	print '%d Forward cost is %.3fs'%(k,time.clock()-st_time)
	
	
    # Parse the outputs.
	det_label = detections[0,0,:,1]
	det_conf = detections[0,0,:,2]
	det_xmin = detections[0,0,:,3]
	det_ymin = detections[0,0,:,4]
	det_xmax = detections[0,0,:,5]
	det_ymax = detections[0,0,:,6]
	
	# Get detections with confidence higher than 0.6.
	top_indices = [i for i, conf in enumerate(det_conf) if conf >=conf_thr]
	top_conf = det_conf[top_indices]
	top_label_indices = det_label[top_indices].tolist()
	top_labels = get_labelname(labelmap, top_label_indices)
	top_xmin = det_xmin[top_indices]
	top_ymin = det_ymin[top_indices]
	top_xmax = det_xmax[top_indices]
	top_ymax = det_ymax[top_indices]
	
	colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()
	plt.imshow(image)
	currentAxis = plt.gca()
	
	for i in xrange(top_conf.shape[0]):
		xmin = int(round(top_xmin[i] * image.shape[1]))
		ymin = int(round(top_ymin[i] * image.shape[0]))
		xmax = int(round(top_xmax[i] * image.shape[1]))
		ymax = int(round(top_ymax[i] * image.shape[0]))
		score = top_conf[i]
		label = int(top_label_indices[i])
		label_name = top_labels[i]
		display_txt = '%s: %.2f'%(label_name, score)
		coords = (xmin, ymin), xmax-xmin+1, ymax-ymin+1
		color = colors[label]
		currentAxis.add_patch(plt.Rectangle(*coords, fill=False, edgecolor=color, linewidth=2))
		currentAxis.text(xmin, ymin, display_txt, bbox={'facecolor':color, 'alpha':0.5})
	
	plt.savefig('./{}.jpg'.format(k))
	plt.close()
	#plt.show()
	
for i in np.linspace(1,8,8):
	conf_thr = 0.6
	filename = '/home/hik/workspace/justin/SSD/caffe/examples/images/%d.jpg'%i
	proc_fun(filename,int(i),conf_thr)

print 'ok'
