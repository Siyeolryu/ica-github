"""
AI 기반 차트 분석 및 요약 모듈
차트 데이터를 분석하여 인사이트 제공
"""

import os
import json
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
import pandas as pd

class ChartAnalyzer:
    """차트 데이터를 AI로 분석하는 클래스"""
    
    SYSTEM_PROMPT = """당신은 데이터 분석 전문가입니다.
차트와 통계 데이터를 분석하여 비즈니스 인사이트를 제공합니다.

**역할:**
- 차트 데이터의 패턴과 트렌드를 분석
- 중요한 발견사항을 명확하게 요약
- 실용적인 인사이트와 권장사항 제공
- 통계적 유의성을 고려한 분석

**출력 형식:**
다음 JSON 형식으로 응답하세요:
{
  "summary": "차트 데이터의 핵심 요약 (2-3문장)",
  "key_findings": [
    "주요 발견사항 1",
    "주요 발견사항 2",
    "주요 발견사항 3"
  ],
  "trends": "트렌드 분석 (상승/하락/안정 등)",
  "insights": "비즈니스 인사이트 및 권장사항",
  "data_quality": "데이터 품질 평가"
}
"""

    def __init__(self, api_key: Optional[str] = None):
        """차트 분석기 초기화"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            # Streamlit secrets에서도 시도
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'ANTHROPIC_API_KEY' in st.secrets:
                    self.api_key = st.secrets['ANTHROPIC_API_KEY']
            except:
                pass
        
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수가 필요합니다. "
                "환경변수 또는 Streamlit secrets에 설정하세요."
            )
        self.client = Anthropic(api_key=self.api_key)

    def analyze_chart_data(
        self,
        chart_type: str,
        data: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        차트 데이터 분석
        
        Args:
            chart_type: 차트 타입 (radar, gauge, bar, line 등)
            data: 차트 데이터
            context: 추가 컨텍스트 정보
        
        Returns:
            분석 결과 딕셔너리
        """
        user_prompt = f"""다음 {chart_type} 차트 데이터를 분석해주세요:

**차트 타입**: {chart_type}
**데이터**: {json.dumps(data, ensure_ascii=False, indent=2)}
{f'**컨텍스트**: {context}' if context else ''}

위 데이터를 분석하여 JSON 형식으로 응답해주세요.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.3,
                system=self.SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            content = response.content[0].text
            
            # JSON 파싱 시도
            try:
                # JSON 코드 블록 제거
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조로 반환
                return {
                    "summary": content[:200] + "..." if len(content) > 200 else content,
                    "key_findings": [content],
                    "trends": "분석 완료",
                    "insights": content,
                    "data_quality": "양호"
                }
        except Exception as e:
            return {
                "error": str(e),
                "summary": "분석 중 오류가 발생했습니다.",
                "key_findings": [],
                "trends": "분석 불가",
                "insights": "데이터를 다시 확인해주세요.",
                "data_quality": "불명"
            }

    def analyze_comparison_chart(
        self,
        products_data: List[Dict],
        chart_type: str = "radar"
    ) -> Dict[str, Any]:
        """
        제품 비교 차트 분석
        
        Args:
            products_data: 제품 비교 데이터 리스트
            chart_type: 차트 타입
        
        Returns:
            비교 분석 결과
        """
        # 데이터 요약
        summary_data = {
            "total_products": len(products_data),
            "products": []
        }
        
        for data in products_data:
            product = data.get("product", {})
            ai_result = data.get("ai_result", {})
            reviews = data.get("reviews", [])
            
            summary_data["products"].append({
                "name": f"{product.get('brand', '')} {product.get('name', product.get('title', ''))}",
                "trust_score": ai_result.get("trust_score", 0),
                "price": product.get("price", 0),
                "review_count": len(reviews),
                "avg_rating": sum(r.get("rating", 5) for r in reviews) / len(reviews) if reviews else 0
            })
        
        context = "건강기능식품 제품 비교 분석 - 신뢰도, 가격, 리뷰 품질을 종합적으로 비교"
        
        return self.analyze_chart_data(chart_type, summary_data, context)

    def analyze_trust_score_distribution(
        self,
        trust_scores: List[float]
    ) -> Dict[str, Any]:
        """
        신뢰도 점수 분포 분석
        
        Args:
            trust_scores: 신뢰도 점수 리스트
        
        Returns:
            분포 분석 결과
        """
        import statistics
        
        if not trust_scores:
            return {
                "summary": "분석할 데이터가 없습니다.",
                "key_findings": [],
                "trends": "데이터 부족",
                "insights": "더 많은 데이터가 필요합니다.",
                "data_quality": "불충분"
            }
        
        data = {
            "count": len(trust_scores),
            "mean": statistics.mean(trust_scores),
            "median": statistics.median(trust_scores),
            "min": min(trust_scores),
            "max": max(trust_scores),
            "distribution": {
                "high": sum(1 for s in trust_scores if s >= 70),
                "medium": sum(1 for s in trust_scores if 50 <= s < 70),
                "low": sum(1 for s in trust_scores if s < 50)
            }
        }
        
        context = "건강기능식품 리뷰 신뢰도 점수 분포 분석"
        
        return self.analyze_chart_data("distribution", data, context)
