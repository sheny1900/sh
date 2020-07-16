@qcom音量下键触发dump
cd /sys/kernel/debug/spmi/spmi-0 
echo 0x844 > address && echo 1 > count && echo 0x00 > data && echo 0x845 > address && echo 0x00 > data && echo 0x846 > address && echo 0x01 > data && echo 0x847 > address && echo 0x80 > data 

@电池欠压保护
@Hysteresis 这个参数就是一个芯片恢复正常状态，也就是退出UVLO状态的电压差值，比如uvlo是2.7V ，Hysteresis 为100mv，那么电压升高到UVLO + Hysteresis 也就是2.8V，芯片就退出UVLO状态
@low battery voltage ---> vph_pwr low ---> uvlo ---> warm reset (SDM450)
The hardware default UVLO rising threshold is 2.725 V, and the hysteresis is 175 mV. For handset applications, the 
UVLO rising threshold and hysteresis are reconfigured in SBL to 2.825 V rising and 425 mV, respectively. 

UVLO: Undervoltage lockout, it is a threshold. 
vph: the system main supply volatage.
