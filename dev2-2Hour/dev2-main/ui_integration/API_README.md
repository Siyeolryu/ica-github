# 건기식 리뷰 팩트체크 API 가이드

## 개요

이 프로젝트는 FastAPI 기반의 OpenAPI 서버와 AI 기반 차트 분석 기능을 제공합니다.

## 주요 기능

1. **OpenAPI 서버**: REST API를 통한 리뷰 분석 및 제품 조회
2. **AI 차트 분석**: 차트 데이터를 AI로 분석하여 인사이트 제공
3. **Database 스키마 분석**: AI를 통한 데이터베이스 스키마 자동 문서화

## 설치 및 실행

### 1. 의존성 설치

```bash
cd ui_integration
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 또는 Streamlit secrets에 다음을 설정:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 3. API 서버 실행

```bash
cd ui_integration
python -m api.main
```

또는 uvicorn 직접 실행:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면 다음 URL에서 접근 가능:
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 헬스 체크: http://localhost:8000/health

## API 엔드포인트

### 1. 리뷰 분석 API

#### POST `/api/v1/reviews/analyze`

리뷰를 분석하여 신뢰도 점수와 AI 인사이트를 제공합니다.

**요청 예시:**
```json
{
  "review_text": "이 제품을 한 달간 사용해보니 정말 좋아요! 눈이 밝아진 것 같습니다.",
  "product_id": 1,
  "length_score": 60,
  "repurchase_score": 70,
  "monthly_use_score": 80,
  "photo_score": 0,
  "consistency_score": 75,
  "use_nutrition_validation": true
}
```

**응답 예시:**
```json
{
  "validation": {
    "trust_score": 65.5,
    "is_ad": false,
    "reasons": [],
    "base_score": 65.5,
    "penalty": 0,
    "detected_count": 0
  },
  "analysis": {
    "summary": "한 달 사용 후 눈 밝아짐 체감",
    "efficacy": "루테인 성분의 시력 개선 효과 체감",
    "side_effects": "정보 없음",
    "tip": "장기 복용 시 더 큰 효과 기대 가능"
  }
}
```

#### GET `/api/v1/reviews/batch-analyze`

제품의 여러 리뷰를 일괄 분석합니다.

**파라미터:**
- `product_id` (required): 제품 ID
- `limit` (optional): 분석할 최대 리뷰 수 (기본값: 10)

### 2. 제품 API

#### GET `/api/v1/products/`

제품 목록을 조회합니다.

**쿼리 파라미터:**
- `category` (optional): 카테고리 필터
- `min_rating` (optional): 최소 평점 (0-5)
- `limit` (optional): 최대 결과 수 (기본값: 100)

#### GET `/api/v1/products/{product_id}`

특정 제품 정보를 조회합니다.

### 3. 차트 분석 API

#### POST `/api/v1/charts/analyze`

차트 데이터를 AI로 분석합니다.

**요청 예시:**
```json
{
  "chart_type": "radar",
  "data": {
    "total_products": 3,
    "products": [
      {
        "name": "제품 A",
        "trust_score": 75,
        "price": 29.99,
        "review_count": 50
      }
    ]
  },
  "context": "건강기능식품 제품 비교 분석"
}
```

**응답 예시:**
```json
{
  "summary": "3개 제품 비교 결과, 제품 A가 신뢰도와 가격 대비 우수",
  "key_findings": [
    "제품 A의 신뢰도 점수가 가장 높음",
    "가격 대비 리뷰 품질이 우수함"
  ],
  "trends": "신뢰도 점수가 높을수록 리뷰 수가 증가하는 경향",
  "insights": "제품 A를 추천하며, 장기 사용 시 더 큰 효과 기대",
  "data_quality": "양호"
}
```

## Streamlit UI에서 AI 차트 분석 사용

1. Streamlit 앱 실행:
```bash
streamlit run app.py
```

2. 대시보드에서 차트 확인 후 "🤖 차트 AI 분석" 버튼 클릭

3. AI가 자동으로 차트를 분석하여 다음 정보 제공:
   - 요약
   - 주요 발견사항
   - 트렌드 분석
   - 비즈니스 인사이트
   - 데이터 품질 평가

## Database 스키마 AI 분석

데이터베이스 스키마를 자동으로 분석하고 문서화:

```bash
cd dev2-2Hour/dev2-main/database
python ai_schema_analyzer.py
```

이 명령어는 `SCHEMA_DOCUMENTATION.md` 파일을 생성합니다.

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `api/routes/` 디렉토리에 새 라우터 파일 생성
2. `api/main.py`에 라우터 등록
3. `api/schemas.py`에 필요한 스키마 정의

### 차트 분석기 확장

`chart_analyzer.py`의 `ChartAnalyzer` 클래스를 확장하여 새로운 차트 타입 지원 추가

## 문제 해결

### API 키 오류

- `ANTHROPIC_API_KEY`가 환경 변수 또는 Streamlit secrets에 설정되어 있는지 확인
- API 키가 유효한지 확인

### Import 오류

- 프로젝트 루트 경로가 Python 경로에 포함되어 있는지 확인
- `requirements.txt`의 모든 패키지가 설치되어 있는지 확인

### 데이터베이스 연결 오류

- `SUPABASE_URL`과 `SUPABASE_ANON_KEY`가 올바르게 설정되어 있는지 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

## 참고 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Anthropic Claude API 문서](https://docs.anthropic.com/)
- [Streamlit 문서](https://docs.streamlit.io/)
