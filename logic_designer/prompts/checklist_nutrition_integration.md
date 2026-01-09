# checklist.py 영양성분 DB 통합 프롬프트

## 목적
식품의약품안전처 건강기능식품 영양성분 DB를 활용하여 `checklist.py`의 13단계 광고 판별 체크리스트를 더욱 정확하고 신뢰도 높게 개선합니다.

## 개선 방향

### 1. 원료 특징 나열 검증 강화 (5번 항목)

**현재 문제점:**
- 단순히 "함유", "성분", "원료" 등의 키워드만으로 감지
- 실제 제품에 없는 성분을 언급한 허위 주장을 구분하지 못함

**개선 방안:**
```python
def _validate_ingredient_claims(self, review_text: str, product_id: Optional[int] = None) -> bool:
    """
    리뷰에서 언급된 성분이 실제 제품에 포함되어 있는지 검증
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID (None이면 검증 생략)
        
    Returns:
        bool: 허위 성분 주장이 있으면 True (광고 의심), 정보 없으면 False
    """
    # 1. product_id가 없으면 검증 생략 (기존 방식으로 동작)
    if not product_id:
        return False
    
    # 2. 영양성분 정보 조회 (오류 발생 시 기본값 반환)
    nutrition_info = self._get_nutrition_info_safe(product_id)
    if not nutrition_info:
        return False  # 정보 없으면 검증 생략 (오류 없이)
    
    # 3. 리뷰 텍스트에서 성분명 추출
    mentioned_ingredients = self._extract_ingredients(review_text)
    if not mentioned_ingredients:
        return False  # 성분 언급 없으면 검증 불가
    
    # 4. 언급된 성분이 실제 제품에 없는 경우 → 허위 주장으로 판단
    for mentioned in mentioned_ingredients:
        if not self._is_valid_ingredient(mentioned, nutrition_info):
            return True  # 허위 주장 발견
    
    return False  # 모든 성분이 유효함

def _get_nutrition_info_safe(self, product_id: int) -> Optional[Dict]:
    """
    영양성분 정보 조회 (안전한 방식 - 오류 발생 시 None 반환)
    
    Args:
        product_id: 제품 ID
        
    Returns:
        Dict: 영양성분 정보 또는 None (오류/정보 없음)
    """
    try:
        from database.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        response = supabase.table('nutrition_info')\
            .select('*')\
            .eq('product_id', product_id)\
            .execute()
        return {'ingredients': response.data} if response.data else None
    except Exception:
        # 모든 예외를 무시하고 None 반환 (오류 없이 기존 방식으로 동작)
        return None
```

**영양성분 DB 활용:**
- 제품별 실제 함유 성분 목록 조회
- 성분명 동의어/별칭 매핑 (예: "비타민C" = "아스코르빅산" = "Ascorbic Acid")
- 함량 정보와 리뷰의 함량 주장 비교

### 2. 전문 용어 오남용 검증 (9번 항목)

**개선 방안:**
```python
def _validate_medical_claims(self, review_text: str, product_id: int) -> bool:
    """
    리뷰의 의학적 주장이 영양성분 DB의 공식 효능과 일치하는지 검증
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID
        
    Returns:
        bool: 허위 의학적 주장이 있으면 True
    """
    # 1. 영양성분 DB에서 해당 성분의 공식 효능 조회
    # 2. 리뷰에서 의학적 주장 추출
    # 3. 공식 효능과 불일치하는 과장된 주장 감지
    #    예: "루테인" → 공식 효능: "눈 건강", 허위 주장: "시력 100% 회복"
    pass
```

**영양성분 DB 활용:**
- 성분별 공식 효능 정보
- 허용된 건강기능식품 표시 문구
- 금지된 의료용어 목록

### 3. 비현실적 효과 강조 검증 (10번 항목)

**개선 방안:**
```python
def _validate_effect_timeline(self, review_text: str, product_id: int) -> bool:
    """
    리뷰의 효과 발현 시점이 현실적인지 검증
    
    Args:
        review_text: 리뷰 텍스트
        product_id: 제품 ID
        
    Returns:
        bool: 비현실적인 효과 시점 주장이 있으면 True
    """
    # 1. 영양성분 DB에서 해당 성분의 일반적인 효과 발현 기간 조회
    # 2. 리뷰에서 "즉시", "하루만에", "일주일만에" 등의 시점 표현 추출
    # 3. 일반적인 효과 발현 기간과 비교하여 비현실적 주장 감지
    #    예: "프로바이오틱스" → 일반적 효과: 2-4주, 비현실적: "하루만에"
    pass
```

### 4. 제품별 체크 기준 강화

**개선 방안:**
```python
def check_ad_patterns(self, review_text: str, product_id: Optional[int] = None) -> Dict[int, str]:
    """
    13단계 광고 판별 체크리스트 검사 (영양성분 DB 통합)
    
    Args:
        review_text: 검사할 리뷰 텍스트
        product_id: 제품 ID (제공 시 영양성분 DB 조회, 없어도 오류 없음)
        
    Returns:
        Dict[int, str]: {항목번호: 항목명} 형태로 감지된 항목 반환
    """
    # 입력 검증: 리뷰가 너무 짧으면 빈 결과 반환
    if not review_text or len(review_text.strip()) < 3:
        return {}
    
    detected_issues = {}
    
    # 기존 13단계 패턴 검사 (항상 수행)
    for item_num, item_data in self.AD_PATTERNS.items():
        # ... 기존 로직 ...
        pass
    
    # 영양성분 DB 기반 추가 검증 (product_id가 있고 정보가 있는 경우만)
    if product_id:
        try:
            # 5번: 원료 특징 나열 - 허위 성분 주장 검증
            if self._validate_ingredient_claims(review_text, product_id):
                # 기존 5번 항목이 있으면 강화, 없으면 추가
                if 5 in detected_issues:
                    detected_issues[5] = f"{detected_issues[5]} (허위 성분 주장 포함)"
                else:
                    detected_issues[5] = "원료 특징 나열 (허위 성분 주장)"
            
            # 9번: 전문 용어 오남용 - 허위 의학적 주장 검증
            if self._validate_medical_claims(review_text, product_id):
                if 9 in detected_issues:
                    detected_issues[9] = f"{detected_issues[9]} (허위 의학적 주장 포함)"
                else:
                    detected_issues[9] = "전문 용어 오남용 (허위 의학적 주장)"
            
            # 10번: 비현실적 효과 강조 - 효과 시점 검증
            if self._validate_effect_timeline(review_text, product_id):
                if 10 in detected_issues:
                    detected_issues[10] = f"{detected_issues[10]} (효과 시점 과장)"
                else:
                    detected_issues[10] = "비현실적 효과 강조 (효과 시점 과장)"
        except Exception:
            # 영양성분 검증 중 오류 발생 시 무시하고 기존 결과만 반환
            pass
    
    return detected_issues
```

## 구현 요구사항

### 1. 영양성분 DB 스키마 가정

```sql
-- nutrition_info 테이블 (가정)
CREATE TABLE nutrition_info (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(id),
    ingredient_name TEXT NOT NULL,           -- 성분명 (공식명)
    ingredient_aliases JSONB,                -- 동의어/별칭 배열
    amount NUMERIC,                          -- 함량
    unit TEXT,                               -- 단위 (mg, g, mcg 등)
    official_efficacy TEXT[],                -- 공식 효능 목록
    prohibited_claims TEXT[],               -- 금지된 주장 목록
    typical_effect_period_days INT,          -- 일반적 효과 발현 기간 (일)
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. Supabase 클라이언트 연동

```python
from database.supabase_client import get_supabase_client

def get_product_nutrition_info(product_id: int) -> Dict:
    """제품의 영양성분 정보 조회"""
    supabase = get_supabase_client()
    response = supabase.table('nutrition_info')\
        .select('*')\
        .eq('product_id', product_id)\
        .execute()
    return response.data if response.data else []
```

### 3. 성분명 매칭 로직

```python
def match_ingredient_name(mentioned_name: str, official_name: str, aliases: List[str]) -> bool:
    """
    리뷰에서 언급된 성분명이 실제 성분과 일치하는지 확인
    
    Args:
        mentioned_name: 리뷰에서 언급된 성분명
        official_name: 공식 성분명
        aliases: 동의어/별칭 목록
        
    Returns:
        bool: 일치 여부
    """
    # 1. 정확한 일치
    if mentioned_name.lower() == official_name.lower():
        return True
    
    # 2. 별칭 일치
    for alias in aliases:
        if mentioned_name.lower() in alias.lower() or alias.lower() in mentioned_name.lower():
            return True
    
    # 3. 부분 일치 (예: "비타민C" vs "Ascorbic Acid")
    # 더 정교한 매칭 로직 필요
    return False
```

## 테스트 시나리오

### 시나리오 1: 허위 성분 주장 감지
```
제품: 루테인 제품 (실제 성분: 루테인, 제아잔틴)
리뷰: "이 제품에는 오메가3와 코엔자임Q10이 함유되어 있어서..."

기대 결과: 5번 항목 감지 (실제 제품에 없는 성분 언급)
```

### 시나리오 2: 허위 의학적 주장 감지
```
제품: 루테인 제품 (공식 효능: "눈 건강 유지")
리뷰: "시력이 100% 회복되었고, 백내장도 완치되었어요!"

기대 결과: 9번 항목 감지 (공식 효능을 초과한 의학적 주장)
```

### 시나리오 3: 비현실적 효과 시점 감지
```
제품: 프로바이오틱스 (일반적 효과 발현: 14-28일)
리뷰: "하루만에 장 건강이 완벽하게 개선되었어요!"

기대 결과: 10번 항목 감지 (비현실적인 효과 시점)
```

## 우선순위

1. **높음**: 원료 특징 나열 검증 (5번) - 허위 성분 주장 감지
2. **중간**: 전문 용어 오남용 검증 (9번) - 허위 의학적 주장 감지
3. **낮음**: 비현실적 효과 강조 검증 (10번) - 효과 시점 검증

## 참고 자료

- 식품의약품안전처 건강기능식품 정보: https://www.foodsafetykorea.go.kr/
- 건강기능식품 공전: 성분별 공식 효능 및 표시 문구
- GitHub 저장소: https://github.com/tturupapa-stack/dev2/
