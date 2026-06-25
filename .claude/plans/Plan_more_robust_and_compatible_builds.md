# Build Robustness & Compatibility Plan (Linux distributable)

## Context

### Why this work exists
The Linux distributable was audited for how robust/self-contained it is on machines
other than the build host. The goal: maximize compatibility/robustness without taking
on disproportionate maintenance effort.

### Decisions already settled in discussion (do not re-litigate)
- **No containerization.** ~90% of dev/testing happens with the *visible* GUI running,
  which a container cannot host (tray icon needs the host desktop's StatusNotifierItem
  host; only X11 forwarding gets windows, not the tray). A container would add a second
  environment to maintain while still requiring host deps — net negative for a solo,
  manual-release project.
- **Build stays on the host.** The host is already **Ubuntu 22.04 / glibc 2.35** — a
  solid LTS floor, the same base a container would have used. The practical rule that
  replaces container enforcement: **do not upgrade this build machine past the oldest
  target distro.** Step 4 makes that floor visible so accidental drift is caught.
- **macOS improvements are deferred** (separate future effort: provisioning script +
  `MACOSX_DEPLOYMENT_TARGET`, not in scope here).

### The core finding driving Step 1
PyInstaller bundles the `AppIndicator3-0.1.typelib` but **not** the shared library that
typelib `dlopen`s at runtime (`libappindicator3.so.1`) — libgirepository loads it by
SONAME at runtime, invisible to PyInstaller's link-time scanner. Verified: zero
appindicator/ayatana `.so` entries in the bundle's `Analysis-00.toc`, while the typelib
*is* present. The app therefore works on other machines **only because they happen to
have `libappindicator3` installed**. On a machine without it, the tray icon fails.
It is also the **legacy** stack (from `gir1.2-appindicator3-0.1` in non-multiarch
`/usr/lib/girepository-1.0/`), which newer distros are dropping.

### Evidence gathered (reference for implementation)
- Legacy chain (currently referenced typelib): `libappindicator3.so.1` →
  `libdbusmenu-gtk.so.4`, `libdbusmenu-glib.so.4`.
- **Ayatana chain (migration target):** `libayatana-appindicator3.so.1` →
  `libayatana-indicator3.so.7`, `libdbusmenu-gtk3.so.4`, `libdbusmenu-glib.so.4`,
  `libayatana-ido3-0.4.so.0`.
- Ayatana GI API is a **drop-in**: same `Indicator`, `IndicatorCategory`,
  `IndicatorStatus`, `.new()`, `.set_label/status/menu/icon()`; same `app_indicator_*`
  C symbols. Host already has `AyatanaAppIndicator3-0.1.typelib` + the `.so` chain.
- Already bundled correctly by PyInstaller's gi hooks: full GTK3 stack (libgtk-3,
  libgdk-3, gdk-pixbuf loaders + `loaders.cache`, pango, cairo, gio modules,
  glib/gobject, libgirepository), all core typelibs, compiled GSettings schema.
- `upx=True` in spec is currently a **silent no-op** (upx not on PATH).
- Current onefile bundle ≈ **138 MB**; per-launch extraction to tmp.
- `clipnotify` already requires `GLIBC_2.34`.
- Dependencies: direct deps mostly `==` pinned, but **no lock file** → transitive deps float.

### Side-question answers (folded into the steps)
- **Q: Does Step 1 also migrate to the newer stack, or is that separate?**
  Fold the migration into Step 1. Bundling the deprecated legacy stack now and replacing
  it later is wasted work, and the migration is a ~2-line drop-in (aliased import).
- **Q: Is UPX actually a problem / could it help with size?**
  UPX trades reliability for size: it can corrupt GTK/gi `.so` files (→ crashes) and
  adds in-memory decompression at every launch (slower cold start, compounding the
  onefile tmp-extraction cost). For a tray app that launches once and runs forever the
  startup hit is one-time, but the corruption risk is not worth it. Keep `upx=False`.
  Pursue size separately and safely (see Step 2 optional note): the big, safe wins are
  `strip=True`, `excludes=[...]` for unused modules, and dropping unneeded gdk-pixbuf
  loaders — not UPX.
- **Q: Lock with hashes (Step 5)?** Deferred — discuss tradeoffs at implementation time.

---

## Steps (in execution order)

### Step 1 — Migrate to Ayatana AppIndicator + bundle its `.so` chain  ★ highest value
Fixes the one real distributable defect and moves off the deprecated stack in one go.

- **Code (`src/Service/StatusbarAppLinux.py`):** change
  `gi.require_version('AppIndicator3', '0.1')` → `('AyatanaAppIndicator3', '0.1')` and
  `from gi.repository import AppIndicator3` → `from gi.repository import
  AyatanaAppIndicator3 as AppIndicator3`. Keep the `AppIndicator3` alias so the rest of
  the file (type hint `AppIndicator3.Indicator`, `.new`, `IndicatorCategory`,
  `IndicatorStatus`) is unchanged.
- **Bundling (`scripts/build-spec.sh` + `build/spec-linux-x86_64.spec`):** explicitly add
  the Ayatana `.so` chain so it ships inside the bundle (loadable by SONAME at runtime):
  `libayatana-appindicator3.so.1`, `libayatana-indicator3.so.7`,
  `libdbusmenu-gtk3.so.4`, `libdbusmenu-glib.so.4`, `libayatana-ido3-0.4.so.0`.
  Preferred implementation: a PyInstaller hook (`hooks/hook-gi.repository.AyatanaAppIndicator3.py`
  wired via `hookspath`) that resolves and collects these libs, so paths aren't hardcoded
  and `build-spec.sh` regeneration stays clean. Acceptable fallback: `--add-binary` flags
  in `build-spec.sh` with paths resolved dynamically (e.g. via `ldconfig -p`), not
  hardcoded `/lib/x86_64-linux-gnu/...`.
- **Host dep note:** build host needs `gir1.2-ayatanaappindicator3-0.1` +
  `libayatana-appindicator3-1` installed (already present here; documented in Step 9).
- **Acceptance:** Step 3 audit reports the appindicator typelib's `.so` as *present in
  bundle*; `just run-dist` shows the tray icon + working menu; ideally confirmed on a
  machine/account without the appindicator runtime lib installed.

### Step 2 — Set `upx=False` explicitly
- **`build/spec-linux-x86_64.spec`** (and macOS spec for parity): `upx=False`.
  No-op today, but prevents a future upx install from silently corrupting a `.so`.
- **Optional (separate, only if size matters):** investigate safe size reduction —
  `strip=True`, `excludes=[...]` for unused stdlib/3rd-party modules, prune unneeded
  gdk-pixbuf loaders. Measure before/after. Do NOT use UPX. Can be skipped/deferred.
- **Acceptance:** spec shows `upx=False`; build still runs.

### Step 3 — "What does the bundle still need from the host?" audit script
Automates detection of the exact bug class found in Step 1, on every build.

- **What a typelib is / why this matters (plain explanation, to include in the script
  header):** a `.typelib` is a small binary file describing a library's API for
  GObject-Introspection; each one names the `.so` it needs (e.g. the AppIndicator typelib
  names `libappindicator3.so.1`). PyInstaller bundles the typelibs but can miss the `.so`
  they point to, because that `.so` is loaded *by name at runtime*, invisible to
  PyInstaller's scanner. When the `.so` is missing from the bundle, the app silently
  falls back to the host's copy — or crashes if the host lacks it.
- **Script (`scripts/audit-bundle-deps.sh`, run post-build):** for each `.typelib` in the
  built bundle, extract its referenced shared-library name (parse with `strings`/similar),
  and check whether that `.so` is present in the bundle. Print a clear PASS/WARN list;
  exit non-zero if any referenced `.so` is missing, so it can gate `just build`.
- **Interaction:** easiest against a **onedir/AppDir** tree of loose files (see Step 7);
  for the current onefile, extract first or scan the pre-pack collected dir.
- **Acceptance:** running it on the Step-1 build reports the appindicator `.so` as
  present, and flags nothing unexpected.

### Step 4 — Print the glibc floor on each build
Turns the invisible compatibility floor into a number seen every release.

- **Script (`scripts/print-glibc-floor.sh`, called from `scripts/build.sh`):** walk the
  bundle's binaries/`.so` files, run `objdump -T`, collect the max `GLIBC_x.y` symbol
  version across all of them, and print it (e.g. "Bundle requires glibc >= 2.35").
- **Interaction:** onefile hides packed `.so` from `objdump`; simplest against the
  onedir/AppDir tree (Step 7) or by scanning the bundled input libs (venv `.so` +
  resolved system libs + clipnotify, which alone needs `GLIBC_2.34`).
- **Acceptance:** build output prints a single max-glibc number; sanity-matches host
  (~2.35) today.

### Step 5 — Lock dependencies with hashes  ⚠ DEFERRED (discuss before implementing)
Goal: reproducible venvs (transitive deps currently float). Likely `pip-compile`
(pip-tools) or `uv pip compile` to generate a fully pinned, hashed lock from `.in` files,
with `venv-install.sh` installing from the lock. **Do not implement yet** — discuss
tooling choice and workflow impact with the user first.

### Step 6 — Strengthen `_verifyGiLoads` in `scripts/venv-install.sh`
Make a missing host dep fail loudly at `just venv-install` (the on-host equivalent of the
container's fail-loud guarantee).

- Extend the existing check (currently only `Gtk`) to also
  `require_version('AyatanaAppIndicator3', '0.1')` and import it.
- Add a Python-version assertion (project pins 3.14).
- **Acceptance:** on a host missing the ayatana typelib, `just venv-install` fails with a
  clear message instead of deferring the failure to runtime.

### Step 7 — Package the distributable as an AppImage
Standard single-file Linux distribution format with desktop integration; can carry extra
system libs for broader compat.

- **Implies switching the Linux build to PyInstaller `--onedir`** (onefile-inside-AppImage
  double-extracts and is wasteful). This also removes the per-launch tmp extraction
  (faster startup) and makes Steps 3 & 4 trivial (loose, auditable files).
- Build an AppDir (PyInstaller onedir output + `.desktop` file + icon), then run
  `appimagetool`/`linuxdeploy`. Replaces the current `.zip` packaging in
  `scripts/build.sh`'s `_createZip` for Linux.
- **Caveat to document:** AppImage needs FUSE (libfuse2) on the host; note in docs.
- **Open question to resolve at implementation:** keep `.zip` too, or AppImage only?
- **Acceptance:** the `.AppImage` launches on the build host and shows the working tray
  app; Step 3 audit + Step 4 floor run against the AppDir.

### Step 8 — macOS environment-as-code & compatibility floor  ⚠ CONTEXT ONLY (analyze in depth at implementation)
Mirror the Linux reproducibility/compatibility goals on macOS. **Only already-gathered
context from discussion is captured here.** This step must be researched/expanded in depth
when it is actually implemented (likely a separate session) — do not treat the list below
as final.

- **Why it's different from Linux:** macOS builds happen natively on the user's MacBook
  (PyInstaller can't cross-compile; there are no macOS containers). The MacBook is always
  relatively up to date and cannot be downgraded.
- **Key insight:** on macOS the compatibility floor is **not** the build host's OS version —
  it's the **deployment target** baked into the toolchain. The python.org **universal2**
  installer is built against a low deployment target (~macOS 11), so building with it (even
  on a current macOS) yields a low floor. The current build sets **no** deployment target
  and doesn't document which Python is used → the floor is implicit and drifting.

Already-identified actions (validate/expand at implementation time):
- **Pin the bundled Python:** python.org **universal2** at a specific version + checksum,
  **not** Homebrew Python (same spirit as the existing "never Homebrew Python" Linux memory;
  here the reason is deployment target, not glibc).
- **Set `MACOSX_DEPLOYMENT_TARGET`** explicitly in `scripts/build.sh` to commit to a floor.
- **Provisioning as code:** `scripts/macos-setup.sh` + a `Brewfile` (`just`, `create-dmg`) —
  the macOS sibling of the Linux host-deps approach; run manually before a release.
- **`upx=False`** parity (already covered by Step 2).
- **Architecture decision to document:** the spec currently targets `arm64` only → won't run
  on Intel Macs (Rosetta only translates the other direction). Decide arm64-only vs
  `universal2` and document the choice.
- **Set aside as overkill** for manual releases (recorded so they aren't re-investigated):
  pinned macOS VM (Tart/Packer) and Nix flake.
- **Tentative files:** `scripts/build.sh` (deployment target), `scripts/macos-setup.sh`
  *(new)*, `Brewfile` *(new)*, `build/spec-macos-arm64.spec`.

### Step 9 — Update `docs/building.md` (LAST)
Done last because earlier steps change the inputs.

- Fix stale content: Python **3.14** (not 3.10); correct apt deps
  (`libgirepository1.0-dev`, `libcairo2-dev`, `pkg-config`, `gir1.2-gtk-3.0`,
  `gir1.2-ayatanaappindicator3-0.1`, `libayatana-appindicator3-1`, `libxfixes-dev` for
  clipnotify; drop the inaccurate `libxcomposite-dev`).
- Document the **glibc-floor rule** (keep build machine on oldest target LTS).
- Document new scripts (audit, glibc floor) and the AppImage/FUSE requirement.
- Optionally add `scripts/host-deps.sh` with the apt list as lightweight "env as code".
- Update `README.md` install instructions if the AppImage changes the download/run UX.
- **Update the supported-environments claim** in `README.md` (currently *"built for and
  tested on Ubuntu, Gnome"*): once verified per the test matrix below, list KDE and state
  the X11/Wayland session caveat.

---

## Files to be modified / created
- `src/Service/StatusbarAppLinux.py` — Ayatana aliased import (Step 1).
- `scripts/build-spec.sh`, `build/spec-linux-x86_64.spec` — bundle `.so` chain, `upx=False`,
  likely `--onedir` (Steps 1, 2, 7).
- `build/spec-macos-arm64.spec` — `upx=False` parity (Step 2).
- `hooks/hook-gi.repository.AyatanaAppIndicator3.py` *(new, preferred)* — collect Ayatana
  libs (Step 1).
- `scripts/audit-bundle-deps.sh` *(new)* — Step 3.
- `scripts/print-glibc-floor.sh` *(new)* — Step 4.
- `scripts/build.sh` — call audit + glibc floor; AppImage packaging (Steps 3, 4, 7).
- `scripts/venv-install.sh` — strengthen `_verifyGiLoads` (Step 6).
- `scripts/build.sh` (`MACOSX_DEPLOYMENT_TARGET`), `scripts/macos-setup.sh` *(new)*,
  `Brewfile` *(new)* — Step 8 (macOS, context-only for now).
- `docs/building.md`, `README.md`, optional `scripts/host-deps.sh` — Step 9.
- *(Deferred)* lock file + `requirements*.in` — Step 5.

## Verification (end-to-end)
1. `just venv-install` — succeeds; Step-6 check passes (and fails loudly if ayatana typelib absent).
2. `just build` — runs; Step-3 audit shows the appindicator `.so` present; Step-4 prints the glibc floor.
3. `just run-dist` (and/or the `.AppImage`) — tray icon appears, menu works, a clipboard
   conversion updates the statusbar label.
4. Strongest check: run the artifact on a machine/user account **without**
   `libayatana-appindicator3-1` installed — it must still show the tray icon (proves the
   `.so` chain is truly bundled).

## Cross-environment test matrix (mostly MANUAL verification)
These are compatibility *verification* tasks, not build changes — the **same single build
targets all desktop environments** (Linux apps are not built per-DE). Noted here so they
aren't lost; almost all require running on real sessions/machines by hand.

**Desktop environments**
- **KDE Plasma — expected to work, but must be tested.** The tray uses the
  StatusNotifierItem (SNI) D-Bus protocol, which originated from KDE; Plasma has *native*
  SNI support, so the Ayatana tray icon (Step 1) should work out of the box — arguably
  better than GNOME, which needs the AppIndicator extension. No code/build change expected;
  confirm tray icon + menu + a clipboard conversion on a real Plasma session.
- GNOME — current primary target (works, with the AppIndicator-extension caveat).
- *(Optional)* XFCE / Cinnamon — same SNI story; test only if reach matters.

**Display server (the axis that actually matters — orthogonal to which DE)**
- App is **X11-based** (`xsel`, `clipnotify`/XFixes). X11 sessions: expected to work.
- **Wayland — must be tested.** Runs via XWayland. Expectation: tray icon works (D-Bus/SNI),
  but **clipboard watching may be limited** — Wayland sandboxes clipboard access, so
  `clipnotify`'s XFixes polling may miss copies made by native Wayland apps. Test on a
  Wayland session (GNOME-Wayland and/or KDE-Wayland) and record the actual clipboard
  behavior.

**Distro / glibc floor**
- **Test on newer Ubuntu versions** (e.g. 24.04) in addition to the 22.04 build base, to
  confirm forward compatibility (a 22.04-built binary running on newer glibc — expected
  fine, but verify). Complements Step 4, which guards the *lower* bound.

## Risks / open questions
- **Step 1 lib placement:** the bundled `.so` must be found by SONAME at runtime; verify
  via Step 3 audit + an actual clean run, not just presence in the TOC.
- **Steps 3/4 vs onefile:** cleanest after the Step-7 onedir switch; if Step 7 slips,
  these scripts must extract/locate packed libs.
- **Step 7 format:** AppImage-only vs AppImage + zip — decide with user.
- **Step 5:** deferred pending discussion.
- **No container = no enforced floor:** mitigated by Step 4 visibility + discipline of not
  upgrading the build host past the oldest target.
