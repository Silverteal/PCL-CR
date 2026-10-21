import argparse
import json
from pathlib import Path
import re


parser = argparse.ArgumentParser()
parser.add_argument("version")
parser.add_argument("configuration", choices=["Release", "Beta"])
parser.add_argument("--code", default="")
parser.add_argument("--check", action="store_true")
args = parser.parse_args()

number = r"(?:0|[1-9][0-9]*)"
identifier = rf"(?:{number}|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
match = re.fullmatch(
    rf"v?(?P<base>{number}\.{number}\.{number})"
    rf"(?:-(?P<pre>{identifier}(?:\.{identifier})*))?"
    r"(?P<build>\+[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)?", args.version,
)
if not match:
    parser.error("Version must be a semantic version")
core, pre, build = match["base"], match["pre"] or "", match["build"] or ""
if any(int(part) > 65534 for part in core.split(".")):
    parser.error("Version components must fit Windows assembly/file versions (0..65534)")
base, suffix = (core, pre + build) if pre else (core + build, "")

path = Path("Plain Craft Launcher 2/metadata.json")
data = json.loads(path.read_text(encoding="utf-8"))
version = data["version"]
if args.code and not re.fullmatch(r"[1-9][0-9]*", args.code):
    parser.error("Version code must be a positive integer")
code = int(args.code) if args.code else version["code"] + (not args.check)
if not args.check and not version["code"] < code <= 2147483647:
    parser.error("Version code must increase and fit a signed 32-bit integer")
project = Path("Plain Craft Launcher 2/Plain Craft Launcher 2.csproj")
original_project = project.read_text(encoding="utf-8")
project_text, count = re.subn(
    r"<(AssemblyVersion|FileVersion)>[^<]*</\1>",
    lambda m: f"<{m[1]}>{core}.0</{m[1]}>", original_project,
)
if count != 2:
    parser.error("Expected exactly one AssemblyVersion and one FileVersion")
if args.check:
    if (version["base"], version["suffix"], version["code"]) != (base, suffix, code):
        parser.error("Requested version does not match metadata.json")
    if project_text != original_project:
        parser.error("AssemblyVersion/FileVersion do not match metadata.json")
    raise SystemExit(0)
version.update(base=base, suffix=suffix, code=code)
path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
project.write_text(project_text, encoding="utf-8", newline="\n")
print(f"Prepared {args.version} ({code})")
