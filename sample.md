# MdToHtml 샘플 문서

이 문서는 MdToHtml 변환기의 기능을 테스트하기 위한 샘플입니다.

## 텍스트 서식

**굵은 텍스트**, *기울임꼴*, ~~취소선~~, `인라인 코드`

[링크 예시](https://example.com)

## 목록

### 순서 있는 목록
1. 첫 번째 항목
2. 두 번째 항목
3. 세 번째 항목

### 순서 없는 목록
- 사과
- 바나나
- 체리

### 작업 목록
- [x] 완료된 작업
- [ ] 진행 중인 작업
- [ ] 예정된 작업

## 인용문

> "디자인은 단순히 어떻게 보이고 느껴지는지가 아니다.
> 디자인은 어떻게 작동하는지다." — 스티브 잡스

## 코드 블록

```python
def convert_markdown(file_path: str, theme: str) -> str:
    """마크다운 파일을 스타일 적용된 HTML로 변환합니다."""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    
    return apply_theme(content, theme)
```

```javascript
const greet = (name) => `안녕하세요, ${name}!`;
console.log(greet('세상'));
```

## 표

| 기능 | 상태 | 설명 |
|------|------|------|
| 마크다운 파싱 | ✅ 완료 | Claude Code 사용 |
| 테마 시스템 | ✅ 완료 | 58개 브랜드 테마 |
| HTML 내보내기 | ✅ 완료 | 독립형 HTML |
| 실시간 로그 | ✅ 완료 | 실시간 출력 표시 |

## 수평선

---

## 이미지 (URL)

![샘플 이미지](https://picsum.photos/600/300)

## 중첩 목록

- 항목 1
  - 하위 항목 1-1
  - 하위 항목 1-2
    - 더 깊은 항목
- 항목 2
  - 하위 항목 2-1

---

*MdToHtml Converter로 변환된 문서입니다.*
