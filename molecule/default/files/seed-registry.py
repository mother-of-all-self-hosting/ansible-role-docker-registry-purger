# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pushes a tiny, distinct container image under each of the given tags.

Usage: seed-registry.py <registry URL> <repository> <tag> [<tag> ...]

Written against the registry HTTP API rather than around `docker push`, for
two reasons:

- Docker only pushes what its image store holds, and a `docker push` of the
  same image under several tags gives every one of them the same manifest
  digest. Deleting a manifest un-tags every tag pointing at it, so the purger
  would appear to delete far more than it was asked to. Every tag here gets a
  layer of its own, and therefore a digest of its own.

- The purger asks for manifests as `application/vnd.docker.distribution
  .manifest.v2+json` and needs the `Docker-Content-Digest` header back before
  it will delete anything. Recent Docker releases push OCI manifests instead,
  which answer that request with a 404, so what a `docker push` produces would
  depend on the Docker version the test happened to run against.
"""

import gzip
import hashlib
import io
import json
import sys
import tarfile
import urllib.request

registry_url, repository, tags = sys.argv[1], sys.argv[2], sys.argv[3:]


def request(url, method, body=None, content_type=None, expected=(200,)):
    # The upload location the registry hands back may be absolute or relative.
    request_url = url if url.startswith("http") else registry_url + url

    http_request = urllib.request.Request(request_url, data=body, method=method)
    if content_type is not None:
        http_request.add_header("Content-Type", content_type)

    with urllib.request.urlopen(http_request) as response:
        if response.status not in expected:
            raise SystemExit("%s %s answered %d" % (method, request_url, response.status))
        return response


def digest_of(blob):
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def push_blob(blob):
    location = request(
        "/v2/%s/blobs/uploads/" % repository, "POST", expected=(202,),
    ).headers["Location"]

    request(
        location + ("&" if "?" in location else "?") + "digest=" + digest_of(blob),
        "PUT",
        body=blob,
        content_type="application/octet-stream",
        expected=(201,),
    )

    return digest_of(blob)


for tag in tags:
    marker = ("%s:%s\n" % (repository, tag)).encode()

    # A real (if minuscule) layer, so that these are genuine container images
    # rather than blobs the registry merely happens to hold.
    layer_tar = io.BytesIO()
    with tarfile.open(fileobj=layer_tar, mode="w") as archive:
        entry = tarfile.TarInfo("marker")
        entry.size = len(marker)
        archive.addfile(entry, io.BytesIO(marker))
    layer = gzip.compress(layer_tar.getvalue(), mtime=0)

    config = json.dumps({
        "architecture": "amd64",
        "os": "linux",
        "config": {},
        "rootfs": {"type": "layers", "diff_ids": [digest_of(layer_tar.getvalue())]},
    }).encode()

    manifest = json.dumps({
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "size": len(config),
            "digest": push_blob(config),
        },
        "layers": [{
            "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
            "size": len(layer),
            "digest": push_blob(layer),
        }],
    }).encode()

    request(
        "/v2/%s/manifests/%s" % (repository, tag),
        "PUT",
        body=manifest,
        content_type="application/vnd.docker.distribution.manifest.v2+json",
        expected=(201,),
    )

    print("pushed %s:%s" % (repository, tag))
