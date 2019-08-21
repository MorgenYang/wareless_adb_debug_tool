::adb shell "echo w:x90000018:x00000055 > /proc/android_touch/register"
adb shell "echo w:x30011000 > /proc/android_touch/register"
adb shell "sleep 1"
adb shell "echo w:x30029000 > /proc/android_touch/register"

pause

