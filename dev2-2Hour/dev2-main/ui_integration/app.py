"""
건기식 리뷰 팩트체크 시스템 - Streamlit UI
모든 데이터를 활용한 종합 분석 대시보드
"""

import streamlit as st
import pandas as pd
import os
from typing import Dict, List, Optional
from datetime import datetime

# 페이지 설정을 먼저 실행 (Streamlit 초기화)
st.set_page_config(
    page_title="건기식 리뷰 팩트체크",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 이후 모듈 import (같은 디렉토리에서 직접 import)
# Supabase 연결 강제 - 목업 데이터 사용 안 함
from supabase_data import (
    get_all_analysis_results, 
    get_all_products, 
    search_products,
    get_products_by_category,
    get_products_by_rating_range,
    get_reviews_by_date_range,
    get_reviews_by_language,
    get_all_categories,
    get_statistics_summary
)
USE_SUPABASE = True

# ========== 성능 최적화: 데이터 캐싱 ==========
@st.cache_data(ttl=300)  # 5분 캐시
def get_cached_products():
    """제품 목록 캐싱"""
    return get_all_products()

@st.cache_data(ttl=300)
def get_cached_categories():
    """카테고리 목록 캐싱"""
    return get_all_categories()

@st.cache_data(ttl=300)
def get_cached_statistics():
    """통계 데이터 캐싱"""
    return get_statistics_summary()

@st.cache_data(ttl=300)
def get_cached_analysis_results():
    """분석 결과 캐싱"""
    return get_all_analysis_results()

# ========== 필터 검증 함수 ==========
def validate_filters(filters: Dict) -> List[str]:
    """필터 값 검증 및 에러 메시지 반환"""
    errors = []
    
    # 날짜 검증 제거됨 (필터 삭제)
    
    # 가격 범위 검증
    if filters.get('price_range'):
        min_price, max_price = filters['price_range']
        if min_price > max_price:
            errors.append("최소 가격은 최대 가격보다 작아야 합니다")
        if min_price < 0 or max_price < 0:
            errors.append("가격은 0 이상이어야 합니다")
    
    # 평점 범위 검증
    if filters.get('rating_range'):
        min_rating, max_rating = filters['rating_range']
        if min_rating > max_rating:
            errors.append("최소 평점은 최대 평점보다 작아야 합니다")
        if min_rating < 0 or max_rating > 5:
            errors.append("평점은 0-5 사이여야 합니다")
    
    # 리뷰 수 범위 검증
    if filters.get('review_count_range'):
        min_reviews, max_reviews = filters['review_count_range']
        if min_reviews > max_reviews:
            errors.append("최소 리뷰 수는 최대 리뷰 수보다 작아야 합니다")
        if min_reviews < 0:
            errors.append("리뷰 수는 0 이상이어야 합니다")
    
    return errors

# ========== 필터 히스토리 관리 ==========
def save_filter_state_to_history(filters: Dict):
    """현재 필터 상태를 히스토리에 저장"""
    if 'filter_history' not in st.session_state:
        st.session_state.filter_history = []
    
    # 현재 상태를 딥 카피하여 저장
    import copy
    current_state = copy.deepcopy(filters)
    st.session_state.filter_history.append(current_state)
    
    # 최대 10개까지만 저장
    if len(st.session_state.filter_history) > 10:
        st.session_state.filter_history.pop(0)

def restore_filter_state_from_history():
    """히스토리에서 이전 필터 상태 복원"""
    if 'filter_history' not in st.session_state or len(st.session_state.filter_history) == 0:
        return None
    
    return st.session_state.filter_history.pop()

def get_active_filters_summary(filters: Dict, all_products_list: List[Dict]) -> List[str]:
    """활성 필터 요약 정보 생성"""
    active_filters = []
    
    if filters.get('category_filter'):
        active_filters.append(f"카테고리: {len(filters['category_filter'])}개")
    
    if filters.get('brand_filter'):
        active_filters.append(f"브랜드: {len(filters['brand_filter'])}개")
    
    if filters.get('price_range') and all_products_list:
        prices = [p.get("price", 0) for p in all_products_list if p.get("price") and p.get("price") > 0]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            if filters['price_range'][0] != min_price or filters['price_range'][1] != max_price:
                active_filters.append(f"가격: ${filters['price_range'][0]:.0f}-${filters['price_range'][1]:.0f}")
    
    if filters.get('rating_range'):
        min_rating, max_rating = filters['rating_range']
        if all_products_list:
            ratings = [p.get("rating_avg", 0) for p in all_products_list if p.get("rating_avg") and p.get("rating_avg") > 0]
            if ratings:
                min_rating_all = min(ratings)
                max_rating_all = max(ratings)
                if min_rating != min_rating_all or max_rating != max_rating_all:
                    active_filters.append(f"평점: {min_rating:.1f}-{max_rating:.1f}")
    
    if filters.get('review_count_range'):
        min_reviews, max_reviews = filters['review_count_range']
        if all_products_list:
            review_counts = [p.get("rating_count", 0) for p in all_products_list if p.get("rating_count")]
            if review_counts:
                min_reviews_all = min(review_counts)
                max_reviews_all = max(review_counts)
                if min_reviews != min_reviews_all or max_reviews != max_reviews_all:
                    active_filters.append(f"리뷰 수: {min_reviews}-{max_reviews}개")
    
    if filters.get('trust_filter') and len(filters['trust_filter']) < 3:
        active_filters.append(f"신뢰도: {', '.join(filters['trust_filter'])}")
    
    if filters.get('search_query'):
        active_filters.append(f"검색: '{filters['search_query']}'")
    
    if filters.get('main_brand'):
        active_filters.append(f"메인 브랜드: {filters['main_brand']}")
    
    # 날짜 필터 및 언어 필터 제거됨
    
    return active_filters

def reset_all_filters(all_products_list: List[Dict], categories: Optional[List[str]], brands: Optional[List[str]]):
    """모든 필터를 초기 상태로 리셋"""
    # 안전한 초기값 설정
    # categories 처리: None 체크 및 리스트 타입 확인
    if categories is not None and isinstance(categories, list) and len(categories) > 0:
        st.session_state.category_filter = categories.copy()
    else:
        st.session_state.category_filter = []
    
    # brands 처리: None 체크 및 리스트 타입 확인
    if brands is not None and isinstance(brands, list) and len(brands) > 0:
        st.session_state.brand_filter = brands.copy()
    else:
        st.session_state.brand_filter = []
    
    # 가격 범위 초기화
    if all_products_list and isinstance(all_products_list, list) and len(all_products_list) > 0:
        prices = [p.get("price", 0) for p in all_products_list if p.get("price") and p.get("price") > 0]
        if prices:
            st.session_state.price_range = (float(min(prices)), float(max(prices)))
        
        ratings = [p.get("rating_avg", 0) for p in all_products_list if p.get("rating_avg") and p.get("rating_avg") > 0]
        if ratings:
            st.session_state.rating_range = (float(min(ratings)), float(max(ratings)))
        
        review_counts = [p.get("rating_count", 0) for p in all_products_list if p.get("rating_count")]
        if review_counts:
            st.session_state.review_count_range = (int(min(review_counts)), int(max(review_counts)))
    
    # 기본 필터 값 설정
    st.session_state.trust_filter = ["HIGH", "MEDIUM", "LOW"]
    
    # 선택적 필터 초기화 (존재하는 경우에만)
    if 'search_query' in st.session_state:
        st.session_state.search_query = ""
    
    # 메인 브랜드 및 제품 초기화
    if 'main_brand' in st.session_state:
        st.session_state.main_brand = ""
    if 'main_product' in st.session_state:
        st.session_state.main_product = None
    if 'main_product_label' in st.session_state:
        st.session_state.main_product_label = ""
    if 'compare_products' in st.session_state:
        st.session_state.compare_products = []
    if 'compare_products_labels' in st.session_state:
        st.session_state.compare_products_labels = []
    
    # 등급 필터 초기화 (별 5등급으로 초기화)
    if 'price_grade' in st.session_state:
        st.session_state.price_grade = 5
    if 'rating_grade' in st.session_state:
        st.session_state.rating_grade = 5
    if 'review_grade' in st.session_state:
        st.session_state.review_grade = 5

try:
    from visualizations import (
        render_gauge_chart,
        render_trust_badge,
        render_comparison_table,
        render_radar_chart,
        render_review_sentiment_chart,
        render_checklist_visual,
        render_price_comparison_chart
    )
except ImportError as e:
    import traceback
    st.error(f"Visualizations import failed: {e}")
    print(f"[ERROR] Visualizations import failed: {e}")
    print(traceback.format_exc())
    raise

# 커스텀 CSS - UI/UX 디자인 시스템 적용
st.markdown("""
<link rel="stylesheet" as="style" crossorigin 
      href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ========== CSS 변수 정의 ========== */
:root {
  /* Primary Colors - 건강 & 신뢰 */
  --primary-50: #F0FDF4;
  --primary-100: #DCFCE7;
  --primary-500: #22C55E;
  --primary-600: #16A34A;
  --primary-700: #15803D;
  
  /* Secondary Colors - 신뢰감 있는 블루 */
  --secondary-500: #3B82F6;
  --secondary-600: #2563EB;
  --secondary-700: #1D4ED8;
  
  /* Neutral Colors */
  --gray-50: #FAFAFA;
  --gray-100: #F5F5F5;
  --gray-200: #E5E5E5;
  --gray-500: #737373;
  --gray-600: #525252;
  --gray-700: #404040;
  --gray-900: #171717;
  --white: #FFFFFF;
  --black: #0A0A0A;
  
  /* Status Colors */
  --success-500: #22C55E;
  --warning-500: #F59E0B;
  --error-500: #EF4444;
  --info-500: #3B82F6;
  
  /* Font */
  --font-primary: 'Pretendard', 'Inter', -apple-system,
                  BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR',
                  'Apple SD Gothic Neo', 'Malgun Gothic', '맑은 고딕',
                  sans-serif;
}

/* ========== 전역 스타일 ========== */
* {
  font-family: var(--font-primary);
}

/* ========== 메인 타이틀 ========== */
.main-title {
  font-family: var(--font-primary);
  font-size: clamp(2rem, 4vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
  color: var(--gray-900);
  text-align: center;
  margin-bottom: 2rem;
}

/* ========== 섹션 헤더 ========== */
.section-header {
  font-family: var(--font-primary);
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 600;
  line-height: 1.3;
  color: var(--primary-600);
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--primary-500);
}

/* ========== 메트릭 카드 ========== */
.metric-card {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-700) 100%);
  padding: 1.5rem;
  border-radius: 12px;
  color: var(--white);
  text-align: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.15);
}

/* ========== 리뷰 카드 ========== */
.review-card {
  background: var(--white);
  padding: 1.25rem;
  border-radius: 8px;
  border-left: 4px solid var(--secondary-500);
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s ease;
}

.review-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.ad-suspected {
  border-left-color: var(--error-500);
  background: #FEF2F2;
}

.verified-review {
  border-left-color: var(--success-500);
  background: #F0FDF4;
}

/* ========== 버튼 스타일 ========== */
.stButton > button {
  font-family: var(--font-primary);
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.stButton > button:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}

/* ========== 입력 필드 ========== */
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
  font-family: var(--font-primary);
  border-radius: 6px;
  border: 1px solid var(--gray-200);
  transition: border-color 0.2s ease;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > div:focus {
  border-color: var(--primary-500);
  outline: none;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

/* ========== 배지/태그 ========== */
.badge-success {
  background: var(--success-500);
  color: var(--white);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge-warning {
  background: var(--warning-500);
  color: var(--white);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge-error {
  background: var(--error-500);
  color: var(--white);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

/* ========== 사이드바 스타일 ========== */
[data-testid="stSidebar"] {
  background: var(--gray-50);
  border-right: 1px solid var(--gray-200);
}

/* ========== 탭 스타일 ========== */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}

.stTabs [data-baseweb="tab"] {
  font-family: var(--font-primary);
  font-weight: 500;
  padding: 0.75rem 1.5rem;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
  background: var(--primary-50);
  color: var(--primary-700);
  border-bottom: 2px solid var(--primary-500);
}

/* ========== 테이블 스타일 ========== */
.stDataFrame {
  font-family: var(--font-primary);
  border-radius: 8px;
  overflow: hidden;
}

.stDataFrame table {
  border-collapse: collapse;
}

.stDataFrame th {
  background: var(--gray-100);
  color: var(--gray-900);
  font-weight: 600;
  padding: 0.75rem 1rem;
  border-bottom: 2px solid var(--gray-200);
}

.stDataFrame td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--gray-200);
}

.stDataFrame tr:hover {
  background: var(--gray-50);
}

/* ========== 알림 메시지 ========== */
.stSuccess {
  background: var(--primary-50);
  border-left: 4px solid var(--success-500);
  color: var(--gray-900);
  border-radius: 6px;
  font-weight: 500;
}

.stWarning {
  background: #FFFBEB;
  border-left: 4px solid var(--warning-500);
  color: var(--gray-900);
  border-radius: 6px;
  font-weight: 500;
}

.stError {
  background: #FEF2F2;
  border-left: 4px solid var(--error-500);
  color: var(--gray-900);
  border-radius: 6px;
  font-weight: 500;
}

.stInfo {
  background: #EFF6FF;
  border-left: 4px solid var(--info-500);
  color: var(--gray-900);
  border-radius: 6px;
  font-weight: 500;
}

/* ========== 접근성 개선 (제안서 #4) ========== */
*:focus-visible {
  outline: 3px solid var(--primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 키보드 포커스 표시 개선 */
.stButton > button:focus,
.stSelectbox > div > div:focus,
.stMultiselect > div > div:focus,
.stTextInput > div > div > input:focus,
.stSlider > div > div:focus {
  outline: 3px solid var(--secondary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* 색상 대비 개선 (WCAG 2.1 AA 준수) */
.stSuccess {
  background-color: #10b981;
  color: #ffffff;
  border-left: 4px solid #059669;
}

.stWarning {
  background-color: #f59e0b;
  color: #ffffff;
  border-left: 4px solid #d97706;
}

.stError {
  background-color: #ef4444;
  color: #ffffff;
  border-left: 4px solid #dc2626;
}

.stInfo {
  background-color: #3b82f6;
  color: #ffffff;
  border-left: 4px solid #2563eb;
}

/* 필터 상태 카드 스타일 */
.filter-status-card {
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--primary-200);
  margin-bottom: 1rem;
}

.filter-status-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-700);
  font-size: 0.875rem;
  font-weight: 600;
}

.filter-status-card .filter-item {
  font-size: 0.75rem;
  color: var(--gray-600);
  margin: 0.25rem 0;
}

/* 필터 그룹 스타일 */
.filter-group {
  background: var(--white);
  padding: 1.25rem;
  border-radius: 8px;
  border: 1px solid var(--gray-200);
  margin-bottom: 1rem;
  transition: box-shadow 0.2s ease;
}

.filter-group:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--gray-700);
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 로딩 스피너 스타일 */
.stSpinner > div {
  border-color: var(--primary-500);
}
</style>
""", unsafe_allow_html=True)


def render_checklist_details(checklist_results: Dict) -> None:
    """체크리스트 상세 정보 표시"""
    checklist_items = {
        "1_verified_purchase": "인증 구매 비율",
        "2_reorder_rate": "재구매율",
        "3_long_term_use": "장기 사용 비율",
        "4_rating_distribution": "평점 분포 적절성",
        "5_review_length": "리뷰 길이",
        "6_time_distribution": "시간 분포 자연성",
        "7_ad_detection": "광고성 리뷰 탐지",
        "8_reviewer_diversity": "리뷰어 다양성"
    }
    
    for key, label in checklist_items.items():
        if key in checklist_results:
            result = checklist_results[key]
            status = "✅" if result.get("passed", False) else "❌"
            rate = result.get("rate", 0) * 100
            desc = result.get("description", "")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**{status} {label}**")
                st.progress(rate / 100)
            with col2:
                st.caption(f"{desc} ({rate:.1f}%)")


def render_rating_analysis(reviews: List[Dict], product_rating_avg: Optional[float] = None) -> None:
    """평점 분석 섹션"""
    if not reviews:
        st.warning("리뷰 데이터가 없습니다.")
        return
    
    # 평점 분포 계산
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating = review.get("rating", 5)
        if rating in rating_counts:
            rating_counts[rating] += 1
    
    total_reviews = len(reviews)
    avg_rating = sum(r.get("rating", 5) for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("평균 평점", f"{avg_rating:.2f}", f"{avg_rating - 3.0:.2f}")
    with col2:
        st.metric("총 리뷰 수", f"{total_reviews}개")
    with col3:
        if product_rating_avg:
            diff = avg_rating - product_rating_avg
            st.metric("제품 평균과 차이", f"{diff:+.2f}")
    
    # 평점 분포 차트
    import plotly.graph_objects as go
    fig = go.Figure(data=[
        go.Bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            marker_color=['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#22c55e'],
            text=[f"{count}개" for count in rating_counts.values()],
            textposition='auto'
        )
    ])
    fig.update_layout(
        title="평점 분포",
        xaxis_title="평점",
        yaxis_title="리뷰 수",
        height=300,
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_individual_review_analysis(reviews: List[Dict]) -> None:
    """개별 리뷰 분석 표시"""
    st.markdown("#### 📝 개별 리뷰 상세 분석")
    
    # 필터 옵션
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        rating_filter = st.multiselect(
            "평점 필터",
            options=[1, 2, 3, 4, 5],
            default=[1, 2, 3, 4, 5],
            key="rating_filter"
        )
    with col_f2:
        highlight_ads = st.checkbox("광고 의심 리뷰 하이라이트", value=True, key="highlight_ads")
    with col_f3:
        show_verified_only = st.checkbox("인증 구매만 보기", value=False, key="verified_only")
    
    # 리뷰 필터링
    filtered_reviews = [
        r for r in reviews
        if r.get("rating") in rating_filter
        and (not show_verified_only or r.get("verified", False))
    ]
    
    if not filtered_reviews:
        st.info("필터 조건에 맞는 리뷰가 없습니다.")
        return
    
    st.markdown(f"**총 {len(filtered_reviews)}개의 리뷰**")
    
    # 리뷰 카드 표시
    for idx, review in enumerate(filtered_reviews[:20]):  # 최대 20개만 표시
        rating = review.get("rating", 5)
        text = review.get("text", "")
        date = review.get("date", "")
        reviewer = review.get("reviewer", "익명")
        verified = review.get("verified", False)
        reorder = review.get("reorder", False)
        one_month = review.get("one_month_use", False)
        
        # 광고 의심 여부 (간단한 휴리스틱)
        is_ad_suspected = (
            rating == 5 and 
            not one_month and 
            len(text) < 100 and
            ("최고" in text or "대박" in text or "강력 추천" in text)
        )
        
        card_class = "review-card"
        if is_ad_suspected and highlight_ads:
            card_class += " ad-suspected"
        elif verified:
            card_class += " verified-review"
        
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns([3, 1])
        with col_r1:
            # 평점 표시
            stars = "⭐" * rating + "☆" * (5 - rating)
            st.markdown(f"**{stars} ({rating}/5)** | {reviewer} | {date}")
            
            # 배지
            badge_html = ""
            if verified:
                badge_html += '<span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">✓ 인증구매</span>'
            if reorder:
                badge_html += '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">🔄 재구매</span>'
            if one_month:
                badge_html += '<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 4px;">📅 1개월+</span>'
            if is_ad_suspected:
                badge_html += '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">⚠️ 광고 의심</span>'
            
            if badge_html:
                st.markdown(badge_html, unsafe_allow_html=True)
            
            # 리뷰 텍스트
            st.markdown(f"<p style='margin-top: 0.5rem;'>{text}</p>", unsafe_allow_html=True)
        
        with col_r2:
            # 통계 정보
            st.caption(f"길이: {len(text)}자")
            if is_ad_suspected:
                st.error("광고 의심")
        
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    """메인 앱 함수"""
    st.markdown('<div class="main-title">🔍 건기식 리뷰 팩트체크 시스템</div>', unsafe_allow_html=True)
    
    # 데이터 로드 - 캐싱된 데이터 사용 (성능 최적화)
    try:
        all_data = get_cached_analysis_results()
        if not all_data:
            st.error("⚠️ Supabase에서 데이터를 가져올 수 없습니다.")
            st.info("""
            **확인 사항:**
            1. `.streamlit/secrets.toml` 파일에 Supabase 설정이 있는지 확인
            2. Supabase 프로젝트가 활성화되어 있는지 확인
            3. 데이터베이스에 `products`와 `reviews` 테이블이 있는지 확인
            """)
            return
    except Exception as e:
        st.error(f"❌ Supabase 연결 실패: {e}")
        st.info("""
        **해결 방법:**
        1. `.streamlit/secrets.toml` 파일 확인:
           - 위치: 프로젝트 루트/.streamlit/secrets.toml
           - 내용: SUPABASE_URL과 SUPABASE_ANON_KEY 설정 확인
        
        2. Streamlit 앱 재시작
        
        3. Supabase 대시보드 확인:
           - https://supabase.com/dashboard/project/bvowxbpqtfpkkxkzsumf
        """)
        import traceback
        with st.expander("상세 에러 정보"):
            st.code(traceback.format_exc())
        return
    
    product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
    
    # 캐싱된 제품 목록 및 카테고리 가져오기 (성능 최적화)
    all_products_list = get_cached_products() or []
    categories_raw = get_cached_categories() or []
    # "카테고리"가 포함된 한국어 카테고리 제거
    categories = [c for c in categories_raw if "카테고리" not in c]
    brands = sorted(list(set(p.get("brand", "") for p in all_products_list if p.get("brand") and p.get("brand")))) if all_products_list else []
    
    # ========== 사이드바: 수직 정렬 구조 ==========
    with st.sidebar:
        # 제품검색 필터 (최상단 배치)
        st.markdown("### 🔎 제품 검색")
        search_query = st.text_input(
            "제품명/브랜드 검색",
            placeholder="예: NOW Foods, Lutein...",
            value=st.session_state.get('search_query', ''),
            key="search_query",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 필터 히스토리 되돌리기 버튼
        if 'filter_history' in st.session_state and len(st.session_state.filter_history) > 0:
            if st.button("↩️ 이전 필터로 되돌리기", use_container_width=True, type="secondary"):
                previous_state = restore_filter_state_from_history()
                if previous_state:
                    # 필터 상태 복원
                    if 'category_filter' in previous_state:
                        st.session_state.category_filter = previous_state['category_filter']
                    if 'main_brand' in previous_state:
                        st.session_state.main_brand = previous_state['main_brand']
                    if 'main_product' in previous_state:
                        st.session_state.main_product = previous_state['main_product']
                    if 'compare_products' in previous_state:
                        st.session_state.compare_products = previous_state['compare_products']
                    if 'price_range' in previous_state:
                        st.session_state.price_range = previous_state['price_range']
                    if 'rating_range' in previous_state:
                        st.session_state.rating_range = previous_state['rating_range']
                    if 'review_count_range' in previous_state:
                        st.session_state.review_count_range = previous_state['review_count_range']
                    if 'trust_filter' in previous_state:
                        st.session_state.trust_filter = previous_state['trust_filter']
                    if 'search_query' in previous_state:
                        st.session_state.search_query = previous_state['search_query']
                    if 'price_grade' in previous_state:
                        st.session_state.price_grade = previous_state['price_grade']
                    if 'rating_grade' in previous_state:
                        st.session_state.rating_grade = previous_state['rating_grade']
                    if 'review_grade' in previous_state:
                        st.session_state.review_grade = previous_state['review_grade']
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔍 제품 선택")
        
        # ========== 필터 상태 표시 (제안서 #1) ==========
        active_filters = []
        price_range = st.session_state.get('price_range')
        rating_range = st.session_state.get('rating_range')
        review_count_range = st.session_state.get('review_count_range')
        search_query = st.session_state.get('search_query', '').strip()
        
        if price_range:
            active_filters.append(f"가격: ${price_range[0]:.0f}-${price_range[1]:.0f}")
        if rating_range:
            active_filters.append(f"평점: {rating_range[0]:.1f}-{rating_range[1]:.1f}점")
        if review_count_range:
            active_filters.append(f"리뷰 수: {review_count_range[0]}-{review_count_range[1]}개")
        if search_query:
            active_filters.append(f"검색: {search_query}")
        
        if active_filters:
            st.info(f"🔍 활성 필터: {len(active_filters)}개")
            for f in active_filters[:3]:  # 최대 3개만 표시
                st.caption(f"  • {f}")
            if len(active_filters) > 3:
                st.caption(f"  ... 외 {len(active_filters) - 3}개")
            
            # 필터 초기화 버튼
            if st.button("🔄 필터 초기화", use_container_width=True, type="secondary", key="quick_reset_filters"):
                st.session_state.price_range = None
                st.session_state.rating_range = None
                st.session_state.review_count_range = None
                st.session_state.search_query = ""
                st.session_state.price_grade = 5
                st.session_state.rating_grade = 5
                st.session_state.review_grade = 5
                st.rerun()
        
        # 제품 선택 탭 구성
        product_select_tab1, product_select_tab2 = st.tabs(["📦 제품 선택", "⚙️ 필터 설정"])
        
        with product_select_tab1:
            # 브랜드 선택과 제품 선택만 진행 (카테고리 선택 제외)
            
            # 필터 값 가져오기 (제품 선택에 적용)
            price_range = st.session_state.get('price_range')
            rating_range = st.session_state.get('rating_range')
            review_count_range = st.session_state.get('review_count_range')
            search_query = st.session_state.get('search_query', '').strip()
            
            # 필터 변경 감지 (제품 선택 초기화용) - 필터가 실제로 변경되었을 때만
            current_filters = (
                price_range,
                rating_range,
                review_count_range,
                search_query
            )
            previous_filters = st.session_state.get('previous_filters')
            
            # 필터가 실제로 변경되었는지 확인
            filters_changed = False
            if previous_filters is None:
                filters_changed = True
                st.session_state.previous_filters = current_filters
            else:
                filters_changed = current_filters != previous_filters
                if filters_changed:
                    # 필터가 변경되면 제품 선택 초기화 (단, 필터가 더 제한적인 경우에만)
                    # 예: 가격 범위를 줄이면 선택된 제품이 범위 밖일 수 있음
                    main_product_id = st.session_state.get('main_product')
                    if main_product_id:
                        # 선택된 제품이 필터 조건에 맞는지 확인
                        # 먼저 필터링 전에 제품 찾기
                        main_product_data = next((p for p in all_products_list if p.get('id') == main_product_id), None)
                        if main_product_data:
                            # 필터 조건 확인
                            should_reset = False
                            if price_range and not (price_range[0] <= main_product_data.get("price", 0) <= price_range[1]):
                                should_reset = True
                            elif rating_range and not (rating_range[0] <= main_product_data.get("rating_avg", 0) <= rating_range[1]):
                                should_reset = True
                            elif review_count_range and not (review_count_range[0] <= main_product_data.get("rating_count", 0) <= review_count_range[1]):
                                should_reset = True
                            elif search_query:
                                search_lower = search_query.lower()
                                if search_lower not in main_product_data.get("name", "").lower() and search_lower not in main_product_data.get("brand", "").lower():
                                    should_reset = True
                            
                            if should_reset:
                                # 선택된 제품이 필터 조건에 맞지 않으면 초기화
                                if 'main_product' in st.session_state:
                                    st.session_state.main_product = None
                                if 'main_product_label' in st.session_state:
                                    st.session_state.main_product_label = ""
                                if 'main_brand' in st.session_state:
                                    st.session_state.main_brand = ""
                                if 'compare_products' in st.session_state:
                                    st.session_state.compare_products = []
                                if 'compare_products_labels' in st.session_state:
                                    st.session_state.compare_products_labels = []
                    st.session_state.previous_filters = current_filters
            
            # 필터링된 제품 목록 (제품 선택용) - 카테고리 필터 제외
            filtered_products = all_products_list.copy()
            
            # 가격 필터 적용
            if price_range:
                filtered_products = [
                    p for p in filtered_products
                    if price_range[0] <= p.get("price", 0) <= price_range[1]
                ]
            
            # 평점 필터 적용
            if rating_range:
                filtered_products = [
                    p for p in filtered_products
                    if rating_range[0] <= p.get("rating_avg", 0) <= rating_range[1]
                ]
            
            # 리뷰 수 필터 적용
            if review_count_range:
                filtered_products = [
                    p for p in filtered_products
                    if review_count_range[0] <= p.get("rating_count", 0) <= review_count_range[1]
                ]
            
            # 검색 필터 적용
            if search_query:
                search_lower = search_query.lower()
                filtered_products = [
                    p for p in filtered_products
                    if search_lower in p.get("name", "").lower() or search_lower in p.get("brand", "").lower()
                ]
            
            # 필터링된 브랜드 목록 (제품 선택용)
            filtered_brands = sorted(list(set(p.get("brand", "") for p in filtered_products if p.get("brand") and p.get("brand"))))
            
            # 2단계: 브랜드 1개(메인) 선택 - 항상 표시
            # 세션 상태의 브랜드가 필터링된 목록에 있는지 안전하게 확인
            current_main_brand = st.session_state.get('main_brand', '')
            safe_index = 0
            
            if filtered_brands:
                if current_main_brand and current_main_brand in filtered_brands:
                    try:
                        safe_index = filtered_brands.index(current_main_brand) + 1
                    except (ValueError, IndexError):
                        safe_index = 0
            else:
                # 필터링된 브랜드가 없으면 세션 상태 초기화
                if current_main_brand:
                    st.session_state.main_brand = ""
                    current_main_brand = ""
                if 'main_product' in st.session_state:
                    st.session_state.main_product = None
                if 'main_product_label' in st.session_state:
                    st.session_state.main_product_label = ""
            
            # 브랜드 선택 UI 항상 표시
            if filtered_brands:
                main_brand = st.selectbox(
                    "🏷️ 메인 브랜드 선택 (1개)",
                    options=[""] + filtered_brands,
                    index=safe_index,
                    key="main_brand"
                )
            else:
                # 필터링된 브랜드가 없을 때 안내 메시지와 함께 빈 selectbox 표시
                st.selectbox(
                    "🏷️ 메인 브랜드 선택 (1개)",
                    options=[""],
                    index=0,
                    key="main_brand",
                    disabled=True,
                    help="필터를 설정하면 브랜드 목록이 표시됩니다."
                )
                main_brand = ""
            
            # 브랜드 필터링된 제품 목록
            filtered_products_by_brand = filtered_products
            if main_brand:
                filtered_products_by_brand = [p for p in filtered_products if p.get("brand") == main_brand]
            
            # 제품 옵션 생성 (메인 브랜드 선택 시 브랜드명 제외, 그 외에는 브랜드 + 제품명)
            if main_brand:
                # 메인 브랜드가 선택된 경우: 제품명만 표시
                product_options_filtered = {p.get('name', ''): p.get('id') for p in filtered_products_by_brand}
                # 내부적으로는 브랜드+제품명으로 저장 (다른 곳에서 사용하기 위해)
                product_options_filtered_full = {f"{p.get('brand', '')} {p.get('name', '')}": p.get('id') for p in filtered_products_by_brand}
            else:
                # 메인 브랜드가 선택되지 않은 경우: 브랜드 + 제품명 표시
                product_options_filtered = {f"{p.get('brand', '')} {p.get('name', '')}": p.get('id') for p in filtered_products_by_brand}
                product_options_filtered_full = product_options_filtered
            
            # 3단계: 제품 1개(메인) 선택 - 항상 표시
            # 세션 상태의 제품 라벨 확인 (브랜드+제품명 형식으로 저장되어 있을 수 있음)
            current_main_product_label = st.session_state.get('main_product_label', '')
            safe_index = 0
            
            if product_options_filtered:
                # 현재 라벨이 표시용 옵션에 있는지 확인
                if current_main_product_label:
                    # 브랜드+제품명 형식인 경우 제품명만 추출
                    if main_brand and current_main_product_label.startswith(main_brand):
                        current_label_display = current_main_product_label.replace(f"{main_brand} ", "", 1)
                    else:
                        current_label_display = current_main_product_label
                    
                    if current_label_display in product_options_filtered.keys():
                        try:
                            safe_index = list(product_options_filtered.keys()).index(current_label_display) + 1
                        except (ValueError, IndexError):
                            safe_index = 0
                
                main_product_label_display = st.selectbox(
                    "📦 메인 제품 선택 (1개)",
                    options=[""] + list(product_options_filtered.keys()),
                    index=safe_index,
                    key="main_product_select"
                )
                
                # 선택된 제품 ID 찾기
                main_product = product_options_filtered.get(main_product_label_display) if main_product_label_display else None
                
                # 내부적으로는 브랜드+제품명 형식으로 저장
                if main_product and main_brand:
                    main_product_label = f"{main_brand} {main_product_label_display}"
                else:
                    main_product_label = main_product_label_display
                
                # 메인 제품이 변경되었는지 확인
                previous_main_product = st.session_state.get('main_product')
                main_product_changed = main_product != previous_main_product
                
                st.session_state.main_product = main_product
                st.session_state.main_product_label = main_product_label
                
                # 메인 제품이 선택되고 변경되었을 때 자동 추천 실행
                if main_product and main_product_changed:
                    # 비교 제품 목록 (필터링된 제품 목록에서 메인 제품 제외, 다른 브랜드 우선)
                    # 필터링된 제품 목록에서 비교 제품 후보 찾기
                    all_compare_options = {}
                    for p in filtered_products:
                        if p.get('id') != main_product:
                            if main_brand:
                                # 메인 브랜드가 선택된 경우: 다른 브랜드 제품은 브랜드+제품명으로 표시
                                compare_label = f"{p.get('brand', '')} {p.get('name', '')}"
                            else:
                                # 메인 브랜드가 선택되지 않은 경우: 브랜드+제품명으로 표시
                                compare_label = f"{p.get('brand', '')} {p.get('name', '')}"
                            all_compare_options[compare_label] = p.get('id')
                    
                    if all_compare_options:
                        # 자동 추천 로직: 다른 브랜드 제품 2개 추천
                        recommended_products = []
                        
                        # 메인 제품 정보 가져오기
                        main_product_data = next((p for p in filtered_products if p.get('id') == main_product), None)
                        
                        if main_product_data:
                            main_category = main_product_data.get('category', '')
                            main_brand_name = main_product_data.get('brand', '')
                            main_price = main_product_data.get('price', 0)
                            main_rating = main_product_data.get('rating_avg', 0)
                            
                            # 추천 점수 계산 (다른 브랜드 우선 > 같은 카테고리 > 비슷한 가격 > 비슷한 평점)
                            scored_products = []
                            for label, product_id in all_compare_options.items():
                                product_data = next((p for p in filtered_products if p.get('id') == product_id), None)
                                if product_data:
                                    score = 0
                                    # 다른 브랜드면 +20점 (우선순위 최상)
                                    if product_data.get('brand') != main_brand_name:
                                        score += 20
                                    # 같은 카테고리면 +10점
                                    if product_data.get('category') == main_category:
                                        score += 10
                                    # 같은 브랜드면 -10점 (페널티)
                                    if product_data.get('brand') == main_brand_name:
                                        score -= 10
                                    # 가격 차이가 작을수록 높은 점수 (차이 $10당 -1점)
                                    price_diff = abs(product_data.get('price', 0) - main_price)
                                    score += max(0, 5 - price_diff / 10)
                                    # 평점 차이가 작을수록 높은 점수 (차이 0.5당 -1점)
                                    rating_diff = abs(product_data.get('rating_avg', 0) - main_rating)
                                    score += max(0, 5 - rating_diff / 0.5)
                                    
                                    scored_products.append((score, label, product_id, product_data.get('brand', '')))
                            
                            # 점수 순으로 정렬하여 상위 2개 선택 (다른 브랜드 2개)
                            scored_products.sort(key=lambda x: x[0], reverse=True)
                            
                            # 다른 브랜드 제품 2개 선택
                            selected_brands = {main_brand_name}  # 메인 브랜드 제외
                            
                            for score, label, product_id, brand in scored_products:
                                if brand not in selected_brands:
                                    recommended_products.append(label)
                                    selected_brands.add(brand)
                                    if len(recommended_products) >= 2:
                                        break
                            
                            # 다른 브랜드 제품이 2개 미만이면 나머지 채우기
                            if len(recommended_products) < 2:
                                for score, label, product_id, brand in scored_products:
                                    if label not in recommended_products:
                                        recommended_products.append(label)
                                        if len(recommended_products) >= 2:
                                            break
                        
                        # 자동 추천된 제품으로 설정
                        if recommended_products:
                            st.session_state.compare_products_labels = recommended_products
                            st.session_state.compare_products = [all_compare_options[label] for label in recommended_products]
                            # 추천 제품 목록을 세션 상태에 저장 (이모지 표시용)
                            st.session_state.recommended_products_labels = recommended_products
                            st.success(f"✨ 비교 제품 자동 추천 (다른 브랜드): {', '.join(recommended_products)}")
            else:
                # 필터링된 제품이 없을 때 안내 메시지와 함께 빈 selectbox 표시
                st.selectbox(
                    "📦 메인 제품 선택 (1개)",
                    options=[""],
                    index=0,
                    key="main_product_select",
                    disabled=True,
                    help="브랜드를 선택하면 제품 목록이 표시됩니다."
                )
                main_product = None
                main_product_label = ""
                st.session_state.main_product = None
                st.session_state.main_product_label = ""
                # 제품이 없으면 비교 제품도 초기화
                if 'compare_products' in st.session_state:
                    st.session_state.compare_products = []
                if 'compare_products_labels' in st.session_state:
                    st.session_state.compare_products_labels = []
            
            # 비교 제품 선택은 메인 대시보드에서만 가능 (사이드바 제거)
            compare_products = st.session_state.get('compare_products', [])
            compare_products_labels = st.session_state.get('compare_products_labels', [])
        
        with product_select_tab2:
            st.markdown("### ⚙️ 필터 설정")
            st.caption("💡 필터를 설정하면 제품 선택 목록이 필터링됩니다. 원하는 조건에 맞는 제품만 표시됩니다.")
            
            # ========== 필터 적용 순서 시각화 (제안서 #2) ==========
            with st.expander("📋 필터 적용 순서", expanded=False):
                st.markdown("""
                **필터는 다음 순서로 적용됩니다:**
                
                1️⃣ **가격 범위** → 2️⃣ **평점 범위** → 3️⃣ **리뷰 수 범위** → 4️⃣ **검색어**
                
                모든 필터는 **AND 조건**으로 적용됩니다 (모든 조건을 만족하는 제품만 표시).
                """)
            
            # 필터 그룹화 (제안서 #2)
            with st.expander("💰 가격 및 평점 필터", expanded=True):
                # 가격 범위 필터 (별 1~5 등급으로 재설정)
                if all_products_list:
                    prices = [p.get("price", 0) for p in all_products_list if p.get("price") and p.get("price") > 0]
                    if prices:
                        prices_sorted = sorted(prices)
                        # 데이터를 5등급으로 분할
                        n = len(prices_sorted)
                        price_grade_1 = prices_sorted[0]  # 최소값
                        price_grade_2 = prices_sorted[n // 5] if n >= 5 else prices_sorted[n // 2]
                        price_grade_3 = prices_sorted[n * 2 // 5] if n >= 5 else prices_sorted[n * 2 // 3]
                        price_grade_4 = prices_sorted[n * 4 // 5] if n >= 5 else prices_sorted[n - 1]
                        price_grade_5 = prices_sorted[-1]  # 최대값
                        
                        # 별 1~5 등급 선택
                        price_grade = st.select_slider(
                            "💰 가격 등급",
                            options=[1, 2, 3, 4, 5],
                            value=st.session_state.get('price_grade', 5),
                            format_func=lambda x: f"⭐{x}등급",
                            key="price_grade",
                            help="가격 범위를 5등급으로 나누어 선택합니다. 등급이 높을수록 더 넓은 가격 범위를 포함합니다."
                        )
                        # 등급에 따른 실제 가격 범위 계산
                        if price_grade == 1:
                            price_range = (float(price_grade_1), float(price_grade_2))
                        elif price_grade == 2:
                            price_range = (float(price_grade_1), float(price_grade_3))
                        elif price_grade == 3:
                            price_range = (float(price_grade_1), float(price_grade_4))
                        elif price_grade == 4:
                            price_range = (float(price_grade_1), float(price_grade_5))
                        else:  # 5
                            price_range = (float(price_grade_1), float(price_grade_5))
                        st.session_state.price_range = price_range
                        st.caption(f"가격 범위: ${price_range[0]:.2f} ~ ${price_range[1]:.2f}")
                
                # 평점 범위 필터 (별 1~5 등급으로 재설정)
                if all_products_list:
                    ratings = [p.get("rating_avg", 0) for p in all_products_list if p.get("rating_avg") and p.get("rating_avg") > 0]
                    if ratings:
                        ratings_sorted = sorted(ratings)
                        # 데이터를 5등급으로 분할
                        n = len(ratings_sorted)
                        rating_grade_1 = ratings_sorted[0]  # 최소값
                        rating_grade_2 = ratings_sorted[n // 5] if n >= 5 else ratings_sorted[n // 2]
                        rating_grade_3 = ratings_sorted[n * 2 // 5] if n >= 5 else ratings_sorted[n * 2 // 3]
                        rating_grade_4 = ratings_sorted[n * 4 // 5] if n >= 5 else ratings_sorted[n - 1]
                        rating_grade_5 = ratings_sorted[-1]  # 최대값
                        
                        # 별 1~5 등급 선택
                        rating_grade = st.select_slider(
                            "⭐ 평점 등급",
                            options=[1, 2, 3, 4, 5],
                            value=st.session_state.get('rating_grade', 5),
                            format_func=lambda x: f"⭐{x}등급",
                            key="rating_grade",
                            help="평점 범위를 5등급으로 나누어 선택합니다. 등급이 높을수록 더 넓은 평점 범위를 포함합니다."
                        )
                        # 등급에 따른 실제 평점 범위 계산
                        if rating_grade == 1:
                            rating_range = (float(rating_grade_1), float(rating_grade_2))
                        elif rating_grade == 2:
                            rating_range = (float(rating_grade_1), float(rating_grade_3))
                        elif rating_grade == 3:
                            rating_range = (float(rating_grade_1), float(rating_grade_4))
                        elif rating_grade == 4:
                            rating_range = (float(rating_grade_1), float(rating_grade_5))
                        else:  # 5
                            rating_range = (float(rating_grade_1), float(rating_grade_5))
                        st.session_state.rating_range = rating_range
                        st.caption(f"평점 범위: {rating_range[0]:.1f} ~ {rating_range[1]:.1f}점")
                
                # 리뷰 수 필터 (별 1~5 등급으로 재설정)
                if all_products_list:
                    review_counts = [p.get("rating_count", 0) for p in all_products_list if p.get("rating_count")]
                    if review_counts:
                        reviews_sorted = sorted(review_counts)
                        # 데이터를 5등급으로 분할
                        n = len(reviews_sorted)
                        review_grade_1 = reviews_sorted[0]  # 최소값
                        review_grade_2 = reviews_sorted[n // 5] if n >= 5 else reviews_sorted[n // 2]
                        review_grade_3 = reviews_sorted[n * 2 // 5] if n >= 5 else reviews_sorted[n * 2 // 3]
                        review_grade_4 = reviews_sorted[n * 4 // 5] if n >= 5 else reviews_sorted[n - 1]
                        review_grade_5 = reviews_sorted[-1]  # 최대값
                        
                        # 별 1~5 등급 선택
                        review_grade = st.select_slider(
                            "💬 리뷰 수 등급",
                            options=[1, 2, 3, 4, 5],
                            value=st.session_state.get('review_grade', 5),
                            format_func=lambda x: f"⭐{x}등급",
                            key="review_grade",
                            help="리뷰 수 범위를 5등급으로 나누어 선택합니다. 등급이 높을수록 더 많은 리뷰를 가진 제품을 포함합니다."
                        )
                        # 등급에 따른 실제 리뷰 수 범위 계산
                        if review_grade == 1:
                            review_count_range = (int(review_grade_1), int(review_grade_2))
                        elif review_grade == 2:
                            review_count_range = (int(review_grade_1), int(review_grade_3))
                        elif review_grade == 3:
                            review_count_range = (int(review_grade_1), int(review_grade_4))
                        elif review_grade == 4:
                            review_count_range = (int(review_grade_1), int(review_grade_5))
                        else:  # 5
                            review_count_range = (int(review_grade_1), int(review_grade_5))
                        st.session_state.review_count_range = review_count_range
                        st.caption(f"리뷰 수 범위: {review_count_range[0]} ~ {review_count_range[1]}개")
            
            # 고급 필터 그룹
            with st.expander("🔍 고급 필터", expanded=False):
                # 신뢰도 필터
                trust_filter = st.multiselect(
                    "🎯 신뢰도 등급",
                    options=["HIGH", "MEDIUM", "LOW"],
                    default=st.session_state.get('trust_filter', ["HIGH", "MEDIUM", "LOW"]),
                    key="trust_filter",
                    help="제품의 신뢰도 등급으로 필터링합니다. HIGH/MEDIUM/LOW 중 선택할 수 있습니다."
                )
            
            st.markdown("---")
            
            # ========== 필터 도움말 (제안서 #9) ==========
            with st.expander("❓ 필터 사용 가이드", expanded=False):
                st.markdown("""
                ### 💰 가격 등급 필터
                제품의 가격 범위를 5등급으로 나누어 필터링합니다. 등급이 높을수록 더 넓은 가격 범위를 포함합니다.
                
                ### ⭐ 평점 등급 필터
                제품의 평균 평점 범위를 5등급으로 나누어 필터링합니다. 등급이 높을수록 더 넓은 평점 범위를 포함합니다.
                
                ### 💬 리뷰 수 등급 필터
                제품의 리뷰 수 범위를 5등급으로 나누어 필터링합니다. 등급이 높을수록 더 많은 리뷰를 가진 제품을 포함합니다.
                
                ### 🎯 신뢰도 등급 필터
                제품의 신뢰도 등급(HIGH/MEDIUM/LOW)으로 필터링합니다. 여러 등급을 선택할 수 있습니다.
                
                ### 💡 사용 팁
                - 필터를 조합하여 원하는 제품을 빠르게 찾을 수 있습니다
                - "필터 초기화" 버튼으로 모든 필터를 한 번에 해제할 수 있습니다
                - 필터 결과는 실시간으로 업데이트됩니다
                - 모든 필터는 AND 조건으로 적용됩니다 (모든 조건을 만족하는 제품만 표시)
                """)
            
            # 필터 관리 버튼
            col_reset, col_save = st.columns(2)
            with col_reset:
                if st.button("🔄 초기화", use_container_width=True, type="secondary", key="reset_filters"):
                    # 안전한 초기화: None 체크 후 전달
                    safe_categories = categories if (categories is not None and isinstance(categories, list)) else []
                    safe_brands = brands if (brands is not None and isinstance(brands, list)) else []
                    safe_products = all_products_list if (all_products_list is not None and isinstance(all_products_list, list)) else []
                    reset_all_filters(safe_products, safe_categories, safe_brands)
                    st.rerun()
            with col_save:
                if st.button("💾 저장", use_container_width=True, type="secondary", key="save_filters"):
                    current_filters = {
                        'category_filter': st.session_state.get('category_filter', []),
                        'main_brand': st.session_state.get('main_brand', ''),
                        'main_product': st.session_state.get('main_product', None),
                        'compare_products': st.session_state.get('compare_products', []),
                        'price_range': st.session_state.get('price_range', None),
                        'price_grade': st.session_state.get('price_grade', 5),
                        'rating_range': st.session_state.get('rating_range', None),
                        'rating_grade': st.session_state.get('rating_grade', 5),
                        'review_count_range': st.session_state.get('review_count_range', None),
                        'review_grade': st.session_state.get('review_grade', 5),
                        'trust_filter': st.session_state.get('trust_filter', []),
                        'search_query': st.session_state.get('search_query', '')
                    }
                    save_filter_state_to_history(current_filters)
                    st.success("저장 완료!")
        
        # 비교 제품 선택은 메인 대시보드에서만 가능 (사이드바 제거)
        compare_products = st.session_state.get('compare_products', [])
        compare_products_labels = st.session_state.get('compare_products_labels', [])
        
        st.markdown("---")
        st.markdown("### 📊 실시간 통계")
        
        # 필터링된 제품 목록 기반 통계 계산
        try:
            # 현재 적용된 필터로 제품 필터링
            filtered_stats_products = all_products_list.copy()
            
            # 가격 필터 적용
            price_range = st.session_state.get('price_range')
            if price_range:
                filtered_stats_products = [
                    p for p in filtered_stats_products
                    if price_range[0] <= p.get("price", 0) <= price_range[1]
                ]
            
            # 평점 필터 적용
            rating_range = st.session_state.get('rating_range')
            if rating_range:
                filtered_stats_products = [
                    p for p in filtered_stats_products
                    if rating_range[0] <= p.get("rating_avg", 0) <= rating_range[1]
                ]
            
            # 리뷰 수 필터 적용
            review_count_range = st.session_state.get('review_count_range')
            if review_count_range:
                filtered_stats_products = [
                    p for p in filtered_stats_products
                    if review_count_range[0] <= p.get("rating_count", 0) <= review_count_range[1]
                ]
            
            # 검색 필터 적용
            search_query = st.session_state.get('search_query', '').strip()
            if search_query:
                search_lower = search_query.lower()
                filtered_stats_products = [
                    p for p in filtered_stats_products
                    if search_lower in p.get("name", "").lower() or search_lower in p.get("brand", "").lower()
                ]
            
            # 필터링된 제품 기반 통계 계산
            filtered_total_products = len(filtered_stats_products)
            filtered_total_reviews = sum(p.get("rating_count", 0) for p in filtered_stats_products)
            filtered_prices = [p.get("price", 0) for p in filtered_stats_products if p.get("price") and p.get("price") > 0]
            filtered_avg_price = sum(filtered_prices) / len(filtered_prices) if filtered_prices else 0
            
            # 필터링된 통계 표시
            st.metric("필터링된 제품 수", f"{filtered_total_products}개")
            st.metric("필터링된 리뷰 수", f"{filtered_total_reviews}개")
            st.metric("평균 가격", f"${filtered_avg_price:.2f}")
            
            st.markdown("---")
            
            # 전체 통계도 함께 표시 (참고용)
            stats = get_cached_statistics()
            with st.expander("📊 전체 통계 (참고)"):
                st.metric("전체 제품 수", f"{stats.get('total_products', 0)}개")
                st.metric("전체 리뷰 수", f"{stats.get('total_reviews', 0)}개")
                st.metric("전체 평균 가격", f"${stats.get('avg_price', 0):.2f}")
            
            st.markdown("---")
            
            # 필터링된 브랜드별 통계
            st.markdown("### 🏷️ 브랜드별 통계 (필터링됨)")
            filtered_brand_stats = {}
            for p in filtered_stats_products:
                brand = p.get('brand', 'Unknown')
                if brand not in filtered_brand_stats:
                    filtered_brand_stats[brand] = {'count': 0, 'total_rating': 0, 'total_reviews': 0}
                filtered_brand_stats[brand]['count'] += 1
                if p.get('rating_avg'):
                    filtered_brand_stats[brand]['total_rating'] += p.get('rating_avg', 0)
                if p.get('rating_count'):
                    filtered_brand_stats[brand]['total_reviews'] += p.get('rating_count', 0)
            
            if filtered_brand_stats:
                for brand, data in sorted(filtered_brand_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
                    avg_rating = data['total_rating'] / data['count'] if data['count'] > 0 else 0
                    st.markdown(f"**{brand}**")
                    st.caption(f"제품: {data['count']}개 | 평균 평점: {avg_rating:.1f} | 리뷰: {data['total_reviews']}개")
            else:
                st.info("필터 조건에 맞는 브랜드가 없습니다.")
            
            st.markdown("---")
            
            # 필터링된 카테고리별 통계
            st.markdown("### 📂 카테고리별 통계 (필터링됨)")
            filtered_category_stats = {}
            for p in filtered_stats_products:
                category = p.get('category', 'Unknown')
                if category not in filtered_category_stats:
                    filtered_category_stats[category] = {'count': 0}
                filtered_category_stats[category]['count'] += 1
            
            if filtered_category_stats:
                for category, data in sorted(filtered_category_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
                    st.markdown(f"**{category}**")
                    st.caption(f"제품: {data['count']}개")
            else:
                st.info("필터 조건에 맞는 카테고리가 없습니다.")
            
            st.markdown("---")
            
            # 평점 분포 (필터링된 제품의 평점 분포)
            st.markdown("### ⭐ 평점 분포 (필터링됨)")
            filtered_rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for p in filtered_stats_products:
                rating_avg = p.get('rating_avg', 0)
                if rating_avg:
                    # 평균 평점을 가장 가까운 정수로 반올림
                    rounded_rating = round(rating_avg)
                    if 1 <= rounded_rating <= 5:
                        filtered_rating_dist[rounded_rating] += 1
            
            if filtered_rating_dist:
                total_ratings = sum(filtered_rating_dist.values())
                if total_ratings > 0:
                    rating_df = pd.DataFrame({
                        '평점': [f"{k}점" for k in filtered_rating_dist.keys()],
                        '제품 수': list(filtered_rating_dist.values())
                    })
                    st.bar_chart(rating_df.set_index('평점'))
                else:
                    st.info("필터 조건에 맞는 평점 데이터가 없습니다.")
            else:
                st.info("필터 조건에 맞는 평점 데이터가 없습니다.")
                for rating in [5, 4, 3, 2, 1]:
                    count = rating_dist.get(rating, 0)
                    percentage = (count / total_ratings * 100) if total_ratings > 0 else 0
                    st.progress(percentage / 100, text=f"{rating}점: {count}개 ({percentage:.1f}%)")
            
        except Exception as e:
            st.error(f"통계 로드 실패: {e}")
            # Fallback: 기존 방식
            total_products = len(all_data)
            total_reviews = sum(len(data.get("reviews", [])) for data in all_data.values())
            avg_trust = sum(data.get("ai_result", {}).get("trust_score", 0) for data in all_data.values()) / total_products if total_products > 0 else 0
            
            st.metric("전체 제품 수", f"{total_products}개")
            st.metric("전체 리뷰 수", f"{total_reviews}개")
            st.metric("평균 신뢰도", f"{avg_trust:.1f}점")
    
    # 제품 선택 검증 (새로운 구조)
    main_product = st.session_state.get('main_product')
    compare_products = st.session_state.get('compare_products', [])
    main_brand = st.session_state.get('main_brand', '')
    
    if not main_product:
        st.warning("메인 제품을 선택해주세요.")
        return
    
    # 비교 제품이 2개 미만이면 자동으로 추가 추천 (다른 브랜드 우선)
    if len(compare_products) < 2:
        # 필터링된 제품 목록 재구성
        category_filter = st.session_state.get('category_filter', [])
        # 필터링된 제품 목록 (카테고리 필터 제외)
        filtered_products_for_compare = all_products_list.copy()
        
        # 가격, 평점, 리뷰 수, 검색 필터 적용
        price_range = st.session_state.get('price_range')
        rating_range = st.session_state.get('rating_range')
        review_count_range = st.session_state.get('review_count_range')
        search_query = st.session_state.get('search_query', '').strip()
        
        if price_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if price_range[0] <= p.get("price", 0) <= price_range[1]
            ]
        if rating_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if rating_range[0] <= p.get("rating_avg", 0) <= rating_range[1]
            ]
        if review_count_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if review_count_range[0] <= p.get("rating_count", 0) <= review_count_range[1]
            ]
        if search_query:
            search_lower = search_query.lower()
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if search_lower in p.get("name", "").lower() or search_lower in p.get("brand", "").lower()
            ]
        
        # 비교 제품은 필터링된 제품에서 선택 (다른 브랜드 우선)
        compare_options = {}
        for p in filtered_products_for_compare:
            if p.get('id') != main_product and p.get('id') not in compare_products:
                compare_label = f"{p.get('brand', '')} {p.get('name', '')}"
                compare_options[compare_label] = p.get('id')
        
        if compare_options:
            # 메인 제품 정보 가져오기
            main_product_data = next((p for p in filtered_products_for_compare if p.get('id') == main_product), None)
            
            if main_product_data:
                main_category = main_product_data.get('category', '')
                main_brand_name = main_product_data.get('brand', '')
                main_price = main_product_data.get('price', 0)
                main_rating = main_product_data.get('rating_avg', 0)
                
                # 추천 점수 계산 (다른 브랜드 우선)
                scored_products = []
                for label, product_id in compare_options.items():
                    product_data = next((p for p in filtered_products_for_compare if p.get('id') == product_id), None)
                    if product_data:
                        score = 0
                        # 다른 브랜드면 +20점 (우선순위 최상)
                        if product_data.get('brand') != main_brand_name:
                            score += 20
                        # 같은 카테고리면 +10점
                        if product_data.get('category') == main_category:
                            score += 10
                        # 같은 브랜드면 -10점 (페널티)
                        if product_data.get('brand') == main_brand_name:
                            score -= 10
                        price_diff = abs(product_data.get('price', 0) - main_price)
                        score += max(0, 5 - price_diff / 10)
                        rating_diff = abs(product_data.get('rating_avg', 0) - main_rating)
                        score += max(0, 5 - rating_diff / 0.5)
                        scored_products.append((score, label, product_id, product_data.get('brand', '')))
                
                # 점수 순으로 정렬
                scored_products.sort(key=lambda x: x[0], reverse=True)
                
                # 다른 브랜드 제품 우선 선택
                needed_count = 2 - len(compare_products)
                additional_recommended = []
                selected_brands = {main_brand_name}
                # 이미 선택된 비교 제품의 브랜드도 제외
                for cp_id in compare_products:
                    cp_data = next((p for p in filtered_products_for_compare if p.get('id') == cp_id), None)
                    if cp_data:
                        selected_brands.add(cp_data.get('brand', ''))
                
                for score, label, product_id, brand in scored_products:
                    if brand not in selected_brands:
                        additional_recommended.append(label)
                        selected_brands.add(brand)
                        if len(additional_recommended) >= needed_count:
                            break
                
                # 다른 브랜드 제품이 부족하면 나머지 채우기
                if len(additional_recommended) < needed_count:
                    for score, label, product_id, brand in scored_products:
                        if label not in additional_recommended:
                            additional_recommended.append(label)
                            if len(additional_recommended) >= needed_count:
                                break
                
                if additional_recommended:
                    compare_products.extend([compare_options[label] for label in additional_recommended])
                    compare_products_labels = st.session_state.get('compare_products_labels', [])
                    compare_products_labels.extend(additional_recommended)
                    st.session_state.compare_products = compare_products
                    st.session_state.compare_products_labels = compare_products_labels
                    # 추천 제품 목록 업데이트
                    recommended_list = st.session_state.get('recommended_products_labels', [])
                    recommended_list.extend(additional_recommended)
                    st.session_state.recommended_products_labels = list(set(recommended_list))  # 중복 제거
    
    # 선택된 제품 목록 구성 (메인 + 비교 제품)
    # 세션 상태에서 비교 제품 가져오기
    compare_products = st.session_state.get('compare_products', [])
    compare_products_labels = st.session_state.get('compare_products_labels', [])
    
    selected_product_ids = [main_product] + compare_products[:2]  # 최대 2개만 사용
    selected_labels = []
    for product_id in selected_product_ids:
        for label, pid in product_options.items():
            if pid == product_id:
                selected_labels.append(label)
                break
    
    if not selected_labels:
        st.warning("선택된 제품을 찾을 수 없습니다.")
        return
    
    # 제품 선택 완료 시 자동으로 분석 실행
    if len(selected_labels) >= 1:  # 메인 제품만 선택되어도 분석 실행
        # 선택된 제품 데이터 가져오기 (all_data에 없으면 직접 조회)
        selected_data = []
        for label in selected_labels:
            if label in product_options:
                product_id = product_options[label]
                
                # all_data에 있으면 가져오기
                if product_id in all_data:
                    selected_data.append(all_data[product_id])
                else:
                    # all_data에 없으면 직접 조회 (비교 제품이 자동 추천된 경우)
                    try:
                        # 제품 정보 찾기
                        product_data = next((p for p in all_products_list if p.get('id') == product_id), None)
                        if product_data:
                            # 리뷰 조회
                            reviews = get_reviews_by_product(product_id)
                            # 체크리스트 생성
                            checklist = generate_checklist_results(reviews)
                            # AI 분석 생성
                            ai_result = generate_ai_analysis(product_data, checklist)
                            
                            # 데이터 구조 생성 및 추가
                            data_entry = {
                                "product": product_data,
                                "reviews": reviews,
                                "checklist_results": checklist,
                                "ai_result": ai_result
                            }
                            selected_data.append(data_entry)
                            # all_data에도 추가 (다음 사용을 위해)
                            all_data[product_id] = data_entry
                    except Exception as e:
                        st.error(f"제품 데이터 조회 실패 ({label}): {e}")
                        continue
        
        if not selected_data:
            st.warning("선택된 제품 데이터를 찾을 수 없습니다.")
            return
        
        # 제품 선택 완료 안내
        if len(selected_labels) >= 3:  # 메인 1개 + 비교 2개
            st.success(f"🎯 제품 선택 완료! {len(selected_data)}개 제품 리뷰 팩트체크 분석 시작!")
        else:
            st.info(f"📦 메인 제품 선택됨. 비교 제품을 추가하면 더 자세한 분석이 가능합니다.")
        
        st.markdown("---")
    else:
        selected_data = []
    
    # ========== 메인 영역: 리뷰 팩트체크 시스템 차트 표시 ==========
    # 메인 제품 선택 시 바로 차트 표시
    
    # 제품 선택 요약
    st.markdown('<div class="section-header">📊 리뷰 팩트체크 시스템</div>', unsafe_allow_html=True)
    
    # selected_data가 없으면 여기서 종료
    if not selected_data or len(selected_data) == 0:
        st.info("📦 제품을 선택하면 분석 결과가 표시됩니다.")
        return
    
    st.markdown("### 🎯 선택된 제품")
    
    # 비교 제품 옵션 구성 (메인 제품이 있을 때만)
    compare_options = {}
    compare_options_with_emoji = {}
    if main_product:
        # 필터 적용하여 비교 제품 목록 구성
        category_filter = st.session_state.get('category_filter', [])
        price_range = st.session_state.get('price_range')
        rating_range = st.session_state.get('rating_range')
        review_count_range = st.session_state.get('review_count_range')
        search_query = st.session_state.get('search_query', '').strip()
        
        # 필터링된 제품 목록 (카테고리 필터 제외)
        filtered_products_for_compare = all_products_list.copy()
        
        # 가격 필터 적용
        if price_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if price_range[0] <= p.get("price", 0) <= price_range[1]
            ]
        
        # 평점 필터 적용
        if rating_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if rating_range[0] <= p.get("rating_avg", 0) <= rating_range[1]
            ]
        
        # 리뷰 수 필터 적용
        if review_count_range:
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if review_count_range[0] <= p.get("rating_count", 0) <= review_count_range[1]
            ]
        
        # 검색 필터 적용
        if search_query:
            search_lower = search_query.lower()
            filtered_products_for_compare = [
                p for p in filtered_products_for_compare
                if search_lower in p.get("name", "").lower() or search_lower in p.get("brand", "").lower()
            ]
        
        for p in filtered_products_for_compare:
            if p.get('id') != main_product:
                compare_label = f"{p.get('brand', '')} {p.get('name', '')}"
                compare_options[compare_label] = p.get('id')
        
        # 추천 제품 목록 가져오기
        recommended_products_labels = st.session_state.get('recommended_products_labels', [])
        
        # 비교 제품 옵션에 추천 이모지 추가
        for label in compare_options.keys():
            if label in recommended_products_labels:
                compare_options_with_emoji[f"⭐ {label} (추천)"] = compare_options[label]
            else:
                compare_options_with_emoji[label] = compare_options[label]
    
    col_summary1, col_summary2, col_summary3 = st.columns(3)
    with col_summary1:
        st.info(f"**메인 제품**: {selected_labels[0] if selected_labels else '없음'}")
    
    with col_summary2:
        # 비교 제품 1 선택
        if main_product and compare_options_with_emoji:
            current_compare_labels = st.session_state.get('compare_products_labels', [])
            compare1_label = current_compare_labels[0] if len(current_compare_labels) > 0 else ""
            
            # 현재 선택된 제품의 표시 라벨 찾기
            compare1_display = ""
            if compare1_label:
                if compare1_label in recommended_products_labels:
                    compare1_display = f"⭐ {compare1_label} (추천)"
                else:
                    compare1_display = compare1_label
            
            # 비교 제품 1 선택 (selectbox)
            compare1_options = [""] + list(compare_options_with_emoji.keys())
            compare1_index = 0
            if compare1_display and compare1_display in compare1_options:
                compare1_index = compare1_options.index(compare1_display)
            
            selected_compare1_display = st.selectbox(
                "**비교 제품 1**",
                options=compare1_options,
                index=compare1_index,
                key="compare_product_1_select"
            )
            
            # 선택된 제품에서 이모지 제거하여 실제 라벨 추출
            if selected_compare1_display:
                if selected_compare1_display.startswith("⭐ "):
                    actual_label = selected_compare1_display.replace("⭐ ", "").replace(" (추천)", "")
                else:
                    actual_label = selected_compare1_display
                
                if actual_label in compare_options:
                    # 세션 상태 업데이트
                    current_compare_labels = st.session_state.get('compare_products_labels', [])
                    # 비교 제품 2와 중복 체크
                    if len(current_compare_labels) > 1 and current_compare_labels[1] == actual_label:
                        # 비교 제품 2와 같으면 비교 제품 2 제거
                        current_compare_labels = [actual_label]
                    else:
                        if len(current_compare_labels) == 0:
                            current_compare_labels = [actual_label]
                        else:
                            current_compare_labels[0] = actual_label
                    # 변경사항이 있을 때만 업데이트
                    old_labels = st.session_state.get('compare_products_labels', [])
                    if set(current_compare_labels[:2]) != set(old_labels):
                        st.session_state.compare_products_labels = current_compare_labels[:2]  # 최대 2개
                        st.session_state.compare_products = [compare_options[label] for label in st.session_state.compare_products_labels if label in compare_options]
                        # 비교 제품 선택 시 자동으로 차트 업데이트
                        st.rerun()
            else:
                # 선택 해제
                current_compare_labels = st.session_state.get('compare_products_labels', [])
                if len(current_compare_labels) > 0:
                    new_labels = current_compare_labels[1:] if len(current_compare_labels) > 1 else []
                    if set(new_labels) != set(current_compare_labels):
                        st.session_state.compare_products_labels = new_labels
                        st.session_state.compare_products = [compare_options[label] for label in new_labels if label in compare_options]
                        # 비교 제품 해제 시 자동으로 차트 업데이트
                        st.rerun()
        else:
            if len(selected_labels) > 1:
                st.success(f"**비교 제품 1**: {selected_labels[1]}")
            else:
                st.caption("비교 제품 미선택")
    
    with col_summary3:
        # 비교 제품 2 선택
        if main_product and compare_options_with_emoji:
            current_compare_labels = st.session_state.get('compare_products_labels', [])
            compare2_label = current_compare_labels[1] if len(current_compare_labels) > 1 else ""
            
            # 현재 선택된 제품의 표시 라벨 찾기
            compare2_display = ""
            if compare2_label:
                recommended_products_labels = st.session_state.get('recommended_products_labels', [])
                if compare2_label in recommended_products_labels:
                    compare2_display = f"⭐ {compare2_label} (추천)"
                else:
                    compare2_display = compare2_label
            
            # 비교 제품 2 선택 (selectbox)
            compare2_options = [""] + list(compare_options_with_emoji.keys())
            # 비교 제품 1과 중복 제거
            if len(current_compare_labels) > 0 and current_compare_labels[0] in compare_options:
                compare1_actual = current_compare_labels[0]
                compare2_options = [""] + [opt for opt in compare_options_with_emoji.keys() 
                                          if not (opt.startswith("⭐ ") and opt.replace("⭐ ", "").replace(" (추천)", "") == compare1_actual)
                                          and not (not opt.startswith("⭐ ") and opt == compare1_actual)]
            
            compare2_index = 0
            if compare2_display and compare2_display in compare2_options:
                compare2_index = compare2_options.index(compare2_display)
            
            selected_compare2_display = st.selectbox(
                "**비교 제품 2**",
                options=compare2_options,
                index=compare2_index,
                key="compare_product_2_select"
            )
            
            # 선택된 제품에서 이모지 제거하여 실제 라벨 추출
            if selected_compare2_display:
                if selected_compare2_display.startswith("⭐ "):
                    actual_label = selected_compare2_display.replace("⭐ ", "").replace(" (추천)", "")
                else:
                    actual_label = selected_compare2_display
                
                if actual_label in compare_options:
                    # 세션 상태 업데이트
                    current_compare_labels = st.session_state.get('compare_products_labels', [])
                    # 비교 제품 1과 중복 체크
                    if len(current_compare_labels) > 0 and current_compare_labels[0] == actual_label:
                        # 비교 제품 1과 같으면 선택 불가 (이미 필터링됨)
                        pass
                    else:
                        if len(current_compare_labels) < 2:
                            current_compare_labels.append(actual_label)
                        else:
                            current_compare_labels[1] = actual_label
                        # 변경사항이 있을 때만 업데이트
                        old_labels = st.session_state.get('compare_products_labels', [])
                        if set(current_compare_labels[:2]) != set(old_labels):
                            st.session_state.compare_products_labels = current_compare_labels[:2]  # 최대 2개
                            st.session_state.compare_products = [compare_options[label] for label in st.session_state.compare_products_labels if label in compare_options]
                            # 비교 제품 선택 시 자동으로 차트 업데이트
                            st.rerun()
            else:
                # 선택 해제
                current_compare_labels = st.session_state.get('compare_products_labels', [])
                if len(current_compare_labels) > 1:
                    new_labels = current_compare_labels[:1]
                    if set(new_labels) != set(current_compare_labels):
                        st.session_state.compare_products_labels = new_labels
                        st.session_state.compare_products = [compare_options[label] for label in new_labels if label in compare_options]
                        # 비교 제품 해제 시 자동으로 차트 업데이트
                        st.rerun()
        else:
            if len(selected_labels) > 2:
                st.success(f"**비교 제품 2**: {selected_labels[2]}")
            else:
                st.caption("비교 제품 미선택")
    
    st.markdown("---")
    
    # 메인 대시보드: 차트 중심 표시
    if selected_data and len(selected_data) > 0:
        st.markdown("### 📈 시각화 분석 차트")
        
        # 레이더 차트와 가격 비교를 더 크게 표시
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("#### 🕸️ 다차원 비교 (레이더 차트)")
            st.caption("신뢰도, 재구매율, 장기사용, 평균평점, 리뷰다양성을 한눈에 비교")
            try:
                if len(selected_data) > 0:
                    fig_radar = render_radar_chart(selected_data)
                    st.plotly_chart(fig_radar, use_container_width=True, height=600)
                else:
                    st.info("비교할 제품을 선택해주세요.")
            except Exception as e:
                st.error(f"레이더 차트 생성 실패: {e}")
                import traceback
                with st.expander("상세 에러 정보"):
                    st.code(traceback.format_exc())
        
        with col2:
            st.markdown("#### 💰 가격 및 신뢰도 비교")
            st.caption("제품별 가격과 신뢰도 점수 비교")
            try:
                if len(selected_data) > 0:
                    fig_price = render_price_comparison_chart(selected_data)
                    st.plotly_chart(fig_price, use_container_width=True, height=400)
                else:
                    st.info("비교할 제품을 선택해주세요.")
            except Exception as e:
                st.error(f"가격 비교 차트 생성 실패: {e}")
                import traceback
                with st.expander("상세 에러 정보"):
                    st.code(traceback.format_exc())
    else:
        st.info("📊 제품을 선택하면 차트가 표시됩니다.")
        
        # 신뢰도 요약 카드
        st.markdown("#### 📊 신뢰도 요약")
        for data in selected_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            trust_score = ai_result.get("trust_score", 0)
            trust_level = ai_result.get("trust_level", "medium")
            
            col_card1, col_card2 = st.columns([2, 1])
            with col_card1:
                st.markdown(f"**{product.get('brand', '')}**")
            with col_card2:
                st.markdown(render_trust_badge(trust_level), unsafe_allow_html=True)
            st.progress(trust_score / 100, text=f"{trust_score:.1f}점")
    
    st.markdown("---")
    st.markdown("#### 📋 세부 지표 비교표")
    try:
        comparison_df = render_comparison_table(selected_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=400)
    except Exception as e:
        st.error(f"비교표 생성 실패: {e}")
    
    st.markdown("---")
    
    # ========== 추가 분석 탭 ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 종합 비교 분석",
        "💊 AI 제품별 정밀 진단",
        "💬 리뷰 딥다이브",
        "📈 상세 통계 분석"
    ])
    
    # 탭 1: 종합 비교 분석 (상세 보기)
    with tab1:
        st.markdown('<div class="section-header">📊 종합 비교 분석 - 상세 보기</div>', unsafe_allow_html=True)
        st.info("💡 메인 대시보드에서 차트를 확인하실 수 있습니다. 이 탭에서는 추가 분석 정보를 제공합니다.")
        
        # 추가 분석 정보 표시 (차트는 메인 대시보드에만 표시)
        st.markdown("### 📊 제품별 상세 정보")
        for idx, data in enumerate(selected_data):
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            
            with st.expander(f"📌 {product.get('brand', '')} {product.get('name', '')}", expanded=False):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("신뢰도 점수", f"{ai_result.get('trust_score', 0):.1f}")
                    st.metric("가격", f"${product.get('price', 0):.2f}")
                with col_info2:
                    st.metric("평균 평점", f"{product.get('rating_avg', 0):.1f}/5")
                    st.metric("리뷰 수", f"{product.get('rating_count', 0)}개")
    
    # 탭 2: AI 제품별 정밀 진단
    with tab2:
        st.markdown('<div class="section-header">💊 제품별 심층 데이터 분석</div>', unsafe_allow_html=True)
        
        for data in selected_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            checklist = data.get("checklist_results", {})
            
            with st.expander(
                f"📌 {product.get('brand', '')} - {product.get('name', '')} 상세 보기",
                expanded=True
            ):
                # 상단: 신뢰도 게이지와 체크리스트
                col_top1, col_top2, col_top3 = st.columns([1, 1, 1.5])
                
                with col_top1:
                    st.markdown("#### 🎯 신뢰도 점수")
                    fig_gauge = render_gauge_chart(ai_result.get("trust_score", 0), "신뢰도")
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.markdown(render_trust_badge(ai_result.get("trust_level", "medium")), unsafe_allow_html=True)
                
                with col_top2:
                    st.markdown("#### ✅ 8단계 체크리스트")
                    render_checklist_visual(checklist)
                
                with col_top3:
                    st.markdown("#### 💡 AI 약사 인사이트")
                    st.info(f"**요약**: {ai_result.get('summary', '정보 없음')}")
                    st.success(f"**효능**: {ai_result.get('efficacy', '정보 없음')}")
                    st.warning(f"**부작용**: {ai_result.get('side_effects', '정보 없음')}")
                    st.info(f"**권장사항**: {ai_result.get('recommendations', '정보 없음')}")
                    st.error(f"**주의사항**: {ai_result.get('warnings', '정보 없음')}")
                
                # 체크리스트 상세
                st.markdown("---")
                st.markdown("#### 📋 체크리스트 상세 분석")
                render_checklist_details(checklist)
                
                # 제품 정보
                st.markdown("---")
                st.markdown("#### 📦 제품 정보")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown(f"**브랜드**: {product.get('brand', '')}")
                    st.markdown(f"**제품명**: {product.get('name', '')}")
                    st.markdown(f"**가격**: ${product.get('price', 0):.2f}")
                with col_info2:
                    st.markdown(f"**용량**: {product.get('serving_size', '')}")
                    st.markdown(f"**총 용량**: {product.get('servings_per_container', '')}정")
                    if product.get('product_url'):
                        st.markdown(f"[제품 링크]({product.get('product_url')})")
    
    # 탭 3: 리뷰 딥다이브
    with tab3:
        st.markdown('<div class="section-header">💬 실제 사용자 리뷰 팩트체크</div>', unsafe_allow_html=True)
        
        # 제품 선택
        target_label = st.selectbox(
            "리뷰를 확인할 제품 선택",
            options=selected_labels,
            key="review_product_select"
        )
        target_data = next(
            d for d in selected_data
            if f"{d['product']['brand']} {d['product']['name']}" == target_label
        )
        
        reviews = target_data.get("reviews", [])
        product = target_data.get("product", {})
        
        if not reviews:
            st.warning("이 제품에 대한 리뷰가 없습니다.")
        else:
            # 평점 분석
            st.markdown("#### 📊 평점 분석")
            product_rating_avg = product.get("rating_avg")
            render_rating_analysis(reviews, product_rating_avg)
            
            # 리뷰 감정 분석 차트
            st.markdown("---")
            col_s1, col_s2 = st.columns([1, 1])
            with col_s1:
                st.markdown("#### 📈 리뷰 감정 분석")
                fig_sentiment = render_review_sentiment_chart(reviews)
                st.plotly_chart(fig_sentiment, use_container_width=True, height=400)
            
            with col_s2:
                st.markdown("#### 📋 리뷰 통계")
                total_reviews = len(reviews)
                verified_count = sum(1 for r in reviews if r.get("verified", False))
                reorder_count = sum(1 for r in reviews if r.get("reorder", False))
                one_month_count = sum(1 for r in reviews if r.get("one_month_use", False))
                
                st.metric("총 리뷰 수", f"{total_reviews}개")
                st.metric("인증 구매", f"{verified_count}개 ({verified_count/total_reviews*100:.1f}%)")
                st.metric("재구매", f"{reorder_count}개 ({reorder_count/total_reviews*100:.1f}%)")
                st.metric("1개월+ 사용", f"{one_month_count}개 ({one_month_count/total_reviews*100:.1f}%)")
            
            # 개별 리뷰 분석
            st.markdown("---")
            render_individual_review_analysis(reviews)
    
    # 탭 4: 상세 통계 분석
    with tab4:
        st.markdown('<div class="section-header">📈 상세 통계 분석</div>', unsafe_allow_html=True)
        
        # 전체 통계 요약
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        total_products = len(selected_data)
        total_reviews_all = sum(len(d.get("reviews", [])) for d in selected_data)
        avg_trust_all = sum(d.get("ai_result", {}).get("trust_score", 0) for d in selected_data) / total_products if total_products > 0 else 0
        avg_price = sum(d.get("product", {}).get("price", 0) for d in selected_data) / total_products if total_products > 0 else 0
        
        with col_stat1:
            st.metric("선택된 제품 수", f"{total_products}개")
        with col_stat2:
            st.metric("총 리뷰 수", f"{total_reviews_all}개")
        with col_stat3:
            st.metric("평균 신뢰도", f"{avg_trust_all:.1f}점")
        with col_stat4:
            st.metric("평균 가격", f"${avg_price:.2f}")
        
        # 제품별 상세 통계 테이블
        st.markdown("#### 📊 제품별 상세 통계")
        stats_data = []
        for data in selected_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            reviews = data.get("reviews", [])
            checklist = data.get("checklist_results", {})
            
            stats_data.append({
                "제품명": f"{product.get('brand', '')} {product.get('name', '')}",
                "가격 ($)": product.get("price", 0),
                "신뢰도 점수": ai_result.get("trust_score", 0),
                "신뢰도 등급": ai_result.get("trust_level", "").upper(),
                "리뷰 수": len(reviews),
                "평균 평점": sum(r.get("rating", 5) for r in reviews) / len(reviews) if reviews else 0,
                "인증 구매 비율": checklist.get("1_verified_purchase", {}).get("rate", 0) * 100,
                "재구매율": checklist.get("2_reorder_rate", {}).get("rate", 0) * 100,
                "장기 사용 비율": checklist.get("3_long_term_use", {}).get("rate", 0) * 100,
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
