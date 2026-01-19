import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st

def render_gauge_chart(score, title="신뢰도 점수"):
    """신뢰도 게이지 차트 - 크기 및 가시성 개선"""
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 20}},
        number={'font': {'size': 40, 'color': color}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},
                {'range': [50, 70], 'color': '#fef3c7'},
                {'range': [70, 100], 'color': '#dcfce7'}
            ],
        }
    ))
    fig.update_layout(height=350, margin=dict(l=30, r=30, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

def render_radar_chart(products_data):
    """다차원 비교 레이더 차트 - 대형 화면 최적화 (안전한 버전)"""
    fig = go.Figure()
    categories = ['신뢰도', '재구매율', '한달사용', '평균평점', '리뷰다양성']
    colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6']

    for idx, data in enumerate(products_data):
        # 안전한 데이터 접근
        p = data.get("product", {})
        ai = data.get("ai_result", {})
        r = data.get("reviews", [])

        # 안전한 값 계산
        trust_score = ai.get('trust_score', 0)
        reorder_rate = (sum(1 for x in r if x.get("reorder", False)) / len(r) * 100) if r else 0
        one_month_rate = (sum(1 for x in r if x.get("one_month_use", False)) / len(r) * 100) if r else 0
        avg_rating = (sum(x.get("rating", 0) for x in r) / len(r) * 20) if r else 0
        diversity_rate = (len(set(x.get("reviewer", "") for x in r)) / len(r) * 100) if r else 0

        vals = [trust_score, reorder_rate, one_month_rate, avg_rating, diversity_rate]

        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories,
            fill='toself',
            name=p.get('brand', 'Unknown'),
            line=dict(color=colors[idx % len(colors)], width=3)
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=550, # 차트 크기 확대
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        margin=dict(l=80, r=80, t=40, b=80),
        font=dict(size=14)
    )
    return fig

def render_price_comparison_chart(products_data):
    """가격 비교 차트 - 가로 폭 강조 (안전한 버전)"""
    names = []
    prices = []
    scores = []

    for d in products_data:
        product = d.get('product', {})
        ai_result = d.get('ai_result', {})

        names.append(product.get('brand', 'Unknown'))
        prices.append(product.get('price', 0))
        scores.append(ai_result.get('trust_score', 0))

    colors = ['#22c55e' if s >= 70 else '#f59e0b' if s >= 50 else '#ef4444' for s in scores]

    fig = go.Figure(go.Bar(
        x=names,
        y=prices,
        marker_color=colors,
        text=[f"${p:.2f}" for p in prices],
        textposition='auto'
    ))
    fig.update_layout(title="제품별 가격 비교 (USD)", height=450, margin=dict(t=60, b=40))
    return fig

def render_trust_badge(level):
    """신뢰도 등급 배지 HTML 생성"""
    level = level.lower()
    if level == "high":
        color = "#22c55e"
        text = "HIGH"
    elif level == "medium":
        color = "#f59e0b"
        text = "MEDIUM"
    else:
        color = "#ef4444"
        text = "LOW"
    
    return f'<div style="background: {color}; color: white; padding: 8px 16px; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 0.9rem;">{text}</div>'


def render_comparison_table(products_data):
    """제품 비교 테이블 생성 (완전히 안전한 버전)"""
    # 기본 컬럼 정의 (항상 동일한 컬럼 구조 보장)
    default_columns = [
        "제품명", "신뢰도", "등급", "가격 ($)", "리뷰 수", 
        "평균 평점", "인증 구매", "재구매율", "1개월+ 사용", "광고 의심률"
    ]
    
    try:
        # 빈 데이터 체크
        if not products_data:
            return pd.DataFrame(columns=default_columns)
        
        if not isinstance(products_data, list):
            return pd.DataFrame(columns=default_columns)
        
        if len(products_data) == 0:
            return pd.DataFrame(columns=default_columns)
        
        table_data = []
        
        for idx, data in enumerate(products_data):
            try:
                # 안전한 데이터 접근
                if not isinstance(data, dict):
                    continue
                    
                product = data.get("product", {})
                ai_result = data.get("ai_result", {})
                reviews = data.get("reviews", [])
                checklist = data.get("checklist_results", {})
                
                # 안전한 타입 검증
                if not isinstance(product, dict):
                    product = {}
                if not isinstance(ai_result, dict):
                    ai_result = {}
                if not isinstance(reviews, list):
                    reviews = []
                if not isinstance(checklist, dict):
                    checklist = {}
                
                # 안전한 통계 계산
                total_reviews = len(reviews)
                
                verified_count = 0
                reorder_count = 0
                one_month_count = 0
                rating_sum = 0
                rating_count = 0
                
                for r in reviews:
                    if isinstance(r, dict):
                        if r.get("verified", False):
                            verified_count += 1
                        if r.get("reorder", False):
                            reorder_count += 1
                        if r.get("one_month_use", False):
                            one_month_count += 1
                        rating = r.get("rating", 0)
                        if isinstance(rating, (int, float)) and 1 <= rating <= 5:
                            rating_sum += rating
                            rating_count += 1
                
                avg_rating = rating_sum / rating_count if rating_count > 0 else 0
                
                # 광고 의심률
                ad_suspected = 0
                for r in reviews:
                    if isinstance(r, dict):
                        rating = r.get("rating", 0)
                        one_month = r.get("one_month_use", False)
                        text = str(r.get("text", ""))
                        if rating == 5 and not one_month and len(text) < 100:
                            ad_suspected += 1
                
                ad_rate = (ad_suspected / total_reviews * 100) if total_reviews > 0 else 0
                
                # 안전한 값 추출 및 포맷팅
                brand = str(product.get('brand', '')).strip()
                name = str(product.get('name', '')).strip()
                product_name = f"{brand} {name}".strip() if brand or name else "Unknown"
                
                trust_score = ai_result.get('trust_score', 0)
                try:
                    trust_score = float(trust_score) if trust_score is not None else 0.0
                except (ValueError, TypeError):
                    trust_score = 0.0
                
                trust_level = str(ai_result.get('trust_level', 'medium')).upper()
                
                price = product.get('price', 0)
                try:
                    price = float(price) if price is not None else 0.0
                except (ValueError, TypeError):
                    price = 0.0
                
                table_data.append({
                    "제품명": product_name,
                    "신뢰도": f"{trust_score:.1f}",
                    "등급": trust_level,
                    "가격 ($)": f"{price:.2f}",
                    "리뷰 수": f"{total_reviews}개",
                    "평균 평점": f"{avg_rating:.1f}/5",
                    "인증 구매": f"{verified_count/total_reviews*100:.1f}%" if total_reviews > 0 else "0%",
                    "재구매율": f"{reorder_count/total_reviews*100:.1f}%" if total_reviews > 0 else "0%",
                    "1개월+ 사용": f"{one_month_count/total_reviews*100:.1f}%" if total_reviews > 0 else "0%",
                    "광고 의심률": f"{ad_rate:.1f}%"
                })
            except Exception as e:
                # 개별 제품 처리 중 오류 발생 시 해당 제품만 스킵
                import traceback
                print(f"[WARNING] 제품 {idx} 처리 중 오류 발생: {str(e)}")
                continue
        
        # 빈 리스트인 경우 빈 DataFrame 반환 (컬럼 구조는 유지)
        if not table_data:
            return pd.DataFrame(columns=default_columns)
        
        # DataFrame 생성 및 검증
        df = pd.DataFrame(table_data)
        
        # 컬럼이 모두 존재하는지 확인
        for col in default_columns:
            if col not in df.columns:
                df[col] = ""  # 누락된 컬럼 추가
        
        # 불필요한 컬럼 제거 (기본 컬럼만 유지)
        df = df[default_columns]
        
        return df
        
    except Exception as e:
        # 전체 함수 실행 중 예상치 못한 오류 발생 시 빈 DataFrame 반환
        import traceback
        print(f"[ERROR] render_comparison_table 실행 중 오류: {str(e)}")
        print(traceback.format_exc())
        return pd.DataFrame(columns=default_columns)


def render_review_sentiment_chart(reviews):
    """리뷰 감정 분석 차트 (평점 분포)"""
    if not reviews:
        # 빈 차트 반환
        fig = go.Figure()
        fig.add_annotation(text="리뷰 데이터가 없습니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(height=300)
        return fig
    
    # 평점 분포 계산
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating = review.get("rating", 5)
        if rating in rating_counts:
            rating_counts[rating] += 1
    
    # 차트 생성
    fig = go.Figure(data=[
        go.Bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            marker_color=['#ef4444', '#f59e0b', '#eab308', '#84cc16', '#22c55e'],
            text=[f"{count}개" for count in rating_counts.values()],
            textposition='auto',
            name="리뷰 수"
        )
    ])
    
    fig.update_layout(
        title="평점 분포",
        xaxis_title="평점",
        yaxis_title="리뷰 수",
        height=400,
        showlegend=False,
        margin=dict(t=50, b=40, l=50, r=50)
    )
    
    return fig


def render_checklist_visual(checklist_results):
    """8단계 체크리스트 시각화"""
    if not checklist_results:
        st.warning("체크리스트 데이터가 없습니다.")
        return
    
    checklist_items = {
        "1_verified_purchase": "인증 구매",
        "2_reorder_rate": "재구매율",
        "3_long_term_use": "장기 사용",
        "4_rating_distribution": "평점 분포",
        "5_review_length": "리뷰 길이",
        "6_time_distribution": "시간 분포",
        "7_ad_detection": "광고 탐지",
        "8_reviewer_diversity": "리뷰어 다양성"
    }
    
    for key, label in checklist_items.items():
        if key in checklist_results:
            result = checklist_results[key]
            passed = result.get("passed", False)
            rate = result.get("rate", 0)
            
            status_icon = "✅" if passed else "❌"
            status_color = "#22c55e" if passed else "#ef4444"
            
            st.markdown(f"{status_icon} **{label}**")
            st.progress(rate, text=f"{rate*100:.1f}%")
