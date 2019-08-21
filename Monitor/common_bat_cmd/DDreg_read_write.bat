@echo Off
adb root
adb remount 
SET Touchpath=/proc/android_touch
echo -------------------------------------------------------------------------
echo 


echo DDreg E8 pa8=0x95 bank0 value is: 
adb shell "echo w:x900000FC:xAAE80008 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"

echo DDreg  BA pa7=0x12 bank0 value is: 
adb shell "echo w:x900000FC:xAABA0020 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"


echo DDreg  B2 pa21=0xA2 bank0 value is: 
adb shell "echo w:x900000FC:xAAB20020 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"

echo DDreg  B2 pa22=0x07 bank0 value is: 
adb shell "echo w:x900000FC:xAAB20020 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"

echo DDreg  B1 pa1=0x4E bank0 value is: 
adb shell "echo w:x900000FC:xAAB10020 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"

echo DDreg  D1 pa4=0x0C bank0 value is: 
adb shell "echo w:x900000FC:xAAD10020 > %Touchpath%/register"
adb shell "echo r:x10007F80 > %Touchpath%/register"
adb shell "cat %Touchpath%/register"

ho.
echo.
echo.
echo.
echo.
echo.
pause
