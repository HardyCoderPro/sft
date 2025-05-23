@echo off
title Telegram Bot Projesi Yöneticisi
color 0a

:: Veritabanını başlat
echo Veritabanı başlatılıyor...
python database.py

:: Admin panelini başlat (yeni terminalde)
start streamlit run admin_panel.py

:: Telegram botunu başlat (yeni terminalde)
start python bot.py

pause
echo Tüm bileşenler başlatıldı!