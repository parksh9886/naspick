# Naspick - Stock Ranking System

실시간 나스닥/S&P 500 종목 분석 및 랭킹 시스템

## 🚀 배포 방법 (GitHub Pages - 초간단!)

### 1단계: GitHub에 업로드
```bash
cd c:\Users\sec\Desktop\Naspick
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/naspick.git
git push -u origin main
```

### 2단계: GitHub Pages 활성화
1. GitHub 저장소 → Settings
2. Pages 섹션
3. Source: **Deploy from a branch**
4. Branch: **main** / **(root)**
5. Save

끝! 🎉 → `https://your-username.github.io/naspick`

### 자동 데이터 업데이트 (선택사항)
GitHub Actions가 15분마다 자동으로 데이터 업데이트합니다.
`.github/workflows/update-data.yml` 파일이 이미 포함되어 있습니다.

## 🔧 로컬 테스트

```bash
# 데이터 생성
python scorer.py

# 서버 실행
start_server.bat

# 브라우저
http://localhost:8000
```

## 대안 배포 옵션

### Vercel (추천!)
```bash
npm i -g vercel
vercel
```
→ 자동 HTTPS, 자동 배포, 무료

### Netlify
Netlify Drop으로 폴더 드래그앤드롭 → 즉시 배포

## 📁 파일 구조
```
Naspick/
├── index.html          # 메인 페이지
├── page.html           # 상세 페이지
├── data.json           # 데이터 (자동 생성)
├── scorer.py           # 데이터 생성 스크립트
├── start_server.bat    # 로컬 테스트용
└── .github/
    └── workflows/
        └── update-data.yml  # 자동 업데이트
```

## ⚡ 특징
- 실시간 주식 데이터 (FinanceDataReader)
- 기술적 분석 (RSI, MACD, MA)
- AI 브리핑
- 피봇 포인트 계산
- 자동 티어 분류
