::adb root
::pause

adb shell "rm /data/user/Flash_Dump.bin"
adb shell "echo 0 > proc/android_touch/diag"
adb shell "echo 1 > proc/android_touch/reset"
adb shell "sleep 2"
adb shell "echo 2_64 > proc/android_touch/flash_dump"
adb shell "sleep 15"
adb shell "echo 1 > proc/android_touch/reset"
adb pull /sdcard/Flash_Dump.bin 


pause
exit






