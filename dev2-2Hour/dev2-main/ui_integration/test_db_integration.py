"""
DB 연동 전면 점검 테스트 스크립트
Supabase products 및 reviews 데이터를 검증하고 UI 연동 상태를 확인합니다.
"""
import sys
import io
import os

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# 현재 디렉토리를 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import requests
from typing import Dict, List

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://bvowxbpqtfpkkxkzsumf.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'sb_publishable_afWmzo_2ypv3liBdpCkJjg_KjS7nqE2')

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("\n" + "="*70)
    print("1️⃣  Supabase 연결 테스트")
    print("="*70)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/"
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code in [200, 401]:  # 401도 연결은 성공
            print("✅ Supabase 연결 성공")
            print(f"   URL: {SUPABASE_URL}")
            return True
        else:
            print(f"❌ Supabase 연결 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def test_products_table():
    """products 테이블 데이터 검증"""
    print("\n" + "="*70)
    print("2️⃣  Products 테이블 검증")
    print("="*70)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/products"
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        params = {'select': '*', 'limit': 5}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Products 조회 성공: {len(products)}개 (샘플)")
            
            if products:
                print("\n📦 샘플 제품 (1개):")
                p = products[0]
                print(f"   ID: {p.get('id')}")
                print(f"   Brand: {p.get('brand', 'N/A')}")
                print(f"   Title: {p.get('title', 'N/A')[:50]}...")
                print(f"   Price: ${p.get('price', 0)}")
                print(f"   Rating: {p.get('rating_avg', 0)} ({p.get('rating_count', 0)} reviews)")
                print(f"   Category: {p.get('category', 'N/A')}")
                
                # 필수 필드 검증
                required_fields = ['id', 'brand', 'title', 'price', 'rating_avg', 'rating_count']
                missing_fields = [f for f in required_fields if p.get(f) is None]
                
                if missing_fields:
                    print(f"\n⚠️  누락된 필드: {missing_fields}")
                else:
                    print("\n✅ 모든 필수 필드 존재")
                
                return True, products
            else:
                print("⚠️  제품 데이터 없음")
                return False, []
        else:
            print(f"❌ Products 조회 실패: {response.status_code}")
            print(f"   응답: {response.text[:200]}")
            return False, []
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False, []

def test_reviews_table(product_id=None):
    """reviews 테이블 데이터 검증"""
    print("\n" + "="*70)
    print("3️⃣  Reviews 테이블 검증")
    print("="*70)
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/reviews"
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 특정 제품의 리뷰 조회 (있는 경우)
        if product_id:
            params = {'select': '*', 'product_id': f'eq.{product_id}', 'limit': 5}
            print(f"🔍 제품 ID {product_id}의 리뷰 조회 중...")
        else:
            params = {'select': '*', 'limit': 5}
            print(f"🔍 전체 리뷰 조회 중 (샘플 5개)...")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            reviews = response.json()
            print(f"✅ Reviews 조회 성공: {len(reviews)}개")
            
            if reviews:
                print("\n💬 샘플 리뷰 (1개):")
                r = reviews[0]
                print(f"   ID: {r.get('id')}")
                print(f"   Product ID: {r.get('product_id')}")
                print(f"   Author: {r.get('author', 'N/A')}")
                print(f"   Rating: {r.get('rating', 0)}")
                print(f"   Title: {r.get('title', 'N/A')}")
                print(f"   Body: {r.get('body', 'N/A')[:80]}...")
                print(f"   Language: {r.get('language', 'N/A')}")
                print(f"   Date: {r.get('review_date', 'N/A')}")
                print(f"   Helpful: {r.get('helpful_count', 0)}")
                
                # 필수 필드 검증
                required_fields = ['id', 'product_id', 'rating', 'body']
                missing_fields = [f for f in required_fields if r.get(f) is None]
                
                if missing_fields:
                    print(f"\n⚠️  누락된 필드: {missing_fields}")
                else:
                    print("\n✅ 모든 필수 필드 존재")
                
                return True, reviews
            else:
                print("⚠️  리뷰 데이터 없음")
                return False, []
        else:
            print(f"❌ Reviews 조회 실패: {response.status_code}")
            print(f"   응답: {response.text[:200]}")
            return False, []
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False, []

def test_supabase_data_module():
    """supabase_data.py 모듈 함수 테스트"""
    print("\n" + "="*70)
    print("4️⃣  supabase_data.py 모듈 테스트")
    print("="*70)
    
    try:
        import supabase_data
        
        # get_all_products 테스트
        print("\n🔹 get_all_products() 테스트...")
        products = supabase_data.get_all_products()
        print(f"✅ 제품 {len(products)}개 조회 성공")
        
        if products:
            p = products[0]
            print(f"   샘플: {p.get('brand', '')} - {p.get('name', '')[:40]}")
        
        # get_reviews_by_product 테스트 (첫 번째 제품)
        if products:
            product_id = products[0].get('id')
            print(f"\n🔹 get_reviews_by_product({product_id}) 테스트...")
            reviews = supabase_data.get_reviews_by_product(product_id)
            print(f"✅ 리뷰 {len(reviews)}개 조회 성공")
            
            if reviews:
                r = reviews[0]
                print(f"   샘플: {r.get('rating')}점 - {r.get('text', '')[:40]}")
        
        # get_all_categories 테스트
        print(f"\n🔹 get_all_categories() 테스트...")
        categories = supabase_data.get_all_categories()
        print(f"✅ 카테고리 {len(categories)}개 조회 성공")
        if categories:
            print(f"   샘플: {categories[:3]}")
        
        # get_statistics_summary 테스트
        print(f"\n🔹 get_statistics_summary() 테스트...")
        stats = supabase_data.get_statistics_summary()
        print(f"✅ 통계 조회 성공")
        print(f"   총 제품: {stats.get('total_products', 0)}개")
        print(f"   총 브랜드: {stats.get('total_brands', 0)}개")
        print(f"   총 리뷰: {stats.get('total_reviews', 0)}개")
        
        return True
    except Exception as e:
        print(f"❌ 모듈 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_product_to_review_flow(product_id):
    """제품 선택 → 리뷰 조회 흐름 테스트"""
    print("\n" + "="*70)
    print("5️⃣  제품 선택 → 리뷰 조회 흐름 테스트")
    print("="*70)
    
    try:
        import supabase_data
        
        print(f"🔹 제품 ID {product_id} 정보 조회...")
        product = supabase_data.get_product_by_id(product_id)
        
        if product:
            print(f"✅ 제품 조회 성공")
            print(f"   이름: {product.get('name', 'N/A')}")
            print(f"   브랜드: {product.get('brand', 'N/A')}")
            print(f"   평점: {product.get('rating_avg', 0)}")
            
            print(f"\n🔹 제품의 리뷰 조회...")
            reviews = supabase_data.get_reviews_by_product(product_id)
            print(f"✅ 리뷰 {len(reviews)}개 조회 성공")
            
            if reviews:
                print(f"\n📊 리뷰 통계:")
                ratings = [r.get('rating', 0) for r in reviews]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                print(f"   평균 평점: {avg_rating:.2f}")
                print(f"   5점: {ratings.count(5)}개")
                print(f"   4점: {ratings.count(4)}개")
                print(f"   3점: {ratings.count(3)}개")
                print(f"   2점: {ratings.count(2)}개")
                print(f"   1점: {ratings.count(1)}개")
                
                print(f"\n🔹 체크리스트 생성 테스트...")
                checklist = supabase_data.generate_checklist_results(reviews)
                print(f"✅ 체크리스트 생성 성공")
                
                # 통과한 항목 수 계산
                passed_count = sum(1 for item in checklist.values() if item.get('passed', False))
                print(f"   통과 항목: {passed_count}/{len(checklist)}개")
                
                # 신뢰도 점수 계산
                trust_score = sum(item.get('rate', 0) for item in checklist.values()) / len(checklist) * 100
                print(f"   신뢰도 점수: {trust_score:.1f}%")
                
                return True
            else:
                print("⚠️  리뷰 데이터 없음 - 리뷰가 있는 제품으로 테스트 필요")
                return False
        else:
            print(f"❌ 제품 조회 실패")
            return False
    except Exception as e:
        print(f"❌ 흐름 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_consistency():
    """데이터 일관성 검증"""
    print("\n" + "="*70)
    print("6️⃣  데이터 일관성 검증")
    print("="*70)
    
    try:
        import supabase_data
        
        print("🔹 products와 reviews 연결 검증...")
        
        # 모든 제품 조회
        products = supabase_data.get_all_products()
        print(f"✅ 전체 제품: {len(products)}개")
        
        # 각 제품의 rating_count와 실제 리뷰 수 비교
        mismatches = []
        products_with_reviews = 0
        
        for p in products[:10]:  # 샘플 10개만 검증
            product_id = p.get('id')
            expected_count = p.get('rating_count', 0)
            
            reviews = supabase_data.get_reviews_by_product(product_id)
            actual_count = len(reviews)
            
            if actual_count > 0:
                products_with_reviews += 1
            
            if expected_count != actual_count:
                mismatches.append({
                    'id': product_id,
                    'name': p.get('name', 'N/A')[:30],
                    'expected': expected_count,
                    'actual': actual_count
                })
        
        print(f"✅ 리뷰가 있는 제품: {products_with_reviews}개 (샘플 10개 중)")
        
        if mismatches:
            print(f"\n⚠️  리뷰 수 불일치 발견: {len(mismatches)}개")
            for m in mismatches[:3]:
                print(f"   제품 {m['id']} ({m['name']}): 예상 {m['expected']}개, 실제 {m['actual']}개")
        else:
            print("✅ 리뷰 수 일치 (샘플 검증)")
        
        return True
    except Exception as e:
        print(f"❌ 일관성 검증 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """전체 테스트 실행"""
    print("\n" + "🔬"*35)
    print("   UI/UX Frontend ↔️ Backend DB 연동 전면 점검")
    print("🔬"*35)
    
    results = {}
    
    # 1. Supabase 연결 테스트
    results['connection'] = test_supabase_connection()
    
    # 2. Products 테이블 테스트
    products_ok, sample_products = test_products_table()
    results['products'] = products_ok
    
    # 3. Reviews 테이블 테스트
    product_id = sample_products[0].get('id') if sample_products else None
    reviews_ok, sample_reviews = test_reviews_table(product_id)
    results['reviews'] = reviews_ok
    
    # 4. supabase_data.py 모듈 테스트
    results['module'] = test_supabase_data_module()
    
    # 5. 제품 → 리뷰 흐름 테스트
    if product_id:
        results['flow'] = test_product_to_review_flow(product_id)
    else:
        results['flow'] = False
        print("\n⚠️  제품 ID를 찾을 수 없어 흐름 테스트 생략")
    
    # 6. 데이터 일관성 검증
    results['consistency'] = test_data_consistency()
    
    # 결과 요약
    print("\n" + "="*70)
    print("📊 테스트 결과 요약")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{status}  {test_name.upper()}")
    
    print("\n" + "-"*70)
    print(f"총 {total_tests}개 테스트 중 {passed_tests}개 성공 ({passed_tests/total_tests*100:.1f}%)")
    print("-"*70)
    
    if passed_tests == total_tests:
        print("\n🎉 모든 테스트 통과! DB 연동 정상 작동 중")
    else:
        print("\n⚠️  일부 테스트 실패 - 문제점을 확인하고 수정 필요")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
