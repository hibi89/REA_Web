"""No-network, two-source Tk controller. Never auto-join or auto-approve."""
from dataclasses import dataclass
from pathlib import Path

from rea.mvp import DataError, REQUIRED
from rea.two_source import preflight_pair, pack_pair
from rea.delivery import verify_delivery


@dataclass(frozen=True)
class PairPreview:
    first: Path
    second: Path
    first_sha: str
    second_sha: str
    first_fields: tuple[str, ...]
    second_fields: tuple[str, ...]
    first_rows: int
    second_rows: int


class PairCreatorController:
    def __init__(self):
        self._preview = None

    @property
    def inspected(self):
        return self._preview

    def clear(self):
        self._preview = None

    def inspect(self, first: Path, second: Path):
        self.clear()
        first, second = Path(first).absolute(), Path(second).absolute()
        data = preflight_pair(first, second)
        a, b = data["sources"]
        self._preview = PairPreview(
            first, second, a["sha256"], b["sha256"],
            tuple(a["columns"]), tuple(b["columns"]),
            a["row_count"], b["row_count"])
        return self._preview

    def export(self, first, second, output, name, mapping,
               first_rights, second_rights, first_confirm, second_confirm,
               append_confirm):
        p = self.inspected
        if p is None:
            raise DataError("Inspect BOTH files before export")
        a, b = Path(first).absolute(), Path(second).absolute()
        dest = Path(output).absolute()
        if (a, b) != (p.first, p.second):
            self.clear()
            raise DataError("Files changed since inspection; inspect BOTH again")
        if not (first_rights and second_rights):
            raise DataError("Separate owner-rights checkboxes are required")
        if (first_confirm, second_confirm) != ("APPROVE", "APPROVE"):
            raise DataError("Separate exact APPROVE required for EACH file")
        if append_confirm != "APPEND":
            raise DataError("Final exact APPEND required; no JOIN")
        if not isinstance(name, str) or not name.strip() or len(name) > 100:
            raise DataError("App name must have 1-100 characters")
        if dest.suffix.lower() != ".zip" or dest in (a, b):
            raise DataError("Destination must be a NEW ZIP, not a source")
        if dest.exists() or dest.is_symlink():
            raise FileExistsError("Existing ZIP cannot be overwritten")
        if (not isinstance(mapping, dict) or set(mapping) != set(REQUIRED)
                or any(type(v) is not str for v in mapping.values())
                or len(set(mapping.values())) != 3
                or any(v not in p.first_fields or v not in p.second_fields
                       for v in mapping.values())):
            raise DataError("Three distinct fields must be present in BOTH files")
        if set(p.first_fields) != set(p.second_fields):
            raise DataError("Only identical column sets supported; no JOIN")
        result = pack_pair(a, b, dest, name.strip(), mapping,
                           p.first_sha, p.second_sha,
                           first_confirm, second_confirm, append_confirm)
        verify_delivery(dest)
        self.clear()
        return result
