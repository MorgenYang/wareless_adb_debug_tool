::adb shell "echo w:x90000018:x00000055 > /proc/android_touch/register"
adb shell "echo register,w:x30011000 > /proc/android_touch/debug"
adb shell "sleep 1"
adb shell "echo register,w:x30029000 > /proc/android_touch/debug"

pause

