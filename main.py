#!/usr/bin/env python3
import os
import json
import argparse
import shutil, errno

def get_configs(args):
    configs = {}

    if args.inputDir:
        path = args.inputDir
        for root, _, files in os.walk(path):
            for file in files:
                if file == "config.json":
                    with open(os.path.join(root, file), "r") as f:
                        configs[root] = json.load(f)
    elif args.input:
        with open(os.path.join(args.input, "config.json"), "r") as f:
            configs[args.input] = json.load(f)
    else:
        raise

    return configs

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: 
            raise

def is_symlink(src, dst):
    return os.path.islink(dst) and os.readlink(dst) == src

def prepare_path(dst):
    if os.path.exists(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    

def link(src, dst):
    if not is_symlink(src, dst):
        prepare_path(dst)
        os.symlink(src, dst)
        print("Linked `{}` to `{}`".format(src, dst))
    else:
        print("`{}` is linking to `{}`, skipping.".format(src, dst))

def blueprint(src, dst):
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        copyanything(src, dst)
        print("Created `{}` from blueprint.".format(dst))
    else:
        print("`{}` exists, skipping.".format(dst))

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble the configuration")
    inputArgs = parser.add_mutually_exclusive_group()
    inputArgs.add_argument("--inputDir", type=str, help="Directory path with config parts")
    inputArgs.add_argument("--input", type=str, help="Config part path")
    
    parser.add_argument("--output", type=str, help="Output config directory", required=True)
    args = parser.parse_args()

    configs = get_configs(args)
    outputDir = args.output

    for dir, config in configs.items():
        if "link" in config.keys() and isinstance(config["link"], list):
            for lk in config["link"]:
                if isinstance(lk, list) and len(lk) == 2:
                    src = os.path.join(dir, lk[0])
                    dst = os.path.join(outputDir, lk[1])
                    link(src, dst)
                elif isinstance(lk, str):
                    src = os.path.join(dir, lk)
                    dst = os.path.join(outputDir, lk)
                    link(src, dst)
                else:
                    print("Skipping invalid entry {!r}".format(link))
        if "blueprint" in config.keys() and isinstance(config["blueprint"], list):
            for bp in config["blueprint"]:
                if isinstance(bp, list) and len(bp) == 2:
                    src = os.path.join(dir, bp[0])
                    dst = os.path.join(outputDir, bp[1])
                    blueprint(src, dst)
                elif isinstance(bp, str):
                    src = os.path.join(dir, bp)
                    dst = os.path.join(outputDir, bp)
                    blueprint(src, dst)
                else:
                    print("Skipping invalid entry {!r}".format(link))
        if "exists" in config.keys() and isinstance(config["exists"], dict):
            if "file" in config["exists"].keys() and isinstance(config["exists"]["file"], list):
                for exists in config["exists"]["file"]:
                    path = os.path.join(outputDir, exists)
                    if not os.path.exists(path):
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        open(path, 'a').close()
            if "dir" in config["exists"].keys() and isinstance(config["exists"]["dir"], list):
                for exists in config["exists"]["dir"]:
                    path = os.path.join(outputDir, exists)
                    if not os.path.exists(path):
                        os.makedirs(path, exist_ok=True)
