"""
Verify that every package in common.lock is platform-neutral. It should flag if any packages are
added to common requirements which actually differ per OS and require different lock versions.
(like pyinstaller, which needs `macholib` only on macOS). Otherwise, common.lock would silently
fail wrong for one OS by installing wrong package.

For each package pinned in the lock, every dependency marker is evaluated under a Linux environment
and a macOS environment; if any marker resolves differently between the two, the package is flagged.

Usage:
    python scripts/verify-common-platform-neutral.py requirements/common.lock
"""

import importlib.metadata as md
import re
import sys

from packaging.requirements import Requirement

LINUX = {"os_name": "posix", "sys_platform": "linux", "platform_system": "Linux",
         "platform_machine": "x86_64", "python_version": "3.14", "python_full_version": "3.14.0",
         "implementation_name": "cpython", "extra": ""}
MAC = {**LINUX, "sys_platform": "darwin", "platform_system": "Darwin", "platform_machine": "arm64"}

# Top-level pinned package names from the lock (e.g. `pyyaml==6.0.3 \`).
_NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==")


def _locked_package_names(lock_path: str) -> list[str]:
    with open(lock_path) as fh:
        return [m.group(1) for line in fh if (m := _NAME_RE.match(line))]


def main() -> int:
    lock_path = sys.argv[1]
    flagged: list[tuple[str, str]] = []

    for name in _locked_package_names(lock_path):
        try:
            reqs = md.requires(name) or []
        except md.PackageNotFoundError:
            print(f'{name}: package not installed', file=sys.stderr)
            return 1

        for raw in reqs:
            marker = Requirement(raw).marker

            if marker and marker.evaluate(LINUX) != marker.evaluate(MAC):
                flagged.append((name, raw))

    if flagged:
        print(
            "common.lock is not platform-neutral - these packages have OS-specific dependencies:",
            file=sys.stderr,
        )

        for name, raw in flagged:
            print(f"  {name}: needs [{raw}]", file=sys.stderr)

        print(
            "Move these packages from common requirements to the OS-specific and regenerate lock files.",
            file=sys.stderr,
        )

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
