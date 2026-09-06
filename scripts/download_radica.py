"""Download the public RADicA release from a verified Figshare manifest.

The script requires an explicit manifest JSON saved from Figshare's API. This
prevents a DOI redirect or HTML error page from being mistaken for data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path, help="Verified Figshare article metadata JSON")
    parser.add_argument("--output", type=Path, default=Path("data/raw/radica"))
    args = parser.parse_args()

    metadata = json.loads(args.manifest.read_text(encoding="utf-8"))
    files = metadata.get("files", [])
    if not files:
        raise SystemExit("Manifest contains no files; refusing to download.")

    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    for item in files:
        name = Path(item["name"]).name
        url = item.get("download_url")
        if not url or not url.startswith("https://"):
            raise SystemExit(f"Missing safe download URL for {name}")
        destination = args.output / name
        request = urllib.request.Request(url, headers={"User-Agent": "breath-to-photonics/0.1"})
        with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        records.append({"name": name, "bytes": destination.stat().st_size, "sha256": sha256(destination)})
        print(f"Downloaded {name} ({destination.stat().st_size} bytes)")

    (args.output / "download_manifest.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()

