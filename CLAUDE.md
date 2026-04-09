# MdToHtml Project Guide

## Overview
마크다운 파일을 스타일 적용된 HTML로 변환하는 데스크톱 GUI 앱.
Claude Code CLI가 실제 변환 작업을 수행하며, Python GUI는 얇은 UI 래퍼 역할.

## 실행 방법
```bash
python gui/app.py
```

## 기술 스택
- **GUI**: customtkinter (Python, Windows 11 네이티브 룩)
- **변환 엔진**: Claude Code CLI (`claude -p` 모드)
- **의존성**: `pip install customtkinter`

## 파일 구조
```
gui/
  app.py          - 메인 GUI (customtkinter)
  converter.py    - Claude Code subprocess 호출 및 HTML 추출
  theme_loader.py - design-md/ 스캔 및 DESIGN.md 로드

design-md/        - 58개 브랜드 디자인 시스템 (stripe, notion, claude 등)
output/           - 변환된 HTML 파일 저장 기본 경로
```

## 변환 흐름
1. 사용자: 마크다운 파일 + 테마 선택 + 프롬프트 입력
2. app.py: converter.run_conversion() 호출 (백그라운드 스레드)
3. converter.py: DESIGN.md + 사용자 프롬프트로 최종 프롬프트 구성
4. `claude -p "prompt" --dangerously-skip-permissions` 실행
5. Claude Code: 마크다운 파일 읽기 → HTML 생성
6. converter.py: HTML 추출 → 파일 저장

## 사용자 요구사항 반영 방법
Claude Code를 이 프로젝트 루트에서 실행하면 CLAUDE.md를 자동 참조합니다.
GUI의 프롬프트 필드로 직접 지시하거나, 이 CLAUDE.md를 수정하여 기본 동작을 변경할 수 있습니다.

## 테마 추가
1. `design-md/새테마/DESIGN.md` 파일 생성
2. GUI 재시작 시 자동으로 테마 목록에 표시됨
