#! /bin/bash
set -ex

BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

BUILD_CONTAINER_IMAGE=${1:-buildah bud}
WORKDIR=${2:-$(mktemp -d)}

mkdir -p ${WORKDIR}/container/
cp pkg/requirements.txt ${WORKDIR}/container/
cp -a src ${WORKDIR}/container/
sed -r "s/@BUILD_DATE@/$BUILD_DATE/g" pkg/Dockerfile.in > ${WORKDIR}/container/Dockerfile
cd ${WORKDIR}/container/ && \
${BUILD_CONTAINER_IMAGE} -t nof:latest .
# run this container image
# podman run -d -p 5000:5000 nof
