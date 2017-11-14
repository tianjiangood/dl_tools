log_filename=$(date "+test_%F_%H-%M.log")
log_out=./$log_filename

cd /home/hik/workspace/justin/SSD/caffe

./build/tools/caffe test \
--model="models/VGGNet/VOCCaltechPed/SSD_500x500/test_bat.prototxt" \
-weights="models/VGGNet/VOCCaltechPed/SSD_500x500/VGG_VOCCaltechPed_SSD_500x500_iter_45000.caffemodel" \
--iterations=2522 \
--gpu 0 2>&1 | tee $log_out
