adb root
adb remount


adb shell "echo w:x30051000:x00ff0f00 > /proc/android_touch/register"
pause


adb shell "echo w:x30053000:x00002400 > /proc/android_touch/register"
pause

adb shell "echo w:x30055000:x00000000 > /proc/android_touch/register"
pause




adb shell "echo r:x30054001 > /proc/android_touch/register"

adb shell "cat /proc/android_touch/register" 

adb shell "echo r:x30056001 > /proc/android_touch/register"

adb shell "cat /proc/android_touch/register" 

adb shell "echo r:x30052001 > /proc/android_touch/register"

adb shell "cat /proc/android_touch/register" 

adb shell "echo r:x30052002 > /proc/android_touch/register"

adb shell "cat /proc/android_touch/register" 



timeout /t 1

pause

