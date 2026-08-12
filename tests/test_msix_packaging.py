from pathlib import Path

import pytest

from scripts import build_msix


def test_msix_manifest_renders_store_identity_and_standard_launcher():
    manifest = build_msix.render_manifest(
        identity_name="12345ZFordDev.SchedPlus",
        publisher="CN=12345678-1234-1234-1234-123456789012",
        publisher_display_name="ZFordDev",
    )

    assert 'Identity Name="12345ZFordDev.SchedPlus"' in manifest
    assert 'Publisher="CN=12345678-1234-1234-1234-123456789012"' in manifest
    assert 'Executable="SchedPlusStandard.exe"' in manifest
    assert 'EntryPoint="Windows.FullTrustApplication"' in manifest
    assert 'Capability Name="runFullTrust"' in manifest
    assert "windows.appExecutionAlias" not in manifest
    assert "{{" not in manifest


def test_msix_manifest_escapes_partner_center_display_name():
    manifest = build_msix.render_manifest(
        identity_name="example",
        publisher="CN=example",
        publisher_display_name="ZFordDev & Co",
    )

    assert "ZFordDev &amp; Co" in manifest


def test_msix_manifest_rejects_missing_or_template_identity_values():
    with pytest.raises(ValueError, match="required"):
        build_msix.render_manifest(identity_name="", publisher="CN=example", publisher_display_name="ZFordDev")
    with pytest.raises(ValueError, match="template markers"):
        build_msix.render_manifest(
            identity_name="{{example}}", publisher="CN=example", publisher_display_name="ZFordDev"
        )


def test_msix_assets_cover_required_store_logo_sizes():
    assert build_msix.ASSET_SIZES == {
        "Square44x44Logo.png": (44, 44),
        "Square71x71Logo.png": (71, 71),
        "Square150x150Logo.png": (150, 150),
        "Square310x310Logo.png": (310, 310),
        "StoreLogo.png": (50, 50),
        "Wide310x150Logo.png": (310, 150),
    }


def test_msix_documentation_records_data_path_and_signing_procedure():
    documentation = (Path(__file__).parents[1] / "packaging" / "msix" / "README.md").read_text(encoding="utf-8")

    assert "%APPDATA%\\ZFordDev\\SchedPlus" in documentation
    assert "self-signed development certificate" in documentation
    assert "Microsoft signs the package" in documentation
