import os
import shutil
import subprocess
import sys
from typing import Optional, Tuple

class ToolchainError(Exception):
    """Raised when toolchain resolution fails."""
    pass

def find_tool(tool_name: str, explicit_path: Optional[str] = None) -> str:
    """
    Resolves the path to a toolchain binary in priority order:
    1. Explicit function argument
    2. Environment variable PGARA_<TOOL_NAME> (e.g. PGARA_CLANG, PGARA_OPT)
    3. shutil.which(tool_name)

    Raises ToolchainError if the tool cannot be found or the resolved path does not exist.
    """
    env_var = f"PGARA_{tool_name.upper()}"
    candidate: Optional[str] = None

    # Priority 1: Explicit argument
    if explicit_path is not None and explicit_path.strip() != "":
        candidate = explicit_path.strip()
        if not os.path.isfile(candidate):
            raise ToolchainError(
                f"'{tool_name}' path does not exist: {candidate}. "
                f"Please verify the path or set the {env_var} environment variable."
            )
        return os.path.abspath(candidate)

    # Priority 2: Environment variable
    env_val = os.environ.get(env_var)
    if env_val is not None and env_val.strip() != "":
        candidate = env_val.strip()
        if not os.path.isfile(candidate):
            raise ToolchainError(
                f"'{tool_name}' path specified in {env_var} does not exist: {candidate}. "
                f"Please set {env_var} to a valid executable path."
            )
        return os.path.abspath(candidate)

    # Priority 3: System PATH via shutil.which
    which_path = shutil.which(tool_name)
    if which_path is not None and os.path.isfile(which_path):
        return os.path.abspath(which_path)

    # Failed to find tool
    raise ToolchainError(
        f"'{tool_name}' executable could not be found. "
        f"Please set the {env_var} environment variable or ensure '{tool_name}' is in your PATH."
    )

def resolve_tool(tool_name: str, explicit_path: Optional[str] = None) -> str:
    """
    Resolves tool path. If resolution fails, prints a clear error message
    and terminates execution with exit code 1 (no traceback).
    """
    try:
        return find_tool(tool_name, explicit_path)
    except ToolchainError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

def get_tool_version(tool_path: str) -> str:
    """Returns the version line of `tool_path --version`."""
    try:
        proc = subprocess.run(
            [tool_path, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if not lines:
            return "unknown version"
        for line in lines:
            if "LLVM version" in line:
                return line
        return lines[0]
    except Exception as err:
        return f"failed to get version: {err}"

def resolve_toolchain(
    clang_path: Optional[str] = None,
    opt_path: Optional[str] = None,
    print_info: bool = True
) -> Tuple[str, str]:
    """Resolves both clang and opt tools and optionally prints their version info."""
    clang = resolve_tool("clang", clang_path)
    opt = resolve_tool("opt", opt_path)
    if print_info:
        print(f"clang: {clang} ({get_tool_version(clang)})")
        print(f"opt  : {opt} ({get_tool_version(opt)})")
    return clang, opt
