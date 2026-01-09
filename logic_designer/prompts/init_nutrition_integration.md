# __init__.py 영양성분 DB 통합 프롬프트

## 목적
식품의약품안전처 건강기능식품 영양성분 DB를 활용하여 `__init__.py`의 통합 분석 함수가 더욱 정확하고 포괄적인 결과를 제공하도록 개선합니다.

## 개선 방향

### 1. 통합 분석 함수에 product_id 추가

**현재 문제점:**
- `analyze()` 함수가 리뷰 텍스트만으로 분석
- 제품 정보를 활용하지 못함
- 영양성분 기반 검증 불가

**개선 방안:**

```python
def analyze(
    review_text: str,
    product_id: Optional[int] = None,
    length_score: float = 50,
    repurchase_score: float = 50,
    monthly_use_score: float = 50,
    photo_score: float = 0,
    consistency_score: float = 50,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-5-20250929",
    use_nutrition_validation: bool = True
) -> Dict:
    """
    리뷰 종합 분석 통합 함수 (영양성분 DB 통합, 안전한 방식)
    
    중요: 영양성분 DB가 없어도 오류 없이 동작합니다.
    리뷰가 짧거나 없어도 적절히 처리합니다.
    """
    """
    리뷰 종합 분석 통합 함수 (영양성분 DB 통합)
    
    검증 로직과 AI 분석을 순차적으로 수행하여 최종 결과를 반환합니다.
    영양성분 DB 정보를 활용하여 더욱 정확한 검증과 분석을 수행합니다.

    Args:
        review_text: 분석할 리뷰 텍스트
        product_id: 제품 ID (제공 시 영양성분 정보 활용)
        length_score: 길이 점수 (기본값: 50)
        repurchase_score: 재구매 점수 (기본값: 50)
        monthly_use_score: 한달 사용 점수 (기본값: 50)
        photo_score: 사진 점수 (기본값: 0)
        consistency_score: 일치도 점수 (기본값: 50)
        api_key: Anthropic API 키 (선택)
        model: 사용할 Claude 모델 (기본값: claude-sonnet-4-5-20250929)
        use_nutrition_validation: 영양성분 검증 사용 여부 (기본값: True)

    Returns:
        Dict: {
            "validation": {
                "trust_score": 최종 신뢰도 점수,
                "is_ad": 광고 여부,
                "reasons": 감점 사유 리스트,
                "base_score": 기본 점수,
                "penalty": 감점 점수,
                "detected_count": 감지된 항목 개수,
                "nutrition_validation": 영양성분 검증 결과 (있는 경우)
            },
            "analysis": {
                "summary": "리뷰 요약",
                "efficacy": "효능 관련 내용",
                "side_effects": "부작용 관련 내용",
                "tip": "약사의 핵심 조언",
                "disclaimer": "부인 공지",
                "ingredient_validation": 성분 검증 결과 (있는 경우)
            } 또는 None (광고인 경우)
        }
    """
    # 입력 검증: 리뷰가 None이거나 빈 문자열
    if not review_text:
        return {
            "error": "REVIEW_EMPTY",
            "message": "리뷰가 비어있습니다.",
            "validation": None,
            "analysis": None
        }
    
    # 리뷰가 너무 짧은 경우 (3자 미만)
    if len(review_text.strip()) < 3:
        return {
            "error": "REVIEW_TOO_SHORT",
            "message": "리뷰가 너무 짧습니다 (최소 3자 이상)",
            "validation": None,
            "analysis": None
        }
    
    # 리뷰가 짧은 경우 (3-10자): 기본 검사만 수행
    is_short_review = len(review_text.strip()) < 10

    # 1단계: 광고 패턴 검사 (영양성분 DB 통합, 안전한 방식)
    checklist = AdChecklist()
    try:
        detected_issues = checklist.check_ad_patterns(
            review_text,
            product_id if (use_nutrition_validation and product_id) else None
        )
        penalty_count = len(detected_issues)
    except Exception:
        # 체크리스트 검사 실패 시 빈 결과로 처리
        detected_issues = {}
        penalty_count = 0

    # 2단계: 신뢰도 점수 계산 (영양성분 일치도 포함, 안전한 방식)
    calculator = TrustScoreCalculator()
    try:
        score_result = calculator.calculate_final_score(
            length_score=length_score,
            repurchase_score=repurchase_score,
            monthly_use_score=monthly_use_score,
            photo_score=photo_score,
            consistency_score=consistency_score,
            penalty_count=penalty_count,
            review_text=review_text if (use_nutrition_validation and not is_short_review) else None,
            product_id=product_id if (use_nutrition_validation and product_id) else None,
            use_nutrition_score=use_nutrition_validation and not is_short_review
        )
    except Exception:
        # 점수 계산 실패 시 기본값 사용
        score_result = calculator.calculate_final_score(
            length_score=length_score,
            repurchase_score=repurchase_score,
            monthly_use_score=monthly_use_score,
            photo_score=photo_score,
            consistency_score=consistency_score,
            penalty_count=penalty_count,
            use_nutrition_score=False  # 영양성분 점수 비활성화
        )

    # 3단계: 광고 여부 판별
    is_ad = calculator.is_ad(
        final_score=score_result["final_score"],
        penalty_count=penalty_count
    )

    # 감점 사유 리스트 생성
    reasons = [f"{num}. {name}" for num, name in detected_issues.items()]

    validation_result = {
        "trust_score": score_result["final_score"],
        "is_ad": is_ad,
        "reasons": reasons,
        "base_score": score_result["base_score"],
        "penalty": score_result["penalty"],
        "detected_count": penalty_count,
        "raw_scores": score_result["raw_scores"]
    }
    
    # 영양성분 검증 결과 추가 (있는 경우, 안전한 방식)
    if use_nutrition_validation and product_id and not is_short_review:
        try:
            nutrition_validation = self._get_nutrition_validation(
                review_text,
                product_id
            )
            if nutrition_validation:
                validation_result["nutrition_validation"] = nutrition_validation
        except Exception:
            # 영양성분 검증 실패 시 무시 (오류 없이)
            pass

    # 4단계: 광고가 아닌 경우에만 AI 분석 수행 (짧은 리뷰는 제외)
    analysis_result = None
    if not is_ad and not is_short_review:
        try:
            analyzer = PharmacistAnalyzer(api_key=api_key)
            analysis_result = analyzer.analyze_safe(
                review_text,
                product_id if (product_id and use_nutrition_validation) else None,  # 영양성분 정보 전달 (있는 경우만)
                model
            )
        except Exception as e:
            analysis_result = {
                "error": "ANALYSIS_ERROR",
                "message": str(e),
                "summary": "분석 실패",
                "efficacy": "정보 없음",
                "side_effects": "정보 없음",
                "tip": "분석 중 오류가 발생했습니다.",
                "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
            }
    elif is_ad:
        # 광고인 경우 분석 생략
        analysis_result = {
            "error": "AD_REVIEW",
            "message": "광고 리뷰는 분석하지 않습니다.",
            "summary": "광고 리뷰",
            "efficacy": "정보 없음",
            "side_effects": "정보 없음",
            "tip": "이 리뷰는 광고로 판별되어 분석하지 않습니다.",
            "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
        }
    else:
        # 짧은 리뷰인 경우
        analysis_result = {
            "error": "REVIEW_TOO_SHORT",
            "message": "리뷰가 너무 짧아 상세 분석이 어렵습니다 (최소 10자 이상 권장).",
            "summary": "리뷰가 짧아 분석 불가",
            "efficacy": "정보 없음",
            "side_effects": "정보 없음",
            "tip": "더 긴 리뷰를 작성해주시면 상세한 분석을 제공할 수 있습니다.",
            "disclaimer": "본 분석은 의학적 진단이 아닌 실사용자 체감 정보를 기반으로 합니다."
        }

    return {
        "validation": validation_result,
        "analysis": analysis_result
    }
```

### 2. 영양성분 검증 결과 조회

```python
def _get_nutrition_validation(
    review_text: str,
    product_id: Optional[int] = None
) -> Optional[Dict]:
    """
    영양성분 검증 결과 조회 (통합용, 안전한 방식)
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID (None이면 None 반환)
        
    Returns:
        Dict: 영양성분 검증 결과 또는 None (오류/정보 없음)
    """
    if not product_id:
        return None
    
    try:
        from .validator import ReviewValidator
        validator = ReviewValidator()
        return validator._validate_nutrition_claims(review_text, product_id)
    except Exception:
        # 모든 예외를 무시하고 None 반환 (오류 없이)
        return None
```

### 3. 하위 호환성 유지

```python
# 기존 함수 시그니처 유지
# product_id가 None이면 기존 방식으로 동작
# use_nutrition_validation=False로 설정하면 영양성분 검증 비활성화
```

## 구현 요구사항

### 1. 의존성 확인

```python
# __init__.py에서 이미 import된 모듈들 확인
from .checklist import AdChecklist, check_ad_patterns
from .trust_score import TrustScoreCalculator, calculate_trust_score
from .analyzer import PharmacistAnalyzer
from .validator import ReviewValidator  # 추가 필요
```

### 2. analyzer.py 수정 필요

`analyzer.py`의 `analyze_safe()` 메서드에 `product_id` 매개변수 추가 필요:
- `analyzer_nutrition_integration.md` 참고

### 3. trust_score.py 수정 필요

`trust_score.py`의 `calculate_final_score()` 메서드에 영양성분 점수 계산 추가 필요:
- `trust_score_nutrition_integration.md` 참고

## 테스트 시나리오

### 시나리오 1: 영양성분 검증 포함 분석
```python
result = analyze(
    review_text="루테인을 먹고 눈 건강이 좋아졌어요",
    product_id=1,  # 루테인 제품
    use_nutrition_validation=True
)

# 기대 결과:
# - validation.nutrition_validation 존재
# - validation.trust_score에 영양성분 점수 반영
# - analysis.ingredient_validation 존재 (있는 경우)
```

### 시나리오 2: 영양성분 검증 없이 분석
```python
result = analyze(
    review_text="제품이 좋아요",
    use_nutrition_validation=False
)

# 기대 결과:
# - 기존 방식으로 동작
# - nutrition_validation 없음
```

### 시나리오 3: product_id 없이 분석
```python
result = analyze(
    review_text="제품이 좋아요"
    # product_id 없음
)

# 기대 결과:
# - 기존 방식으로 동작
# - 영양성분 검증 자동 비활성화
```

## 우선순위

1. **높음**: `analyze()` 함수에 `product_id` 매개변수 추가
2. **높음**: 영양성분 검증 결과를 validation에 포함
3. **중간**: analyzer.py와 trust_score.py 연동 확인
4. **낮음**: 배치 분석 함수 추가 (여러 리뷰 동시 분석)

## 참고 자료

- checklist_nutrition_integration.md
- analyzer_nutrition_integration.md
- trust_score_nutrition_integration.md
- validator_nutrition_integration.md
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/
