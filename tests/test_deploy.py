import ast
from pathlib import Path

from deploy_space import APP_FILES

ROOT = Path(__file__).resolve().parent.parent


def local_imports(module):
    tree = ast.parse((ROOT / f"{module}.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return {n for n in names if (ROOT / f"{n}.py").exists()}


def test_every_imported_module_is_deployed():
    needed, to_check = set(), ["gradio_app"]
    while to_check:
        module = to_check.pop()
        if module in needed:
            continue
        needed.add(module)
        to_check.extend(local_imports(module))

    missing = sorted(f"{m}.py" for m in needed if f"{m}.py" not in APP_FILES)
    assert missing == [], f"Not in APP_FILES: {missing}"