REM By Ը�������
REM ����޸���2020.9.1
@echo off
MODE con: COLS=80 LINES=18
color b & title �Զ��ػ�����������

:main
echo ������������������������������������������������
echo ��     ���ö�ʱ����     ��
echo ��  1.��ʱ�ػ�          ��
echo ��  2.��ʱ����          ��
echo ��  3.ȡ����ʱ����      ��
echo ��  4.�˳�              ��
echo ������������������������������������������������
set /p id=��ѡ����Ҫִ�е�����
if %id%==1 cls & goto shutdown
if %id%==2 cls & goto restart
if %id%==3 cls & goto cancel
if %id%==4 exit
goto main

:shutdown
set /p t=�������ڶ�ú��Զ��ػ�(/��)��
set /a s=t*60
shutdown.exe -s -t %s%
if %errorlevel%==0 echo �����ö�ʱ����,���������%t%���Ӻ�ػ�!
goto :main

:restart
set /p t=�������ڶ�ú��Զ�����(/��)��
set /a s=t*60
shutdown.exe -r -t %s%
if %errorlevel%==0 echo �����ö�ʱ����,���������%t%���Ӻ�����!
goto :main

:cancel
shutdown.exe -a
if %errorlevel%==0 echo ��ȡ����ʱ����
goto :main