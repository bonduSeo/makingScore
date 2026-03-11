# makingScore

혼합/마스터 음원(mp3/wav)을 입력받아 MIDI 또는 악보(MusicXML) 출력까지 연결하는 **wrapper 앱 초안**입니다.

## 포함된 초안 기능

- 접근 A: 엔드-투-엔드(예: MT3 계열) 호출 래퍼
- 접근 B: 분리(Demucs) → 스템별 전사(Basic Pitch/Omnizart) 래퍼
- MusicXML 변환(옵션, `musescore` CLI 사용)
- GPT 기반 추천 엔드포인트(`/advice`, `OPENAI_API_KEY` 사용)
- OAuth 스캐폴딩(`/auth/login`, `/auth/callback`)

> 실제 모델 CLI가 설치되어 있지 않으면 placeholder MIDI/MusicXML을 생성하도록 구현되어, 파이프라인 wiring을 먼저 확인할 수 있습니다.

## 빠른 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

브라우저에서 `http://localhost:8000` 접속.

## 환경 변수

```bash
OPENAI_API_KEY=...
OAUTH_ENABLED=true
OAUTH_CLIENT_ID=...
OAUTH_CLIENT_SECRET=...
OAUTH_AUTHORIZE_URL=https://auth.openai.com/oauth/authorize
OAUTH_TOKEN_URL=https://auth.openai.com/oauth/token
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
```

## 테스트

```bash
pytest
```
