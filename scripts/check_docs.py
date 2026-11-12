"""Execute documentation examples, including notebook cells with top-level await."""

import ast
import asyncio
import inspect
import subprocess
import sys
from pathlib import Path


async def run_example(path: Path) -> None:
    """Run a guide in a notebook-compatible event loop and namespace."""
    code = compile(path.read_text(), str(path), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    namespace = {"__name__": "__main__", "__file__": str(path)}
    result = eval(code, namespace)
    if inspect.isawaitable(result):
        await result


def main() -> int:
    """Run each document in a fresh process so examples cannot share state."""
    if len(sys.argv) == 2:
        asyncio.run(run_example(Path(sys.argv[1])))
        return 0

    root = Path(__file__).resolve().parent.parent
    examples = sorted((root / "docs/guides").glob("*.py")) + sorted((root / "docs/tutorial").glob("*.py"))
    for path in examples:
        result = subprocess.run([sys.executable, __file__, str(path)], cwd=root, check=False, timeout=60)
        if result.returncode:
            sys.stderr.write(f"Documentation example failed: {path.relative_to(root)}\n")
            return result.returncode
    sys.stdout.write(f"Executed {len(examples)} documentation examples.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
