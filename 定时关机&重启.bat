REM By 愿与君长安
REM 最后修改于2020.9.1
@echo off
MODE con: COLS=80 LINES=18
color b & title 自动关机＆重启程序

:main
echo ┌──────────────────────┐
echo ├     设置定时任务     ┤
echo ├  1.定时关机          ┤
echo ├  2.定时重启          ┤
echo ├  3.取消定时任务      ┤
echo ├  4.退出              ┤
echo └──────────────────────┘
set /p id=请选择您要执行的任务：
if %id%==1 cls & goto shutdown
if %id%==2 cls & goto restart
if %id%==3 cls & goto cancel
if %id%==4 exit
goto main

:shutdown
set /p t=请输入在多久后自动关机(/分)：
set /a s=t*60
shutdown.exe -s -t %s%
if %errorlevel%==0 echo 已设置定时任务,计算机将在%t%分钟后关机!
goto :main

:restart
set /p t=请输入在多久后自动重启(/分)：
set /a s=t*60
shutdown.exe -r -t %s%
if %errorlevel%==0 echo 已设置定时任务,计算机将在%t%分钟后重启!
goto :main

:cancel
shutdown.exe -a
if %errorlevel%==0 echo 已取消定时任务
goto :main