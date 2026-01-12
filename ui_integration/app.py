import streamlit as st
import pandas as pd
import sys
import os

# 상위 디렉토리를 경로에 추가하여 supabase_data 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Supabase 연동 시도 (ui_integration 폴더 내의 supabase_data 모듈)
    from supabase_data import get_all_analysis_results
    USE_SUPABASE = True
except (ImportError, Exception) as e:
    # Supabase 연동 실패 시 mock_data 사용
    from mock_data import get_all_analysis_results
    USE_SUPABASE = False
    if hasattr(st, 'warning'):
        st.warning("⚠️ Supabase 연동 실패: 목업 데이터를 사용합니다.")

from visualizations import *

st.set_page_config(page_title="건기식 팩트체크", page_icon="🔍", layout="wide")

# CSS 생략 (기존 스타일 유지)

def main():
    st.markdown('<div class="main-title">🔍 건기식 리뷰 팩트체크 시스템</div>', unsafe_allow_html=True)
    
    # Supabase 연결 상태 표시
    if USE_SUPABASE:
        st.sidebar.success("✅ Supabase 연동 활성화")
    else:
        st.sidebar.warning("⚠️ 목업 데이터 사용 중")
    
    # 1. 사이드바: 제품 멀티 선택
    try:
        all_data = get_all_analysis_results()
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        st.info("목업 데이터로 전환합니다.")
        from mock_data import get_all_analysis_results as get_mock_data
        all_data = get_mock_data()
    product_options = {f"{v['product']['brand']} {v['product']['name']}": k for k, v in all_data.items()}
    
    with st.sidebar:
        st.header("⚙️ 분석 설정")
        selected_labels = st.multiselect(
            "분석할 제품을 선택하세요",
            options=list(product_options.keys()),
            default=list(product_options.keys())[:3] # 상위 3개 기본값
        )
        st.info("신뢰도 등급 안내: 70↑ HIGH / 50↑ MEDIUM / 50↓ LOW")

    if not selected_labels:
        st.warning("분석할 제품을 하나 이상 선택해주세요.")
        return

    # 선택된 데이터 필터링
    selected_data = [all_data[product_options[label]] for label in selected_labels]

    # 2. 메인 레이아웃: Tab 구성
    tab1, tab2, tab3 = st.tabs(["📊 종합 비교 분석", "💊 AI 제품별 정밀 진단", "💬 리뷰 딥다이브"])

    with tab1:
        st.subheader("모든 제품 한눈에 비교")
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            st.plotly_chart(render_radar_chart(selected_data), use_container_width=True)
        with col2:
            st.markdown("#### 💰 가격 및 신뢰도 요약")
            st.plotly_chart(render_price_comparison_chart(selected_data), use_container_width=True)
        
        st.markdown("#### 📋 세부 지표 비교")
        st.dataframe(render_comparison_table(selected_data), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("제품별 심층 데이터 분석")
        for data in selected_data:
            with st.expander(f"📌 {data['product']['brand']} - {data['product']['name']} 상세 보기", expanded=True):
                c1, c2, c3 = st.columns([1, 1, 1.2])
                with c1:
                    st.plotly_chart(render_gauge_chart(data['ai_result']['trust_score']), use_container_width=True)
                    st.markdown(render_trust_badge(data['ai_result']['trust_level']), unsafe_allow_html=True)
                with c2:
                    st.markdown("**🎯 8단계 체크리스트**")
                    render_checklist_visual(data['checklist_results'])
                with c3:
                    st.markdown("**💡 AI 약사 인사이트**")
                    st.info(data['ai_result']['summary'])
                    st.warning(f"🚨 주의사항: {data['ai_result']['warnings']}")

    with tab3:
        st.subheader("실제 사용자 리뷰 팩트체크")
        target_label = st.selectbox("리뷰를 확인할 제품 선택", options=selected_labels)
        target_data = next(d for d in selected_data if f"{d['product']['brand']} {d['product']['name']}" == target_label)
        
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.plotly_chart(render_review_sentiment_chart(target_data['reviews']), use_container_width=True)
        with col_s2:
            st.markdown(f"#### 💬 {target_label} 리뷰 리스트")
            # 리뷰 필터링 및 출력 로직 (기존 app.py 로직 활용)

if __name__ == "__main__":
    main()
    