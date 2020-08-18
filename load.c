@qcom音量下键触发dump
cd /sys/kernel/debug/spmi/spmi-0 
echo 0x844 > address && echo 1 > count && echo 0x00 > data && echo 0x845 > address && echo 0x00 > data && echo 0x846 > address && echo 0x01 > data && echo 0x847 > address && echo 0x80 > data 

@进入模式：
  edl（9008）
    FORCED_USB_BOOT is connected to 1.8V ------硬件强制下载模式
    "BOOT config" configure to boot from USB -----DP接地
    NOHLOS\BOOT.BF.3.3\boot_images\core\wiredconnectivity\qusb\src\dci\qusb_dci_8953.c qusb_forced_download_feature_supported = TRUE; TRUE修改为
    3.PBL cannot run SBL normally 
      3.1 no emmc 
      3.2 cannot communicate with emmc 
      3.3 emmc is empty 
    4. secure boot pin is wrongly configured, or secure boot fuse is wrongly burned 
    5 some error happened in SBL or LK, then it reboots to EDL; (In this situation, there is some log printed in UART) 
    6 adb reboot edl
  recovery:
    adb reboot recovery
    presistent apk 在一段时间内的频繁crash导致系统保护进入recovery模式---services/core/java/com/android/server/RescueParty.java
    misc分区烧录boot-recovery的misc.img，recovery界面try again的misc.img
    boot-recovery                                                   recovery
    --prompt_and_wipe_data
    --reason=RescueParty
    --locale=zh_CN
                                                       
   
@电池欠压保护
@Hysteresis 这个参数就是一个芯片恢复正常状态，也就是退出UVLO状态的电压差值，比如uvlo是2.7V ，Hysteresis 为100mv，那么电压升高到UVLO + Hysteresis 也就是2.8V，芯片就退出UVLO状态
@low battery voltage ---> vph_pwr low ---> uvlo ---> warm reset (SDM450)
The hardware default UVLO rising threshold is 2.725 V, and the hysteresis is 175 mV. For handset applications, the 
UVLO rising threshold and hysteresis are reconfigured in SBL to 2.825 V rising and 425 mV, respectively. 
UVLO: Undervoltage lockout, it is a threshold. 
vph: the system main supply volatage.
batt-id 电阻值需要看下spec,SDM450不支持140K-170K

@fsg包制作：
@删除mbn_ota.txt,重新编译代码生产不含运营商的版本--重要
fsg时在删除policyman目录时保留device_config.xml.
Please just keep device_config and remove the other files in policyman/
1. add dummy key
2. 导入QCN
3. 开机后删除 EFS/policyman/
4. perl efsreadimage.pl -z 
4. perl efsreadimage.pl -z 
5. python sectools.py mbngen -i fs_image.tar.gz -t efs_tar_40 -o ./out/ -g
6. Python sectools.py secimage -p sdm450 ./out/fs_image.tar.gz.mbn -f efs_tar -o . -sa
7. python efs_image_create.py efs_image_meta.bin fs_image.tar.gz.mbn
8. 擦除modem_st1, modem_st2, fsg,fsc 分区然后下载
nv850 ps模式下校准无问题，注网后会断开。
nv947 0x01在cs模式下无法正常代价
perl 版本需要参与编译xml文件，没有xml::parser命令无法解析，导致efs修改的mbn无法生效
8953 MPSS needs Perl 5.14.2 or later version

@系统重启相关：
/sys/bus/msm_subsys/devices/subsys4/restart_level
SYSTEM modem crash  系统重启     
RELATED modem crash  modem重启
setprop persist.sys.ssr.restart_level ALL_ENABLE   N测子模块单方面重启
CONFIG_MSM_DLOAD_MODE=n 等同于write /sys/module/msm_poweroff/parameters/download_mode 0 相当于不进入dump，改为重启
static int download_mode = 1; in drivers/power/reset/msm-poweroff.c,可以在user版本的情况下刷入修改的userdebug kernel修改重启机制，来抓取dumplog

@kye&input相关：
1）frameworks/base/data/keyboards/Generic.kl 
键盘布局文件添加键值映射，这里的键值对应kernel里面的键值，按键名字对应上层InputEventLabels.h里面定义的按键名字
key 497 GESTURE_WAKELOCK
2）frameworks/base/core/res/res/values/attrs.xml
<enum name="KEYCODE_GESTURE_WAKELOCK" value="267"
3）frameworks\native\include\android\keycodes.h
AKEYCODE_GESTURE_WAKEUP       =267
4）frameworks\native\include\input\InputEventLabels.h  定义键值
DEFINE_KEYCODE(GESTURE_WAKELOCK) 
5）frameworks/base/core/java/android/view/KeyEvent.java
public static final int KEYCODE_GESTURE_WAKELOCK = 267; 

@usb协议和charge相关：
PD（portable device）便携式设备连接到host或hub后，USB2.0协议规定了三种情况下PD汲取电流的最大值：
（1）bus在suspend(挂起)时，最大汲取电流2.5mA；
（2）bus没suspend(挂起)并且未被配置时，最大汲取电流100mA；
（3）bus没suspend(挂起)并被配置时，最大汲取电流500mA.

@空间问题：
1没有space
2inode number被耗尽
cd /data
ls -aliR 遍历所有data目录下的子目录和文件
stat -f /data 查看data目录下inode的使用情况
adb shell dumpsys storage
