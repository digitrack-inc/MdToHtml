"""
theme_loader.py
design-md/ 디렉토리에서 디자인 테마를 스캔하고 로드합니다.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DESIGN_MD_DIR = PROJECT_ROOT / "design-md"


def list_themes() -> list[str]:
    """design-md/ 에서 DESIGN.md가 있는 테마 목록을 반환합니다."""
    themes = []
    if not DESIGN_MD_DIR.exists():
        return themes

    for entry in sorted(DESIGN_MD_DIR.iterdir()):
        if entry.is_dir() and (entry / "DESIGN.md").exists():
            themes.append(entry.name)

    return themes


def load_theme(theme_name: str) -> str:
    """선택된 테마의 DESIGN.md 내용을 반환합니다."""
    design_path = DESIGN_MD_DIR / theme_name / "DESIGN.md"
    if not design_path.exists():
        return ""
    return design_path.read_text(encoding="utf-8")


def get_display_name(theme_name: str) -> str:
    """폴더명을 읽기 좋은 표시 이름으로 변환합니다."""
    return theme_name.replace("-", " ").replace(".", " ").title()


if __name__ == "__main__":
    themes = list_themes()
    print(f"발견된 테마: {len(themes)}개")
    for t in themes:
        print(f"  {t}")
