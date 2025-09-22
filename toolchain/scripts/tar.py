#!/usr/bin/env python3

"""
Cross-platform tar assembly script.

Creates reproducible tar.zst archives with path mappings and exclusions configured via Json files.
"""

import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

def should_exclude(rel_path, exclusions):
    """Exclude a file if it contains any of the excluded path components"""
    return any(pattern in rel_path.parts for pattern in exclusions)

def add_file_reproducible(tar, file_path, arc_name):
    """Add file with reproducible metadata"""
    tarinfo = tar.gettarinfo(file_path, arcname=arc_name)
    tarinfo.mtime = 946684800
    tarinfo.uid = 0
    tarinfo.gid = 0
    tarinfo.uname = ""
    tarinfo.gname = ""

    is_executable = tarinfo.mode & 0o111
    tarinfo.mode = 0o644
    if tarinfo.isdir() or is_executable:
        tarinfo.mode |= 0o111

    if tarinfo.isreg():
        with open(file_path, 'rb') as f:
            tar.addfile(tarinfo, f)
    else:
        tar.addfile(tarinfo)

def collect_directory_files(source_dir, target_path, exclusions):
    """Collect all files from directory with their archive paths"""
    source_path = Path(source_dir)
    assert source_path.exists(), f"Source directory {source_dir} does not exist"

    # First, collect all files and directory symlinks
    all_items = []
    for root, dirs, files in os.walk(source_path, followlinks=False):
        root_path = Path(root)
        for item_name in files + [d for d in dirs if (root_path / d).is_symlink()]:
            item_path = root_path / item_name
            all_items.append(item_path)

    # Then filter and create archive entries
    files_to_add = []
    for file_path in all_items:
        rel_path = file_path.relative_to(source_path)

        if should_exclude(rel_path, exclusions):
            continue

        arc_name = (Path(target_path) / rel_path).as_posix()
        files_to_add.append((str(file_path), arc_name))

    return files_to_add

def collect_all_files(config):
    """Parse config and collect all files to be archived"""
    all_files = []

    # Collect files from directories
    for mapping in config.get('directories', []):
        source = mapping['source']
        target = mapping.get('target', '')
        exclusions = mapping.get('exclude', [])
        directory_files = collect_directory_files(source, target, exclusions)
        all_files.extend(directory_files)

    # Collect individual files
    for file_mapping in config.get('files', []):
        source = Path(file_mapping['source'])
        target = file_mapping['target']
        assert source.exists(), f"Source file {source} does not exist"
        all_files.append((str(source), target))

    return all_files

def create_tar(output_file, config):
    """Create tar.zst file from config"""
    all_files = collect_all_files(config)
    all_files.sort(key=lambda x: x[1])  # Sort by archive name
    with tempfile.NamedTemporaryFile(suffix='.tar') as temp_tar:
        with tarfile.open(temp_tar.name, 'w') as tar:
            for file_path, arc_name in all_files:
                add_file_reproducible(tar, file_path, arc_name)
        try:
            subprocess.run(["zstd", "--ultra", "-22", temp_tar.name, "-o", output_file], check=True)
        except FileNotFoundError:
            print("Error: zstd binary not found.", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: zstd failed with status {e.returncode}", file=sys.stderr)
            sys.exit(1)

def merge_configs(config_files):
    """Merge multiple config files into a single config"""
    merged_config = {
        'directories': [],
        'files': []
    }

    for config_file in config_files:
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Merge directories and files
        merged_config['directories'].extend(config.get('directories', []))
        merged_config['files'].extend(config.get('files', []))

    return merged_config

def main():
    if len(sys.argv) < 3:
        print("Usage: tar.py <output.tar.zst> <config1.json> [config2.json] ...")
        sys.exit(1)

    output_file = sys.argv[1]
    config_files = sys.argv[2:]

    config = merge_configs(config_files)

    create_tar(output_file, config)

    print(f"Created {output_file}")

if __name__ == "__main__":
    main()
