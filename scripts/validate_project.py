#!/usr/bin/env python3
"""Fail-fast validation of the PanVK project inputs before extraction/build."""
import argparse
import json
import zipfile
from pathlib import PurePosixPath

EXPECTED = {
    "gpu_id": "0xc8700010",
    "gpu": "Mali-G720 MC7",
    "architecture": "Mali v12 CSF",
    "abi": "arm64-v8a",
    "os": "Android 16",
}

def fail(message):
    raise SystemExit(f"VALIDATION ERROR: {message}")

def load_json(path):
    try:
        with open(path, encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--meta", required=True)
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()

    meta = load_json(args.meta)
    profile = load_json(args.profile)

    for key, expected in EXPECTED.items():
        actual = str(profile.get(key, "")).lower() if key == "gpu_id" else profile.get(key)
        if actual != expected:
            fail(f"profile {key!r}: expected {expected!r}, got {actual!r}")

    if meta.get("library") != "libvulkan_panfrost.so":
        fail("meta.json must identify libvulkan_panfrost.so")
    if meta.get("gpu") != EXPECTED["gpu"]:
        fail("meta.json GPU does not match the POCO X7 Pro profile")
    if "POCO X7 Pro" not in meta.get("supported_devices", []):
        fail("meta.json does not list POCO X7 Pro as a supported target")

    try:
        archive = zipfile.ZipFile(args.archive)
    except (OSError, zipfile.BadZipFile) as exc:
        fail(f"cannot open source archive: {exc}")

    with archive:
        bad_member = archive.testzip()
        if bad_member:
            fail(f"ZIP CRC check failed for {bad_member}")

        names = archive.namelist()
        if len(names) != len(set(names)):
            fail("source ZIP contains duplicate member paths")

        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\\\" in name:
                fail(f"unsafe path in source ZIP: {name!r}")

        required = {
            "mali-panvk-main/build.sh",
            "mali-panvk-main/meson.build",
        }
        missing = sorted(required.difference(names))
        if missing:
            fail("source ZIP is missing required project files: " + ", ".join(missing))

    print("INPUT VALIDATION PASSED")
    print(f"Target: {EXPECTED['gpu']} / {EXPECTED['gpu_id']}")
    print("Source ZIP: CRC valid; expected build entry points present")
    print("Note: this validates inputs only; it does not prove GPU runtime compatibility.")

if __name__ == "__main__":
    main()
