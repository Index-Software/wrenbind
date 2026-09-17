#!/usr/bin/env python3
import argparse
import subprocess
import sys

from binding_generator import BindingGenerator, generate_empty_output


def detect_cxx_include_paths() -> list[str]:
    paths: list[str] = []
    try:
        result = subprocess.run(
            ["g++", "-E", "-x", "c++", "-v", "-"],
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return paths

    capture = False
    for line in result.stderr.split("\n"):
        if line.startswith("#include <...> search starts here"):
            capture = True
            continue
        if line.startswith("End of search list"):
            break
        if capture:
            path = line.strip()
            if path:
                paths.append(path)

    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Wren binding code")

    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Input header file(s) with WREN_BIND annotations",
    )
    parser.add_argument("--output", required=True, help="Output .gen.cpp file path")
    parser.add_argument(
        "--header-output",
        required=True,
        help="Output .gen.h file path for setter declarations",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Include paths for libclang parsing (repeatable)",
    )
    parser.add_argument(
        "--force-include",
        action="append",
        default=[],
        help="Additional header path to emit as #include in the generated "
        "source (repeatable)",
    )
    parser.add_argument(
        "--wren-scripts",
        default=None,
        help="Root directory of Wren scripts for foreign class discovery",
    )
    parser.add_argument(
        "--no-auto-cxx-includes",
        action="store_true",
        help="Disable automatic detection of C++ stdlib includes",
    )
    parser.add_argument(
        "--libclang",
        default=None,
        help="Path to libclang shared library",
    )
    parser.add_argument(
        "--no-warn-empty",
        action="store_true",
        help="Suppress warning when no annotations are found",
    )

    args = parser.parse_args()

    include_args = ["-std=c++98", "-x", "c++", "-DWREN_BIND_CODEGEN"]
    for path in args.include:
        include_args.append(f"-I{path}")

    if not args.no_auto_cxx_includes:
        for path in detect_cxx_include_paths():
            include_args.append(f"-I{path}")

    generator = BindingGenerator(args.wren_scripts, args.include, libclang_path=args.libclang)
    generator.parse_files(args.input, include_args)

    if not generator.all_methods:
        if not args.no_warn_empty:
            print(
                "[WARNING] No WREN_BIND annotations found in input files",
                file=sys.stderr,
            )
        generate_empty_output(args.output)
        return

    generator.generate(args.output, args.header_output, args.force_include)


if __name__ == "__main__":
    main()