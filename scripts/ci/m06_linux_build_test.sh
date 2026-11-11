#!/usr/bin/env bash
# M06 Linux build/test lane (aligned with M01 math + M04 core patterns). Run inside carbon-linux-gcc-buildenv.
set -euo pipefail

: "${WORK_ROOT:?WORK_ROOT must be set (writable build root)}"
: "${SRC_ROOT:=/src/carbon-math}"

mkdir -p "${WORK_ROOT}/logs" "${WORK_ROOT}/writable" "${WORK_ROOT}/build/carbon-math"
export VCPKG_DOWNLOADS="${WORK_ROOT}/.vcpkg-cache/downloads"
export VCPKG_DEFAULT_BINARY_CACHE="${WORK_ROOT}/.vcpkg-cache/binary"
mkdir -p "${VCPKG_DOWNLOADS}" "${VCPKG_DEFAULT_BINARY_CACHE}"

if [ ! -f "${WORK_ROOT}/writable/vcpkg/.vcpkg-root" ]; then
  cp -a "${SRC_ROOT}/vendor/github.com/microsoft/vcpkg/." "${WORK_ROOT}/writable/vcpkg/"
  "${WORK_ROOT}/writable/vcpkg/bootstrap-vcpkg.sh" -disableMetrics
fi
export VCPKG_ROOT="${WORK_ROOT}/writable/vcpkg"
export PATH_TO_VCPKG_ROOT="${VCPKG_ROOT}"

INSTALL_ROOT="${WORK_ROOT}/build/carbon-math/vcpkg_installed"
mkdir -p "${INSTALL_ROOT}"

"${VCPKG_ROOT}/vcpkg" install \
  --triplet x64-linux-release \
  --x-manifest-root="${SRC_ROOT}" \
  --x-install-root="${INSTALL_ROOT}" \
  --feature-flags=manifests,versions \
  2>&1 | tee "${WORK_ROOT}/logs/carbon-math-vcpkg-install.log"

cmake -G Ninja -S "${SRC_ROOT}" -B "${WORK_ROOT}/build/carbon-math" \
  -DCMAKE_TOOLCHAIN_FILE="${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" \
  -DVCPKG_OVERLAY_TRIPLETS="${SRC_ROOT}/vendor/github.com/carbonengine/vcpkg-registry/triplets" \
  -DVCPKG_TARGET_TRIPLET=x64-linux-release \
  -DVCPKG_HOST_TRIPLET=x64-linux-release \
  -DCMAKE_BUILD_TYPE=Release \
  -DVCPKG_CHAINLOAD_TOOLCHAIN_FILE="${SRC_ROOT}/vendor/github.com/carbonengine/vcpkg-registry/toolchains/x64-linux-carbon.cmake" \
  -DVCPKG_USE_HOST_TOOLS=ON \
  -DVCPKG_INSTALLED_DIR="${INSTALL_ROOT}" \
  2>&1 | tee "${WORK_ROOT}/logs/carbon-math-configure.log"

cmake --build "${WORK_ROOT}/build/carbon-math" -j "$(nproc)" \
  2>&1 | tee "${WORK_ROOT}/logs/carbon-math-build.log"

ctest --test-dir "${WORK_ROOT}/build/carbon-math" --output-on-failure \
  2>&1 | tee "${WORK_ROOT}/logs/carbon-math-test.log"

python3 "${SRC_ROOT}/scripts/ci/assert_ctest_results.py" \
  --min-passed 90 --exact-disabled 0 \
  "${WORK_ROOT}/logs/carbon-math-test.log"
