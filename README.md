# Toolchains

This repository contains [CMake] targets and GitHub Actions' workflows that build and package a complete C/C++ [LLVM] toolchain.

Each toolchain [release] provides a [sysroot] and LLVM distribution, the latter containing only a minimal subset of available `clang*` and `llvm-*` related tools. The release archives are standalone and can be used in a variety of ways, although we use them specifically with [Bazel] and [toolchains_llvm]. Tool dependencies are statically linked, where applicable.

## License

This code in this repository is _heavily_ based upon the hard work done by:

* [CACI-International/cpp-toolchain] - Portable C++ Toolchain for CMake and Bazel.
* [MaterializeInc/toolchains] - Github Actions to build and package Rust and C toolchains for consumption with Bazel.

Both of these projects are licensed under the [Apache 2.0](./LICENSE) license.

> [!IMPORTANT]
> The release archives are licensed under the terms of their respective projects, [LLVM], [crosstool-NG], and in turn each project built by [crosstool-NG]. See the contents of the release archives for more information.

## Platforms

The following platforms are supported:

* Linux
  - `x86_64-unknown-linux-gnu`
  - `x86_64-unknown-linux-musl`
  - `aarch64-unknown-linux-gnu`
  - `aarch64-unknown-linux-musl`
* Apple (requires Xcode)
  - `x86_64-apple-macos`
  - `arm64-apple-macos`
* Windows (requires Windows SDK)
  - `x86_64-pc-windows-msvc`

This list can potentially be extended to anything supported by [crosstool-NG].

## Why?

### LLVM

The [LLVM] that [toolchains_llvm] downloads by default contains many unused tools and is approximately 1.6 GB, at time of writing. Additionally, the releases provided by `llvm-project.org` are dynamically linked, which in turn requires CI or development machines to have libraries such as `ncurses5` or `libxml2` installed and accessible outside of the sandbox.

### Sysroot

The easiest existing way to obtain a [sysroot] is to use one of the various [Chromium sysroot] archives. These sysroots are tailored to the Chromium browser's dependency requirements, including libraries such as `gtk` and `qt` that we do not require. Customizing the sysroot contents and having control over the versioning is therefore important to ensure the toolchain is as hermetic as possible.

### Compression

All toolchain [release] artifacts are compressed using [zstd]'s maximum compression ratio to optimize for network transmission, at the cost of CPU. This is mostly a CI optimization, but [zstd]'s decompression speed at such ratios is still faster than the more common [xz].

## How?

The general steps taken to produce a complete toolchain for a given target platform are as follows:

1. Configure and build GCC for the target platform (ie. the current GitHub runner's platform) using [crosstool-NG].
2. Build a sysroot for the target platform and package it using the filtering rules defined in [./toolchain/config/sysroot.json](./toolchain/config/sysroot.json).
3. Build the desired LLVM packages for the target platform.

For a more comprehensive introduction to C/C++ toolchains, [crosstool-NG] has excellent documentation such as [toolchain types] and [toolchain construction] that is worth reading.

## Compatibility

Older versions of Linux kernel headers and `glibc` are intentionally used to maximize compatiblity,
while more recent [LLVM] releases are used.

See the release notes or each target's `deconfig` under [gcc/targets](./toolchain/gcc/targets) for the specific versions used.

[release]: https://github.com/rillanetwork/toolchains/releases
[Bazel]: https://bazel.build
[Chromium sysroot]: https://chromium.googlesource.com/chromium/src.git/+/master/docs/linux/sysroot.md
[toolchains_llvm]: https://github.com/bazel-contrib/toolchains_llvm
[sysroot]: https://www.baeldung.com/linux/sysroot
[CMake]: https://cmake.org
[LLVM]: https://github.com/llvm/llvm-project
[crosstool-NG]: https://crosstool-ng.github.io
[toolchain types]: https://crosstool-ng.github.io/docs/toolchain-types/
[toolchain construction]: https://crosstool-ng.github.io/docs/toolchain-construction/
[CACI-International/cpp-toolchain]: https://github.com/CACI-International/cpp-toolchain
[MaterializeInc/toolchains]: https://github.com/MaterializeInc/toolchains
[zstd]: https://github.com/facebook/zstd
[xz]: https://docs.kernel.org/staging/xz.html
