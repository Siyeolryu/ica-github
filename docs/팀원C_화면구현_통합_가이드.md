# 팀원 C: 화면 구현 및 통합 담당 가이드

## 📋 역할 개요

**목표:** "결과물을 멋진 웹 대시보드로 보여준다."

팀원 A(데이터 수집)와 팀원 B(로직 설계 및 AI 분석)가 만든 기능을 연결하여 하나의 Streamlit 웹 서비스로 통합하고, 게이지 차트, 파이 차트 등을 활용해 신뢰도를 시각화하는 역할을 담당합니다.

---

## 🎯 상세 미션

### 1. 팀원 A, B 기능 통합
- 데이터 수집 모듈 연결
- 로직 분석 모듈 연결
- 전체 워크플로우 구현

### 2. Streamlit 웹 서비스 구현
- 사이드바: URL 입력, 설정 옵션
- 메인 화면: 분석 결과 표시
- 3종 비교 기능

### 3. 시각화 구현
- 게이지 차트 (신뢰도 점수)
- 파이 차트 (광고 의심 비율 등)
- 레이더 차트 (3종 비교)
- 바 차트 (재구매율, 사용기간 등)

---

## 🏗️ 시스템 아키텍처

```mermaid
flowchart TD
    Start[사용자 접속] --> Streamlit[Streamlit 앱 시작]
    
    Streamlit --> Sidebar[사이드바 렌더링]
    Sidebar --> Input[URL 입력 받기]
    Sidebar --> Settings[설정 옵션]
    
    Input --> Validate{URL 유효성 검사}
    Validate -->|유효| Trigger[분석 시작 버튼]
    Validate -->|무효| Error[에러 메시지]
    
    Trigger --> Workflow[워크플로우 실행]
    
    Workflow --> TeamA[팀원 A 모듈 호출]
    TeamA --> Scrape[리뷰 수집]
    Scrape --> Clean[데이터 정제]
    Clean --> CSV[CSV 저장]
    
    CSV --> TeamB[팀원 B 모듈 호출]
    TeamB --> Checklist[체크리스트 분석]
    Checklist --> Trust[신뢰도 계산]
    Trust --> AI[GPT-4o 분석]
    
    AI --> Results[결과 데이터]
    
    Results --> Visualize[시각화 생성]
    Visualize --> Gauge[게이지 차트]
    Visualize --> Pie[파이 차트]
    Visualize --> Radar[레이더 차트]
    Visualize --> Bar[바 차트]
    
    Gauge --> MainUI[메인 UI 렌더링]
    Pie --> MainUI
    Radar --> MainUI
    Bar --> MainUI
    
    MainUI --> Display[결과 표시]
    Display --> End[완료]
    
    Error --> End
```

---

## 📁 파일 구조

```
ui_integration/
├── __init__.py              # 패키지 초기화
├── app.py                   # Streamlit 메인 앱
│   ├── main()              # 메인 함수
│   ├── render_sidebar()    # 사이드바 렌더링
│   ├── render_main()       # 메인 화면 렌더링
│   └── run_analysis()      # 분석 실행 함수
├── components.py            # 재사용 가능한 UI 컴포넌트
│   ├── render_trust_gauge() # 신뢰도 게이지
│   ├── render_product_card() # 제품 카드
│   ├── render_comparison_table() # 비교 테이블
│   └── render_pharmacist_insight() # 약사 인사이트
├── visualizations.py        # 차트 및 시각화 함수
│   ├── create_gauge_chart() # 게이지 차트
│   ├── create_pie_chart()   # 파이 차트
│   ├── create_radar_chart() # 레이더 차트
│   ├── create_bar_chart()   # 바 차트
│   └── create_comparison_chart() # 비교 차트
└── utils.py                 # UI 유틸리티
    ├── format_number()      # 숫자 포맷팅
    ├── get_color_by_level() # 신뢰도별 색상
    └── validate_inputs()    # 입력 검증
```

---

## 🔧 기술 스택

- **웹 프레임워크:**
  - `streamlit` (1.28.0+): 웹 앱 프레임워크

- **시각화:**
  - `plotly` (5.17.0+): 인터랙티브 차트
  - `matplotlib` (3.7.0+): 기본 차트 (선택)

- **데이터 처리:**
  - `pandas` (2.0.0+): 데이터 조작

- **기타:**
  - `streamlit-option-menu`: 메뉴 컴포넌트 (선택)
  - `streamlit-aggrid`: 고급 테이블 (선택)

---

## 📝 주요 함수 설계

### 1. `app.py`

#### `main()`
```python
def main():
    """Streamlit 메인 함수"""
    st.set_page_config(
        page_title="건기식 리뷰 팩트체크",
        page_icon="🔍",
        layout="wide"
    )
    
    # 사이드바 렌더링
    sidebar_data = render_sidebar()
    
    # 메인 화면 렌더링
    if sidebar_data.get('analyze_clicked'):
        run_analysis(sidebar_data)
    else:
        render_welcome_screen()
```

#### `render_sidebar()`
```python
def render_sidebar() -> Dict:
    """
    사이드바 렌더링
    
    Returns:
        Dict: 사용자 입력 데이터
        {
            'urls': [url1, url2, url3],
            'max_reviews': 50,
            'filter_ads': True,
            'analyze_clicked': bool
        }
    """
    with st.sidebar:
        st.title("🔍 분석 설정")
        
        # URL 입력 (3개)
        urls = []
        for i in range(3):
            url = st.text_input(
                f"제품 {i+1} URL",
                key=f"url_{i}",
                placeholder="https://shopping.naver.com/..."
            )
            urls.append(url)
        
        # 리뷰 개수 설정
        max_reviews = st.slider(
            "제품당 분석할 리뷰 개수",
            min_value=10,
            max_value=100,
            value=50,
            step=10
        )
        
        # 필터 옵션
        filter_ads = st.checkbox("광고 의심 리뷰 자동 필터링", value=True)
        
        # 분석 시작 버튼
        analyze_clicked = st.button(
            "분석 시작",
            type="primary",
            use_container_width=True
        )
        
        return {
            'urls': urls,
            'max_reviews': max_reviews,
            'filter_ads': filter_ads,
            'analyze_clicked': analyze_clicked
        }
```

#### `run_analysis()`
```python
def run_analysis(sidebar_data: Dict):
    """
    분석 실행 및 결과 표시
    
    Args:
        sidebar_data: 사이드바에서 받은 입력 데이터
    """
    urls = [url for url in sidebar_data['urls'] if url]
    
    if not urls:
        st.error("최소 1개 이상의 URL을 입력해주세요.")
        return
    
    # 진행 상황 표시
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    for idx, url in enumerate(urls):
        status_text.text(f"제품 {idx+1} 분석 중... ({idx+1}/{len(urls)})")
        
        # 팀원 A: 데이터 수집
        progress_bar.progress((idx * 3 + 1) / (len(urls) * 3))
        reviews = collect_reviews(url, sidebar_data['max_reviews'])
        
        # 팀원 B: 분석
        progress_bar.progress((idx * 3 + 2) / (len(urls) * 3))
        analysis_result = analyze_reviews(reviews, url)
        
        results.append(analysis_result)
        progress_bar.progress((idx * 3 + 3) / (len(urls) * 3))
    
    # 결과 표시
    status_text.text("분석 완료!")
    progress_bar.empty()
    
    if len(results) == 1:
        render_single_result(results[0])
    else:
        render_comparison_results(results)
```

### 2. `components.py`

#### `render_trust_gauge()`
```python
def render_trust_gauge(score: float, level: str, size: int = 200):
    """
    신뢰도 게이지 차트 렌더링
    
    Args:
        score: 신뢰도 점수 (0 ~ 100)
        level: 신뢰도 등급 ('high' | 'medium' | 'low')
        size: 차트 크기
    """
    fig = create_gauge_chart(score, level, size)
    st.plotly_chart(fig, use_container_width=True)
```

#### `render_product_card()`
```python
def render_product_card(product_data: Dict):
    """
    제품 카드 컴포넌트 렌더링
    
    Args:
        product_data: {
            'name': '제품명',
            'trust_score': 85,
            'trust_level': 'high',
            'review_count': 127,
            'badge': '가장 정직한 리뷰'
        }
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"### {product_data['name']}")
        render_trust_gauge(
            product_data['trust_score'],
            product_data['trust_level']
        )
        st.caption(f"{product_data['review_count']}개 리뷰 분석")
```

#### `render_comparison_table()`
```python
def render_comparison_table(products: List[Dict]):
    """
    비교 테이블 렌더링
    
    Args:
        products: 제품 분석 결과 리스트
    """
    # 테이블 데이터 구성
    table_data = {
        '비교 항목': [
            '광고 의심 비율',
            '핵심 체감 효능',
            '주요 부작용 리포트',
            '실제 재구매율',
            '한 달 이상 사용자 비율',
            '포토 리뷰 비율'
        ]
    }
    
    for idx, product in enumerate(products):
        table_data[f'제품 {idx+1}'] = [
            f"{product['ad_suspicion_rate']:.1f}%",
            format_efficacy(product['efficacy']),
            format_side_effects(product['side_effects']),
            f"{product['reorder_rate']:.1f}%",
            f"{product['usage_period_rate']:.1f}%",
            f"{product['photo_review_rate']:.1f}%"
        ]
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
```

### 3. `visualizations.py`

#### `create_gauge_chart()`
```python
import plotly.graph_objects as go

def create_gauge_chart(score: float, level: str, size: int = 200) -> go.Figure:
    """
    게이지 차트 생성
    
    Args:
        score: 신뢰도 점수 (0 ~ 100)
        level: 신뢰도 등급
        size: 차트 크기
    
    Returns:
        go.Figure: Plotly Figure 객체
    """
    # 색상 설정
    colors = {
        'high': '#10b981',
        'medium': '#f59e0b',
        'low': '#ef4444'
    }
    color = colors.get(level, '#666')
    
    # 게이지 각도 계산
    angle = (score / 100) * 360
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "신뢰도 점수"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=size, margin=dict(l=20, r=20, t=40, b=20))
    return fig
```

#### `create_pie_chart()`
```python
def create_pie_chart(data: Dict, title: str = "") -> go.Figure:
    """
    파이 차트 생성
    
    Args:
        data: {
            'labels': ['항목1', '항목2', ...],
            'values': [값1, 값2, ...],
            'colors': ['색상1', '색상2', ...]
        }
        title: 차트 제목
    """
    fig = go.Figure(data=[go.Pie(
        labels=data['labels'],
        values=data['values'],
        hole=0.3,
        marker_colors=data.get('colors', None)
    )])
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(
        title=title,
        showlegend=True
    )
    
    return fig
```

#### `create_radar_chart()`
```python
def create_radar_chart(products: List[Dict]) -> go.Figure:
    """
    레이더 차트 생성 (3종 비교)
    
    Args:
        products: 제품 분석 결과 리스트
    
    Returns:
        go.Figure: Plotly 레이더 차트
    """
    categories = [
        '신뢰도',
        '재구매율',
        '사용기간',
        '효능',
        '가격대비'
    ]
    
    fig = go.Figure()
    
    colors = ['#3b82f6', '#ef4444', '#10b981']
    
    for idx, product in enumerate(products):
        values = [
            product['trust_score'] / 100 * 10,
            product['reorder_rate'] / 100 * 10,
            product['usage_period_rate'] / 100 * 10,
            product.get('efficacy_score', 7),
            product.get('value_score', 7)
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f"제품 {idx+1}",
            line_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        title="3종 비교 레이더 차트"
    )
    
    return fig
```

#### `create_bar_chart()`
```python
def create_bar_chart(data: Dict, title: str = "") -> go.Figure:
    """
    바 차트 생성
    
    Args:
        data: {
            'x': ['항목1', '항목2', ...],
            'y': [값1, 값2, ...],
            'colors': ['색상1', '색상2', ...]
        }
        title: 차트 제목
    """
    fig = go.Figure(data=[
        go.Bar(
            x=data['x'],
            y=data['y'],
            marker_color=data.get('colors', '#2563eb')
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title="항목",
        yaxis_title="값"
    )
    
    return fig
```

---

## 🔄 전체 워크플로우

```mermaid
sequenceDiagram
    participant User as 사용자
    participant UI as Streamlit UI
    participant TeamA as 팀원 A 모듈
    participant TeamB as 팀원 B 모듈
    participant Viz as 시각화 모듈
    
    User->>UI: URL 입력 및 설정
    User->>UI: 분석 시작 버튼 클릭
    
    UI->>UI: 입력 검증
    UI->>TeamA: 리뷰 수집 요청
    TeamA->>TeamA: 웹 스크래핑
    TeamA->>TeamA: 데이터 정제
    TeamA->>UI: 리뷰 데이터 반환
    
    UI->>TeamB: 분석 요청
    TeamB->>TeamB: 체크리스트 분석
    TeamB->>TeamB: 신뢰도 계산
    TeamB->>TeamB: GPT-4o 분석
    TeamB->>UI: 분석 결과 반환
    
    UI->>Viz: 시각화 생성 요청
    Viz->>Viz: 게이지 차트 생성
    Viz->>Viz: 파이 차트 생성
    Viz->>Viz: 레이더 차트 생성
    Viz->>UI: 차트 반환
    
    UI->>User: 결과 표시
```

---

## 🎨 UI 레이아웃 설계

### 메인 레이아웃 구조

```
┌─────────────────────────────────────────────────┐
│  사이드바 (고정)  │  메인 콘텐츠 영역            │
│                  │                              │
│  🔍 분석 설정     │  📊 분석 결과                 │
│                  │                              │
│  URL 입력        │  ┌────────────────────────┐  │
│  [URL 1]        │  │  제품 카드 (3개)        │  │
│  [URL 2]        │  │  [게이지] [게이지] [게이지]│  │
│  [URL 3]        │  └────────────────────────┘  │
│                  │                              │
│  리뷰 개수       │  ┌────────────────────────┐  │
│  [슬라이더]      │  │  비교 테이블            │  │
│                  │  └────────────────────────┘  │
│  필터 옵션       │                              │
│  [체크박스]      │  ┌────────────────────────┐  │
│                  │  │  약사 인사이트          │  │
│  [분석 시작]     │  └────────────────────────┘  │
│                  │                              │
│                  │  ┌────────────────────────┐  │
│                  │  │  레이더 차트            │  │
│                  │  └────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ 구현 가이드

### 1단계: 기본 Streamlit 앱 구조

```python
# ui_integration/app.py
import streamlit as st
import sys
import os

# 상위 디렉토리 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_manager.scraper import create_scraper
from data_manager.data_cleaner import save_to_csv
from logic_designer.checklist import AdPatternChecker
from logic_designer.trust_score import TrustScoreCalculator
from logic_designer.ai_analyzer import PharmacistAnalyzer

def main():
    st.set_page_config(
        page_title="건기식 리뷰 팩트체크",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 커스텀 CSS
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    sidebar_data = render_sidebar()
    
    if sidebar_data.get('analyze_clicked'):
        run_analysis(sidebar_data)
    else:
        render_welcome_screen()

if __name__ == "__main__":
    main()
```

### 2단계: 분석 실행 함수

```python
def run_analysis(sidebar_data: Dict):
    """분석 실행"""
    urls = [url for url in sidebar_data['urls'] if url.strip()]
    
    if not urls:
        st.error("❌ 최소 1개 이상의 URL을 입력해주세요.")
        return
    
    # 진행 상황 표시
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    results = []
    
    try:
        for idx, url in enumerate(urls):
            status_text.info(f"📦 제품 {idx+1} 분석 중... ({idx+1}/{len(urls)})")
            
            # 팀원 A: 데이터 수집
            progress = (idx * 4 + 1) / (len(urls) * 4)
            progress_bar.progress(progress)
            
            with st.spinner("리뷰 수집 중..."):
                scraper = create_scraper(url, sidebar_data['max_reviews'])
                reviews = scraper.scrape()
            
            if not reviews:
                st.warning(f"제품 {idx+1}: 리뷰를 수집할 수 없습니다.")
                continue
            
            # 팀원 B: 체크리스트 분석
            progress = (idx * 4 + 2) / (len(urls) * 4)
            progress_bar.progress(progress)
            
            with st.spinner("광고 패턴 분석 중..."):
                checker = AdPatternChecker()
                checklist_results = []
                for review in reviews:
                    check_result = checker.check_all_patterns(review)
                    checklist_results.append(check_result)
            
            # 팀원 B: 신뢰도 계산
            progress = (idx * 4 + 3) / (len(urls) * 4)
            progress_bar.progress(progress)
            
            with st.spinner("신뢰도 계산 중..."):
                from logic_designer.checklist import ChecklistScorer
                scorer = ChecklistScorer()
                checklist_score = scorer.calculate(checklist_results[0])
                
                trust_calc = TrustScoreCalculator()
                trust_score = trust_calc.calculate(reviews, checklist_score)
                trust_level = TrustLevelClassifier().classify(trust_score)
            
            # 팀원 B: AI 분석
            progress = (idx * 4 + 4) / (len(urls) * 4)
            progress_bar.progress(progress)
            
            with st.spinner("AI 약사 분석 중..."):
                analyzer = PharmacistAnalyzer()
                ai_result = analyzer.analyze(reviews, f"제품 {idx+1}")
            
            # 결과 저장
            results.append({
                'url': url,
                'reviews': reviews,
                'trust_score': trust_score,
                'trust_level': trust_level,
                'checklist_results': checklist_results,
                'ai_result': ai_result
            })
        
        # 진행 상황 완료
        progress_bar.progress(1.0)
        status_text.success("✅ 분석 완료!")
        
        # 결과 표시
        if len(results) == 1:
            render_single_result(results[0])
        else:
            render_comparison_results(results)
    
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        st.exception(e)
```

### 3단계: 결과 표시 함수

```python
def render_single_result(result: Dict):
    """단일 제품 결과 표시"""
    st.header("📊 분석 결과")
    
    # 제품 카드
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        render_product_card({
            'name': '제품명',
            'trust_score': result['trust_score'],
            'trust_level': result['trust_level'],
            'review_count': len(result['reviews'])
        })
    
    # 상세 비교 테이블
    st.subheader("📋 상세 분석")
    render_comparison_table([result])
    
    # 약사 인사이트
    st.subheader("💊 AI 약사의 인사이트")
    render_pharmacist_insight(result['ai_result'])

def render_comparison_results(results: List[Dict]):
    """3종 비교 결과 표시"""
    st.header("🔍 3종 비교 분석 리포트")
    
    # 제품 카드 3개
    cols = st.columns(3)
    for idx, (col, result) in enumerate(zip(cols, results)):
        with col:
            render_product_card({
                'name': f'제품 {idx+1}',
                'trust_score': result['trust_score'],
                'trust_level': result['trust_level'],
                'review_count': len(result['reviews'])
            })
    
    # 비교 테이블
    st.subheader("📋 팩트체크 상세 비교")
    render_comparison_table(results)
    
    # 약사 인사이트
    st.subheader("💊 AI 약사의 심층 비교 리포트")
    for idx, result in enumerate(results):
        with st.expander(f"제품 {idx+1} 상세 분석"):
            render_pharmacist_insight(result['ai_result'])
    
    # 레이더 차트
    st.subheader("📊 신뢰도-효능-가격 비교")
    radar_fig = create_radar_chart(results)
    st.plotly_chart(radar_fig, use_container_width=True)
```

---

## 🎨 시각화 예시 코드

### 게이지 차트 상세 구현

```python
# ui_integration/visualizations.py
import plotly.graph_objects as go

def create_gauge_chart(score: float, level: str, size: int = 200) -> go.Figure:
    """게이지 차트 생성"""
    # 색상 설정
    color_map = {
        'high': '#10b981',
        'medium': '#f59e0b',
        'low': '#ef4444'
    }
    color = color_map.get(level, '#666')
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "신뢰도 점수", 'font': {'size': 20}},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=size,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig
```

---

## ⚠️ 주의사항 및 베스트 프랙티스

### 1. Streamlit 성능
- **캐싱 활용:** `@st.cache_data` 데코레이터로 데이터 캐싱
- **세션 상태:** 사용자 입력 상태 관리
- **비동기 처리:** 긴 작업은 백그라운드 처리 고려

### 2. 에러 핸들링
- **입력 검증:** URL 형식, 빈 값 체크
- **예외 처리:** 각 모듈 호출 시 try-except
- **사용자 피드백:** 명확한 에러 메시지

### 3. UI/UX
- **로딩 표시:** 진행 상황 표시
- **반응형 디자인:** 다양한 화면 크기 대응
- **접근성:** 색상 대비, 텍스트 크기 고려

### 4. 모듈 통합
- **의존성 관리:** 상대 경로, 절대 경로 명확히
- **데이터 형식:** 모듈 간 데이터 형식 통일
- **로깅:** 디버깅을 위한 로그 추가

---

## 🧪 테스트 예시

```python
# tests/test_ui.py
import streamlit as st
from ui_integration.components import render_trust_gauge
from ui_integration.visualizations import create_gauge_chart

def test_gauge_chart():
    fig = create_gauge_chart(85, 'high')
    assert fig is not None
    assert len(fig.data) > 0
```

---

## 📚 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Plotly Python 문서](https://plotly.com/python/)
- [Streamlit 컴포넌트](https://streamlit.io/components)

---

## ✅ 체크리스트

- [ ] Streamlit 기본 앱 구조 구현
- [ ] 사이드바 UI 구현
- [ ] 메인 화면 레이아웃 구현
- [ ] 팀원 A 모듈 통합
- [ ] 팀원 B 모듈 통합
- [ ] 게이지 차트 구현
- [ ] 파이 차트 구현
- [ ] 레이더 차트 구현
- [ ] 바 차트 구현
- [ ] 비교 테이블 구현
- [ ] 약사 인사이트 섹션 구현
- [ ] 3종 비교 기능 구현
- [ ] 에러 핸들링 추가
- [ ] 로딩 상태 표시
- [ ] 반응형 디자인 적용

---

## 🚀 실행 방법

```bash
# Streamlit 앱 실행
streamlit run ui_integration/app.py

# 또는 포트 지정
streamlit run ui_integration/app.py --server.port 8501
```

---

## 📌 통합 체크리스트

### 팀원 A 모듈 연동
- [ ] `data_manager` 패키지 import 확인
- [ ] `collect_reviews()` 함수 호출 테스트
- [ ] CSV 파일 저장 경로 확인

### 팀원 B 모듈 연동
- [ ] `logic_designer` 패키지 import 확인
- [ ] `AdPatternChecker` 사용 테스트
- [ ] `TrustScoreCalculator` 사용 테스트
- [ ] `PharmacistAnalyzer` API 키 설정 확인

### 전체 워크플로우
- [ ] URL 입력 → 리뷰 수집 → 분석 → 시각화 전체 플로우 테스트
- [ ] 에러 발생 시 적절한 메시지 표시
- [ ] 진행 상황 표시 정확성 확인

