cmake_minimum_required(VERSION 3.20)
project(GccImplementation NONE)

include(ExternalProject)

set(toolchain_targets
    "x86_64-unknown-linux-gnu"
    # "aarch64-unknown-linux-gnu"
    "x86_64-unknown-linux-musl"
    # "aarch64-unknown-linux-musl"
)

ExternalProject_Add(crosstool-ng
    GIT_REPOSITORY https://github.com/crosstool-ng/crosstool-ng.git
    GIT_TAG ec7070da386b6526d7fbd0246adcccb9cc095d8b
    UPDATE_COMMAND ""
    CONFIGURE_COMMAND
        ./bootstrap && ./configure --prefix=<INSTALL_DIR>
    BUILD_COMMAND
        make -j${CMAKE_BUILD_PARALLEL_LEVEL}
    INSTALL_COMMAND 
        make install
    BUILD_IN_SOURCE TRUE
)

ExternalProject_Get_Property(crosstool-ng INSTALL_DIR)
set(ct_ng ${INSTALL_DIR}/bin/ct-ng)

# Build crosstool-ng toolchains
function(build_crosstool_ng_toolchain target_arch)
    if(GCC_CACHE_DIR)
        ExternalProject_Add(gcc-toolchain-${target_arch}
            DOWNLOAD_COMMAND ""
            CONFIGURE_COMMAND ""
            BUILD_COMMAND ""
            INSTALL_COMMAND ""
            BINARY_DIR "${GCC_CACHE_DIR}/${target_arch}"
        )
    else()
        ExternalProject_Add(gcc-toolchain-${target_arch}
            DEPENDS crosstool-ng
            SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/targets/${target_arch}
            UPDATE_COMMAND ""
            BINARY_DIR "${CMAKE_BINARY_DIR}/${target_arch}"
            CONFIGURE_COMMAND
                ${CMAKE_COMMAND} -E copy <SOURCE_DIR>/defconfig defconfig && 
                ${ct_ng} defconfig
            BUILD_COMMAND
                ${CMAKE_COMMAND} -E env --unset=LD_LIBRARY_PATH
                ${ct_ng} build
            INSTALL_COMMAND ""
        )
    endif()
endfunction()

# Build all crosstool-ng toolchains
foreach(target_arch IN LISTS toolchain_targets)
    build_crosstool_ng_toolchain(${target_arch})
endforeach()
