import hashlib
import json
from pathlib import Path
import zipfile


release = json.loads(Path("release.json").read_text(encoding="utf-8"))
version = json.loads(Path("release-metadata.json").read_text(encoding="utf-8"))["version"]
name = version["base"] + ("-" + version["suffix"] if version["suffix"] else "")
if release["isDraft"] or release["tagName"] != "v" + name:
    raise SystemExit("Expected a published release matching source metadata")
configuration = "Beta" if release["isPrerelease"] else "Release"
prefix = "fr" if release["isPrerelease"] else "sr"
root = Path("server/apiv2")
cache_path = root / "cache.json"
cache = json.loads(cache_path.read_text(encoding="utf-8"))
assets = {asset["name"]: asset["url"] for asset in release["assets"]}
updates = {}
for arch in ("x64", "ARM64"):
    filename = f"PCL2_CE_{configuration}_{arch}.exe"
    archive = filename.removesuffix(".exe") + ".zip"
    if filename not in assets or archive not in assets:
        raise SystemExit(f"Missing published asset: {filename} or {archive}")
    binary = (Path("release-assets") / filename).read_bytes()
    with zipfile.ZipFile(Path("release-assets") / archive) as package:
        if package.namelist() != [filename] or package.read(filename) != binary:
            raise SystemExit(f"ZIP must contain exactly the published EXE: {archive}")
    channel = prefix + arch.lower()
    data = {"assets": [{
        "file_name": filename,
        "version": {"channel": channel, "name": name, "code": version["code"]},
        "upd_time": release["publishedAt"], "downloads": [assets[archive]],
        "patches": [], "sha256": hashlib.sha256(binary).hexdigest(),
        "changelog": release["body"],
    }]}
    updates[root / "updates" / f"updates-{channel}.json"] = (
        json.dumps(data, ensure_ascii=False, indent=4) + "\n"
    ).encode("utf-8")
for path, content in updates.items():
    path.write_bytes(content)
    cache[path.stem] = hashlib.md5(content).hexdigest()
cache_path.write_text(json.dumps(cache) + "\n", encoding="utf-8", newline="\n")
print(f"Updated {configuration} channels to {name}; announcements unchanged")
