@echo off

echo.
echo Start to rotate your diag arrange.
:loop
echo.
SET /P val="Please enter number 0~7 to diag_arr(bit2-bit0:[RxTx][Tx][Rx]): " 
::else�������if���Ӻ������)����, elseǰ�������ո�.
IF %val% GTR 7 (
echo. 
echo Invalid Input try again...
echo.
goto loop 
) else (
	adb shell "echo %val% > proc/android_touch/diag_arr"
	echo.
	echo rotate done.
	echo.
	goto :eof
)

