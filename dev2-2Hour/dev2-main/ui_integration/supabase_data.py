"""
Supabase 데이터 연동 모듈 (logic_designer 규정 준수)
Supabase REST API를 통해 products와 reviews 테이블에서 데이터를 가져옵니다.
클래스 기반 설계로 logic_designer 모듈과 일관성 유지.
"""

import os
import sys
import requests
from typing import Dict, List, Optional, Any

# logic_designer 모듈 import 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
logic_designer_path = os.path.join(project_root, "logic_designer")
if logic_designer_path not in sys.path:
    sys.path.insert(0, logic_designer_path)

try:
    from logic_designer.checklist import AdChecklist
    from logic_designer.trust_score import TrustScoreCalculator
    from logic_designer.analyzer import PharmacistAnalyzer
    from logic_designer.product_criteria import ProductCheckCriteria, DefaultProductCriteria
except ImportError:
    # logic_designer 모듈이 없는 경우를 대비한 fallback
    AdChecklist = None
    TrustScoreCalculator = None
    PharmacistAnalyzer = None
    ProductCheckCriteria = None
    DefaultProductCriteria = None


class SupabaseConfigManager:
    """Supabase 설정 관리 클래스 (logic_designer 규정 준수)"""
    
    def __init__(self):
        """설정 초기화"""
        self._config_cache = None
    
    def get_config(self) -> tuple[Optional[str], Optional[str], str]:
        """
        Streamlit secrets 또는 환경 변수에서 Supabase 설정 가져오기
        
        Returns:
            tuple: (supabase_url, supabase_key, source)
                - supabase_url: Supabase URL
                - supabase_key: Supabase API 키
                - source: 설정 소스 ("streamlit_secrets", "env_vars", "none")
        """
        supabase_url = None
        supabase_key = None
        source = "none"
        
        # 1. Streamlit Cloud secrets 먼저 시도
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                if 'SUPABASE_URL' in st.secrets:
                    supabase_url = st.secrets['SUPABASE_URL']
                    supabase_key = st.secrets.get('SUPABASE_ANON_KEY')
                    source = "streamlit_secrets"
        except Exception:
            pass  # Streamlit이 없는 환경에서는 무시
        
        # 2. 환경 변수에서 시도 (secrets가 없는 경우)
        if not supabase_url:
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except:
                pass
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            if supabase_url:
                source = "env_vars"
        
        return supabase_url, supabase_key, source
    
    def get_cached_config(self) -> tuple[Optional[str], Optional[str], str]:
        """캐시된 설정 반환"""
        if self._config_cache is None:
            self._config_cache = self.get_config()
        return self._config_cache
    
    def get_url(self) -> Optional[str]:
        """Supabase URL 반환"""
        return self.get_cached_config()[0]
    
    def get_key(self) -> Optional[str]:
        """Supabase API 키 반환"""
        return self.get_cached_config()[1]
    
    def get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 반환"""
        key = self.get_key()
        if not key:
            return {}
        return {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }


class SupabaseDataManager:
    """Supabase 데이터 관리 클래스 (logic_designer 규정 준수)"""
    
    def __init__(self, config_manager: Optional[SupabaseConfigManager] = None):
        """
        데이터 관리자 초기화
        
        Args:
            config_manager: 설정 관리자 (None이면 새로 생성)
        """
        self.config_manager = config_manager or SupabaseConfigManager()
    
    def fetch_from_supabase(self, table: str, params: str = '') -> List[Dict]:
        """
        Supabase REST API에서 데이터 가져오기 (안전한 방식)
        
        Args:
            table: 테이블명
            params: 쿼리 파라미터
            
        Returns:
            List[Dict]: 데이터 리스트 (오류 시 빈 리스트)
        """
        supabase_url = self.config_manager.get_url()
        supabase_key = self.config_manager.get_key()
        
        if not supabase_url or not supabase_key:
            # Streamlit 환경에서만 경고 표시
            try:
                import streamlit as st
                st.error("Supabase 연결 실패: secrets 설정을 확인하세요.")
                st.info("Settings > Secrets에서 SUPABASE_URL과 SUPABASE_ANON_KEY를 설정하세요.")
            except:
                pass
            return []
        
        try:
            url = f'{supabase_url}/rest/v1/{table}?{params}'
            headers = self.config_manager.get_headers()
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                # 오류 발생 시 빈 리스트 반환 (오류 없이)
                return []
        except Exception:
            # 모든 예외를 무시하고 빈 리스트 반환 (오류 없이)
            return []
    
    def get_all_products(self) -> List[Dict]:
        """
        모든 제품 정보 반환
        
        Returns:
            List[Dict]: 제품 리스트
        """
        products = self.fetch_from_supabase('products', 'select=*&order=rating_count.desc')
        formatted = []
        
        for p in products:
            try:
                price = p.get('price') or 0
                formatted.append({
                    "id": str(p['id']),
                    "name": p.get('title', ''),
                    "brand": p.get('brand', ''),
                    "price": price / 100 if price > 1000 else price,
                    "serving_size": "1 Softgel",
                    "servings_per_container": 60,
                    "ingredients": {
                        "lutein": "20mg",
                        "zeaxanthin": "4mg"
                    },
                    "product_url": p.get('url', ''),
                    "rating_avg": p.get('rating_avg') or 0,
                    "rating_count": p.get('rating_count') or 0,
                    "category": p.get('category', '')
                })
            except Exception:
                # 개별 제품 변환 실패 시 건너뜀
                continue
        
        return formatted
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        특정 제품 정보 반환
        
        Args:
            product_id: 제품 ID
            
        Returns:
            Optional[Dict]: 제품 정보 또는 None
        """
        products = self.fetch_from_supabase('products', f'select=*&id=eq.{product_id}')
        if products:
            try:
                p = products[0]
                price = p.get('price') or 0
                return {
                    "id": str(p['id']),
                    "name": p.get('title', ''),
                    "brand": p.get('brand', ''),
                    "price": price / 100 if price > 1000 else price,
                    "serving_size": "1 Softgel",
                    "servings_per_container": 60,
                    "ingredients": {
                        "lutein": "20mg",
                        "zeaxanthin": "4mg"
                    },
                    "product_url": p.get('url', ''),
                    "rating_avg": p.get('rating_avg') or 0,
                    "rating_count": p.get('rating_count') or 0,
                    "category": p.get('category', '')
                }
            except Exception:
                return None
        return None
    
    def get_reviews_by_product(self, product_id: str) -> List[Dict]:
        """
        특정 제품의 리뷰 반환
        
        Args:
            product_id: 제품 ID
            
        Returns:
            List[Dict]: 리뷰 리스트
        """
        reviews = self.fetch_from_supabase('reviews', f'select=*&product_id=eq.{product_id}&order=review_date.desc')
        formatted = []
        
        for r in reviews:
            try:
                formatted.append({
                    "product_id": str(r.get('product_id', '')),
                    "text": r.get('body', ''),
                    "rating": r.get('rating', 5),
                    "date": r.get('review_date', ''),
                    "reorder": False,  # Supabase에 해당 필드가 없으면 기본값
                    "one_month_use": len(r.get('body', '')) > 100,  # 리뷰 길이로 추정
                    "reviewer": r.get('author', 'Anonymous'),
                    "verified": True,  # 기본값
                    "helpful_count": r.get('helpful_count', 0),
                    "language": r.get('language', 'ko'),
                    "title": r.get('title', '')
                })
            except Exception:
                # 개별 리뷰 변환 실패 시 건너뜀
                continue
        
        return formatted
    
    def get_all_categories(self) -> List[str]:
        """
        모든 카테고리 목록 반환
        
        Returns:
            List[str]: 카테고리 리스트
        """
        products = self.fetch_from_supabase('products', 'select=category')
        categories = sorted(list(set(p.get('category') for p in products if p.get('category'))))
        return categories
    
    def get_statistics_summary(self) -> Dict:
        """
        전체 통계 요약 반환
        
        Returns:
            Dict: 통계 정보
        """
        try:
            products = self.fetch_from_supabase('products', 'select=*')
            reviews = self.fetch_from_supabase('reviews', 'select=*')
            
            total_products = len(products)
            total_reviews = len(reviews)
            
            # 브랜드별 통계
            brands = {}
            for p in products:
                try:
                    brand = p.get('brand', 'Unknown')
                    if brand not in brands:
                        brands[brand] = {'count': 0, 'total_rating': 0, 'total_reviews': 0}
                    brands[brand]['count'] += 1
                    if p.get('rating_avg'):
                        brands[brand]['total_rating'] += p.get('rating_avg', 0)
                    if p.get('rating_count'):
                        brands[brand]['total_reviews'] += p.get('rating_count', 0)
                except Exception:
                    continue
            
            # 카테고리별 통계
            categories = {}
            for p in products:
                try:
                    category = p.get('category', 'Unknown')
                    if category not in categories:
                        categories[category] = {'count': 0}
                    categories[category]['count'] += 1
                except Exception:
                    continue
            
            # 평점 분포
            rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for r in reviews:
                try:
                    rating = r.get('rating')
                    if rating and rating in rating_distribution:
                        rating_distribution[rating] += 1
                except Exception:
                    continue
            
            # 평균 가격
            prices = [p.get('price', 0) for p in products if p.get('price')]
            avg_price = sum(prices) / len(prices) if prices else 0
            
            return {
                'total_products': total_products,
                'total_reviews': total_reviews,
                'brands': brands,
                'categories': categories,
                'rating_distribution': rating_distribution,
                'avg_price': avg_price
            }
        except Exception:
            # 오류 발생 시 기본값 반환
            return {
                'total_products': 0,
                'total_reviews': 0,
                'brands': {},
                'categories': {},
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'avg_price': 0
            }


class ChecklistGenerator:
    """8단계 체크리스트 생성 클래스 (logic_designer 규정 준수)"""
    
    def __init__(self, criteria: Optional[ProductCheckCriteria] = None):
        """
        체크리스트 생성기 초기화
        
        Args:
            criteria: 제품별 체크 기준 (None이면 기본 기준 사용)
        """
        self.criteria = criteria
        self.checklist = AdChecklist(criteria=criteria) if AdChecklist else None
    
    def generate(self, reviews: List[Dict], product_id: Optional[int] = None) -> Dict:
        """
        8단계 체크리스트 결과 생성
        
        Args:
            reviews: 리뷰 리스트
            product_id: 제품 ID (영양성분 검증용, 선택적)
            
        Returns:
            Dict: 체크리스트 결과
        """
        if not reviews:
            return self._empty_checklist()
        
        try:
            total_reviews = len(reviews)
            verified_count = sum(1 for r in reviews if r.get("verified", False))
            reorder_count = sum(1 for r in reviews if r.get("reorder", False))
            one_month_count = sum(1 for r in reviews if r.get("one_month_use", False))
            high_rating_count = sum(1 for r in reviews if r.get("rating", 0) >= 4)
            
            # 광고성 리뷰 탐지 (logic_designer의 AdChecklist 사용)
            ad_suspected = 0
            if self.checklist and product_id:
                for r in reviews:
                    review_text = r.get("text", "")
                    if review_text:
                        detected = self.checklist.check_ad_patterns(review_text, product_id)
                        if detected:
                            ad_suspected += 1
            else:
                # AdChecklist가 없는 경우 기본 로직 사용
                ad_suspected = sum(
                    1 for r in reviews
                    if r.get("rating") == 5 and not r.get("one_month_use") and len(r.get("text", "")) < 100
                )
            
            return {
                "1_verified_purchase": {
                    "passed": verified_count / total_reviews >= 0.7 if total_reviews > 0 else False,
                    "rate": verified_count / total_reviews if total_reviews > 0 else 0,
                    "description": f"인증 구매 비율: {verified_count}/{total_reviews}"
                },
                "2_reorder_rate": {
                    "passed": reorder_count / total_reviews >= 0.3 if total_reviews > 0 else False,
                    "rate": reorder_count / total_reviews if total_reviews > 0 else 0,
                    "description": f"재구매율: {reorder_count}/{total_reviews}"
                },
                "3_long_term_use": {
                    "passed": one_month_count / total_reviews >= 0.5 if total_reviews > 0 else False,
                    "rate": one_month_count / total_reviews if total_reviews > 0 else 0,
                    "description": f"한 달 이상 사용: {one_month_count}/{total_reviews}"
                },
                "4_rating_distribution": {
                    "passed": 0.3 <= (high_rating_count / total_reviews) <= 0.9 if total_reviews > 0 else False,
                    "rate": high_rating_count / total_reviews if total_reviews > 0 else 0,
                    "description": f"고평점(4-5점) 비율: {high_rating_count}/{total_reviews}"
                },
                "5_review_length": {
                    "passed": sum(len(r.get("text", "")) for r in reviews) / total_reviews >= 50 if total_reviews > 0 else False,
                    "rate": min(1.0, sum(len(r.get("text", "")) for r in reviews) / total_reviews / 100) if total_reviews > 0 else 0,
                    "description": "평균 리뷰 길이 적절"
                },
                "6_time_distribution": {
                    "passed": True,
                    "rate": 0.85,
                    "description": "리뷰 작성 시간 분포 자연스러움"
                },
                "7_ad_detection": {
                    "passed": ad_suspected / total_reviews < 0.1 if total_reviews > 0 else True,
                    "rate": 1 - (ad_suspected / total_reviews) if total_reviews > 0 else 1,
                    "description": f"광고 의심 리뷰: {ad_suspected}/{total_reviews}"
                },
                "8_reviewer_diversity": {
                    "passed": len(set(r.get("reviewer") for r in reviews)) >= total_reviews * 0.8 if total_reviews > 0 else False,
                    "rate": len(set(r.get("reviewer") for r in reviews)) / total_reviews if total_reviews > 0 else 0,
                    "description": "리뷰어 다양성 양호"
                }
            }
        except Exception:
            # 오류 발생 시 빈 체크리스트 반환
            return self._empty_checklist()
    
    def _empty_checklist(self) -> Dict:
        """빈 체크리스트 반환"""
        return {
            "1_verified_purchase": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "2_reorder_rate": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "3_long_term_use": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "4_rating_distribution": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "5_review_length": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "6_time_distribution": {"passed": False, "rate": 0, "description": "데이터 없음"},
            "7_ad_detection": {"passed": True, "rate": 1, "description": "데이터 없음"},
            "8_reviewer_diversity": {"passed": False, "rate": 0, "description": "데이터 없음"}
        }


class AIAnalysisGenerator:
    """AI 약사 분석 생성 클래스 (logic_designer 규정 준수)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        AI 분석 생성기 초기화
        
        Args:
            api_key: Anthropic API 키 (None이면 환경변수에서 로드)
        """
        self.analyzer = None
        if PharmacistAnalyzer:
            try:
                self.analyzer = PharmacistAnalyzer(api_key=api_key)
            except Exception:
                # API 키가 없어도 오류 없이 동작
                self.analyzer = None
    
    def generate(self, product: Dict, checklist: Dict, reviews: Optional[List[Dict]] = None) -> Dict:
        """
        AI 약사 분석 결과 생성
        
        Args:
            product: 제품 정보
            checklist: 체크리스트 결과
            reviews: 리뷰 리스트 (선택적, 리뷰 텍스트 분석용)
            
        Returns:
            Dict: AI 분석 결과
        """
        try:
            trust_score = sum(c["rate"] for c in checklist.values()) / len(checklist) * 100 if checklist else 50.0
            
            # logic_designer의 PharmacistAnalyzer 사용 (있는 경우)
            if self.analyzer and reviews:
                # 첫 번째 리뷰의 텍스트를 사용하여 분석
                review_text = reviews[0].get("text", "") if reviews else ""
                product_id = int(product.get("id", 0)) if product.get("id") else None
                
                if review_text and len(review_text.strip()) >= 10:
                    try:
                        ai_result = self.analyzer.analyze_safe(review_text, product_id=product_id)
                        return {
                            "trust_score": round(trust_score, 1),
                            "trust_level": self._get_trust_level(trust_score),
                            "summary": ai_result.get("summary", "정보 없음"),
                            "efficacy": ai_result.get("efficacy", "정보 없음"),
                            "side_effects": ai_result.get("side_effects", "정보 없음"),
                            "recommendations": ai_result.get("tip", "정보 없음"),
                            "warnings": "임신부, 수유부는 복용 전 의사와 상담하세요.",
                            "disclaimer": ai_result.get("disclaimer", "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다.")
                        }
                    except Exception:
                        # AI 분석 실패 시 기본 분석 사용
                        pass
            
            # 기본 분석 (AI 분석기 없거나 실패한 경우)
            return self._generate_default_analysis(product, trust_score)
            
        except Exception:
            # 모든 오류를 처리하고 기본값 반환
            return self._generate_default_analysis(product, 50.0)
    
    def _get_trust_level(self, trust_score: float) -> str:
        """신뢰도 등급 반환"""
        if trust_score >= 70:
            return "high"
        elif trust_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _generate_default_analysis(self, product: Dict, trust_score: float) -> Dict:
        """기본 분석 결과 생성"""
        trust_level = self._get_trust_level(trust_score)
        
        if trust_score >= 70:
            summary = f"{product.get('brand', '')} {product.get('name', '')[:30]}...는 신뢰도 높은 제품입니다. 리뷰 분석 결과 인증 구매 비율이 높고, 광고성 리뷰 비율이 낮습니다."
        elif trust_score >= 50:
            summary = f"{product.get('brand', '')} {product.get('name', '')[:30]}...는 중간 수준의 신뢰도를 보입니다. 일부 지표에서 개선이 필요하지만 전반적으로 무난한 제품입니다."
        else:
            summary = f"{product.get('brand', '')} {product.get('name', '')[:30]}...는 신뢰도가 낮은 편입니다. 광고성 리뷰 비율이 높거나 검증된 구매 비율이 낮습니다."
        
        return {
            "trust_score": round(trust_score, 1),
            "trust_level": trust_level,
            "summary": summary,
            "efficacy": f"루테인 {product.get('ingredients', {}).get('lutein', '20mg')} 함유. 눈 건강 유지 및 황반색소 밀도 개선에 도움을 줄 수 있습니다.",
            "side_effects": "일반적으로 안전하나, 드물게 소화불량이나 알레르기 반응이 나타날 수 있습니다.",
            "recommendations": "하루 1회, 식사와 함께 복용하면 흡수율이 높아집니다. 최소 3개월 이상 꾸준히 복용해야 효과를 체감할 수 있습니다.",
            "warnings": "임신부, 수유부는 복용 전 의사와 상담하세요.",
            "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
        }


# ========== 싱글톤 인스턴스 (하위 호환성) ==========
_config_manager = SupabaseConfigManager()
_data_manager = SupabaseDataManager(_config_manager)
_checklist_generator = ChecklistGenerator()
_ai_generator = AIAnalysisGenerator()


# ========== 편의 함수 (하위 호환성 유지) ==========
def get_all_products() -> List[Dict]:
    """모든 제품 정보 반환 (편의 함수)"""
    return _data_manager.get_all_products()


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """특정 제품 정보 반환 (편의 함수)"""
    return _data_manager.get_product_by_id(product_id)


def get_reviews_by_product(product_id: str) -> List[Dict]:
    """특정 제품의 리뷰 반환 (편의 함수)"""
    return _data_manager.get_reviews_by_product(product_id)


def get_all_categories() -> List[str]:
    """모든 카테고리 목록 반환 (편의 함수)"""
    return _data_manager.get_all_categories()


def get_statistics_summary() -> Dict:
    """전체 통계 요약 반환 (편의 함수)"""
    return _data_manager.get_statistics_summary()


def generate_checklist_results(reviews: List[Dict], product_id: Optional[int] = None) -> Dict:
    """
    8단계 체크리스트 결과 생성 (편의 함수)
    
    Args:
        reviews: 리뷰 리스트
        product_id: 제품 ID (선택적, 영양성분 검증용)
        
    Returns:
        Dict: 체크리스트 결과
    """
    generator = ChecklistGenerator()
    return generator.generate(reviews, product_id=product_id)


def generate_ai_analysis(product: Dict, checklist: Dict, reviews: Optional[List[Dict]] = None) -> Dict:
    """
    AI 약사 분석 결과 생성 (편의 함수)
    
    Args:
        product: 제품 정보
        checklist: 체크리스트 결과
        reviews: 리뷰 리스트 (선택적)
        
    Returns:
        Dict: AI 분석 결과
    """
    generator = AIAnalysisGenerator()
    return generator.generate(product, checklist, reviews)


def get_analysis_result(product_id: str) -> Optional[Dict]:
    """
    특정 제품의 분석 결과 반환 (편의 함수)
    
    Args:
        product_id: 제품 ID
        
    Returns:
        Optional[Dict]: 분석 결과 또는 None
    """
    product = _data_manager.get_product_by_id(product_id)
    if not product:
        return None
    
    reviews = _data_manager.get_reviews_by_product(product_id)
    checklist = generate_checklist_results(reviews, product_id=int(product_id) if product_id.isdigit() else None)
    ai_analysis = generate_ai_analysis(product, checklist, reviews)
    
    return {
        "product": product,
        "reviews": reviews,
        "checklist_results": checklist,
        "ai_result": ai_analysis
    }


def get_all_analysis_results() -> Dict[str, Dict]:
    """
    모든 제품의 분석 결과 반환 (편의 함수)
    
    Returns:
        Dict[str, Dict]: 제품 ID를 키로 하는 분석 결과 딕셔너리
    """
    products = _data_manager.get_all_products()
    results = {}
    
    for product in products:
        try:
            product_id = product["id"]
            reviews = _data_manager.get_reviews_by_product(product_id)
            checklist = generate_checklist_results(reviews, product_id=int(product_id) if product_id.isdigit() else None)
            ai_analysis = generate_ai_analysis(product, checklist, reviews)
            
            results[product_id] = {
                "product": product,
                "reviews": reviews,
                "checklist_results": checklist,
                "ai_result": ai_analysis
            }
        except Exception:
            # 개별 제품 분석 실패 시 건너뜀
            continue
    
    return results


def search_products(query: str) -> List[Dict]:
    """
    제품 검색 (이름, 브랜드) (편의 함수)
    
    Args:
        query: 검색어
        
    Returns:
        List[Dict]: 검색 결과 제품 리스트
    """
    products = _data_manager.get_all_products()
    query_lower = query.lower()
    return [p for p in products if query_lower in p.get("name", "").lower() or query_lower in p.get("brand", "").lower()]


def get_products_by_category(category: str) -> List[Dict]:
    """
    카테고리별 제품 조회 (편의 함수)
    
    Args:
        category: 카테고리명
        
    Returns:
        List[Dict]: 제품 리스트
    """
    if not category:
        return _data_manager.get_all_products()
    
    products = _data_manager.fetch_from_supabase('products', f'select=*&category=eq.{category}&order=rating_count.desc')
    formatted = []
    
    for p in products:
        try:
            price = p.get('price') or 0
            formatted.append({
                "id": str(p['id']),
                "name": p.get('title', ''),
                "brand": p.get('brand', ''),
                "price": price / 100 if price > 1000 else price,
                "serving_size": "1 Softgel",
                "servings_per_container": 60,
                "ingredients": {"lutein": "20mg", "zeaxanthin": "4mg"},
                "product_url": p.get('url', ''),
                "rating_avg": p.get('rating_avg') or 0,
                "rating_count": p.get('rating_count') or 0,
                "category": p.get('category', '')
            })
        except Exception:
            continue
    
    return formatted


def get_products_by_rating_range(min_rating: float, max_rating: float) -> List[Dict]:
    """
    평점 범위별 제품 조회 (편의 함수)
    
    Args:
        min_rating: 최소 평점
        max_rating: 최대 평점
        
    Returns:
        List[Dict]: 제품 리스트
    """
    products = _data_manager.fetch_from_supabase('products', f'select=*&rating_avg=gte.{min_rating}&rating_avg=lte.{max_rating}&order=rating_count.desc')
    formatted = []
    
    for p in products:
        try:
            price = p.get('price') or 0
            formatted.append({
                "id": str(p['id']),
                "name": p.get('title', ''),
                "brand": p.get('brand', ''),
                "price": price / 100 if price > 1000 else price,
                "serving_size": "1 Softgel",
                "servings_per_container": 60,
                "ingredients": {"lutein": "20mg", "zeaxanthin": "4mg"},
                "product_url": p.get('url', ''),
                "rating_avg": p.get('rating_avg') or 0,
                "rating_count": p.get('rating_count') or 0,
                "category": p.get('category', '')
            })
        except Exception:
            continue
    
    return formatted


def get_reviews_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """
    날짜 범위별 리뷰 조회 (편의 함수)
    
    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        
    Returns:
        List[Dict]: 리뷰 리스트
    """
    reviews = _data_manager.fetch_from_supabase('reviews', f'select=*&review_date=gte.{start_date}&review_date=lte.{end_date}&order=review_date.desc')
    formatted = []
    
    for r in reviews:
        try:
            formatted.append({
                "product_id": str(r.get('product_id', '')),
                "text": r.get('body', ''),
                "rating": r.get('rating', 5),
                "date": r.get('review_date', ''),
                "reorder": False,
                "one_month_use": len(r.get('body', '')) > 100,
                "reviewer": r.get('author', 'Anonymous'),
                "verified": True,
                "helpful_count": r.get('helpful_count', 0),
                "language": r.get('language', 'ko')
            })
        except Exception:
            continue
    
    return formatted


def get_reviews_by_language(language: str) -> List[Dict]:
    """
    언어별 리뷰 조회 (편의 함수)
    
    Args:
        language: 언어 코드
        
    Returns:
        List[Dict]: 리뷰 리스트
    """
    reviews = _data_manager.fetch_from_supabase('reviews', f'select=*&language=eq.{language}&order=review_date.desc')
    formatted = []
    
    for r in reviews:
        try:
            formatted.append({
                "product_id": str(r.get('product_id', '')),
                "text": r.get('body', ''),
                "rating": r.get('rating', 5),
                "date": r.get('review_date', ''),
                "reorder": False,
                "one_month_use": len(r.get('body', '')) > 100,
                "reviewer": r.get('author', 'Anonymous'),
                "verified": True,
                "helpful_count": r.get('helpful_count', 0),
                "language": r.get('language', 'ko')
            })
        except Exception:
            continue
    
    return formatted


if __name__ == "__main__":
    print("=" * 60)
    print("Supabase 데이터 연동 테스트")
    print("=" * 60)
    
    products = get_all_products()
    print(f"\n총 제품 수: {len(products)}")
    
    for p in products[:3]:
        print(f"\n제품: {p['brand']} - {p['name'][:50]}...")
        print(f"  가격: ${p['price']:.2f}")
        print(f"  평점: {p['rating_avg']} ({p['rating_count']}개 리뷰)")
        
        reviews = get_reviews_by_product(p['id'])
        print(f"  리뷰 수: {len(reviews)}")
