#!/bin/sh
#caffe root dir
root_dir=/home/hik/workspace/justin/SSD/caffe

cd $root_dir

#如果data_save_dir存在则重新生成,否则报错退出
redo=1

#数据库名字
dataset_name="VOCCaltechPed"

#数据源目录
data_root_dir=/home/hik/workspace/justin/darknet/darknet-master/train/VOCdevkit

#保存目录
data_save_dir=/home/hik/workspace/justin/SSD/caffe/data/VOCdevkit/$dataset_name

#label标签名
mapfile="$root_dir/data/VOCdevkit/$dataset_name/labelmap_voc.prototxt"

#标签类型,用于检测或者分类?
anno_type="detection"

#输出数据库类型
db="lmdb"

#等比例缩放,保持原有图像的高宽比不变
min_dim=0
max_dim=0

#强制缩放到统一大小,改变原有图像的高宽比
width=0
height=0

echo $data_save_dir
#sudo chmod -R 777 $data_save_dir

#--check-label检查mapfile中的标签名是否有重复
extra_cmd="--check-label --encode-type=jpg --encoded"

if [ $redo -eq 1 ]
then
  extra_cmd="$extra_cmd --redo"
fi


for subset in test train
#for subset in test
do 
  extra_cmd_exec=$extra_cmd
  #训练集需要打乱
  if [ "$subset" = "train" ]
  then
  	extra_cmd_exec="$extra_cmd_exec --shuffle"
  fi
  
  echo "extra_cmd_exec=" $extra_cmd_exec
  
  python $root_dir/scripts/create_annoset.py \
  --anno-type=$anno_type \
  --label-map-file=$mapfile \
  --min-dim=$min_dim --max-dim=$max_dim --resize-width=$width --resize-height=$height \
  $extra_cmd_exec \
  $data_root_dir \
  $root_dir/data/VOCdevkit/$dataset_name/$subset.txt \
  $data_save_dir/$db/$dataset_name"_"$subset"_"$db \
  examples/$dataset_name 
done


