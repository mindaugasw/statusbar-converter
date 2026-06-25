# Written by AI. Was needed to bundle tray icon dependencies together in the
# distributable instead of implicitly relying on them being available on other machines.
# ---
#
# PyInstaller hook for gi.repository.AyatanaAppIndicator3.
#
# Why this exists:
# A GObject-Introspection ".typelib" describes a library's API; at runtime libgirepository
# dlopen()s the library it names *by SONAME*. PyInstaller's link-time scanner can't see that
# dlopen, so it bundles the typelib but can miss the shared library behind it. The app then
# silently uses the host's copy of that library -- or fails on a host that lacks it.
#
# PyInstaller's built-in AyatanaAppIndicator3 hook collects the typelib and the *direct*
# library (libayatana-appindicator3.so.1). Its transitive .so chain (indicator/dbusmenu/ido)
# otherwise ships only because PyInstaller's binary-dependency scan happens to follow each
# library's DT_NEEDED entries. This hook makes that chain explicit and auditable so the tray
# icon works on machines without the Ayatana AppIndicator runtime installed.
#
# Paths are resolved dynamically (findSystemLibrary -> ldconfig), never hardcoded, so this
# stays correct across multiarch layouts and distros.

from PyInstaller.depend.bindepend import findSystemLibrary
from PyInstaller.utils.hooks.gi import get_gi_typelibs

# Typelib + direct shared library (libayatana-appindicator3.so.1). Self-sufficient: keeps
# working whether this hook overrides PyInstaller's built-in one or runs alongside it.
binaries, datas, hiddenimports = get_gi_typelibs('AyatanaAppIndicator3', '0.1')

# Transitive .so chain that the direct library pulls in at runtime. Bundled at the root (".")
# so libgirepository finds them by SONAME via PyInstaller's runtime library search path.
_transitiveSonames = [
    'libayatana-indicator3.so.7',
    'libdbusmenu-gtk3.so.4',
    'libdbusmenu-glib.so.4',
    'libayatana-ido3-0.4.so.0',
]

for _soname in _transitiveSonames:
    _path = findSystemLibrary(_soname)
    if _path:
        binaries.append((_path, '.'))
    else:
        from PyInstaller import log as logging

        logging.getLogger(__name__).warning(
            'AyatanaAppIndicator3 hook: could not resolve %s; tray icon may fail on hosts '
            'without it installed', _soname
        )
