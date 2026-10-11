import importlib
import pkgutil
import src

def test_import_all_src_modules():
    """Smoke test ensuring every module under src/ can be cleanly imported."""
    discovered = []
    for module_info in pkgutil.walk_packages(src.__path__, prefix="src."):
        discovered.append(module_info.name)
        mod = importlib.import_module(module_info.name)
        assert mod is not None
    assert len(discovered) > 0
