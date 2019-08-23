
adb shell "echo register,w:x30028000 > /proc/android_touch/debug"
adb shell "sleep 1"
adb shell "echo register,w:x30010000 > /proc/android_touch/debug"

pause

