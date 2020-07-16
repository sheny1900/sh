qcom音量下键触发dump
cd /sys/kernel/debug/spmi/spmi-0 
echo 0x844 > address && echo 1 > count && echo 0x00 > data && echo 0x845 > address && echo 0x00 > data && echo 0x846 > address && echo 0x01 > data && echo 0x847 > address && echo 0x80 > data 
