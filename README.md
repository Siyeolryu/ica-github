# 건기식 리뷰 팩트체크 시스템

건강기능식품 제품의 온라인 리뷰를 수집하고, AI를 활용하여 광고성 리뷰를 판별하며, 약사의 시각으로 분석 결과를 제공하는 웹 서비스 프로토타입입니다.

## 📖 프로젝트 소개

이 프로젝트는 iHerb에서 수집한 루테인 제품 5종의 리뷰 데이터를 분석하여:
- **광고성 리뷰 판별**: 13단계 체크리스트 기반 자동 검증
- **신뢰도 점수 계산**: 정량적 평가 시스템
- **AI 약사 분석**: Claude AI를 활용한 전문적인 인사이트 제공
- **시각화 대시보드**: Streamlit 기반 인터랙티브 UI

## 🏗️ 프로젝트 구조

```
ica-github/
├── dev2-2Hour/
│   └── dev2-main/          # 메인 프로젝트 폴더
│       ├── docs/           # 프로젝트 문서
│       ├── database/       # 데이터베이스 모듈
│       ├── logic_designer/ # 로직 설계 및 AI 분석
│       ├── ui_integration/ # Streamlit UI
│       ├── data_manager/   # 데이터 수집 및 업로드
│       └── 개발일지/       # 개발 일지
└── README.md               # 이 파일
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/Siyeolryu/ica-github.git
cd ica-github/dev2-2Hour/dev2-main
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
cd ui_integration
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```env
# Supabase 설정
SUPABASE_URL=https://bvowxbpqtfpkkxkzsumf.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# Anthropic Claude API (선택사항)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Streamlit 앱 실행

```bash
cd ui_integration
streamlit run app.py
```

## 📚 주요 기능

### 1. 신뢰도 검증 엔진
- 13단계 광고 판별 체크리스트
- 정량적 신뢰도 점수 계산 (0-100)
- 자동 광고 리뷰 감지

### 2. AI 약사 분석
- Claude AI 기반 전문 분석
- 효능, 부작용, 조언 제공
- 할루시네이션 방지 로직

### 3. 시각화 대시보드
- 신뢰도 게이지 차트
- 레이더 차트 (5개 지표 비교)
- 가격 비교 바 차트
- 리뷰 상세 보기

## 📖 상세 문서

프로젝트의 상세한 문서는 `dev2-2Hour/dev2-main/docs/` 폴더를 참조하세요:

- [프로젝트 전체 개요](dev2-2Hour/dev2-main/docs/프로젝트_전체_개요.md)
- [팀원 협업 가이드](dev2-2Hour/dev2-main/docs/팀원_협업_가이드_1주차.md)
- [사용자 시나리오](dev2-2Hour/dev2-main/docs/사용자_시나리오.md)

## 🛠️ 기술 스택

- **Database**: Supabase (PostgreSQL)
- **AI Analysis**: Anthropic Claude API
- **UI Framework**: Streamlit
- **Visualization**: Plotly
- **Language**: Python 3.8+

## 📝 개발 일지

프로젝트의 개발 과정은 `dev2-2Hour/dev2-main/개발일지/` 폴더에서 확인할 수 있습니다.

## 🤝 기여하기

이 프로젝트는 팀 프로젝트입니다. 기여를 원하시면 이슈를 생성하거나 Pull Request를 제출해주세요.

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 🔗 관련 링크

- [Supabase Dashboard](https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf)
- [Streamlit Cloud](https://streamlit.io/cloud)
