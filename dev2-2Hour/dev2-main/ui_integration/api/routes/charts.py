"""
차트 분석 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from api.schemas import ChartAnalysisRequest, ChartAnalysisResponse

router = APIRouter()

@router.post("/analyze", response_model=ChartAnalysisResponse)
async def analyze_chart(request: ChartAnalysisRequest):
    """
    차트 데이터 분석
    
    Args:
        request: 차트 분석 요청 (차트 타입, 데이터, 컨텍스트)
    
    Returns:
        차트 분석 결과 (요약, 주요 발견사항, 트렌드, 인사이트)
    """
    try:
        # chart_analyzer 모듈 import
        from chart_analyzer import ChartAnalyzer
        
        analyzer = ChartAnalyzer()
        result = analyzer.analyze_chart_data(
            chart_type=request.chart_type,
            data=request.data,
            context=request.context
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ChartAnalysisResponse(**result)
    except ImportError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"차트 분석기 모듈을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 분석 중 오류 발생: {str(e)}")

@router.post("/analyze-comparison")
async def analyze_comparison_chart(products_data: list):
    """
    제품 비교 차트 분석
    
    Args:
        products_data: 제품 비교 데이터 리스트
    
    Returns:
        비교 분석 결과
    """
    try:
        from chart_analyzer import ChartAnalyzer
        
        analyzer = ChartAnalyzer()
        result = analyzer.analyze_comparison_chart(products_data, "radar")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"비교 차트 분석 중 오류 발생: {str(e)}")
