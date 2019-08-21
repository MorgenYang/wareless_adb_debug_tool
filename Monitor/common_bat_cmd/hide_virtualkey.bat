@echo off 
:cho
echo ========================Himax Touch HideVirtualKey===========================
echo.
echo 1.hide_virtual_key_and_topbar
echo.
echo 2.hide_topbar
echo.
echo 3.hide_virtual_key
echo.
echo 4.default
echo.
echo 4.exit: ctrl+c
echo.
echo ======================================================================
SET /P choice=Please choice your item and press Enter: 

IF NOT "%choice%"=="" SET choice=%choice:~0,4%
if /i "%choice%"=="1" goto hide_virtual_key_and_topbar
if /i "%choice%"=="2" goto hide_topbar
if /i "%choice%"=="3" goto hide_virtual_key
if /i "%choice%"=="4" Back_to_default

echo Invalid choice, choice again!
echo.
goto cho

:hide_virtual_key_and_topbar
::Òþ²ØÐéÄâ¼ü¼°¶¥²¿×´Ì¬À¸£º

adb shell settings put global policy_control immersive.full=*
goto cho

:hide_topbar
::Òþ²Ø¶¥²¿×´Ì¬À¸£¨µ×²¿ÐéÄâ¼ü»áÏÔÊ¾£©£º

adb shell settings put global policy_control immersive.status=*
goto cho

:hide_virtual_key
::Òþ²ØÐéÄâ¼ü£¨¶¥²¿×´Ì¬À¸»áÏÔÊ¾£©£º

:Back_to_default
adb shell settings put global policy_control immersive.navigation=*
goto cho

::»Ö¸´Ô­À´µÄÉèÖÃ£º

adb shell settings put global policy_control null 
goto cho