#! /usr/bin/env python

import argparse
import glob
import json
import os
import yaml

def cell(type, source, **kwargs):
    c = {"cell_type": type, "source": source}
    c.update(kwargs)
    c.setdefault("metadata", {})
    return c

def to_markdown(meta):
    return "\n".join([meta["name"], "-" * len(meta["name"]), "", meta["description"]])

def to_code(code_files):
    # Sort file by base name and reverse extension (ads before adb),
    # taking advantage of sort stability.

    res = ""
    splits = {f: os.path.splitext(f) for f in code_files}
    for f in sorted(sorted(splits, key=lambda s: s[1], reverse=True),
                    key=lambda s: s[0]):
        res += "-- {filename}\n\n{contents}\n".format(filename=f, contents=code_files[f])
    return res

def to_meta(desc, context):
    m = desc.get("metadata", {})
    m.update({"context_files": context})
    return m

def convert_dir(d, nb):
    code = {}
    context = {"main.gpr": "project Main is end Main;"}
    desc = None
    for path in glob.glob(os.path.join(d, "*")):
        fdir, fname = os.path.split(path)
        with open(path) as f:
            if fname == "example.yaml":
                desc = yaml.load(f)
                continue

            fbase, fext = os.path.splitext(fname)
            if fext in {".ads", ".adb"}:
                code[fname] = f.read()
            else:
                context[fname] = f.read()

    notebook = {
        "metadata": {
          "kernel_info": { "name": "sparkdisc_kernel" },
          "kernelspec": {
            "name": "sparkdisc_kernel",
            "display_name": "SPARK Discovery",
            "language": "SPARK"
          },
          "language_info": {
            "name": "SPARK",
            "version": "SPARK 2014",
            "codemirror_mode": "ada"
          },
        },
        "nbformat": 4, "nbformat_minor": 0,
        "cells": [
           cell("markdown", to_markdown(desc)),
           cell("code", to_code(code),
                metadata=to_meta(desc, context),
                execution_count=None,
                outputs=[])
        ]
    }

    with open(nb, "w") as nbf:
        json.dump(notebook, nbf)

def main():
    p = argparse.ArgumentParser(description="Convert examples to Jupyter notebooks")
    p.add_argument("dir", nargs='+', help="example directory")
    args = p.parse_args()

    for d in args.dir:
        try:
            convert_dir(d, os.path.basename(d) + ".ipynb")
        except Exception as e:
            print("Failed to convert {dir}: {exc}".format(dir=d, exc=e))

if __name__ == "__main__":
    main()
