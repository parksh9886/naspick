@echo off
echo ================================
echo Naspick 로컬 서버 실행
echo ================================
echo.
echo 브라우저에서 다음 주소로 접속하세요:
echo http://localhost:8000
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
python -m http.server 8000
