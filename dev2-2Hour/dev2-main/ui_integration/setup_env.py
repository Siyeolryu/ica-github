"""
환경 변수 설정 도우미 스크립트
사용자가 API 키를 안전하게 설정할 수 있도록 도와줍니다.
"""

import os
from pathlib import Path

def setup_env_file():
    """환경 변수 파일 설정 도우미"""
    print("=" * 60)
    print("환경 변수 설정 도우미")
    print("=" * 60)
    print()
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    # .env.example이 없으면 생성
    if not env_example.exists():
        print("❌ .env.example 파일을 찾을 수 없습니다.")
        return
    
    # .env 파일이 이미 있으면 확인
    if env_file.exists():
        response = input("⚠️  .env 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("취소되었습니다.")
            return
    
    print("다음 정보를 입력하세요 (Enter를 누르면 건너뜁니다):")
    print()
    
    # API 키 입력
    anthropic_key = input("1. Anthropic Claude API 키 (sk-ant-api03-...): ").strip()
    if not anthropic_key:
        print("⚠️  API 키를 입력하지 않았습니다. 나중에 .env 파일을 직접 수정하세요.")
        anthropic_key = "your-anthropic-api-key-here"
    
    # Supabase 설정
    supabase_url = input("2. Supabase URL (https://xxx.supabase.co): ").strip()
    if not supabase_url:
        supabase_url = "https://your-project.supabase.co"
    
    supabase_key = input("3. Supabase Anon Key: ").strip()
    if not supabase_key:
        supabase_key = "your-supabase-anon-key-here"
    
    # .env 파일 생성
    env_content = f"""# 환경 변수 설정 파일
# 이 파일은 .gitignore에 포함되어 Git에 업로드되지 않습니다.

# Anthropic Claude API 키
ANTHROPIC_API_KEY={anthropic_key}

# Supabase 설정
SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={supabase_key}
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print()
    print("✅ .env 파일이 생성되었습니다!")
    print(f"   위치: {env_file.absolute()}")
    print()
    print("⚠️  보안 주의사항:")
    print("   - .env 파일은 절대 Git에 커밋하지 마세요")
    print("   - API 키를 다른 사람과 공유하지 마세요")
    print("   - 키가 노출되면 즉시 재생성하세요")
    print()

def verify_env_setup():
    """환경 변수 설정 확인"""
    print("=" * 60)
    print("환경 변수 설정 확인")
    print("=" * 60)
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print("현재 설정 상태:")
    print()
    
    if anthropic_key and anthropic_key != "your-anthropic-api-key-here":
        masked_key = anthropic_key[:20] + "..." if len(anthropic_key) > 20 else "***"
        print(f"✅ ANTHROPIC_API_KEY: {masked_key}")
    else:
        print("❌ ANTHROPIC_API_KEY: 설정되지 않음")
    
    if supabase_url and supabase_url != "https://your-project.supabase.co":
        print(f"✅ SUPABASE_URL: {supabase_url}")
    else:
        print("❌ SUPABASE_URL: 설정되지 않음")
    
    if supabase_key and supabase_key != "your-supabase-anon-key-here":
        masked_key = supabase_key[:20] + "..." if len(supabase_key) > 20 else "***"
        print(f"✅ SUPABASE_ANON_KEY: {masked_key}")
    else:
        print("❌ SUPABASE_ANON_KEY: 설정되지 않음")
    
    print()
    
    if all([
        anthropic_key and anthropic_key != "your-anthropic-api-key-here",
        supabase_url and supabase_url != "https://your-project.supabase.co",
        supabase_key and supabase_key != "your-supabase-anon-key-here"
    ]):
        print("✅ 모든 환경 변수가 올바르게 설정되었습니다!")
    else:
        print("⚠️  일부 환경 변수가 설정되지 않았습니다.")
        print("   setup_env.py를 실행하거나 .env 파일을 직접 수정하세요.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_env_setup()
    else:
        setup_env_file()
        verify_env_setup()
