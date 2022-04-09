@echo off
:: 检查是否存在环境变量 ADB_HOME,存在则删除
wmic ENVIRONMENT where "name='ADB_HOME'" delete
:: 设置环境变量 ADB_HOME
wmic ENVIRONMENT create name="ADB_HOME",username="<system>",VariableValue="%~dp0"

wmic ENVIRONMENT where "name='Path' and username='<system>'" set VariableValue="%PATH%;%ADB_HOME%;"
 
pause