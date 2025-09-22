SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

WORKSPACE_DIR := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))

#
# Task runner to share steps between .github/workflows and scripts/docker-dev for development.
#

all:

.PHONY: configure-gcc
configure-gcc:
	cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -B built-gcc -S toolchain/gcc

.PHONY: build-gcc
build-gcc: check-env
	cmake --build built-gcc --parallel --target "gcc-toolchain-$(TARGET_NAME)" -- --verbose

.PHONY: package-gcc
package-gcc: check-env
	tar --exclude .build -cf "gcc-$(TARGET_NAME).tar" "built-gcc/$(TARGET_NAME)/toolchain"

.PHONY: extract-gcc
extract-gcc:
	find . -name 'gcc-*.tar' -exec tar -xf {} \;

.PHONY: configure-toolchain
configure-toolchain:
	cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DGCC_CACHE_DIR="$(WORKSPACE_DIR)/built-gcc" -B build -S toolchain

.PHONY: build-sysroot
build-sysroot: check-env
	cmake --build build --parallel --target "sysroot-package-$(TARGET_NAME)" -- --verbose

.PHONY: build-llvm
build-llvm:
	cmake --build build --parallel --target llvm-package -- --verbose

.PHONY: version-info
version-info:
	cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=portable_cc_toolchain/toolchain.cmake
	cmake --build build

.PHONY: check-env
check-env:
ifndef TARGET_NAME
	$(error TARGET_NAME is undefined)
endif
