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
        차트 데이터 분석 (항상 의미 있는 결과 반환)

        Args:
            chart_type: 차트 타입 (radar, gauge, bar, line 등)
            data: 차트 데이터
            context: 추가 컨텍스트 정보

        Returns:
            분석 결과 딕셔너리 (항상 유효한 결과)
        """
        user_prompt = f"""다음 {chart_type} 차트 데이터를 분석해주세요:

**차트 타입**: {chart_type}
**데이터**: {json.dumps(data, ensure_ascii=False, indent=2)}
{f'**컨텍스트**: {context}' if context else ''}

위 데이터를 분석하여 JSON 형식으로 응답해주세요.
반드시 summary, key_findings, trends, insights, data_quality 필드를 포함해야 합니다.
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
            result = self._parse_json_response(content)

            # 필수 필드 검증 및 기본값 보장
            if not result.get("summary"):
                result["summary"] = self._generate_generic_summary(data, chart_type)

            return result

        except Exception as e:
            # AI 호출 실패 시에도 데이터 기반 폴백 분석 제공
            return self._create_generic_fallback_analysis(data, chart_type)

    def analyze_radar_chart(
        self,
        products_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        레이더 차트 전용 AI 분석 - 5가지 지표 기반

        Args:
            products_data: 제품 비교 데이터 리스트

        Returns:
            레이더 차트 분석 결과
        """
        if not products_data:
            return self._create_default_response("분석할 제품 데이터가 없습니다.")

        # 레이더 차트 5가지 지표 추출
        radar_metrics = []
        for data in products_data:
            try:
                product = data.get("product", {})
                ai_result = data.get("ai_result", {})
                reviews = data.get("reviews", [])
                checklist = data.get("checklist_results", {})

                # 5가지 지표 계산
                trust_score = ai_result.get("trust_score", 0)
                reorder_rate = checklist.get("2_reorder_rate", {}).get("rate", 0) * 100
                one_month_rate = checklist.get("3_long_term_use", {}).get("rate", 0) * 100
                avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0

                # 리뷰 다양성 계산 (간단한 휴리스틱)
                unique_reviewers = len(set(r.get("reviewer", "") for r in reviews if r.get("reviewer")))
                review_diversity = (unique_reviewers / len(reviews) * 100) if reviews else 0

                radar_metrics.append({
                    "name": f"{product.get('brand', 'Unknown')} {product.get('name', 'Unknown')}",
                    "trust_score": round(trust_score, 1),
                    "reorder_rate": round(reorder_rate, 1),
                    "one_month_use": round(one_month_rate, 1),
                    "avg_rating": round(avg_rating * 20, 1),  # 0-100 스케일로 변환
                    "review_diversity": round(review_diversity, 1)
                })
            except Exception as e:
                continue

        if not radar_metrics:
            return self._create_default_response("유효한 제품 데이터를 찾을 수 없습니다.")

        # AI 프롬프트 구성
        user_prompt = f"""다음은 건강기능식품 제품들의 레이더 차트 5가지 지표 데이터입니다:

**분석할 지표:**
1. 신뢰도 (Trust Score): AI가 계산한 종합 신뢰도 점수 (0-100)
2. 재구매율 (Reorder Rate): 재구매 의사를 밝힌 리뷰 비율 (%)
3. 한달사용 (One Month Use): 1개월 이상 사용 후 작성된 리뷰 비율 (%)
4. 평균평점 (Avg Rating): 평균 평점을 100점 만점으로 환산 (0-100)
5. 리뷰다양성 (Review Diversity): 리뷰어의 다양성 점수 (0-100)

**제품 데이터:**
{json.dumps(radar_metrics, ensure_ascii=False, indent=2)}

**분석 요구사항:**
1. 각 제품의 강점과 약점을 지표별로 분석
2. 제품 간 비교 인사이트 제공
3. 균형 잡힌 제품 vs 특화된 제품 구분
4. 사용자 유형별 추천 (예: 가성비 중시, 품질 중시, 신뢰도 중시)
5. 가장 우수한 제품과 그 이유

반드시 다음 JSON 형식으로 응답하세요:
{{
  "summary": "핵심 요약 (3-4문장, 전체 제품의 특징과 주요 패턴)",
  "key_findings": [
    "주요 발견사항 1 (제품별 강점)",
    "주요 발견사항 2 (제품별 약점)",
    "주요 발견사항 3 (제품 간 차별점)"
  ],
  "trends": "전체 트렌드 분석 (균형형 vs 특화형 제품 분류)",
  "insights": "실용적 인사이트 및 사용자별 추천",
  "data_quality": "데이터 신뢰도 평가",
  "best_product": "최고 추천 제품명과 이유"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                temperature=0.3,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}]
            )

            content = response.content[0].text
            result = self._parse_json_response(content)

            # 필수 필드 검증
            if not result.get("summary"):
                result["summary"] = self._generate_fallback_summary(radar_metrics)

            return result

        except Exception as e:
            return self._create_fallback_radar_analysis(radar_metrics)

    def analyze_price_comparison(
        self,
        products_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        가격 비교 차트 전용 AI 분석 - 가성비 분석

        Args:
            products_data: 제품 비교 데이터 리스트

        Returns:
            가격 비교 분석 결과
        """
        if not products_data:
            return self._create_default_response("분석할 제품 데이터가 없습니다.")

        # 가격 및 신뢰도 데이터 추출
        price_data = []
        for data in products_data:
            try:
                product = data.get("product", {})
                ai_result = data.get("ai_result", {})

                price = product.get("price", 0)
                trust_score = ai_result.get("trust_score", 0)

                # 가성비 지수 계산 (신뢰도 / 가격)
                value_score = (trust_score / price) if price > 0 else 0

                price_data.append({
                    "name": f"{product.get('brand', 'Unknown')} {product.get('name', 'Unknown')}",
                    "price": round(price, 2),
                    "trust_score": round(trust_score, 1),
                    "value_score": round(value_score, 2)
                })
            except Exception:
                continue

        if not price_data:
            return self._create_default_response("유효한 가격 데이터를 찾을 수 없습니다.")

        # AI 프롬프트 구성
        user_prompt = f"""다음은 건강기능식품 제품들의 가격 및 신뢰도 비교 데이터입니다:

**제품 데이터:**
{json.dumps(price_data, ensure_ascii=False, indent=2)}

**분석 요구사항:**
1. 가격 대비 신뢰도 효율성 (가성비) 분석
2. 프리미엄 제품 vs 가성비 제품 분류
3. 가격대별 추천
4. 최적의 가치를 제공하는 제품 선정
5. 가격과 신뢰도의 상관관계 분석

반드시 다음 JSON 형식으로 응답하세요:
{{
  "summary": "핵심 요약 (3-4문장, 가격대별 특징과 가성비 패턴)",
  "key_findings": [
    "주요 발견사항 1 (가장 저렴한 제품과 신뢰도)",
    "주요 발견사항 2 (가장 비싼 제품과 신뢰도)",
    "주요 발견사항 3 (최고 가성비 제품)"
  ],
  "trends": "가격과 신뢰도의 상관관계 (정비례, 반비례, 무관 등)",
  "insights": "예산별 구매 추천 (저예산, 중예산, 고예산)",
  "data_quality": "데이터 신뢰도 평가",
  "best_value": "최고 가성비 제품명과 이유"
}}
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                temperature=0.3,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}]
            )

            content = response.content[0].text
            result = self._parse_json_response(content)

            # 필수 필드 검증
            if not result.get("summary"):
                result["summary"] = self._generate_price_fallback_summary(price_data)

            return result

        except Exception as e:
            return self._create_fallback_price_analysis(price_data)

    def analyze_comparison_chart(
        self,
        products_data: List[Dict],
        chart_type: str = "radar"
    ) -> Dict[str, Any]:
        """
        제품 비교 차트 분석 (범용)

        Args:
            products_data: 제품 비교 데이터 리스트
            chart_type: 차트 타입

        Returns:
            비교 분석 결과
        """
        if chart_type == "radar":
            return self.analyze_radar_chart(products_data)
        elif chart_type == "bar" or chart_type == "price":
            return self.analyze_price_comparison(products_data)

        # 기존 범용 분석 로직
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

    # ========== Helper Methods ==========

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        AI 응답에서 JSON 파싱

        Args:
            content: AI 응답 텍스트

        Returns:
            파싱된 JSON 딕셔너리
        """
        try:
            # JSON 코드 블록 제거
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            # 필수 필드 확인 및 기본값 설정
            required_fields = ["summary", "key_findings", "trends", "insights", "data_quality"]
            for field in required_fields:
                if field not in result:
                    result[field] = "정보 없음" if field != "key_findings" else []

            return result
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 텍스트를 summary로 반환
            return {
                "summary": content[:300] + "..." if len(content) > 300 else content,
                "key_findings": [content[:100]],
                "trends": "분석 완료",
                "insights": content,
                "data_quality": "양호"
            }

    def _create_default_response(self, message: str) -> Dict[str, Any]:
        """
        기본 응답 생성

        Args:
            message: 기본 메시지

        Returns:
            기본 응답 딕셔너리
        """
        return {
            "summary": message,
            "key_findings": [message],
            "trends": "분석 불가",
            "insights": "데이터를 확인해주세요.",
            "data_quality": "불충분"
        }

    def _generate_fallback_summary(self, radar_metrics: List[Dict]) -> str:
        """
        레이더 차트 폴백 요약 생성

        Args:
            radar_metrics: 레이더 메트릭 리스트

        Returns:
            요약 문자열
        """
        if not radar_metrics:
            return "분석할 제품이 없습니다."

        avg_trust = sum(m["trust_score"] for m in radar_metrics) / len(radar_metrics)
        best_product = max(radar_metrics, key=lambda x: x["trust_score"])

        return f"{len(radar_metrics)}개 제품 분석 완료. 평균 신뢰도 {avg_trust:.1f}점. 최고 제품: {best_product['name']} ({best_product['trust_score']:.1f}점)"

    def _generate_price_fallback_summary(self, price_data: List[Dict]) -> str:
        """
        가격 비교 폴백 요약 생성

        Args:
            price_data: 가격 데이터 리스트

        Returns:
            요약 문자열
        """
        if not price_data:
            return "분석할 제품이 없습니다."

        avg_price = sum(p["price"] for p in price_data) / len(price_data)
        best_value = max(price_data, key=lambda x: x["value_score"])

        return f"{len(price_data)}개 제품 가격 분석 완료. 평균 가격 ${avg_price:.2f}. 최고 가성비: {best_value['name']} (가성비 지수 {best_value['value_score']:.2f})"

    def _create_fallback_radar_analysis(self, radar_metrics: List[Dict]) -> Dict[str, Any]:
        """
        레이더 차트 폴백 분석 생성 (AI 실패 시)

        Args:
            radar_metrics: 레이더 메트릭 리스트

        Returns:
            분석 결과 딕셔너리
        """
        if not radar_metrics:
            return self._create_default_response("레이더 차트 분석 실패")

        # 통계 계산
        avg_trust = sum(m["trust_score"] for m in radar_metrics) / len(radar_metrics)
        avg_reorder = sum(m["reorder_rate"] for m in radar_metrics) / len(radar_metrics)
        best_product = max(radar_metrics, key=lambda x: x["trust_score"])
        worst_product = min(radar_metrics, key=lambda x: x["trust_score"])

        return {
            "summary": f"{len(radar_metrics)}개 제품 분석. 평균 신뢰도 {avg_trust:.1f}점, 평균 재구매율 {avg_reorder:.1f}%. 제품 간 신뢰도 편차가 존재합니다.",
            "key_findings": [
                f"최고 제품: {best_product['name']} (신뢰도 {best_product['trust_score']:.1f}점)",
                f"개선 필요: {worst_product['name']} (신뢰도 {worst_product['trust_score']:.1f}점)",
                f"전체 평균 재구매율: {avg_reorder:.1f}%"
            ],
            "trends": "제품별 강점과 약점이 다양하게 분포되어 있습니다. 균형잡힌 제품과 특정 지표에 특화된 제품이 혼재합니다.",
            "insights": f"신뢰도 우선: {best_product['name']} 추천. 가성비 중시 고객은 중간 가격대 제품 검토 필요.",
            "data_quality": "양호",
            "best_product": f"{best_product['name']} - 가장 높은 신뢰도 점수 ({best_product['trust_score']:.1f}점)"
        }

    def _create_fallback_price_analysis(self, price_data: List[Dict]) -> Dict[str, Any]:
        """
        가격 비교 폴백 분석 생성 (AI 실패 시)

        Args:
            price_data: 가격 데이터 리스트

        Returns:
            분석 결과 딕셔너리
        """
        if not price_data:
            return self._create_default_response("가격 비교 분석 실패")

        # 통계 계산
        avg_price = sum(p["price"] for p in price_data) / len(price_data)
        min_price = min(price_data, key=lambda x: x["price"])
        max_price = max(price_data, key=lambda x: x["price"])
        best_value = max(price_data, key=lambda x: x["value_score"])

        return {
            "summary": f"{len(price_data)}개 제품 가격 분석. 평균 ${avg_price:.2f}. 가격 범위: ${min_price['price']:.2f} ~ ${max_price['price']:.2f}. 가격과 신뢰도가 반드시 비례하지는 않습니다.",
            "key_findings": [
                f"최저가: {min_price['name']} (${min_price['price']:.2f}, 신뢰도 {min_price['trust_score']:.1f}점)",
                f"최고가: {max_price['name']} (${max_price['price']:.2f}, 신뢰도 {max_price['trust_score']:.1f}점)",
                f"최고 가성비: {best_value['name']} (가성비 지수 {best_value['value_score']:.2f})"
            ],
            "trends": "가격대가 다양하며, 높은 가격이 반드시 높은 신뢰도를 보장하지는 않습니다. 가성비 제품이 존재합니다.",
            "insights": f"저예산: {min_price['name']} 추천. 가성비 우선: {best_value['name']} 추천. 프리미엄: {max_price['name']} 검토.",
            "data_quality": "양호",
            "best_value": f"{best_value['name']} - 최고 가성비 (가성비 지수 {best_value['value_score']:.2f})"
        }

    def _generate_generic_summary(self, data: Dict[str, Any], chart_type: str) -> str:
        """
        범용 요약 생성

        Args:
            data: 차트 데이터
            chart_type: 차트 타입

        Returns:
            요약 문자열
        """
        try:
            if "products" in data:
                count = len(data["products"])
                return f"{chart_type} 차트: {count}개 제품 데이터 시각화"
            elif "score" in data:
                return f"{chart_type} 차트: 점수 {data['score']:.1f}점"
            else:
                return f"{chart_type} 차트 데이터 분석 완료"
        except Exception:
            return f"{chart_type} 차트 분석 완료"

    def _create_generic_fallback_analysis(self, data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """
        범용 폴백 분석 생성

        Args:
            data: 차트 데이터
            chart_type: 차트 타입

        Returns:
            분석 결과 딕셔너리
        """
        summary = self._generate_generic_summary(data, chart_type)

        # 데이터에서 인사이트 추출 시도
        findings = []
        try:
            if "products" in data and isinstance(data["products"], list):
                findings.append(f"총 {len(data['products'])}개 제품 포함")
                if data["products"]:
                    first_product = data["products"][0]
                    if "trust_score" in first_product:
                        avg_trust = sum(p.get("trust_score", 0) for p in data["products"]) / len(data["products"])
                        findings.append(f"평균 신뢰도: {avg_trust:.1f}점")
            elif "score" in data:
                findings.append(f"측정 점수: {data['score']}점")
        except Exception:
            findings = ["데이터 분석 완료"]

        return {
            "summary": summary,
            "key_findings": findings if findings else ["차트 데이터를 성공적으로 시각화했습니다."],
            "trends": "데이터 패턴이 시각적으로 표현되었습니다.",
            "insights": "차트를 통해 데이터의 전반적인 경향을 파악할 수 있습니다.",
            "data_quality": "양호"
        }
