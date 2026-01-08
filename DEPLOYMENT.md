# Naspick 서버 배포 가이드 (Vultr)

## 준비물
- ✅ Vultr 서버 (Ubuntu 22.04 권장)
- ✅ 도메인 (예: naspick.com)
- ✅ SSH 접근 권한

## 1단계: 서버 초기 설정

### SSH 접속
```bash
ssh root@your-server-ip
```

### 필수 패키지 설치
```bash
# 시스템 업데이트
apt update && apt upgrade -y

# Python 및 필수 도구
apt install -y python3-pip python3-venv nginx git

# 방화벽 설정
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
```

## 2단계: 프로젝트 배포

### 프로젝트 디렉토리 생성
```bash
mkdir -p /var/www/naspick
cd /var/www/naspick
```

### 파일 업로드
로컬에서 서버로 파일 전송:
```bash
# 로컬 PC에서 실행
scp -r c:\Users\sec\Desktop\Naspick/* root@your-server-ip:/var/www/naspick/
```

또는 Git 사용:
```bash
# 서버에서 실행
git clone your-repo-url .
```

### Python 가상환경 설정
```bash
cd /var/www/naspick
python3 -m venv venv
source venv/bin/activate
pip install FinanceDataReader pandas numpy
```

## 3단계: 자동 업데이트 설정 (Cron)

### 업데이트 스크립트 생성
```bash
nano /var/www/naspick/update_data.sh
```

내용:
```bash
#!/bin/bash
cd /var/www/naspick
source venv/bin/activate
python3 scorer.py
echo "Data updated at $(date)" >> /var/log/naspick_update.log
```

실행 권한:
```bash
chmod +x /var/www/naspick/update_data.sh
```

### Cron 설정 (15분마다)
```bash
crontab -e
```

추가:
```
*/15 * * * * /var/www/naspick/update_data.sh
```

## 4단계: Nginx 웹서버 설정

### Nginx 설정 파일 생성
```bash
nano /etc/nginx/sites-available/naspick
```

내용:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    root /var/www/naspick;
    index index.html;
    
    # Gzip 압축
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # JSON 파일 캐싱 방지
    location ~ \.json$ {
        add_header Cache-Control "no-store, no-cache, must-revalidate";
        expires -1;
    }
    
    # 정적 파일 캐싱
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 설정 활성화
```bash
ln -s /etc/nginx/sites-available/naspick /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## 5단계: SSL 인증서 (HTTPS) 설정

### Certbot 설치
```bash
apt install -y certbot python3-certbot-nginx
```

### SSL 인증서 발급
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

자동 갱신 확인:
```bash
certbot renew --dry-run
```

## 6단계: 도메인 DNS 설정

Vultr 서버 IP를 도메인에 연결:

| 타입 | 호스트 | 값 | TTL |
|------|--------|-----|-----|
| A | @ | your-server-ip | 3600 |
| A | www | your-server-ip | 3600 |

## 7단계: 모니터링 & 유지보수

### 로그 확인
```bash
# Nginx 로그
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 업데이트 로그
tail -f /var/log/naspick_update.log
```

### 수동 데이터 업데이트
```bash
cd /var/www/naspick
source venv/bin/activate
python3 scorer.py
```

### 서비스 상태 확인
```bash
systemctl status nginx
crontab -l
```

## 옵션: PM2로 실시간 업데이트 (대안)

Cron 대신 PM2로 연속 실행:

```bash
# Node.js & PM2 설치
apt install -y nodejs npm
npm install -g pm2

# Python 스크립트를 PM2로 실행
pm2 start scorer.py --name naspick-updater --interpreter python3 --cron "*/15 * * * *"
pm2 save
pm2 startup
```

## 배포 완료 체크리스트

- [ ] 서버에 모든 파일 업로드
- [ ] Python 패키지 설치
- [ ] 첫 데이터 생성 (`python3 scorer.py`)
- [ ] Nginx 설정 및 재시작
- [ ] SSL 인증서 설치
- [ ] 도메인 DNS A 레코드 설정
- [ ] Cron 자동 업데이트 설정
- [ ] 브라우저에서 접속 확인

## 배포 후 접속

```
https://your-domain.com
```

데이터는 15분마다 자동 업데이트됩니다!
