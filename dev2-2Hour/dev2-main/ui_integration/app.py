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

/* ========== 접근성 개선 ========== */
*:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
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
        
        # 1단계: 카테고리 선택
        if categories:
            category_filter = st.multiselect(
                "📂 카테고리 선택",
                options=categories,
                default=st.session_state.get('category_filter', categories),
                key="category_filter"
            )
        else:
            category_filter = []
        
        # 카테고리 필터링된 제품 목록
        filtered_products_by_category = all_products_list
        if category_filter:
            filtered_products_by_category = [p for p in all_products_list if p.get("category") in category_filter]
        
        # 카테고리 필터링된 브랜드 목록
        filtered_brands = sorted(list(set(p.get("brand", "") for p in filtered_products_by_category if p.get("brand") and p.get("brand"))))
        
        # 2단계: 브랜드 1개(메인) 선택
        if filtered_brands:
            main_brand = st.selectbox(
                "🏷️ 메인 브랜드 선택 (1개)",
                options=[""] + filtered_brands,
                index=0 if not st.session_state.get('main_brand') else (filtered_brands.index(st.session_state.get('main_brand')) + 1 if st.session_state.get('main_brand') in filtered_brands else 0),
                key="main_brand"
            )
        else:
            main_brand = ""
        
        # 브랜드 필터링된 제품 목록
        filtered_products_by_brand = filtered_products_by_category
        if main_brand:
            filtered_products_by_brand = [p for p in filtered_products_by_category if p.get("brand") == main_brand]
        
        # 제품 옵션 생성 (브랜드 + 제품명)
        product_options_filtered = {f"{p.get('brand', '')} {p.get('name', '')}": p.get('id') for p in filtered_products_by_brand}
        
        # 3단계: 제품 1개(메인) 선택
        if product_options_filtered:
            main_product_label = st.selectbox(
                "📦 메인 제품 선택 (1개)",
                options=[""] + list(product_options_filtered.keys()),
                index=0 if not st.session_state.get('main_product') else (list(product_options_filtered.keys()).index(st.session_state.get('main_product_label', "")) + 1 if st.session_state.get('main_product_label') in product_options_filtered.keys() else 0),
                key="main_product_select"
            )
            main_product = product_options_filtered.get(main_product_label) if main_product_label else None
            st.session_state.main_product = main_product
            st.session_state.main_product_label = main_product_label
        else:
            main_product = None
            main_product_label = ""
        
        # 비교 제품 목록 (메인 제품 제외)
        compare_options = {k: v for k, v in product_options_filtered.items() if v != main_product}
        
        # 4단계: 비교 제품 선택 (최대 2개)
        if compare_options:
            compare_products_labels = st.multiselect(
                "🔄 비교 제품 선택 (최대 2개)",
                options=list(compare_options.keys()),
                default=st.session_state.get('compare_products_labels', []),
                max_selections=2,
                key="compare_products_select"
            )
            compare_products = [compare_options[label] for label in compare_products_labels]
            st.session_state.compare_products = compare_products
            st.session_state.compare_products_labels = compare_products_labels
        else:
            compare_products = []
        
        st.markdown("---")
        st.markdown("### ⚙️ 필터 설정")
        
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
                    key="price_grade"
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
                    key="rating_grade"
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
                    key="review_grade"
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
        
        # 신뢰도 필터
        trust_filter = st.multiselect(
            "🎯 신뢰도 등급",
            options=["HIGH", "MEDIUM", "LOW"],
            default=st.session_state.get('trust_filter', ["HIGH", "MEDIUM", "LOW"]),
            key="trust_filter"
        )
        
        st.markdown("---")
        
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
        
        st.markdown("---")
        st.markdown("### 📊 실시간 통계")
        
        # 실시간 통계 (Supabase 데이터 기반)
        try:
            stats = get_cached_statistics()
            
            # 전체 통계
            st.metric("전체 제품 수", f"{stats.get('total_products', 0)}개")
            st.metric("전체 리뷰 수", f"{stats.get('total_reviews', 0)}개")
            st.metric("평균 가격", f"${stats.get('avg_price', 0):.2f}")
            
            st.markdown("---")
            
            # 브랜드별 통계
            st.markdown("### 🏷️ 브랜드별 통계")
            brand_stats = stats.get('brands', {})
            if brand_stats:
                for brand, data in sorted(brand_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
                    avg_rating = data['total_rating'] / data['count'] if data['count'] > 0 else 0
                    st.markdown(f"**{brand}**")
                    st.caption(f"제품: {data['count']}개 | 평균 평점: {avg_rating:.1f} | 리뷰: {data['total_reviews']}개")
            
            st.markdown("---")
            
            # 카테고리별 통계
            st.markdown("### 📂 카테고리별 통계")
            category_stats = stats.get('categories', {})
            if category_stats:
                for category, data in sorted(category_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:5]:
                    st.markdown(f"**{category}**")
                    st.caption(f"제품: {data['count']}개")
            
            st.markdown("---")
            
            # 평점 분포
            st.markdown("### ⭐ 평점 분포")
            rating_dist = stats.get('rating_distribution', {})
            if rating_dist:
                total_ratings = sum(rating_dist.values())
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
    
    if not main_product:
        st.warning("메인 제품을 선택해주세요.")
        return
    
    # 선택된 제품 목록 구성 (메인 + 비교 제품)
    selected_product_ids = [main_product] + compare_products
    selected_labels = []
    for product_id in selected_product_ids:
        for label, pid in product_options.items():
            if pid == product_id:
                selected_labels.append(label)
                break
    
    if not selected_labels:
        st.warning("선택된 제품을 찾을 수 없습니다.")
        return
    
    # 필터 값 수집 및 검증 (리뷰날짜, 언어 필터 제거)
    filters_dict = {
        'category_filter': st.session_state.get('category_filter', []),
        'main_brand': st.session_state.get('main_brand', ''),
        'price_range': st.session_state.get('price_range', None),
        'rating_range': st.session_state.get('rating_range', None),
        'review_count_range': st.session_state.get('review_count_range', None),
        'trust_filter': st.session_state.get('trust_filter', []),
        'search_query': st.session_state.get('search_query', '')
    }
    
    # 필터 검증
    validation_errors = validate_filters(filters_dict)
    if validation_errors:
        for error in validation_errors:
            st.error(f"⚠️ {error}")
        st.stop()  # 필터 적용 중단
    
    # 필터 상태 표시 (사이드바 상단)
    with st.sidebar:
        active_filters = get_active_filters_summary(filters_dict, all_products_list)
        if active_filters:
            st.markdown("---")
            st.info(f"🔍 활성 필터: {len(active_filters)}개")
            for f in active_filters:
                st.caption(f"  • {f}")
    
    # 필터링 적용 (로딩 표시)
    with st.spinner("필터 적용 중..."):
        selected_data = [all_data[product_options[label]] for label in selected_labels]
    
        # 카테고리 필터 적용 (Supabase category 필드)
        category_filter = filters_dict.get('category_filter', [])
        if category_filter:
            selected_data = [
                d for d in selected_data
                if d.get("product", {}).get("category", "") in category_filter
            ]
        
        # 브랜드 필터 적용 (메인 브랜드만)
        main_brand = filters_dict.get('main_brand', '')
        if main_brand:
            selected_data = [
                d for d in selected_data
                if d.get("product", {}).get("brand", "") == main_brand
            ]
        
        # 가격 필터 적용
        price_range = filters_dict.get('price_range')
        if price_range:
            selected_data = [
                d for d in selected_data
                if price_range[0] <= d.get("product", {}).get("price", 0) <= price_range[1]
            ]
        
        # 평점 범위 필터 적용 (Supabase rating_avg 필드)
        rating_range = filters_dict.get('rating_range')
        if rating_range:
            selected_data = [
                d for d in selected_data
                if rating_range[0] <= d.get("product", {}).get("rating_avg", 0) <= rating_range[1]
            ]
        
        # 리뷰 수 범위 필터 적용 (Supabase rating_count 필드)
        review_count_range = filters_dict.get('review_count_range')
        if review_count_range:
            selected_data = [
                d for d in selected_data
                if review_count_range[0] <= d.get("product", {}).get("rating_count", 0) <= review_count_range[1]
            ]
        
        # 신뢰도 필터 적용
        trust_filter = filters_dict.get('trust_filter', [])
        if trust_filter:
            selected_data = [
                d for d in selected_data
                if d.get("ai_result", {}).get("trust_level", "").upper() in [f.upper() for f in trust_filter]
            ]
        
        # 검색 필터 적용
        search_query = filters_dict.get('search_query', '')
        if search_query:
            search_results = search_products(search_query)
            search_ids = [p.get("id") for p in search_results]
            selected_data = [
                d for d in selected_data
                if d.get("product", {}).get("id") in search_ids
            ]
        
        # 날짜 필터 및 언어 필터 제거됨 (사용자 요청)
    
    # 필터 적용 결과 피드백
    if not selected_data:
        st.warning("⚠️ 필터 조건에 맞는 제품이 없습니다.")
        return
    else:
        # 필터 상태를 히스토리에 저장 (자동)
        save_filter_state_to_history(filters_dict)
        
        # 결과 미리보기
        st.success(f"✅ {len(selected_data)}개 제품이 표시됩니다")
    
    # ========== 메인 영역: 탭 구성 ==========
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 종합 비교 분석",
        "💊 AI 제품별 정밀 진단",
        "💬 리뷰 딥다이브",
        "📈 상세 통계 분석"
    ])
    
    # 탭 1: 종합 비교 분석
    with tab1:
        st.markdown('<div class="section-header">📊 모든 제품 한눈에 비교</div>', unsafe_allow_html=True)
        
        # 레이더 차트와 가격 비교를 더 크게 표시
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("#### 🕸️ 다차원 비교 (레이더 차트)")
            fig_radar = render_radar_chart(selected_data)
            st.plotly_chart(fig_radar, use_container_width=True, height=600)
        
        with col2:
            st.markdown("#### 💰 가격 및 신뢰도 요약")
            fig_price = render_price_comparison_chart(selected_data)
            st.plotly_chart(fig_price, use_container_width=True, height=400)
            
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
        
        st.markdown("#### 📋 세부 지표 비교표")
        comparison_df = render_comparison_table(selected_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=400)
    
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
