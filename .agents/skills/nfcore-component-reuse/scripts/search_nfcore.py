#!/usr/bin/env python3

import argparse
import json
import yaml

from nf_core.modules.modules_repo import ModulesRepo


def compact(meta):
    tools = []
    for entry in meta.get("tools", []):
        if isinstance(entry, dict):
            tools.extend(entry.keys())

    return {
        "description": meta.get("description"),
        "keywords": meta.get("keywords", []),
        "tools": tools,
        "input": meta.get("input"),
        "output": meta.get("output"),
        "components": meta.get("components", []),
    }


parser = argparse.ArgumentParser()
parser.add_argument("terms", nargs="*")
args = parser.parse_args()

terms = [x.lower() for x in args.terms]

repo = ModulesRepo(hide_progress=True)

result = {
    "remote": repo.remote_url,
    "sha": repo.repo.head.commit.hexsha,
    "modules": [],
    "subworkflows": [],
}

for kind in ("modules", "subworkflows"):
    for name in repo.get_avail_components(kind):
        raw = repo.get_meta_yml(kind, name)
        meta = yaml.safe_load(raw) if raw else {}

        item = {
            "name": name,
            **compact(meta),
        }

        searchable = json.dumps(item).lower()

        if terms and not any(term in searchable for term in terms):
            continue

        result[kind].append(item)

print(json.dumps(result, indent=2))