#!/usr/bin/env python3

import re
from pathlib import Path

import requests


def extract_dependencies(pyproject_path):
    """Extract dependencies from the dependencies block in pyproject.toml."""
    deps = []
    in_deps_block = False
    with open(pyproject_path, "r") as f:
        for line in f:
            if line.strip().startswith("dependencies = ["):
                in_deps_block = True
                continue
            if in_deps_block:
                if line.strip().startswith("]"):
                    break
                dep = line.strip().strip('",')
                if dep:
                    pkg_name = re.split(r"[ <>=]", dep)[0]
                    deps.append((pkg_name, dep))
    return deps


def get_pypi_info(pkg_name):
    """Fetch package info from PyPI."""
    try:
        resp = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=5)
        if resp.status_code == 200:
            info = resp.json()["info"]
            summary = info.get("summary", "").strip()
            homepage = (
                info.get("home_page", None)
                or info.get("project_urls", None).get("homepage", None)
                or info.get("project_url", None)
            )
            if homepage:
                homepage = homepage.strip()
            if not homepage:
                homepage = f"https://pypi.org/project/{pkg_name}/"
            return summary, homepage
    except Exception:
        pass
    return "No description found.", f"https://pypi.org/project/{pkg_name}/"


def write_markdown_table(deps, md_path):
    """Write dependencies and descriptions as a markdown table."""
    with open(md_path, "w") as f:
        f.write("# Project Dependencies\n\n")
        f.write("| Package | Version Spec | Description | Homepage |\n")
        f.write("|---------|--------------|-------------|----------|\n")
        for pkg_name, dep in deps:
            desc, homepage = get_pypi_info(pkg_name)
            version_spec = dep[len(pkg_name) :].strip()
            f.write(
                f"| `{pkg_name}` | `{version_spec}` | {desc} | [{homepage}]({homepage}) |\n"
            )


if __name__ == "__main__":
    pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
    md_file = Path(__file__).parent.parent / "DEPENDENCIES.md"
    dependencies = extract_dependencies(pyproject_file)
    write_markdown_table(dependencies, md_file)
    print(f"Wrote {len(dependencies)} dependencies as a markdown table to {md_file}")
