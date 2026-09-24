# Docker Image ಅನ್ನು GHCR (GitHub Container Registry) ಗೆ Push ಮಾಡುವ Guide

## 1. PAT Token Create ಮಾಡಿ

GitHub → Settings → Developer settings → Personal access tokens

Classic Token ಗೆ permissions: - write:packages - read:packages - repo
(private repo ಆದರೆ)

## 2. GHCR Login

``` bash
docker login ghcr.io
```

Username: GitHub Username

Password: PAT Token

## 3. Image Tag

``` bash
docker tag hello-world-image ghcr.io/srujankn762/hello-world-image:latest
```

## 4. Push

``` bash
docker push ghcr.io/srujankn762/hello-world-image:latest
```

Success ಆದರೆ:

``` text
latest: digest: sha256:...
```

## 5. Verify

GitHub → Profile → Packages

ಅಥವಾ

``` bash
docker pull ghcr.io/srujankn762/hello-world-image:latest
```

## Common Error

permission_denied → PAT permissions ತಪ್ಪಿದೆ.

ಹೊಸ PAT create ಮಾಡಿ:

-   write:packages
-   read:packages
-   repo

ಮತ್ತೆ:

``` bash
docker logout ghcr.io
docker login ghcr.io
docker push ghcr.io/srujankn762/hello-world-image:latest
```
