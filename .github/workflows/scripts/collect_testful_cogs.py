#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys
from typing import List, Set, Union

import pytest


class CogCollector:
    """Pytest plugin to collect cogs relative to a cogs directory."""

    def __init__(
        self,
        cogs_path: Union[str, Path],
    ) -> None:
        self.cogs_path = Path(cogs_path).resolve()
        self.collected_cogs: Set[str] = set()

    def pytest_collection_modifyitems(
        self,
        session: pytest.Session,
        config: pytest.Config,
        items: List[pytest.Item],
    ) -> None:
        for item in items:
            rel_path = item.path.relative_to(self.cogs_path)
            cog_name = rel_path.parts[0]
            self.collected_cogs.add(cog_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cogs-path", type=str, default="cogs", help="Path to cogs directory")
    parser.add_argument("--output-file", type=str, default=None, help="File to write output JSON")
    parser.add_argument("--pytest-ini", type=str, default=None, help="Path to pytest.ini file")

    args = parser.parse_args()
    cogs_path: str = args.cogs_path

    pytest_args = ["--collect-only", "--quiet"]
    if args.pytest_ini:
        pytest_args.extend(["--config-file", args.pytest_ini])
    pytest_args.append(str(Path(cogs_path).resolve()))

    cog_collector_plugin = CogCollector(cogs_path)
    pytest_plugins = [cog_collector_plugin]

    pytest.main(pytest_args, plugins=pytest_plugins)

    if args.output_file:
        with open(file=args.output_file, mode="w") as f:
            json.dump(sorted(cog_collector_plugin.collected_cogs), f)
    else:
        json.dump(sorted(cog_collector_plugin.collected_cogs), sys.stdout)


if __name__ == "__main__":
    main()
