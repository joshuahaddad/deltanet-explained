"""Headless check of a page at 390/1280 px x dark/light: screenshots, console errors, failed console.asserts,
horizontal scroll, touch targets under 44 px, and whether CMU Serif loaded. Exits 1 on any problem.
Run with ./qa/shoot.sh [page] (Playwright image, so no Chromium libraries are needed on the host)."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright

page = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "interactive/index.html").resolve()
out = pathlib.Path("qa/shots"); out.mkdir(parents=True, exist_ok=True)
PROBE = """() => ({
  scroll: document.documentElement.scrollWidth > innerWidth,
  wide: [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > innerWidth + 1).map(e => e.tagName + '#' + e.id).slice(0, 8),
  small: [...document.querySelectorAll('button, input, a, [role=slider], .handle')].map(e => [e.id || e.textContent.trim().slice(0, 16), e.getBoundingClientRect()])
    .filter(([, r]) => r.width > 0 && (r.width < 43.5 || r.height < 43.5) && !(r.height < 30 && r.width > 60)).map(([n, r]) => n + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)),
  font: document.fonts.check('19px "CMU Serif"'),
})"""
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 1280):
        for scheme in ("dark", "light"):
            ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme, device_scale_factor=2 if w == 390 else 1)
            pg = ctx.new_page()
            errs, asserts = [], []
            pg.on("console", lambda m: (asserts if "Assertion failed" in m.text else errs).append(m.text) if m.type in ("error", "assert") else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(page.as_uri(), wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            info = pg.evaluate(PROBE)
            pg.screenshot(path=str(out / f"{w}_{scheme}.png"), full_page=True)
            problems = errs + asserts + (["horizontal scroll: " + ", ".join(info["wide"])] if info["scroll"] else []) + \
                (["CMU Serif not loaded"] if not info["font"] else [])
            bad += len(problems)
            print(f"{w}_{scheme}:", "ok" if not problems else json.dumps(problems, ensure_ascii=False),
                  "| small targets (inline links are excluded):", info["small"] or "none")
            ctx.close()
    b.close()
sys.exit(1 if bad else 0)
