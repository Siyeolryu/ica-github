"""
AI 기반 데이터베이스 스키마 분석 및 정리 모듈
"""

import os
import json
from typing import Dict, Optional
from anthropic import Anthropic
from pathlib import Path

class SchemaAnalyzer:
    """데이터베이스 스키마를 AI로 분석하는 클래스"""
    
    SYSTEM_PROMPT = """당신은 데이터베이스 설계 전문가입니다.
SQL 스키마를 분석하여 다음을 제공합니다:

1. 스키마 구조 요약
2. 테이블 간 관계 분석
3. 인덱스 및 성능 최적화 제안
4. 데이터 무결성 검증
5. 개선 제안사항

**출력 형식:**
{
  "schema_summary": "스키마 전체 요약",
  "tables": [
    {
      "name": "테이블명",
      "purpose": "목적",
      "key_fields": ["주요 필드"],
      "relationships": ["관계 설명"]
    }
  ],
  "indexes": ["인덱스 분석"],
  "optimization_suggestions": ["최적화 제안"],
  "data_quality": "데이터 품질 평가"
}
"""

    def __init__(self, api_key: Optional[str] = None):
        """스키마 분석기 초기화"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY 환경변수가 필요합니다. "
                "환경변수 또는 .env 파일에 설정하세요."
            )
        self.client = Anthropic(api_key=self.api_key)

    def analyze_schema_file(self, schema_file_path: str) -> Dict:
        """
        SQL 스키마 파일 분석
        
        Args:
            schema_file_path: 스키마 파일 경로
        
        Returns:
            분석 결과 딕셔너리
        """
        schema_path = Path(schema_file_path)
        if not schema_path.exists():
            return {"error": f"스키마 파일을 찾을 수 없습니다: {schema_file_path}"}
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        user_prompt = f"""다음 SQL 스키마를 분석해주세요:

```sql
{schema_sql}
```

위 스키마를 분석하여 JSON 형식으로 응답해주세요.
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.2,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            content = response.content[0].text
            
            # JSON 파싱
            try:
                # JSON 코드 블록 제거
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "error": "JSON 파싱 실패",
                    "raw_response": content
                }
        except Exception as e:
            return {"error": str(e)}

    def generate_schema_documentation(self, schema_dir: Optional[str] = None) -> str:
        """
        스키마 문서 자동 생성
        
        Args:
            schema_dir: 스키마 디렉토리 경로 (None이면 현재 디렉토리)
        
        Returns:
            마크다운 형식의 문서 문자열
        """
        if schema_dir is None:
            schema_dir = Path(__file__).parent
        else:
            schema_dir = Path(schema_dir)
        
        schema_file = schema_dir / "schema.sql"
        if not schema_file.exists():
            return "스키마 파일을 찾을 수 없습니다."
        
        analysis = self.analyze_schema_file(str(schema_file))
        
        if "error" in analysis:
            return f"분석 중 오류 발생: {analysis['error']}"
        
        # 마크다운 문서 생성
        doc = f"""# 데이터베이스 스키마 문서

## 스키마 요약
{analysis.get('schema_summary', 'N/A')}

## 테이블 구조

"""
        for table in analysis.get('tables', []):
            doc += f"""### {table.get('name', 'Unknown')}
- **목적**: {table.get('purpose', 'N/A')}
- **주요 필드**: {', '.join(table.get('key_fields', []))}
- **관계**: {', '.join(table.get('relationships', []))}

"""
        
        doc += f"""## 인덱스 분석
{chr(10).join(f'- {idx}' for idx in analysis.get('indexes', []))}

## 최적화 제안
{chr(10).join(f'- {sug}' for sug in analysis.get('optimization_suggestions', []))}

## 데이터 품질 평가
{analysis.get('data_quality', 'N/A')}
"""
        
        return doc

    def save_documentation(self, output_path: str, schema_dir: Optional[str] = None):
        """
        문서를 파일로 저장
        
        Args:
            output_path: 출력 파일 경로
            schema_dir: 스키마 디렉토리 경로
        """
        doc = self.generate_schema_documentation(schema_dir)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc)
        
        print(f"문서가 저장되었습니다: {output_path}")

if __name__ == "__main__":
    analyzer = SchemaAnalyzer()
    schema_dir = Path(__file__).parent
    doc = analyzer.generate_schema_documentation(str(schema_dir))
    print(doc)
    
    # 문서 저장
    output_path = schema_dir / "SCHEMA_DOCUMENTATION.md"
    analyzer.save_documentation(str(output_path), str(schema_dir))
