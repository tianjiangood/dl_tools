cd /home/hik/workspace/justin/SSD/caffe
./build/tools/caffe train \
--solver="models/VGGNet/VOCInriaPed/SSD_300x300/solver.prototxt" \
--snapshot="models/VGGNet/VOCInriaPed/SSD_300x300/VGG_VOCInriaPed_SSD_300x300_iter_30000.solverstate" \
--gpu 0 2>&1 | tee jobs/VGGNet/VOCInriaPed/SSD_300x300/VGG_VOCInriaPed_SSD_300x300_2.log
30