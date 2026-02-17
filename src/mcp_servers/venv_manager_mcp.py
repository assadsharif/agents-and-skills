"""
Venv Manager MCP Server — exposes 5 venv management tools via FastMCP (stdio transport).

Tools:
    venv_create         Create a Python virtual environment
    venv_install        Install dependencies into a venv
    venv_diagnose       Diagnose venv health and report issues
    venv_list_packages  List installed packages in a venv
    venv_detect         Detect existing venvs in a project directory
"""

import json
import platform
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP("venv_manager_mcp")

# ---------------------------------------------------------------------------
# Pydantic Input Models
# ---------------------------------------------------------------------------


def _check_path_traversal(v: str) -> str:
    if ".." in v:
        raise ValueError("Path traversal not allowed: '..' in path")
    return v


class VenvCreateInput(BaseModel):
    """Input for venv_create."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        default=".venv",
        description="Directory path for the virtual environment",
    )
    python: Optional[str] = Field(
        None,
        description="Python interpreter to use (e.g., python3.11). Auto-detected if omitted.",
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        return _check_path_traversal(v)


class VenvInstallInput(BaseModel):
    """Input for venv_install."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    venv_path: str = Field(
        default=".venv",
        description="Path to the virtual environment",
    )
    requirements: Optional[str] = Field(
        None,
        description="Path to requirements.txt file",
    )
    packages: Optional[list[str]] = Field(
        None,
        description="List of packages to install (e.g., ['fastapi', 'uvicorn'])",
    )
    editable: Optional[str] = Field(
        None,
        description="Editable install spec (e.g., '.' or '.[dev]')",
    )

    @field_validator("venv_path")
    @classmethod
    def validate_venv_path(cls, v: str) -> str:
        return _check_path_traversal(v)


class VenvDiagnoseInput(BaseModel):
    """Input for venv_diagnose."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        default=".venv",
        description="Path to virtual environment to diagnose",
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        return _check_path_traversal(v)


class VenvListPackagesInput(BaseModel):
    """Input for venv_list_packages."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    venv_path: str = Field(
        default=".venv",
        description="Path to virtual environment",
    )

    @field_validator("venv_path")
    @classmethod
    def validate_venv_path(cls, v: str) -> str:
        return _check_path_traversal(v)


class VenvDetectInput(BaseModel):
    """Input for venv_detect."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    project_dir: Optional[str] = Field(
        None,
        description="Project directory to search. Defaults to current directory.",
    )


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_bin_dir(venv_path: Path) -> Path:
    """Get bin/Scripts directory for the platform."""
    return venv_path / ("Scripts" if platform.system() == "Windows" else "bin")


def _find_python(requested: Optional[str] = None) -> str:
    """Find the best available Python interpreter."""
    candidates = [requested] if requested else []
    candidates += ["python3.12", "python3.11", "python3.10", "python3"]
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    return "python3"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def venv_create(path: str = ".venv", python: Optional[str] = None) -> str:
    """Create a Python virtual environment with pip bootstrap fallback.

    Args:
        path: Directory path for the virtual environment (default: .venv)
        python: Python interpreter to use (auto-detected if omitted)

    Returns JSON: {status, path, python_version, activate_command, message}
    """
    venv_path = Path(path).resolve()
    python_cmd = _find_python(python)
    bin_dir = _get_bin_dir(venv_path)

    # Check existing
    py_bin = bin_dir / "python"
    if py_bin.exists():
        try:
            r = subprocess.run([str(py_bin), "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return json.dumps({
                    "status": "exists",
                    "path": str(venv_path),
                    "python_version": r.stdout.strip(),
                    "message": "Healthy venv already exists",
                })
        except Exception:
            shutil.rmtree(venv_path, ignore_errors=True)

    # Create venv
    r = subprocess.run([python_cmd, "-m", "venv", str(venv_path)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        if "ensurepip" in r.stderr:
            r2 = subprocess.run(
                [python_cmd, "-m", "venv", "--without-pip", str(venv_path)],
                capture_output=True, text=True, timeout=60,
            )
            if r2.returncode != 0:
                return json.dumps({"status": "error", "message": r2.stderr.strip()})
            # Bootstrap pip
            get_pip = Path(tempfile.gettempdir()) / "get-pip.py"
            urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", get_pip)
            r3 = subprocess.run(
                [str(bin_dir / "python"), str(get_pip)],
                capture_output=True, text=True, timeout=120,
            )
            get_pip.unlink(missing_ok=True)
            if r3.returncode != 0:
                return json.dumps({"status": "error", "message": f"pip bootstrap failed: {r3.stderr.strip()}"})
        else:
            return json.dumps({"status": "error", "message": r.stderr.strip()})

    # Upgrade pip
    subprocess.run([str(bin_dir / "pip"), "install", "--upgrade", "pip"], capture_output=True, timeout=60)

    # Get version
    r = subprocess.run([str(bin_dir / "python"), "--version"], capture_output=True, text=True, timeout=5)
    py_version = r.stdout.strip() if r.returncode == 0 else "unknown"

    activate = f"source {venv_path}/bin/activate" if platform.system() != "Windows" else f"{venv_path}\\Scripts\\activate"

    return json.dumps({
        "status": "created",
        "path": str(venv_path),
        "python_version": py_version,
        "activate_command": activate,
        "message": f"Venv created at {venv_path}",
    })


@mcp.tool()
def venv_install(
    venv_path: str = ".venv",
    requirements: Optional[str] = None,
    packages: Optional[list[str]] = None,
    editable: Optional[str] = None,
) -> str:
    """Install dependencies into a virtual environment.

    Args:
        venv_path: Path to the virtual environment
        requirements: Path to requirements.txt file
        packages: List of package names to install
        editable: Editable install spec (e.g., '.[dev]')

    Returns JSON: {status, installed, errors}
    """
    venv = Path(venv_path).resolve()
    pip_bin = str(_get_bin_dir(venv) / "pip")

    if not Path(pip_bin).exists():
        return json.dumps({"status": "error", "message": f"pip not found at {pip_bin}"})

    # Upgrade pip
    subprocess.run([pip_bin, "install", "--upgrade", "pip"], capture_output=True, timeout=60)

    results = []

    if requirements:
        r = subprocess.run([pip_bin, "install", "-r", requirements], capture_output=True, text=True, timeout=300)
        results.append({"source": requirements, "ok": r.returncode == 0, "error": r.stderr.strip()[-200:] if r.returncode else None})

    if packages:
        r = subprocess.run([pip_bin, "install", *packages], capture_output=True, text=True, timeout=300)
        results.append({"source": "packages", "packages": packages, "ok": r.returncode == 0, "error": r.stderr.strip()[-200:] if r.returncode else None})

    if editable:
        r = subprocess.run([pip_bin, "install", "-e", editable], capture_output=True, text=True, timeout=300)
        results.append({"source": "editable", "spec": editable, "ok": r.returncode == 0, "error": r.stderr.strip()[-200:] if r.returncode else None})

    all_ok = all(r["ok"] for r in results)
    return json.dumps({"status": "ok" if all_ok else "partial", "results": results})


@mcp.tool()
def venv_diagnose(path: str = ".venv") -> str:
    """Diagnose virtual environment health and report issues.

    Args:
        path: Path to virtual environment to diagnose

    Returns JSON: {healthy, path, issues, info}
    """
    venv_path = Path(path).resolve()
    issues = []
    info = {}

    if not venv_path.exists():
        return json.dumps({"healthy": False, "path": str(venv_path), "issues": [{"severity": "critical", "message": "Venv does not exist"}], "info": {}})

    bin_dir = _get_bin_dir(venv_path)
    py_bin = bin_dir / "python"
    pip_bin = bin_dir / "pip"

    # Check python
    if py_bin.exists():
        try:
            r = subprocess.run([str(py_bin), "--version"], capture_output=True, text=True, timeout=5)
            info["python"] = r.stdout.strip()
        except Exception as e:
            issues.append({"severity": "critical", "message": f"Python not executable: {e}"})
    else:
        issues.append({"severity": "critical", "message": "Python binary missing"})

    # Check pip
    if pip_bin.exists():
        try:
            r = subprocess.run([str(pip_bin), "--version"], capture_output=True, text=True, timeout=5)
            info["pip"] = r.stdout.strip()
        except Exception as e:
            issues.append({"severity": "high", "message": f"pip not executable: {e}"})
    else:
        issues.append({"severity": "high", "message": "pip binary missing"})

    # WSL NTFS check
    is_wsl = "microsoft" in platform.release().lower() if platform.system() == "Linux" else False
    if is_wsl and str(venv_path).startswith("/mnt/"):
        issues.append({"severity": "warning", "message": "Venv on NTFS mount (/mnt/). Permission issues likely."})

    # Package count
    if pip_bin.exists():
        try:
            r = subprocess.run([str(pip_bin), "list", "--format=json"], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                info["package_count"] = len(json.loads(r.stdout))
        except Exception:
            pass

    critical = [i for i in issues if i["severity"] == "critical"]
    return json.dumps({"healthy": len(critical) == 0, "path": str(venv_path), "issues": issues, "info": info})


@mcp.tool()
def venv_list_packages(venv_path: str = ".venv") -> str:
    """List all installed packages in a virtual environment.

    Args:
        venv_path: Path to virtual environment

    Returns JSON: {status, packages: [{name, version}]}
    """
    venv = Path(venv_path).resolve()
    pip_bin = str(_get_bin_dir(venv) / "pip")

    if not Path(pip_bin).exists():
        return json.dumps({"status": "error", "message": f"pip not found at {pip_bin}"})

    r = subprocess.run([pip_bin, "list", "--format=json"], capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        return json.dumps({"status": "error", "message": r.stderr.strip()})

    packages = json.loads(r.stdout)
    return json.dumps({"status": "ok", "packages": packages, "count": len(packages)})


@mcp.tool()
def venv_detect(project_dir: Optional[str] = None) -> str:
    """Detect existing virtual environments in a project directory.

    Args:
        project_dir: Directory to search. Defaults to current directory.

    Returns JSON: {found: [{path, healthy, python_version}]}
    """
    base = Path(project_dir).resolve() if project_dir else Path.cwd()
    candidates = [".venv", "venv", "env", ".env", "ENV"]
    found = []

    for name in candidates:
        venv_path = base / name
        bin_dir = _get_bin_dir(venv_path)
        py_bin = bin_dir / "python"

        if py_bin.exists():
            try:
                r = subprocess.run([str(py_bin), "--version"], capture_output=True, text=True, timeout=5)
                found.append({
                    "path": str(venv_path),
                    "name": name,
                    "healthy": r.returncode == 0,
                    "python_version": r.stdout.strip() if r.returncode == 0 else None,
                })
            except Exception:
                found.append({"path": str(venv_path), "name": name, "healthy": False, "python_version": None})

    # Also check requirements files
    dep_files = []
    for f in ["requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py", "setup.cfg"]:
        if (base / f).exists():
            dep_files.append(f)

    return json.dumps({"found": found, "dependency_files": dep_files})
