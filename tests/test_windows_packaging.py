import json
import zipfile
from pathlib import Path

import tomllib

from scripts import build_windows_packages, validate_windows_artifacts


def _frozen_profile(root: Path, name: str) -> None:
    directory = root / name
    directory.mkdir(parents=True)
    (directory / f"{name}.exe").write_bytes(b"launcher")
    (directory / "LICENSE").write_text("GPL", encoding="utf-8")


def test_portable_packages_include_source_information(tmp_path):
    frozen_root = tmp_path / "dist"
    output_dir = tmp_path / "artifacts"
    for edition in build_windows_packages.EDITIONS:
        _frozen_profile(frozen_root, edition.frozen_directory)

    artifacts = build_windows_packages.build_portables(
        frozen_root=frozen_root, output_dir=output_dir, version="0.8.0"
    )

    assert len(artifacts) == 4
    for artifact in artifacts:
        with zipfile.ZipFile(artifact) as archive:
            assert any(name.endswith("/SOURCE.txt") for name in archive.namelist())
            build_info_name = next(
                name for name in archive.namelist() if name.endswith("schedplus/build-info.json")
            )
            build_info = json.loads(archive.read(build_info_name))
            assert build_info["format"] == "managed-zip"
            assert build_info["version"] == "0.8.0"


def test_windows_artifact_validator_checks_source_and_checksums(tmp_path):
    output_dir = tmp_path / "artifacts"
    output_dir.mkdir()
    artifacts = []
    for edition in build_windows_packages.EDITIONS:
        name = build_windows_packages._portable_name(edition, "0.8.0")
        archive = output_dir / f"{name}.zip"
        with zipfile.ZipFile(archive, "w") as contents:
            contents.writestr(f"{name}/SOURCE.txt", "source")
        artifacts.append(archive)
    installer = output_dir / "SchedPlus-Setup-0.8.0-windows-x86_64.exe"
    installer.write_bytes(b"installer")
    artifacts.append(installer)
    build_windows_packages.write_checksums(artifacts, output_dir)

    assert validate_windows_artifacts.validate(output_dir, "0.8.0") == []

    installer.unlink()
    assert "missing installer artifact: SchedPlus-Setup-0.8.0-windows-x86_64.exe" in validate_windows_artifacts.validate(output_dir, "0.8.0")


def test_windows_installer_manifest_is_user_scoped_and_preserves_data():
    source = (Path(__file__).parents[1] / "packaging" / "windows" / "SchedPlus.iss").read_text(encoding="utf-8")

    assert "DefaultDirName={localappdata}\\Programs\\SchedPlus" in source
    assert "PrivilegesRequired=lowest" in source
    assert "AppId={{0C6F3E15-5245-4C9F-AB2F-5FF94DC9D85E}" in source
    assert 'OutputDir={#GetEnv("SCHEDPLUS_OUTPUT_DIR")}' in source
    assert 'MyAppExeName "SchedPlusStandard.exe"' in source
    assert 'Filename: "{app}\\{#MyAppExeName}"' in source


def test_windows_version_resource_matches_current_release():
    project_root = Path(__file__).parents[1]
    source = (project_root / "packaging" / "pyinstaller" / "version_info.txt").read_text(encoding="utf-8")
    version = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    numeric_version = ", ".join(version.split(".") + ["0"] * (4 - len(version.split("."))))

    assert f"filevers=({numeric_version})" in source
    assert f"ProductVersion', '{version}'" in source
    assert "ProductName', 'SchedPlus'" in source
