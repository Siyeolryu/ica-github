"""
평균 가격 통계 계산 스크립트
"""
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_integration.supabase_data import get_statistics_summary, _fetch_from_supabase

def calculate_price_statistics():
    """평균 가격 통계 계산 및 출력"""
    print("=" * 60)
    print("평균 가격 통계 분석")
    print("=" * 60)
    
    # 통계 요약 가져오기
    stats = get_statistics_summary()
    
    print(f"\n[전체 통계] (최근 30개 제품 기준)")
    print(f"  - 제품 수: {stats.get('total_products', 0)}개")
    print(f"  - 평균 가격: ${stats.get('avg_price', 0):.2f}")
    
    # 상세 가격 분석
    print(f"\n[상세 가격 분석]")
    products = _fetch_from_supabase('products', 'select=*&order=rating_count.desc')[:30]
    
    valid_prices = []
    invalid_prices = []
    
    for p in products:
        price = p.get('price')
        if price is None:
            invalid_prices.append({"product": p.get('title', 'Unknown'), "reason": "가격 없음"})
            continue
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            invalid_prices.append({"product": p.get('title', 'Unknown'), "reason": "가격 형식 오류"})
            continue
        
        # 가격 변환
        original_price = price
        if price > 1000:
            price = price / 100
        
        # 가격 검증
        if 0 < price <= 1000:
            valid_prices.append({
                "product": p.get('title', 'Unknown'),
                "brand": p.get('brand', 'Unknown'),
                "original_price": original_price,
                "converted_price": price
            })
        else:
            invalid_prices.append({
                "product": p.get('title', 'Unknown'),
                "reason": f"가격 범위 초과 (변환 후: ${price:.2f})"
            })
    
    if valid_prices:
        prices_only = [p["converted_price"] for p in valid_prices]
        
        print(f"\n[유효한 가격 데이터] {len(valid_prices)}개")
        print(f"  - 최소 가격: ${min(prices_only):.2f}")
        print(f"  - 최대 가격: ${max(prices_only):.2f}")
        print(f"  - 평균 가격: ${sum(prices_only) / len(prices_only):.2f}")
        print(f"  - 중앙값: ${sorted(prices_only)[len(prices_only)//2]:.2f}")
        
        # 가격 분포
        print(f"\n[가격 분포]")
        price_ranges = [
            (0, 10, "$0-$10"),
            (10, 20, "$10-$20"),
            (20, 30, "$20-$30"),
            (30, 50, "$30-$50"),
            (50, 100, "$50-$100"),
            (100, 1000, "$100+")
        ]
        
        for min_p, max_p, label in price_ranges:
            count = sum(1 for p in prices_only if min_p <= p < max_p)
            if count > 0:
                percentage = (count / len(prices_only)) * 100
                print(f"  - {label}: {count}개 ({percentage:.1f}%)")
        
        # 상위/하위 5개 제품
        print(f"\n[가격 상위 5개 제품]")
        sorted_by_price = sorted(valid_prices, key=lambda x: x["converted_price"], reverse=True)
        for i, p in enumerate(sorted_by_price[:5], 1):
            print(f"  {i}. {p['brand']} - {p['product'][:40]}: ${p['converted_price']:.2f}")
        
        print(f"\n[가격 하위 5개 제품]")
        for i, p in enumerate(sorted_by_price[-5:], 1):
            print(f"  {i}. {p['brand']} - {p['product'][:40]}: ${p['converted_price']:.2f}")
    
    if invalid_prices:
        print(f"\n[유효하지 않은 가격 데이터] {len(invalid_prices)}개")
        for p in invalid_prices[:5]:
            print(f"  - {p['product'][:40]}: {p['reason']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        calculate_price_statistics()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
