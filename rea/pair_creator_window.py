"""Optional, separate Tk window for two-owner same-schema ROW APPEND."""
from pathlib import Path
from types import SimpleNamespace

from rea.mvp import REQUIRED
from rea.pair_creator import PairCreatorController


def build_pair_window(parent):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    window = tk.Toplevel(parent)
    window.title("REA_Web · 두 파일 ROW APPEND (JOIN 아님)")
    window.geometry("820x740")
    body = ttk.Frame(window, padding=15)
    body.pack(fill="both", expand=True)
    controller = PairCreatorController()
    ttk.Label(body, text="동일 컬럼 두 파일만 행 추가 · JOIN 불가",
              font=("", 14, "bold")).pack(anchor="w")
    ttk.Label(body, wraplength=780, justify="left", text=(
        "두 파일 모두 사용 권한이 있는 비민감 자료만 선택하십시오. "
        "행은 생성 ZIP 내부 SQLite에 포함됩니다. 개별 APPROVE 두 번과 최종 APPEND가 필요합니다."
    )).pack(anchor="w", pady=6)

    sources = [tk.StringVar(), tk.StringVar()]
    destination = tk.StringVar()
    name = tk.StringVar(value="REA two-source append")
    rights = [tk.BooleanVar(value=False), tk.BooleanVar(value=False)]
    approvals = [tk.StringVar(), tk.StringVar()]
    final_approval = tk.StringVar()
    fields = {key: tk.StringVar() for key in REQUIRED}
    status = tk.StringVar(value="먼저 두 파일을 선택하고 검사하세요.")

    def reset_tokens(*_):
        for v in approvals:
            v.set("")
        for v in rights:
            v.set(False)
        final_approval.set("")

    def reset_inspection(*_):
        controller.clear()
        reset_tokens()
        for v in fields.values():
            v.set("")
        for combo in combos.values():
            combo.configure(values=())
        preview.configure(text="검사 무효화 · 다시 검사")
        status.set("파일 변경됨. 새 검사·매핑·승인이 필요합니다.")

    def choose_source(i):
        path = filedialog.askopenfilename(filetypes=[("CSV/JSON", "*.csv *.json")])
        if path:
            sources[i].set(path)

    def choose_zip():
        path = filedialog.asksaveasfilename(defaultextension=".zip",
                                           filetypes=[("ZIP", "*.zip")])
        if path:
            destination.set(path)

    buttons = []
    for i in range(2):
        line = ttk.Frame(body)
        line.pack(fill="x", pady=3)
        ttk.Label(line, text=f"파일 {i+1}", width=12).pack(side="left")
        ttk.Entry(line, textvariable=sources[i]).pack(side="left", fill="x", expand=True)
        button = ttk.Button(line, text="선택", command=lambda j=i: choose_source(j))
        button.pack(side="left")
        buttons.append(button)

    line = ttk.Frame(body)
    line.pack(fill="x", pady=3)
    ttk.Label(line, text="새 ZIP", width=12).pack(side="left")
    ttk.Entry(line, textvariable=destination).pack(side="left", fill="x", expand=True)
    ttk.Button(line, text="선택", command=choose_zip).pack(side="left")
    line = ttk.Frame(body)
    line.pack(fill="x", pady=3)
    ttk.Label(line, text="앱 이름", width=12).pack(side="left")
    ttk.Entry(line, textvariable=name).pack(side="left", fill="x", expand=True)
    preview = ttk.Label(body, text="두 파일 검사 전", wraplength=780, justify="left")
    preview.pack(anchor="w", pady=8)

    combo_area = ttk.Frame(body)
    combo_area.pack(fill="x", pady=4)
    combos = {}
    for i, role in enumerate(REQUIRED):
        ttk.Label(combo_area, text=f"{role}에 대응하는 공통 원본 컬럼").grid(
            row=i, column=0, sticky="w", pady=3)
        c = ttk.Combobox(combo_area, textvariable=fields[role],
                         values=(), state="readonly", width=42)
        c.grid(row=i, column=1, sticky="ew", padx=5)
        combos[role] = c

    def inspect_action():
        try:
            p = controller.inspect(Path(sources[0].get()), Path(sources[1].get()))
            common = tuple(x for x in p.first_fields if x in p.second_fields)
            for c in combos.values():
                c.configure(values=common)
            for v in fields.values():
                v.set("")
            reset_tokens()
            same = set(p.first_fields) == set(p.second_fields)
            preview.configure(text=(
                f"1번 {p.first_rows}행 SHA256 {p.first_sha[:16]}… 컬럼 {', '.join(p.first_fields)}\n"
                f"2번 {p.second_rows}행 SHA256 {p.second_sha[:16]}… 컬럼 {', '.join(p.second_fields)}\n"
                f"같은 스키마: {'YES' if same else 'NO — ZIP 불가'} · 셀 값 미표시"))
            status.set("서로 다른 세 원본 컬럼을 직접 고르고 양쪽 권한·승인과 APPEND를 입력하세요.")
        except (OSError, ValueError, UnicodeError) as exc:
            reset_inspection()
            messagebox.showerror("검사 거부", str(exc))

    inspect_button = ttk.Button(body, text="1. 두 파일 구조 검사", command=inspect_action)
    inspect_button.pack(anchor="w", pady=7)

    checkboxes, entries = [], []
    for i in range(2):
        line = ttk.Frame(body)
        line.pack(fill="x", pady=4)
        ck = ttk.Checkbutton(line, text=f"{i+1}번 사용 권한 확인", variable=rights[i])
        ck.pack(side="left")
        ttk.Label(line, text="직접 APPROVE").pack(side="left", padx=(15, 5))
        ent = ttk.Entry(line, textvariable=approvals[i], width=14)
        ent.pack(side="left")
        checkboxes.append(ck)
        entries.append(ent)
    line = ttk.Frame(body)
    line.pack(fill="x", pady=7)
    ttk.Label(line, text="최종 행 추가 승인 APPEND").pack(side="left")
    append_entry = ttk.Entry(line, textvariable=final_approval, width=16)
    append_entry.pack(side="left", padx=8)

    def export_action():
        try:
            controller.export(
                Path(sources[0].get()), Path(sources[1].get()),
                Path(destination.get()), name.get(),
                {role: fields[role].get() for role in REQUIRED},
                rights[0].get(), rights[1].get(),
                approvals[0].get(), approvals[1].get(), final_approval.get())
            reset_tokens()
            status.set("ZIP 무결성 PASS (상용 권한·비개발자 Windows 검수와 별개)")
            messagebox.showinfo("ROW APPEND 완료", "두 파일의 행을 이어 붙인 로컬 ZIP을 생성했습니다.")
        except (OSError, ValueError, UnicodeError) as exc:
            status.set("생성 거부. 원본은 변경하지 않았습니다.")
            messagebox.showerror("APPEND 거부", str(exc))

    export_button = ttk.Button(body, text="2. 각 파일 승인·APPEND 후 ZIP 생성",
                               command=export_action)
    export_button.pack(anchor="w", pady=8)
    ttk.Label(body, textvariable=status, wraplength=780).pack(anchor="w")

    for v in sources:
        v.trace_add("write", reset_inspection)
    for v in list(fields.values()) + [destination, name]:
        v.trace_add("write", reset_tokens)

    return SimpleNamespace(
        window=window, controller=controller, source_vars=sources,
        output_var=destination, name_var=name, rights_vars=rights,
        approval_vars=approvals, append_var=final_approval,
        mapped_vars=fields, combos=combos, preview_label=preview,
        status_var=status, source_buttons=buttons, choose_source=choose_source,
        choose_output=choose_zip, inspect_button=inspect_button,
        export_button=export_button, rights_checkboxes=checkboxes,
        approval_entries=entries, append_entry=append_entry,
    )
