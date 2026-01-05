"""
Supabase 연결 테스트 스크립트
"""

from database.supabase_client import test_connection, get_supabase_client


def main():
    """연결 테스트 및 기본 정보 출력"""
    print("=" * 50)
    print("Supabase 연결 테스트")
    print("=" * 50)
    
    if test_connection():
        print("\n✅ Supabase 연결 성공!")
        
        # 클라이언트 정보 출력
        client = get_supabase_client()
        print(f"\n📊 Supabase URL: {client.supabase_url}")
        print(f"🔑 API Key 설정: {'✅' if client.supabase_key else '❌'}")
        
        print("\n" + "=" * 50)
        print("연결 테스트 완료")
        print("=" * 50)
    else:
        print("\n❌ Supabase 연결 실패!")
        print("\n확인 사항:")
        print("1. .env 파일이 프로젝트 루트에 있는지 확인")
        print("2. SUPABASE_URL이 올바르게 설정되었는지 확인")
        print("3. SUPABASE_ANON_KEY가 올바르게 설정되었는지 확인")


if __name__ == "__main__":
    main()

