"""
최종 통합 테스트: 제품 선택부터 리뷰 분석까지 전체 흐름 검증
실제 UI 사용 시나리오를 시뮬레이션합니다.
"""
import sys
import io

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_complete_user_flow():
    """사용자 시나리오: 제품 선택 → 리뷰 조회 → 분석"""
    print("\n" + "🎯"*35)
    print("   최종 통합 테스트: 제품 선택 → 리뷰 분석 흐름")
    print("🎯"*35)
    
    try:
        from supabase_data import (
            get_all_products,
            get_all_categories,
            get_reviews_by_product,
            generate_checklist_results,
            generate_ai_analysis
        )
        
        # Step 1: 사용자가 앱을 열면 제품 목록 로드
        print("\n" + "="*70)
        print("Step 1: 제품 목록 로드")
        print("="*70)
        products = get_all_products()
        print(f"✅ 총 {len(products)}개 제품 로드 완료")
        
        if not products:
            print("❌ 제품이 없습니다!")
            return False
        
        # 평점과 리뷰 수가 있는 제품 확인
        products_with_ratings = [p for p in products if p.get('rating_avg', 0) > 0]
        print(f"✅ 평점 정보가 있는 제품: {len(products_with_ratings)}개")
        
        # Step 2: 카테고리 목록 로드
        print("\n" + "="*70)
        print("Step 2: 카테고리 필터 로드")
        print("="*70)
        categories = get_all_categories()
        print(f"✅ {len(categories)}개 카테고리 로드 완료")
        for cat in categories:
            print(f"   - {cat}")
        
        # Step 3: 사용자가 메인 제품 선택 (평점이 높은 제품)
        print("\n" + "="*70)
        print("Step 3: 메인 제품 선택 (평점 높은 제품)")
        print("="*70)
        
        # 평점이 가장 높은 제품 찾기
        best_product = max(products, key=lambda p: (p.get('rating_avg', 0), p.get('rating_count', 0)))
        print(f"✅ 선택된 제품:")
        print(f"   ID: {best_product['id']}")
        print(f"   이름: {best_product['name']}")
        print(f"   브랜드: {best_product['brand']}")
        print(f"   평점: {best_product['rating_avg']:.2f} ({best_product['rating_count']}개 리뷰)")
        print(f"   가격: ${best_product['price']:.2f}")
        
        # Step 4: 선택된 제품의 리뷰 조회
        print("\n" + "="*70)
        print("Step 4: 선택된 제품의 리뷰 조회")
        print("="*70)
        reviews = get_reviews_by_product(best_product['id'])
        print(f"✅ {len(reviews)}개 리뷰 조회 완료")
        
        if not reviews:
            print("⚠️  리뷰가 없습니다!")
            return False
        
        # 리뷰 통계
        ratings = [r.get('rating', 0) for r in reviews]
        print(f"\n📊 리뷰 통계:")
        print(f"   평균 평점: {sum(ratings)/len(ratings):.2f}")
        print(f"   5점: {ratings.count(5)}개")
        print(f"   4점: {ratings.count(4)}개")
        print(f"   3점: {ratings.count(3)}개")
        print(f"   2점: {ratings.count(2)}개")
        print(f"   1점: {ratings.count(1)}개")
        
        # 샘플 리뷰 표시
        print(f"\n💬 샘플 리뷰:")
        sample_review = reviews[0]
        print(f"   작성자: {sample_review.get('reviewer', 'N/A')}")
        print(f"   평점: {sample_review.get('rating', 0)}점")
        print(f"   내용: {sample_review.get('text', 'N/A')[:80]}...")
        
        # Step 5: 8단계 체크리스트 생성
        print("\n" + "="*70)
        print("Step 5: 8단계 리뷰 팩트체크 실행")
        print("="*70)
        checklist = generate_checklist_results(reviews)
        print("✅ 체크리스트 생성 완료")
        
        passed_items = []
        failed_items = []
        
        for key, item in checklist.items():
            status = "✅ 통과" if item.get('passed', False) else "❌ 미흡"
            rate = item.get('rate', 0) * 100
            desc = item.get('description', 'N/A')
            
            print(f"   {status} {key}: {rate:.0f}% - {desc}")
            
            if item.get('passed', False):
                passed_items.append(key)
            else:
                failed_items.append(key)
        
        # 신뢰도 점수 계산
        trust_score = sum(item.get('rate', 0) for item in checklist.values()) / len(checklist) * 100
        print(f"\n📊 종합 신뢰도 점수: {trust_score:.1f}%")
        print(f"   통과: {len(passed_items)}/8개")
        print(f"   미흡: {len(failed_items)}/8개")
        
        # Step 6: AI 약사 분석 생성
        print("\n" + "="*70)
        print("Step 6: AI 약사 종합 분석")
        print("="*70)
        ai_analysis = generate_ai_analysis(best_product, checklist)
        print(f"✅ AI 분석 완료")
        print(f"   신뢰도: {ai_analysis.get('trust_score', 0):.1f}%")
        print(f"   추천 여부: {ai_analysis.get('recommendation', 'N/A')}")
        print(f"   주요 장점: {ai_analysis.get('strengths', ['없음'])[0] if ai_analysis.get('strengths') else '없음'}")
        print(f"   주의사항: {ai_analysis.get('warnings', ['없음'])[0] if ai_analysis.get('warnings') else '없음'}")
        
        # Step 7: 비교 제품 추천 (간단 버전)
        print("\n" + "="*70)
        print("Step 7: 비교 제품 추천")
        print("="*70)
        
        # 같은 카테고리의 다른 제품 추천
        same_category = [p for p in products 
                        if p.get('category') == best_product.get('category') 
                        and p['id'] != best_product['id']
                        and p.get('rating_count', 0) > 0]
        
        if same_category:
            # 평점순으로 정렬하여 상위 2개 추천
            recommended = sorted(same_category, 
                               key=lambda p: (p.get('rating_avg', 0), p.get('rating_count', 0)), 
                               reverse=True)[:2]
            
            print(f"✅ 비교 제품 {len(recommended)}개 추천 완료")
            for i, rec in enumerate(recommended, 1):
                print(f"\n   추천 {i}:")
                print(f"   이름: {rec['name']}")
                print(f"   브랜드: {rec['brand']}")
                print(f"   평점: {rec['rating_avg']:.2f} ({rec['rating_count']}개 리뷰)")
                print(f"   가격: ${rec['price']:.2f}")
        else:
            print("⚠️  같은 카테고리의 다른 제품이 없습니다")
        
        # 최종 결과
        print("\n" + "="*70)
        print("✅ 전체 흐름 테스트 성공!")
        print("="*70)
        print(f"✅ 제품 로드 → 필터링 → 선택 → 리뷰 조회 → 분석 → 추천")
        print(f"✅ 모든 단계 정상 작동 확인")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_display_data():
    """UI에서 표시할 데이터 검증"""
    print("\n" + "🖥️ "*35)
    print("   UI 표시 데이터 검증")
    print("🖥️ "*35)
    
    try:
        from supabase_data import get_all_products
        
        products = get_all_products()
        
        print("\n📊 UI에서 표시될 데이터:")
        print("="*70)
        
        # 샘플 제품 5개
        for i, p in enumerate(products[:5], 1):
            print(f"\n제품 {i}:")
            print(f"  브랜드: {p.get('brand', 'N/A')}")
            print(f"  이름: {p.get('name', 'N/A')[:50]}...")
            print(f"  가격: ${p.get('price', 0):.2f}")
            print(f"  ⭐ 평점: {p.get('rating_avg', 0):.2f}/5.0")
            print(f"  💬 리뷰: {p.get('rating_count', 0)}개")
            print(f"  카테고리: {p.get('category', 'N/A')}")
        
        # 데이터 품질 체크
        print("\n" + "="*70)
        print("데이터 품질 체크:")
        print("="*70)
        
        has_rating = sum(1 for p in products if p.get('rating_avg', 0) > 0)
        has_reviews = sum(1 for p in products if p.get('rating_count', 0) > 0)
        
        print(f"✅ 평점이 있는 제품: {has_rating}/{len(products)}개 ({has_rating/len(products)*100:.1f}%)")
        print(f"✅ 리뷰가 있는 제품: {has_reviews}/{len(products)}개 ({has_reviews/len(products)*100:.1f}%)")
        
        if has_rating == len(products) and has_reviews == len(products):
            print("\n🎉 모든 제품에 평점과 리뷰 정보가 있습니다!")
            return True
        else:
            print(f"\n⚠️  {len(products) - has_rating}개 제품에 평점 정보 누락")
            print(f"⚠️  {len(products) - has_reviews}개 제품에 리뷰 정보 누락")
            return False
            
    except Exception as e:
        print(f"❌ UI 데이터 검증 실패: {e}")
        return False

def main():
    print("\n" + "🚀"*35)
    print("   최종 통합 테스트 시작")
    print("🚀"*35)
    
    # 테스트 1: UI 표시 데이터 검증
    ui_test = test_ui_display_data()
    
    # 테스트 2: 전체 흐름 테스트
    flow_test = test_complete_user_flow()
    
    # 결과 요약
    print("\n" + "="*70)
    print("📊 최종 결과")
    print("="*70)
    print(f"{'✅' if ui_test else '❌'} UI 표시 데이터 검증")
    print(f"{'✅' if flow_test else '❌'} 제품 선택 → 리뷰 분석 흐름")
    
    if ui_test and flow_test:
        print("\n🎉🎉🎉 모든 테스트 통과! 프로덕션 배포 준비 완료 🎉🎉🎉")
        return True
    else:
        print("\n⚠️  일부 테스트 실패 - 문제를 확인하고 수정하세요")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
