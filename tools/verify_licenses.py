#!/usr/bin/env python3
"""Inventário reproduzível das licenças Python instaladas."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path


def inventory() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for distribution in importlib.metadata.distributions():
        metadata = distribution.metadata
        licenses = "; ".join(metadata.get_all("License-Expression") or [])
        licenses = licenses or metadata["License"] or "NÃO DECLARADA"
        records.append(
            {
                "name": metadata["Name"] or distribution.name,
                "version": distribution.version,
                "license": licenses,
            }
        )
    return sorted(records, key=lambda item: item["name"].casefold())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(inventory(), ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
