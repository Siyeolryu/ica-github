"""
빠른 앱 테스트 - 주요 기능만 확인
"""

import sys
import os
import io

# Windows 인코딩 문제 해결
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_basic_functionality():
    """기본 기능 테스트"""
    print("=" * 60)
    print("빠른 기능 테스트")
    print("=" * 60)
    
    # 1. Supabase 연결 테스트
    print("\n1. Supabase 연결 테스트...")
    try:
        from supabase_data import get_all_products, get_all_categories
        products = get_all_products()
        categories = get_all_categories()
        print(f"   ✅ 연결 성공: {len(products)}개 제품, {len(categories)}개 카테고리")
    except Exception as e:
        print(f"   ❌ 연결 실패: {e}")
        return False
    
    # 2. 앱 파일 구조 확인
    print("\n2. 앱 파일 구조 확인...")
    app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    if os.path.exists(app_path):
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            checks = [
                ('캐싱 함수', '@st.cache_data' in content),
                ('필터 검증', 'validate_filters' in content),
                ('필터 히스토리', 'filter_history' in content),
                ('디자인 시스템', 'Pretendard' in content and '--primary-500' in content),
                ('필터 상태 표시', '활성 필터' in content),
            ]
            
            for name, result in checks:
                status = "✅" if result else "❌"
                print(f"   {status} {name}")
            
            return all(result for _, result in checks)
    else:
        print("   ❌ app.py 파일을 찾을 수 없습니다")
        return False

if __name__ == "__main__":
    result = test_basic_functionality()
    print("\n" + "=" * 60)
    if result:
        print("✅ 기본 기능 테스트 통과!")
        print("   Streamlit 앱을 실행할 준비가 되었습니다.")
        print("\n   실행 방법:")
        print("   cd ui_integration")
        print("   streamlit run app.py")
    else:
        print("❌ 일부 기능에 문제가 있습니다.")
    print("=" * 60)
