@echo off
echo ================================
echo  Iniciando servidor Django + Ngrok
echo ================================

cd /d C:\Users\aux5g\Downloads\NX_01

:: Activar entorno virtual
call venv\Scripts\activate

:: Iniciar servidor Django en una nueva ventana
echo 🚀 Iniciando Django...
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

:: Esperar 8 segundos para asegurar que Django ya esté activo
timeout /t 8 >nul

:: Iniciar ngrok
echo 🌐 Iniciando túnel ngrok...
start "Ngrok Tunnel" cmd /k "ngrok http 8000"

:: Esperar 10 segundos para que ngrok levante el túnel antes de reportarlo
timeout /t 10 >nul

:: Enviar automáticamente la URL pública de ngrok a Render
echo 📡 Reportando URL pública a Render...
start "" cmd /k "python reportar_ngrok.py"

echo =====================================
echo ✅ Servidor Django + Ngrok iniciados correctamente
echo =====================================
exit
