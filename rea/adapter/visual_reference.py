"""Bounded computed-style observations for REA reference design proposals.

Only structural counts and CSS colors leave the browser. No page HTML, text,
URLs beyond the origin, screenshots, asset bytes, or cookies are exported.
The standalone URL capture runs with JavaScript disabled and same-origin GET
requests only; observations are hints, never licensed design/source assets.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import socket
from urllib.parse import urlsplit

SCHEMA = "rea.visual_reference.v0.1"
COLOR = re.compile(r"^#[0-9a-f]{6}$")
MAX_JSON_BYTES = 16 * 1024
MAX_COMPONENTS = 30
COLOR_KEYS = ("canvas", "surface", "ink", "navigation", "accent")
JS_OBSERVE = r"""() => {
  const first = (s) => document.querySelector(s);
  const style = (el, key) => el ? getComputedStyle(el)[key] : null;
  const nav = first('aside nav, nav, [role="navigation"]');
  const shell = nav ? (nav.closest('aside') || nav.closest('header') || nav) : null;
  const navbox = shell ? shell.getBoundingClientRect() : null;
  const panel = first('main article, main section, .panel, .card, article, section');
  const button = first('button, [role="button"]');
  const link = first('a[href]');
  let layout='unknown';
  if (navbox && navbox.width > 0 && navbox.height > 0) {
    if (navbox.width < innerWidth*0.36 && navbox.height > innerHeight*0.42 && navbox.left < innerWidth*0.24) layout='sidebar';
    else if(navbox.width > innerWidth*0.42 && navbox.height < innerHeight*0.35) layout='topbar';
  }
  const visible = el => !!(el && el.getBoundingClientRect().width && el.getBoundingClientRect().height);
  const counts = {
    navigation: document.querySelectorAll('nav, [role="navigation"]').length,
    buttons: document.querySelectorAll('button,[role="button"]').length,
    tables: document.querySelectorAll('table').length,
    forms: document.querySelectorAll('form').length,
    inputs: document.querySelectorAll('input, select, textarea').length,
    card_like: document.querySelectorAll('.card,.panel,article,[class*="metric"],[class*="widget"]').length
  };
  for (const k of Object.keys(counts)) counts[k]=Math.min(counts[k],30);
  return {
    origin: location.origin,
    layout,
    viewport: {width:innerWidth,height:innerHeight},
    colors: {
      canvas: style(document.body,'backgroundColor'),
      surface: style(panel,'backgroundColor'),
      ink: style(document.body,'color'),
      navigation: style(shell,'backgroundColor'),
      accent: style(button,'backgroundColor') || style(link,'color')
    },
    components: counts,
    evidence: {navigation_visible: visible(nav), panel_visible: visible(panel), button_visible: visible(button)}
  };
}"""


class VisualError(ValueError):
    """Untrusted or weak visual evidence cannot be used for a design claim."""


def _hex_color(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 40:
        return None
    if COLOR.fullmatch(value.lower()):
        return value.lower()
    match = re.fullmatch(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*([\d.]+))?\s*\)", value)
    if not match:
        return None
    channels = [int(match.group(i)) for i in range(1, 4)]
    if any(c > 255 for c in channels):
        return None
    if match.group(4) is not None and float(match.group(4)) < 0.99:
        return None
    return "#" + "".join(f"{n:02x}" for n in channels)


def _origin(value: object, *, allow_loopback: bool = False) -> str:
    if not isinstance(value, str) or len(value) > 2100:
        raise VisualError("invalid browser origin")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if (parsed.scheme not in ("http", "https") or parsed.username is not None
                or parsed.password is not None or not host or parsed.path not in ("", "/")
                or parsed.query or parsed.fragment or not re.fullmatch(r"[a-zA-Z0-9.\-]+", host)):
            raise VisualError("invalid browser origin")
        if not allow_loopback and (host.lower() == "localhost" or host.lower().endswith(".localhost")):
            raise VisualError("local target is not a public reference")
        return f"{parsed.scheme}://{host.lower()}" + (f":{parsed.port}" if parsed.port is not None else "")
    except ValueError as exc:
        raise VisualError("invalid browser origin") from exc


def sanitize_observation(raw: dict, *, allow_loopback: bool = False) -> dict:
    """Whitelist schema after observing actual DOM; discard strings/content/URLs."""
    if not isinstance(raw, dict):
        raise VisualError("visual observation must be an object")
    origin = _origin(raw.get("origin"), allow_loopback=allow_loopback)
    layout = raw.get("layout")
    if layout not in ("sidebar", "topbar", "unknown"):
        raise VisualError("invalid layout")
    viewport = raw.get("viewport")
    if not isinstance(viewport, dict) or any(type(viewport.get(k)) is not int or not 320 <= viewport[k] <= 3840 for k in ("width", "height")):
        raise VisualError("invalid viewport")
    colors = raw.get("colors")
    if not isinstance(colors, dict):
        raise VisualError("missing colors")
    safe_colors = {key: _hex_color(colors.get(key)) for key in COLOR_KEYS}
    components = raw.get("components")
    expected = ("navigation", "buttons", "tables", "forms", "inputs", "card_like")
    if not isinstance(components, dict) or any(type(components.get(k)) is not int or not 0 <= components[k] <= MAX_COMPONENTS for k in expected):
        raise VisualError("invalid component counts")
    evidence = raw.get("evidence")
    if not isinstance(evidence, dict) or any(type(evidence.get(k)) is not bool for k in ("navigation_visible", "panel_visible", "button_visible")):
        raise VisualError("invalid visibility evidence")
    measured = sum(c is not None for c in safe_colors.values())
    if measured < 2:
        raise VisualError("insufficient observable colors")
    body = {
        "schema_version": SCHEMA,
        "status": "REVIEW_REQUIRED",
        "origin": origin,
        "capture_method": "BROWSER_COMPUTED_STYLE_DOM",
        "layout": layout,
        "viewport": {"width": viewport["width"], "height": viewport["height"]},
        "colors": safe_colors,
        "components": {key: components[key] for key in expected},
        "evidence": {key: evidence[key] for key in ("navigation_visible", "panel_visible", "button_visible")},
        "limitations": ["single_viewport_only", "structure_and_color_hints_not_pixel_replica",
                        "no_external_fonts_or_assets_copied", "computed_styles_not_ownership_proof"],
    }
    body["sha256"] = hashlib.sha256(json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if len(json.dumps(body).encode()) > MAX_JSON_BYTES:
        raise VisualError("visual observation too large")
    return body


def validate_visual(visual: dict, *, expected_origin: str, allow_loopback: bool = False) -> dict:
    """Normalize and rehash an untrusted stored artifact; never trust unvalidated CSS."""
    if not isinstance(visual, dict) or visual.get("schema_version") != SCHEMA or visual.get("status") != "REVIEW_REQUIRED" or visual.get("capture_method") != "BROWSER_COMPUTED_STYLE_DOM":
        raise VisualError("unsupported visual reference contract")
    normalized = sanitize_observation(visual, allow_loopback=allow_loopback)
    if normalized["sha256"] != visual.get("sha256"):
        raise VisualError("visual artifact hash mismatch")
    if normalized["origin"] != expected_origin:
        raise VisualError("visual and Fable origins differ")
    return normalized


def capture_page(page, *, allow_loopback: bool = False) -> dict:
    """Observe a page already opened by the caller; no network requests here."""
    return sanitize_observation(page.evaluate(JS_OBSERVE), allow_loopback=allow_loopback)


def _safe_public_target(url: str) -> tuple[str, str]:
    """Return (origin, public IPv4) for one explicitly chosen HTTPS host."""
    if not isinstance(url, str) or len(url) > 2048:
        raise VisualError("invalid URL")
    try:
        p = urlsplit(url)
        host = p.hostname or ""
        if (p.scheme != "https" or p.port not in (None, 443) or p.username is not None or p.password is not None
                or not re.fullmatch(r"[a-zA-Z0-9.\-]+", host) or p.query or p.fragment
                or host.lower() in ("localhost", "metadata.google.internal") or host.lower().endswith(".localhost")):
            raise VisualError("only a public HTTPS URL without query/credentials is permitted")
        # Reject literals, even when a public IP, to require a normal DNS name.
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise VisualError("IP-literal reference targets not allowed")
        candidates = socket.getaddrinfo(host, 443, family=socket.AF_INET, type=socket.SOCK_STREAM)
        public_ips = sorted({item[4][0] for item in candidates if ipaddress.ip_address(item[4][0]).is_global})
        if not candidates or len(public_ips) != len({item[4][0] for item in candidates}):
            raise VisualError("reference DNS contains nonpublic addresses")
        return f"https://{host.lower()}", public_ips[0]
    except (OSError, OverflowError, ValueError) as exc:
        raise VisualError("public HTTPS DNS validation failed") from exc


def capture_public_url(url: str) -> dict:
    """Isolated static-CSS capture, GET-only same-origin, DNS-pinned, JS off.

    Public third-party URL requests are opt-in via CLI; no login/cookies, no
    form posts or cross-origin asset loads. Does not guarantee visual fidelity.
    """
    origin, ip = _safe_public_target(url)
    from playwright.sync_api import sync_playwright
    hostname = urlsplit(origin).hostname
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=[f"--host-resolver-rules=MAP {hostname} {ip}, EXCLUDE localhost"])
        try:
            context = browser.new_context(java_script_enabled=False, service_workers="block", accept_downloads=False)
            def allow(route):
                request = route.request
                u = urlsplit(request.url)
                if (u.scheme == "https" and f"https://{u.hostname}" == origin
                        and u.port in (None, 443) and request.method == "GET"):
                    route.continue_()
                else:
                    route.abort()
            context.route("**/*", allow)
            page = context.new_page()
            page.set_viewport_size({"width": 1365, "height": 900})
            response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
            if response is None or response.status >= 400 or _origin(f"{urlsplit(page.url).scheme}://{urlsplit(page.url).netloc}") != origin:
                raise VisualError("reference navigation refused or failed")
            return capture_page(page)
        finally:
            browser.close()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="REA limited public reference visual evidence capture")
    p.add_argument("--url", required=True, help="authorized public HTTPS URL without query")
    p.add_argument("--out", type=Path, required=True, help="new JSON path; never overwrite")
    p.add_argument("--allow-network", action="store_true", help="explicitly authorize public GET requests")
    args = p.parse_args(argv)
    try:
        if not args.allow_network:
            raise VisualError("public network consent requires --allow-network")
        result = capture_public_url(args.url)
        with args.out.open("x", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except (VisualError, OSError, RuntimeError) as exc:
        p.exit(2, f"VISUAL_CAPTURE_REFUSED: {exc}\n")
    print(f"Visual reference contract: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
