"""
converter.py
Claude Code CLI를 subprocess로 호출하여 마크다운을 HTML로 변환합니다.
--output-format stream-json 으로 실행하여 JSON 이벤트를 실시간 파싱합니다.
"""

import subprocess
import threading
import shutil
import re
import json
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).parent.parent


def find_claude() -> str | None:
    """Claude Code CLI 실행 파일 경로를 찾습니다."""
    # shutil.which로 PATH에서 탐색
    found = shutil.which("claude")
    if found:
        return found

    # Windows 일반 설치 경로
    candidates = [
        Path.home() / ".local" / "bin" / "claude",
        Path("C:/Users") / Path.home().name / "AppData/Local/Programs/claude/claude.exe",
        Path("C:/Program Files/claude/claude.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)

    return None


def build_prompt(md_file_path: str, user_prompt: str, theme_content: str) -> str:
    """Claude Code에 전달할 최종 프롬프트를 구성합니다."""

    theme_section = ""
    if theme_content.strip():
        # DESIGN.md가 너무 길면 앞 200줄만 사용 (토큰 절약)
        lines = theme_content.strip().splitlines()
        if len(lines) > 200:
            lines = lines[:200]
            theme_section = f"""
다음 디자인 시스템 사양을 참고하여 스타일링하세요:

{chr(10).join(lines)}

... (이하 생략)
"""
        else:
            theme_section = f"""
다음 디자인 시스템 사양을 참고하여 스타일링하세요:

{theme_content.strip()}
"""

    user_instruction = user_prompt.strip() if user_prompt.strip() else "아름답고 읽기 좋은 스타일로 변환하세요."

    prompt = f"""마크다운 파일 "{md_file_path}"를 읽고, 스타일이 적용된 완전한 독립형 HTML 파일로 변환하세요.

사용자 지시사항:
{user_instruction}
{theme_section}
요구사항:
- <!DOCTYPE html>로 시작하는 완전한 HTML 파일을 출력하세요
- 모든 CSS는 <style> 태그 안에 인라인으로 포함하세요 (외부 파일 참조 없음)
- Google Fonts는 @import로 포함해도 됩니다
- 코드 블록, 표, 인용문, 목록 등 모든 마크다운 요소를 스타일링하세요
- 반응형 디자인으로 만드세요
- 출력은 오직 HTML 코드만 포함하세요. 설명, 코드 펜스(```), 마크다운 없이 <!DOCTYPE html>로 바로 시작하세요
"""

    return prompt


def extract_html(raw_output: str) -> str:
    """Claude Code 출력에서 순수 HTML을 추출합니다."""
    text = raw_output.strip()

    # 코드 펜스 제거
    if text.startswith("```"):
        # ```html 또는 ``` 제거
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    # <!DOCTYPE html> 이전 내용 제거
    doctype_idx = text.lower().find("<!doctype html")
    if doctype_idx > 0:
        text = text[doctype_idx:]
    elif doctype_idx == -1:
        # DOCTYPE이 없으면 <html 태그 찾기
        html_idx = text.lower().find("<html")
        if html_idx > 0:
            text = text[html_idx:]

    return text


def _format_event(event: dict) -> str | None:
    """stream-json 이벤트를 사람이 읽기 좋은 로그 문자열로 변환합니다."""
    etype = event.get("type", "")
    subtype = event.get("subtype", "")

    # ── 무시할 이벤트 (노이즈) ──────────────────────────────
    if etype == "system" and subtype in ("hook_started", "hook_response"):
        return None
    if etype in ("rate_limit_event",):
        return None

    # ── 세션 초기화 ─────────────────────────────────────────
    if etype == "system" and subtype == "init":
        model = event.get("model", "?")
        return f"[세션 시작] 모델: {model}\n"

    # ── 어시스턴트 메시지 (텍스트 + 도구 호출) ──────────────
    if etype == "assistant":
        message = event.get("message", {})
        lines = []
        for block in message.get("content", []):
            btype = block.get("type", "")

            if btype == "text":
                text = block.get("text", "").strip()
                if text:
                    preview = text[:300] + ("..." if len(text) > 300 else "")
                    lines.append(f"[Claude] {preview}")

            elif btype == "tool_use":
                name = block.get("name", "")
                inp = block.get("input", {})
                # 파일 경로 또는 명령어만 추출해 간결하게 표시
                detail = (
                    inp.get("file_path")
                    or inp.get("path")
                    or inp.get("command")
                    or str(inp)[:100]
                )
                lines.append(f"[도구] {name} → {detail}")

        return "\n".join(lines) + "\n" if lines else None

    # ── 도구 실행 결과 ───────────────────────────────────────
    if etype == "tool_result":
        tool_name = event.get("tool_name", event.get("name", ""))
        return f"[도구 완료] {tool_name}\n" if tool_name else None

    # ── 오류 ────────────────────────────────────────────────
    if etype == "result" and subtype == "error_during_execution":
        err = event.get("error", "알 수 없는 오류")
        return f"[오류] {err}\n"

    # result/success는 run_conversion에서 별도 처리
    return None


def run_conversion(
    md_file_path: str,
    user_prompt: str,
    theme_content: str,
    output_path: str,
    on_output: Callable[[str], None],
    on_done: Callable[[bool, str], None],
) -> None:
    """
    Claude Code CLI를 --output-format stream-json 으로 실행합니다.
    stdout의 JSON 이벤트를 한 줄씩 파싱하여 실시간으로 로그에 표시합니다.
    on_output: 실시간 로그 콜백 (str)
    on_done: 완료 콜백 (success: bool, message: str)
    """

    def _run():
        claude_path = find_claude()
        if not claude_path:
            on_done(False, "Claude Code CLI를 찾을 수 없습니다.")
            return

        prompt = build_prompt(md_file_path, user_prompt, theme_content)

        on_output(f"[INFO] Claude Code: {claude_path}\n")
        on_output(f"[INFO] 입력: {md_file_path}\n")
        on_output(f"[INFO] 출력: {output_path}\n")
        on_output("─" * 60 + "\n\n")

        try:
            proc = subprocess.Popen(
                [
                    claude_path,
                    "--output-format", "stream-json",
                    "--verbose",
                    "-p", prompt,
                    "--dangerously-skip-permissions",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                cwd=str(PROJECT_ROOT),
            )

            html_content = ""

            # stdout: stream-json 이벤트를 한 줄씩 실시간 파싱
            for raw_line in proc.stdout:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    etype = event.get("type", "")

                    # result 이벤트에서 HTML 추출
                    if etype == "result":
                        result_text = event.get("result", "")
                        if result_text:
                            html_content = extract_html(result_text)
                            on_output(f"[결과] HTML 생성 완료 ({len(html_content):,} 자)\n")

                    # 그 외 이벤트는 로그에 표시
                    else:
                        msg = _format_event(event)
                        if msg:
                            on_output(msg)

                except json.JSONDecodeError:
                    # JSON 아닌 줄은 그대로 표시
                    if line:
                        on_output(line + "\n")

            # stderr는 오류 메시지용 (블로킹 없이 한번에)
            stderr = proc.stderr.read()
            if stderr.strip():
                on_output(f"\n[stderr]\n{stderr}\n")

            proc.wait()

            on_output("\n" + "─" * 60 + "\n")

            if proc.returncode != 0:
                on_done(False, f"Claude Code 오류 (코드 {proc.returncode})")
                return

            if not html_content or len(html_content) < 50:
                on_done(False, "HTML 출력이 비어있습니다. 프롬프트를 수정하고 다시 시도하세요.")
                return

            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(html_content, encoding="utf-8")

            on_output(f"[저장] {output_path}\n")
            on_done(True, f"변환 완료! → {output_path}")

        except FileNotFoundError:
            on_done(False, "Claude Code 실행 파일을 찾을 수 없습니다.")
        except Exception as e:
            on_done(False, f"오류 발생: {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
