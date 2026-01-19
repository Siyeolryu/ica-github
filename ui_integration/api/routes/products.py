"""
제품 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from api.schemas import ProductResponse

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="최소 평점"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 수")
):
    """
    제품 목록 조회
    
    Args:
        category: 카테고리 필터
        min_rating: 최소 평점
        limit: 최대 결과 수
    """
    try:
        from supabase_data import get_all_products, get_products_by_category
        
        if category:
            products = get_products_by_category(category)
        else:
            products = get_all_products()
        
        # 평점 필터 적용
        if min_rating:
            products = [p for p in products if p.get("rating_avg", 0) >= min_rating]
        
        # 제한 적용
        products = products[:limit]
        
        # 응답 모델로 변환
        return [
            ProductResponse(
                id=p.get("id", 0),
                name=p.get("name", p.get("title", "")),
                brand=p.get("brand", ""),
                price=float(p.get("price", 0)),
                rating_avg=p.get("rating_avg"),
                rating_count=p.get("rating_count", 0)
            )
            for p in products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류 발생: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """
    특정 제품 조회
    
    Args:
        product_id: 제품 ID
    """
    try:
        from supabase_data import get_all_products
        
        products = get_all_products()
        product = next((p for p in products if p.get("id") == product_id), None)
        
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        return ProductResponse(
            id=product.get("id", 0),
            name=product.get("name", product.get("title", "")),
            brand=product.get("brand", ""),
            price=float(product.get("price", 0)),
            rating_avg=product.get("rating_avg"),
            rating_count=product.get("rating_count", 0)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류 발생: {str(e)}")
