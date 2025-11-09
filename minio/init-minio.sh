#!/usr/bin/env bash
set -e


# Leverages mc (MinIO Client) to create the bucket and apply policies
# To install mc: https://min.io/docs/minio/linux/reference/minio-mc.html


MC_HOST_ALIAS=localminio
MC="mc --insecure"
q
$MC alias set $MC_HOST_ALIAS http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
$MC mb $MC_HOST_ALIAS/${MINIO_BUCKET} || true
# Default policy is private ; keep access through presigned URLs
# $MC policy set none $MC_HOST_ALIAS/${MINIO_BUCKET}


echo "Bucket '${MINIO_BUCKET}' ready."