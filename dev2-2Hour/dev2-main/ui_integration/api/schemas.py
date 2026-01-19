"""
API 스키마 정의 (Pydantic 모델)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class HealthCheck(BaseModel):
    """헬스 체크 응답 모델"""
    status: str
    message: str

class ReviewAnalysisRequest(BaseModel):
    """리뷰 분석 요청 모델"""
    review_text: str = Field(..., description="분석할 리뷰 텍스트", min_length=10)
    product_id: Optional[int] = Field(None, description="제품 ID (선택적)")
    length_score: float = Field(50, ge=0, le=100, description="리뷰 길이 점수")
    repurchase_score: float = Field(50, ge=0, le=100, description="재구매 점수")
    monthly_use_score: float = Field(50, ge=0, le=100, description="한달 사용 점수")
    photo_score: float = Field(0, ge=0, le=100, description="사진 첨부 점수")
    consistency_score: float = Field(50, ge=0, le=100, description="내용 일치도 점수")
    use_nutrition_validation: bool = Field(True, description="영양성분 검증 사용 여부")

class ReviewAnalysisResponse(BaseModel):
    """리뷰 분석 응답 모델"""
    validation: Dict[str, Any]
    analysis: Optional[Dict[str, Any]] = None

class ProductResponse(BaseModel):
    """제품 응답 모델"""
    id: int
    name: str
    brand: str
    price: float
    rating_avg: Optional[float] = None
    rating_count: int = 0

class ChartAnalysisRequest(BaseModel):
    """차트 분석 요청 모델"""
    chart_type: str = Field(..., description="차트 타입 (radar, gauge, bar, line 등)")
    data: Dict[str, Any] = Field(..., description="차트 데이터")
    context: Optional[str] = Field(None, description="추가 컨텍스트 정보")

class ChartAnalysisResponse(BaseModel):
    """차트 분석 응답 모델"""
    summary: str
    key_findings: List[str]
    trends: str
    insights: str
    data_quality: str
