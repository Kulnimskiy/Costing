@echo off
cd C:\Users\User\Desktop\Projects\Costing
call venv\Scripts\activate
start flask --app .\project\app run --host=0.0.0.0 --port=5000 --debug
timeout /t 2
start http://192.168.1.87:5000