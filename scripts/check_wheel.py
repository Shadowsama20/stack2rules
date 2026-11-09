"""Validate the built wheel, then install and run it without third-party packages."""

from email.parser import Parser
import os
from pathlib import Path
import subprocess
import tempfile
import venv
import zipfile


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    wheels = list((repository / "dist").glob("stack2rules-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one stack2rules wheel in dist; remove stale builds.")
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
        metadata = Parser().parsestr(archive.read(metadata_name).decode("utf-8"))
        if metadata.get_all("Requires-Dist"):
            raise SystemExit("Wheel unexpectedly declares runtime dependencies.")
        if metadata.get("License-Expression") != "MIT":
            raise SystemExit("Wheel is missing MIT license metadata.")
        license_name = next(n for n in archive.namelist() if n.endswith("/licenses/LICENSE"))
        if archive.read(license_name) != (repository / "LICENSE").read_bytes():
            raise SystemExit("Wheel license does not match source.")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        cli = scripts / ("stack2rules.exe" if os.name == "nt" else "stack2rules")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONNOUSERSITE"] = "1"
        subprocess.run([str(python), "-m", "pip", "install", "--no-index",
                        "--no-deps", str(wheel)], cwd=root, env=env, check=True)
        project = root / "project"
        project.mkdir()
        (project / "requirements.txt").write_text("fastapi\npandas\n", encoding="utf-8")
        subprocess.run([str(cli)], cwd=project, env=env, check=True)
        content = (project / "CLAUDE.md").read_text(encoding="utf-8")
        if "## FastAPI\n" not in content or "## Pandas\n" not in content:
            raise SystemExit("Installed wheel did not generate the expected rules.")
    print("Wheel metadata, bundled license, isolated installation and CLI: OK")


if __name__ == "__main__":
    main()
