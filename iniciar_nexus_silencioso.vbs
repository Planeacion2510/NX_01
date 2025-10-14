Set WshShell = CreateObject("WScript.Shell")

' Inicia Django en segundo plano
WshShell.Run "cmd /c cd /d C:\Users\aux5g\Downloads\NX_01 && call venv\Scripts\activate && start /min python manage.py runserver 0.0.0.0:8000", 0, False

' Esperar a que Django se inicie antes de abrir ngrok
WScript.Sleep 8000

' Inicia ngrok en segundo plano
WshShell.Run "cmd /c cd /d C:\Users\aux5g\Downloads\NX_01 && call venv\Scripts\activate && start /min ngrok http 8000", 0, False
