"""
app.py
MdToHtml - Markdown to HTML Converter GUI
customtkinter 기반 데스크톱 앱
실행: python gui/app.py
"""

import os
import sys
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gui"))

from theme_loader import list_themes, load_theme, get_display_name
from converter import run_conversion, find_claude

# 앱 테마 설정
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MdToHtml Converter")
        self.geometry("800x720")
        self.minsize(640, 580)
        self.resizable(True, True)

        # 상태
        self._is_running = False
        self._themes = ["(테마 없음 - 자유 프롬프트)"] + list_themes()

        self._build_ui()
        self._check_claude()

    # ─── UI 구성 ───────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 메인 프레임
        main = ctk.CTkScrollableFrame(self, corner_radius=0)
        main.grid(row=0, column=0, sticky="nsew")
        main.grid_columnconfigure(1, weight=1)

        pad = {"padx": 16, "pady": (8, 4)}
        label_w = 120

        row = 0

        # ── 제목 ──
        title = ctk.CTkLabel(
            main, text="MdToHtml Converter",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=row, column=0, columnspan=3, padx=16, pady=(16, 4), sticky="w")
        row += 1

        subtitle = ctk.CTkLabel(
            main, text="마크다운 파일을 Claude Code가 스타일링된 HTML로 변환합니다.",
            font=ctk.CTkFont(size=12), text_color="gray"
        )
        subtitle.grid(row=row, column=0, columnspan=3, padx=16, pady=(0, 12), sticky="w")
        row += 1

        # ── 구분선 ──
        sep1 = ctk.CTkFrame(main, height=1, fg_color="gray70")
        sep1.grid(row=row, column=0, columnspan=3, sticky="ew", padx=16, pady=4)
        row += 1

        # ── 마크다운 파일 ──
        ctk.CTkLabel(main, text="마크다운 파일", width=label_w, anchor="w").grid(
            row=row, column=0, **pad, sticky="w"
        )
        self._md_entry = ctk.CTkEntry(main, placeholder_text="*.md 파일 경로를 선택하거나 입력하세요")
        self._md_entry.grid(row=row, column=1, **pad, sticky="ew")
        ctk.CTkButton(main, text="찾아보기", width=80, command=self._browse_md).grid(
            row=row, column=2, padx=(0, 16), pady=(8, 4)
        )
        row += 1

        # ── 디자인 테마 ──
        ctk.CTkLabel(main, text="디자인 테마", width=label_w, anchor="w").grid(
            row=row, column=0, **pad, sticky="w"
        )
        self._theme_var = ctk.StringVar(value=self._themes[0])
        self._theme_combo = ctk.CTkComboBox(
            main,
            variable=self._theme_var,
            values=self._themes,
            command=self._on_theme_change,
            state="readonly",
        )
        self._theme_combo.grid(row=row, column=1, **pad, sticky="ew")

        self._theme_count_label = ctk.CTkLabel(
            main, text=f"{len(self._themes) - 1}개 테마",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self._theme_count_label.grid(row=row, column=2, padx=(0, 16), pady=(8, 4))
        row += 1

        # ── 프롬프트 ──
        ctk.CTkLabel(main, text="프롬프트", width=label_w, anchor="nw").grid(
            row=row, column=0, padx=16, pady=(8, 4), sticky="nw"
        )
        self._prompt_box = ctk.CTkTextbox(main, height=140, wrap="word")
        self._prompt_box.grid(row=row, column=1, columnspan=2, padx=(0, 16), pady=(8, 4), sticky="ew")
        self._prompt_box.insert("1.0", "아름답고 읽기 좋은 스타일로 변환하세요. 제목, 본문, 코드 블록, 표 등 모든 요소를 디자인 시스템에 맞게 스타일링하세요.")
        row += 1

        # ── 출력 파일 ──
        ctk.CTkLabel(main, text="출력 HTML 파일", width=label_w, anchor="w").grid(
            row=row, column=0, **pad, sticky="w"
        )
        self._out_entry = ctk.CTkEntry(main, placeholder_text="저장할 HTML 파일 경로")
        self._out_entry.grid(row=row, column=1, **pad, sticky="ew")
        ctk.CTkButton(main, text="찾아보기", width=80, command=self._browse_out).grid(
            row=row, column=2, padx=(0, 16), pady=(8, 4)
        )
        row += 1

        # ── 구분선 ──
        sep2 = ctk.CTkFrame(main, height=1, fg_color="gray70")
        sep2.grid(row=row, column=0, columnspan=3, sticky="ew", padx=16, pady=8)
        row += 1

        # ── 실행 버튼 ──
        self._run_btn = ctk.CTkButton(
            main,
            text="▶  실 행",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=44,
            command=self._execute,
        )
        self._run_btn.grid(row=row, column=0, columnspan=3, padx=16, pady=4, sticky="ew")
        row += 1

        # ── 상태 표시 ──
        self._status_label = ctk.CTkLabel(
            main, text="대기 중...",
            font=ctk.CTkFont(size=11), text_color="gray"
        )
        self._status_label.grid(row=row, column=0, columnspan=3, padx=16, pady=(2, 8), sticky="w")
        row += 1

        # ── 출력 로그 ──
        ctk.CTkLabel(main, text="실행 로그", anchor="w", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=row, column=0, columnspan=3, padx=16, pady=(4, 2), sticky="w"
        )
        row += 1

        self._log_box = ctk.CTkTextbox(
            main, height=220,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            state="disabled",
        )
        self._log_box.grid(row=row, column=0, columnspan=3, padx=16, pady=(0, 16), sticky="ew")
        row += 1

        # 하단 버튼 행
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=3, padx=16, pady=(0, 16), sticky="ew")
        btn_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            btn_frame, text="로그 지우기", width=100,
            fg_color="gray50", hover_color="gray40",
            command=self._clear_log
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            btn_frame, text="출력 파일 열기", width=120,
            fg_color="green", hover_color="darkgreen",
            command=self._open_output
        ).grid(row=0, column=2, padx=4)

    # ─── 이벤트 핸들러 ──────────────────────────────────────────

    def _check_claude(self):
        claude = find_claude()
        if not claude:
            self._log("⚠️  Claude Code CLI를 찾을 수 없습니다.\n'claude'가 PATH에 설치되어 있는지 확인하세요.\n\n")
            self._set_status("Claude Code를 찾을 수 없음", "red")
        else:
            self._log(f"✓ Claude Code 발견: {claude}\n")
            self._log(f"✓ 테마 {len(self._themes) - 1}개 로드됨\n\n")
            self._set_status("준비 완료", "green")

    def _browse_md(self):
        path = filedialog.askopenfilename(
            title="마크다운 파일 선택",
            filetypes=[("Markdown", "*.md *.markdown"), ("All files", "*.*")],
        )
        if not path:
            return
        self._md_entry.delete(0, "end")
        self._md_entry.insert(0, path)

        # 출력 경로 자동 설정
        if not self._out_entry.get():
            out_dir = Path(PROJECT_ROOT) / "output"
            stem = Path(path).stem
            theme = self._theme_var.get()
            theme_suffix = f"-{theme}" if theme != "(테마 없음 - 자유 프롬프트)" else ""
            auto_out = out_dir / f"{stem}{theme_suffix}.html"
            self._out_entry.delete(0, "end")
            self._out_entry.insert(0, str(auto_out))

    def _browse_out(self):
        path = filedialog.asksaveasfilename(
            title="출력 HTML 파일 저장",
            defaultextension=".html",
            filetypes=[("HTML", "*.html"), ("All files", "*.*")],
        )
        if path:
            self._out_entry.delete(0, "end")
            self._out_entry.insert(0, path)

    def _on_theme_change(self, theme_name: str):
        # 출력 파일명에 테마명 반영
        md_path = self._md_entry.get()
        out_path = self._out_entry.get()
        if md_path and out_path:
            stem = Path(md_path).stem
            out_dir = Path(out_path).parent
            theme_suffix = f"-{theme_name}" if theme_name != "(테마 없음 - 자유 프롬프트)" else ""
            new_out = out_dir / f"{stem}{theme_suffix}.html"
            self._out_entry.delete(0, "end")
            self._out_entry.insert(0, str(new_out))

    def _execute(self):
        md_path = self._md_entry.get().strip()
        out_path = self._out_entry.get().strip()
        user_prompt = self._prompt_box.get("1.0", "end").strip()
        theme_name = self._theme_var.get()

        # 유효성 검사
        if not md_path:
            messagebox.showerror("오류", "마크다운 파일을 선택하세요.")
            return
        if not Path(md_path).exists():
            messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{md_path}")
            return
        if not out_path:
            messagebox.showerror("오류", "출력 파일 경로를 지정하세요.")
            return

        # 테마 내용 로드
        theme_content = ""
        if theme_name != "(테마 없음 - 자유 프롬프트)":
            theme_content = load_theme(theme_name)
            if not theme_content:
                self._log(f"⚠️  테마 '{theme_name}'의 DESIGN.md를 로드할 수 없습니다.\n")

        self._set_running(True)
        self._clear_log()
        self._log(f"🚀 변환 시작\n")
        self._log(f"   입력: {md_path}\n")
        self._log(f"   테마: {theme_name}\n")
        self._log(f"   출력: {out_path}\n\n")

        run_conversion(
            md_file_path=md_path,
            user_prompt=user_prompt,
            theme_content=theme_content,
            output_path=out_path,
            on_output=self._on_output,
            on_done=self._on_done,
        )

    def _on_output(self, text: str):
        """백그라운드 스레드에서 안전하게 UI 업데이트."""
        self.after(0, lambda: self._log(text))

    def _on_done(self, success: bool, message: str):
        def _update():
            self._set_running(False)
            if success:
                self._set_status(f"✓ {message}", "green")
                self._log(f"\n✅ {message}\n")
                # 완료 팝업
                if messagebox.askyesno("완료", f"{message}\n\n파일을 지금 열겠습니까?"):
                    self._open_output()
            else:
                self._set_status(f"✗ {message}", "red")
                self._log(f"\n❌ {message}\n")
                messagebox.showerror("오류", message)

        self.after(0, _update)

    # ─── 헬퍼 ────────────────────────────────────────────────────

    def _log(self, text: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _set_status(self, text: str, color: str = "gray"):
        self._status_label.configure(text=text, text_color=color)

    def _set_running(self, running: bool):
        self._is_running = running
        self._run_btn.configure(
            state="disabled" if running else "normal",
            text="⏳ 실행 중..." if running else "▶  실 행",
        )

    def _open_output(self):
        out_path = self._out_entry.get().strip()
        if out_path and Path(out_path).exists():
            os.startfile(out_path)
        else:
            messagebox.showwarning("알림", "출력 파일이 아직 생성되지 않았습니다.")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
