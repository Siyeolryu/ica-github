# Scripts 폴더

유틸리티 스크립트 및 데이터 관리 스크립트를 모아둔 폴더입니다.

## 파일 목록

### `export_supabase_data.py`
Supabase 데이터베이스에서 데이터를 추출하여 CSV/JSON 형식으로 내보내는 스크립트입니다.

**사용 방법**:
```bash
python scripts/export_supabase_data.py
```

**기능**:
- Supabase REST API를 통해 테이블 데이터 조회
- JSON 및 CSV 형식으로 데이터 저장
- 지원 테이블: products, reviews, nutrition_info 등

**환경 변수**:
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_ANON_KEY`: Supabase Anon Key

**출력 위치**: `data/` 폴더
