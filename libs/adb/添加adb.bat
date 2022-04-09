:: 设置环境变量
:: 关闭终端回显
:: SETX 永久设置用户环境变量
:: SETX /M 永久设置系统环境变量
:: SET 临时设置用户环境变量
:: SET /M  临时设置系统环境变量
@echo off
SET ADB_PATH=%cd%
setx /M "%path%" "%path%[%ADB_PATH%];"

@echo %PATH%
:: SETX PATH "%PATH%;%ADB_PATH%;"
wmic ENVIRONMENT where "name='Path' and username='<system>'" set VariableValue="%PATH%;%ADB_PATH%;"
 
pause