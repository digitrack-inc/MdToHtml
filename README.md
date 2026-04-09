# MdToHtml

마크다운 파일을 58개 브랜드 디자인 테마로 스타일링된 HTML로 변환하는 Python 데스크톱 GUI 앱.

## 개요

MdToHtml은 Claude Code CLI를 변환 엔진으로 활용하는 얇은 GUI 래퍼입니다. 사용자가 마크다운 파일과 디자인 테마를 선택하면, Claude Code가 해당 브랜드의 디자인 시스템을 반영한 독립형(standalone) HTML 파일을 생성합니다.

- Python + customtkinter 기반의 데스크톱 앱 (Windows 11 최적화)
- Stripe, Notion, Vercel, Linear 등 58개 브랜드 디자인 테마 내장
- Claude Code의 `--output-format stream-json` 옵션으로 변환 과정을 실시간 로그에 표시

## 주요 기능

- 마크다운 파일 선택 및 출력 경로 자동 설정
- 58개 브랜드 디자인 테마 드롭다운 선택
- 테마 없이 자유 프롬프트로 변환 가능
- 변환 과정 실시간 스트리밍 로그
- 변환 완료 후 HTML 파일 즉시 열기
- 반응형 독립형 HTML 출력 (CSS 인라인 포함)

## 기술 스택

| 항목 | 내용 |
|------|------|
| GUI 프레임워크 | Python + customtkinter |
| 변환 엔진 | Claude Code CLI (`claude -p --output-format stream-json`) |
| 스트리밍 방식 | subprocess + 백그라운드 스레드 |
| 디자인 테마 | design-md/ 폴더의 DESIGN.md 파일 58개 |

## 사전 요구사항

- **Python 3.11 이상**
- **Claude Code CLI** — PATH에 `claude` 명령어가 설치되어 있어야 합니다.
  - 설치: [Claude Code 공식 문서](https://docs.anthropic.com/ko/docs/claude-code) 참조
- **customtkinter** Python 패키지

## 설치

```bash
# 저장소 클론
git clone https://github.com/JinminKim/MdToHtml.git
cd MdToHtml

# 의존성 설치
pip install customtkinter
```

Claude Code CLI가 PATH에 설치되어 있는지 확인합니다.

```bash
claude --version
```

## 실행

```bash
python gui/app.py
```

앱이 실행되면 하단에 `Claude Code 발견: <경로>` 메시지와 함께 로드된 테마 수가 표시됩니다.

## 사용법

1. **마크다운 파일** — "찾아보기" 버튼으로 변환할 `.md` 파일을 선택합니다. 출력 경로가 자동으로 설정됩니다.
2. **디자인 테마** — 드롭다운에서 원하는 브랜드 테마를 선택합니다. 테마 없이 자유 프롬프트를 사용하려면 `(테마 없음 - 자유 프롬프트)`를 선택합니다.
3. **프롬프트** — 변환 지시사항을 수정하거나 기본값을 그대로 사용합니다.
4. **출력 HTML 파일** — 저장 경로를 확인하거나 변경합니다.
5. **실행** 버튼 클릭 후 실행 로그에서 변환 과정을 실시간으로 확인합니다.
6. 변환 완료 팝업에서 "예"를 선택하면 생성된 HTML 파일이 브라우저에서 열립니다.

### 변환 흐름

```
사용자 입력 (파일 + 테마 + 프롬프트)
        ↓
app.py → converter.run_conversion() 백그라운드 스레드 실행
        ↓
converter.py → DESIGN.md + 프롬프트로 최종 프롬프트 구성
        ↓
claude --output-format stream-json --verbose -p "..." --dangerously-skip-permissions
        ↓
JSON 이벤트 실시간 파싱 → UI 로그 표시
        ↓
result 이벤트에서 HTML 추출 → output/ 폴더에 저장
```

## 디자인 테마 목록 (58개)

| 카테고리 | 테마 |
|----------|------|
| AI / LLM | claude, cohere, minimax, mistral.ai, ollama, opencode.ai, replicate, together.ai, x.ai |
| 개발 도구 | cursor, expo, framer, hashicorp, linear.app, lovable, mintlify, posthog, raycast, sentry, voltagent, warp, webflow, zapier |
| 클라우드 / 인프라 | ibm, mongodb, supabase |
| 디자인 / 협업 | figma, miro, sanity |
| 핀테크 / 금융 | coinbase, kraken, revolut, stripe, wise |
| 커머스 / 소비자 | airbnb, pinterest, spotify, uber |
| 엔터프라이즈 / 기타 | apple, bmw, ferrari, lamborghini, renault, spacex, tesla, nvidia |
| SaaS / 생산성 | airtable, cal, clickhouse, clay, composio, elevenlabs, intercom, resend, runwayml, superhuman, vercel, notion |

## 프로젝트 구조

```
MdToHtml/
├── gui/
│   ├── app.py            # 메인 GUI (customtkinter)
│   ├── converter.py      # Claude Code subprocess 호출 및 HTML 추출
│   └── theme_loader.py   # design-md/ 스캔 및 DESIGN.md 로드
├── design-md/            # 브랜드 디자인 시스템 (58개 테마)
│   ├── stripe/
│   │   └── DESIGN.md
│   ├── notion/
│   │   └── DESIGN.md
│   └── ...
├── output/               # 변환된 HTML 파일 저장 기본 경로
├── sample.md             # 테스트용 샘플 마크다운
├── CLAUDE.md             # Claude Code 프로젝트 가이드
└── README.md
```

## 커스텀 테마 추가

1. `design-md/` 폴더 아래 새 폴더를 만듭니다.
2. 해당 폴더에 `DESIGN.md` 파일을 작성합니다. 컬러 팔레트, 타이포그래피, 컴포넌트 스타일 등 디자인 시스템 사양을 마크다운으로 기술합니다.
3. GUI를 재시작하면 테마 드롭다운에 자동으로 표시됩니다.

```
design-md/
└── my-brand/
    └── DESIGN.md   ← 여기에 디자인 시스템 사양 작성
```

`DESIGN.md`가 200줄을 초과하는 경우 앞 200줄만 Claude Code에 전달됩니다 (토큰 절약).

## 출력 예시

변환된 HTML 파일은 `output/` 폴더에 저장됩니다. 파일명은 입력 파일명과 선택한 테마명을 조합하여 자동 생성됩니다.

```
sample.md + stripe 테마 → output/sample-stripe.html
sample.md + 테마 없음   → output/sample.html
```

생성된 HTML은 모든 CSS가 인라인으로 포함된 독립형 파일로, 별도 의존성 없이 브라우저에서 바로 열 수 있습니다.

## 라이선스

MIT
