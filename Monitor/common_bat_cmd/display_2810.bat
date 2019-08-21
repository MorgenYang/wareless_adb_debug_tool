
adb shell "echo w:x30028000 > /proc/android_touch/register"
adb shell "sleep 1"
adb shell "echo w:x30010000 > /proc/android_touch/register"

pause

