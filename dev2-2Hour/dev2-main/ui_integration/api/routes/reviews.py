"""
리뷰 분석 API 엔드포인트
logic_designer의 검증 로직을 REST API로 제공
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import sys
import os

# 프로젝트 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
logic_designer_path = os.path.join(project_root, 'dev2-2Hour', 'dev2-main', 'logic_designer')

sys.path.insert(0, logic_designer_path)
sys.path.insert(0, project_root)

from api.schemas import ReviewAnalysisRequest, ReviewAnalysisResponse

router = APIRouter()

try:
    from logic_designer import analyze as analyze_review
except ImportError:
    # 로컬 개발 환경에서 경로가 다를 수 있음
    sys.path.insert(0, os.path.join(project_root, 'dev2-2Hour', 'dev2-main'))
    from logic_designer import analyze as analyze_review

@router.post("/analyze", response_model=ReviewAnalysisResponse)
async def analyze_review_endpoint(request: ReviewAnalysisRequest):
    """
    리뷰 분석 엔드포인트
    
    logic_designer의 검증 로직을 사용하여 리뷰를 분석합니다.
    """
    try:
        result = analyze_review(
            review_text=request.review_text,
            product_id=request.product_id,
            length_score=request.length_score,
            repurchase_score=request.repurchase_score,
            monthly_use_score=request.monthly_use_score,
            photo_score=request.photo_score,
            consistency_score=request.consistency_score,
            use_nutrition_validation=request.use_nutrition_validation
        )
        
        return ReviewAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@router.get("/batch-analyze")
async def batch_analyze_reviews(
    product_id: int,
    limit: int = 10
):
    """
    제품의 여러 리뷰를 일괄 분석
    
    Args:
        product_id: 제품 ID
        limit: 분석할 최대 리뷰 수
    """
    try:
        # Supabase에서 리뷰 가져오기
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))
        from supabase_data import get_reviews_by_product_id
        
        reviews = get_reviews_by_product_id(product_id)[:limit]
        
        results = []
        for review in reviews:
            try:
                result = analyze_review(
                    review_text=review.get("body", review.get("text", "")),
                    product_id=product_id
                )
                results.append({
                    "review_id": review.get("id"),
                    "analysis": result
                })
            except Exception as e:
                results.append({
                    "review_id": review.get("id"),
                    "error": str(e)
                })
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일괄 분석 중 오류 발생: {str(e)}")
