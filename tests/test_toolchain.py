import os
import sys
import pytest
from src.toolchain import resolve_tool, find_tool, ToolchainError

def _create_fake_executable(dir_path, name):
    f1 = dir_path / name
    f1.write_text("#!/bin/sh\nexit 0\n")
    f2 = dir_path / f"{name}.exe"
    f2.write_text("fake binary")
    return str(f2) if sys.platform == "win32" else str(f1)

def test_explicit_arg_priority(tmp_path, monkeypatch):
    dir_path = tmp_path / "bin_path"
    dir_path.mkdir()
    _create_fake_executable(dir_path, "clang")

    dir_env = tmp_path / "bin_env"
    dir_env.mkdir()
    env_file = _create_fake_executable(dir_env, "clang")

    dir_arg = tmp_path / "bin_arg"
    dir_arg.mkdir()
    arg_file = _create_fake_executable(dir_arg, "custom_clang")

    monkeypatch.setenv("PATH", str(dir_path))
    monkeypatch.setenv("PGARA_CLANG", env_file)

    resolved = resolve_tool("clang", explicit_path=arg_file)
    assert os.path.samefile(resolved, arg_file)

def test_env_var_priority_over_path(tmp_path, monkeypatch):
    dir_path = tmp_path / "bin_path"
    dir_path.mkdir()
    _create_fake_executable(dir_path, "clang")

    dir_env = tmp_path / "bin_env"
    dir_env.mkdir()
    env_file = _create_fake_executable(dir_env, "custom_clang")

    monkeypatch.setenv("PATH", str(dir_path))
    monkeypatch.setenv("PGARA_CLANG", env_file)

    resolved = resolve_tool("clang")
    assert os.path.samefile(resolved, env_file)

def test_path_resolution_when_only_path_set(tmp_path, monkeypatch):
    dir_path = tmp_path / "bin_path"
    dir_path.mkdir()
    path_file = _create_fake_executable(dir_path, "opt")

    monkeypatch.delenv("PGARA_OPT", raising=False)
    monkeypatch.setenv("PATH", str(dir_path))

    resolved = resolve_tool("opt")
    assert os.path.samefile(resolved, path_file)

def test_nonexistent_explicit_path_exits(capsys):
    nonexistent = "/nonexistent/custom_clang_binary"
    with pytest.raises(SystemExit) as exc_info:
        resolve_tool("clang", explicit_path=nonexistent)
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "clang" in captured.err.lower()
    assert "PGARA_CLANG" in captured.err

def test_nonexistent_env_var_path_exits(monkeypatch, capsys):
    monkeypatch.setenv("PGARA_OPT", "/nonexistent/custom_opt_binary")
    with pytest.raises(SystemExit) as exc_info:
        resolve_tool("opt")
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "opt" in captured.err.lower()
    assert "PGARA_OPT" in captured.err

def test_tool_not_found_exits(monkeypatch, capsys):
    monkeypatch.delenv("PGARA_OPT", raising=False)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(SystemExit) as exc_info:
        resolve_tool("opt")
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "opt" in captured.err.lower()
    assert "PGARA_OPT" in captured.err

def test_find_tool_raises_toolchain_error(monkeypatch):
    monkeypatch.delenv("PGARA_CLANG", raising=False)
    monkeypatch.setenv("PATH", "")
    with pytest.raises(ToolchainError) as exc_info:
        find_tool("clang")
    assert "clang" in str(exc_info.value).lower()
    assert "PGARA_CLANG" in str(exc_info.value)
