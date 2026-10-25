"""Optional offline creator GUI: owner explicitly selects local fields and approves ZIP.

No tkinter import at module load; CI can test its pure controller without a display.
No network, no real files in tests, no Fable/Astra inference, and no override.
Run: python -m rea.creator_gui
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from rea.guided import approved_selection, preflight
from rea.delivery import create_delivery, verify_delivery
from rea.mvp import DataError, REQUIRED

OWNER_NOTICE = (
    "본인이 사용 권한을 가진 비민감 CSV/JSON만 사용하세요. "
    "데이터 원본은 로컬에서만 처리되지만 생성 ZIP의 data.sqlite에는 데이터 행이 포함됩니다. "
    "외부 업로드, 호스팅, 라이선스 승인은 제공하지 않습니다."
)
CLI_FALLBACK = (
    "오프라인 GUI(Tkinter/화면)를 사용할 수 없습니다. "
    "터미널에서 python -m rea.guided inspect --csv 또는 --json <파일>을 실행하고 "
    "python -m rea.guided pack 명령으로 명시적 승인 후 ZIP을 생성하세요."
)


@dataclass(frozen=True)
class Preview:
    source: Path
    sha256: str
    kind: str
    rows: int
    fields: tuple[str, ...]
    field_details: tuple[dict, ...]


class CreatorController:
    """Single-source, one-time reviewed explicit owner ZIP export."""

    def __init__(self):
        self._preview: Preview | None = None

    @property
    def inspected(self) -> Preview | None:
        return self._preview

    def clear(self) -> None:
        self._preview = None

    def inspect(self, source: Path) -> Preview:
        # Clearing FIRST means a malformed/stale next selection never retains consent.
        self.clear()
        source = Path(source).absolute()
        if source.suffix.lower() not in (".csv", ".json"):
            raise DataError("Only one local .csv or flat .json source is supported")
        info = preflight(source)  # rejects symlink, oversized, invalid data
        result = Preview(
            source=source,
            sha256=info["source_sha256"],
            kind=info["source_kind"],
            rows=info["row_count"],
            fields=tuple(field["name"] for field in info["fields"]),
            field_details=tuple(dict(field) for field in info["fields"]),
        )
        self._preview = result
        return result

    def export(self, source: Path, output: Path, app_name: str,
               mapping: dict[str, str], owner_rights: bool, confirmation: str) -> dict:
        preview = self._preview
        if preview is None:
            raise DataError("Inspect a local CSV/JSON before export")
        source = Path(source).absolute()
        output = Path(output).absolute()
        if source != preview.source:
            self.clear()
            raise DataError("Input changed since inspection; inspect again")
        if not owner_rights or confirmation != "APPROVE":
            raise DataError("Owner rights checkbox and exact APPROVE are required")
        if not isinstance(app_name, str) or not app_name.strip() or len(app_name) > 100:
            raise DataError("App name must be 1-100 characters")
        if output.suffix.lower() != ".zip":
            raise DataError("Choose a NEW .zip output name")
        if output == source or output.exists() or output.is_symlink():
            raise FileExistsError("Output exists or is the original; choose a new ZIP path")
        if not isinstance(mapping, dict) or set(mapping) != set(REQUIRED):
            raise DataError("Choose id/title/category explicitly")
        if any(not isinstance(value, str) or value not in preview.fields
               for value in mapping.values()):
            raise DataError("Chosen source column was not in the inspected preview")
        # This confirms current source SHA and validated unique semantic fields.
        approved_selection(source, mapping, preview.sha256, confirmation)
        # Generate only from the inspected source; existing core enforces no-overwrite,
        # SHA pinning, read-only output, atomic ZIP publication and manifest audit.
        result = create_delivery(source, output, app_name.strip(),
                                 approved_mapping=mapping,
                                 expected_source_sha256=preview.sha256)
        verify_delivery(output)
        self.clear()  # no implicit repeat approval after success
        return result


def launch() -> int:
    """GUI initialization is optional; no dependency/display breaks the CLI."""
    try:
        import tkinter as tk
        root = tk.Tk()
        from tkinter import filedialog, messagebox, ttk
    except (ImportError, RuntimeError, OSError, Exception) as exc:
        # Catch TclError in headless runners without requiring tkinter to import.
        # Never report success if the GUI could not be opened.
        print(CLI_FALLBACK + " (" + type(exc).__name__ + ")", file=sys.stderr)
        return 2

    controller = CreatorController()
    root.title("REA_Web | 로컬 웹앱 제작")
    root.minsize(670, 610)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="REA_Web · 오프라인 웹앱 제작", font=("", 16, "bold")).pack(anchor="w")
    ttk.Label(frame, text=OWNER_NOTICE, wraplength=620, justify="left").pack(
        anchor="w", pady=(10, 18))

    source_var = tk.StringVar()
    output_var = tk.StringVar()
    name_var = tk.StringVar(value="REA local owner app")
    approval_var = tk.StringVar()
    rights_var = tk.BooleanVar(value=False)
    mapped_vars = {role: tk.StringVar(value="") for role in REQUIRED}
    status_var = tk.StringVar(value="① 원본 파일을 검사하세요. 셀 원본값은 표시하지 않습니다.")

    def invalidate(*_):
        controller.clear()
        approval_var.set("")
        rights_var.set(False)
        for var in mapped_vars.values():
            var.set("")
        for combo in combos.values():
            combo.configure(values=())
        preview_label.configure(text="검사 전 · 데이터 내용 미표시")
        status_var.set("원본 변경됨. 다시 검사해야 합니다.")

    def add_row(label: str, variable, command, text: str):
        r = ttk.Frame(frame)
        r.pack(fill="x", pady=6)
        ttk.Label(r, text=label, width=15).pack(side="left")
        ttk.Entry(r, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(r, text=text, command=command).pack(side="left", padx=(8, 0))

    def choose_source():
        path = filedialog.askopenfilename(
            title="사용 권한이 있는 비민감 CSV/JSON 선택",
            filetypes=[("CSV / JSON", "*.csv *.json")],
        )
        if path:
            source_var.set(path)

    def choose_output():
        path = filedialog.asksaveasfilename(
            title="새 ZIP 경로 선택 (기존 파일은 덮어쓰지 않음)",
            defaultextension=".zip", filetypes=[("ZIP", "*.zip")],
        )
        if path:
            output_var.set(path)

    add_row("고객 데이터", source_var, choose_source, "파일 선택")
    add_row("납품 ZIP", output_var, choose_output, "새 경로")
    row = ttk.Frame(frame)
    row.pack(fill="x", pady=6)
    ttk.Label(row, text="앱 이름", width=15).pack(side="left")
    ttk.Entry(row, textvariable=name_var).pack(side="left", fill="x", expand=True)

    preview_label = ttk.Label(frame, text="검사 전 · 데이터 내용 미표시",
                              wraplength=620, justify="left")
    preview_label.pack(anchor="w", pady=(15, 6))

    combo_area = ttk.Frame(frame)
    combo_area.pack(fill="x", pady=(5, 10))
    combos = {}
    for index, role in enumerate(REQUIRED):
        ttk.Label(combo_area, text=role + "에 사용할 원본 컬럼").grid(
            row=index, column=0, sticky="w", pady=4)
        combo = ttk.Combobox(combo_area, textvariable=mapped_vars[role],
                             state="readonly", width=40, values=())
        combo.grid(row=index, column=1, sticky="ew", padx=(12, 0))
        combos[role] = combo
    combo_area.columnconfigure(1, weight=1)

    def inspect_action():
        try:
            info = controller.inspect(Path(source_var.get()))
            for combo in combos.values():
                combo.configure(values=info.fields)
            for var in mapped_vars.values():
                var.set("")  # never automatically assign any mapping
            rights_var.set(False)
            approval_var.set("")
            description = " · ".join(
                f"{field['name']} ({field['inferred_type']}, 빈 칸 {field['missing_count']})"
                for field in info.field_details)
            preview_label.configure(
                text=f"입력 {info.kind} · {info.rows}행 · SHA256 {info.sha256[:16]}…\n"
                     f"미승인 컬럼 힌트: {description}")
            status_var.set("② 각 역할의 원본 컬럼을 직접 선택하고 소유권/승인을 확인하세요.")
        except (OSError, ValueError, UnicodeError) as exc:
            invalidate()
            messagebox.showerror("검사 거부", str(exc))

    ttk.Button(frame, text="1. 원본 검사 / 컬럼 미리보기",
               command=inspect_action).pack(anchor="w", pady=(5, 12))
    source_var.trace_add("write", invalidate)
    ttk.Checkbutton(frame, text="원본 데이터의 사용 권한이 있고 비민감 정보임을 확인합니다.",
                    variable=rights_var).pack(anchor="w", pady=(8, 6))
    confirm_row = ttk.Frame(frame)
    confirm_row.pack(fill="x", pady=(3, 10))
    ttk.Label(confirm_row, text="직접 APPROVE 입력").pack(side="left")
    ttk.Entry(confirm_row, textvariable=approval_var, width=18).pack(
        side="left", padx=8)
    ttk.Label(frame, text="구분된 2개 파일 JOIN/데이터 수집/공개 호스팅은 지원하지 않습니다.",
              wraplength=620).pack(anchor="w", pady=(0, 10))

    def export_action():
        try:
            controller.export(
                Path(source_var.get()), Path(output_var.get()), name_var.get(),
                {role: var.get() for role, var in mapped_vars.items()},
                rights_var.get(), approval_var.get(),
            )
            status_var.set("ZIP 생성·무결성 검사 통과 (상용 승인/실사용 Windows 검수 아님)")
            rights_var.set(False)
            approval_var.set("")
            messagebox.showinfo("합성/사용자 제공 로컬 ZIP 생성",
                                "새 ZIP 생성·해시 검사가 완료되었습니다. "
                                "제품/법적 상용 출시는 아직 승인되지 않았습니다.")
        except (OSError, ValueError, UnicodeError) as exc:
            status_var.set("생성 거부. 원본은 보존됩니다. 오류를 확인하세요.")
            messagebox.showerror("생성 거부", str(exc))

    ttk.Button(frame, text="2. 승인 후 새 ZIP 생성", command=export_action).pack(anchor="w")
    ttk.Label(frame, textvariable=status_var, wraplength=620).pack(
        anchor="w", pady=(14, 0))
    root.mainloop()
    return 0


def main() -> int:
    return launch()


if __name__ == "__main__":
    raise SystemExit(main())
