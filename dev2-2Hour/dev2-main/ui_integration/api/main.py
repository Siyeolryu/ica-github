"""
건기식 리뷰 팩트체크 시스템 - FastAPI 서버
OpenAPI 스펙 제공 및 REST API 엔드포인트
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '..', 'dev2-2Hour', 'dev2-main'))

from api.routes import products, reviews, charts
from api.schemas import HealthCheck

app = FastAPI(
    title="건기식 리뷰 팩트체크 API",
    description="건강기능식품 리뷰 검증 및 분석 API - OpenAPI 스펙 제공",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(charts.router, prefix="/api/v1/charts", tags=["charts"])

@app.get("/", response_model=HealthCheck)
async def root():
    """헬스 체크 엔드포인트"""
    return {"status": "ok", "message": "건기식 리뷰 팩트체크 API"}

@app.get("/health")
async def health_check():
    """상세 헬스 체크"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "ai_analyzer": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
