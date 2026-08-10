# Kubernetes Deployment + Service — ಕನ್ನಡದಲ್ಲಿ Full Notes

> ಈ README ನಿನ್ನ **current project configuration** ಆಧರಿಸಿದೆ.
>
> **Docker Image:** `ghcr.io/srujankn762/hello-world-image:latest`
>
> **Django/Gunicorn Port:** `8055`
>
> **Kubernetes Service Port:** `8008`
>
> **NodePort:** `30000`

---

# 1. ಮೊದಲು Big Picture

ನಮ್ಮ application flow ಹೀಗಿದೆ:

```text
Browser
   |
   | http://localhost:30000
   v
NodePort :30000
   |
   v
Kubernetes Service :8008
   |
   | targetPort :8055
   v
Pod
   |
   v
Container :8055
   |
   v
Django + Gunicorn
```

ಸರಳವಾಗಿ ನೆನಪಿಟ್ಟುಕೊಳ್ಳಿ:

```text
30000  →  8008  →  8055
NodePort → Service Port → Application Port
```

---

# 2. Deployment ಅಂದ್ರೆ ಏನು?

**Deployment** ಅಂದ್ರೆ Kubernetesಗೆ:

> "ನನ್ನ application ಹೇಗೆ run ಆಗಬೇಕು, ಎಷ್ಟು Pods ಇರಬೇಕು, ಯಾವ Docker image ಬಳಸಬೇಕು" ಅಂತ ಹೇಳುವ object.

ನಮ್ಮ Deployment:

```text
Deployment
    |
    v
ReplicaSet
    |
    v
Pod
    |
    v
Container
    |
    v
Django Application
```

Deploymentನ ಮುಖ್ಯ ಕೆಲಸ:

- Pod create ಮಾಡುವುದು
- ಎಷ್ಟು replicas ಬೇಕು ಅಂತ maintain ಮಾಡುವುದು
- Pod crash ಆದರೆ replacement Pod create ಮಾಡುವುದು
- Application update/manage ಮಾಡುವುದು

---

# 3. ನಮ್ಮ `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: hello-world

spec:
  replicas: 1

  selector:
    matchLabels:
      app: hello-world

  template:
    metadata:
      labels:
        app: hello-world

    spec:
      imagePullSecrets:
        - name: ghcr-secret

      containers:
        - name: hello-world
          image: ghcr.io/srujankn762/hello-world-image:latest
          ports:
            - containerPort: 8055
```

ಈಗ ಒಂದೊಂದು ಭಾಗ ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳೋಣ.

---

# 4. `apiVersion`

```yaml
apiVersion: apps/v1
```

ಇದು Kubernetesಗೆ:

> "Deployment resourceಗಾಗಿ `apps/v1` API version ಬಳಸು."

ಅಂತ ಹೇಳುತ್ತದೆ.

---

# 5. `kind`

```yaml
kind: Deployment
```

ಇದು:

> "ನಾವು Kubernetesನಲ್ಲಿ Deployment create ಮಾಡುತ್ತಿದ್ದೇವೆ."

ಅಂತ ಹೇಳುತ್ತದೆ.

---

# 6. `metadata`

```yaml
metadata:
  name: hello-world
```

ಇದು Deploymentನ ಹೆಸರು.

ನಂತರ:

```bash
kubectl get deployments
```

ಕೊಟ್ಟಾಗ:

```text
hello-world
```

ಅಂತ ಕಾಣುತ್ತದೆ.

---

# 7. `replicas`

```yaml
replicas: 1
```

ಅರ್ಥ:

> "ನನ್ನ applicationನ ಒಂದು Pod run ಆಗಿರಬೇಕು."

ಹೀಗೆ:

```text
Deployment
    |
    v
  Pod 1
```

ನಾವು:

```yaml
replicas: 3
```

ಅಂತ ಮಾಡಿದರೆ:

```text
Deployment
    |
    +---- Pod 1
    |
    +---- Pod 2
    |
    +---- Pod 3
```

Kubernetes ಈ desired number of Pods maintain ಮಾಡಲು ಪ್ರಯತ್ನಿಸುತ್ತದೆ.

---

# 8. `selector` ಅಂದ್ರೆ ಏನು?

ನಮ್ಮ YAML:

```yaml
selector:
  matchLabels:
    app: hello-world
```

ಇದು Deploymentಗೆ:

> "ಯಾವ Pods ನನ್ನ Pods ಅಂತ ಗುರುತಿಸಬೇಕು?"

ಅಂತ ಹೇಳುತ್ತದೆ.

ಅದು `app=hello-world` label ಹುಡುಕುತ್ತದೆ.

---

# 9. `template` ಅಂದ್ರೆ ಏನು?

```yaml
template:
```

`template` ಅಂದ್ರೆ **Pod create ಮಾಡುವ blueprint / ನಕ್ಷೆ**.

ಅಂದರೆ:

> "ನನ್ನ Pod ಹೇಗಿರಬೇಕು ಅನ್ನೋದನ್ನು ಇಲ್ಲಿ define ಮಾಡು."

Template ಒಳಗೆ:

- Pod labels
- Container
- Docker image
- Container port
- Image pull secret

ಇವೆಲ್ಲ define ಮಾಡುತ್ತೇವೆ.

---

# 10. `labels`

ನಮ್ಮ template:

```yaml
template:
  metadata:
    labels:
      app: hello-world
```

ಇದು Podಗೆ:

```text
app=hello-world
```

ಅಂತ label ಹಾಕುತ್ತದೆ.

ಇದು ತುಂಬಾ important.

ಏಕೆಂದರೆ ನಮ್ಮ Service ಕೂಡ ಇದೇ label ಬಳಸಿ Pod ಹುಡುಕುತ್ತದೆ.

---

# 11. Selector + Label Relationship

Deploymentನಲ್ಲಿ:

```yaml
selector:
  matchLabels:
    app: hello-world
```

Pod templateನಲ್ಲಿ:

```yaml
labels:
  app: hello-world
```

ಎರಡೂ match ಆಗುತ್ತವೆ.

```text
Deployment
 selector:
 app=hello-world
       |
       v
Pod
 label:
 app=hello-world
```

ಅಂದರೆ Deploymentಗೆ:

> "ಈ label ಇರುವ Pod ನನ್ನದು."

ಅಂತ ಗೊತ್ತಾಗುತ್ತದೆ.

---

# 12. Service ಕೂಡ ಇದೇ Label ಬಳಸುತ್ತದೆ

Serviceನಲ್ಲಿ:

```yaml
selector:
  app: hello-world
```

ಅಂದರೆ Service:

> "app=hello-world label ಇರುವ Pods ಹುಡುಕು."

ಅಂತ ಹೇಳುತ್ತದೆ.

ಹೀಗಾಗಿ:

```text
Deployment
    |
    | creates
    v
Pod
label = app=hello-world
    ^
    |
Service selector
app=hello-world
```

ಇದು Kubernetesನಲ್ಲಿ ತುಂಬಾ important concept.

---

# 13. Selector ತಪ್ಪಾದರೆ ಏನಾಗುತ್ತದೆ?

Suppose Serviceನಲ್ಲಿ:

```yaml
selector:
  app: something-else
```

ಆದರೆ Podನಲ್ಲಿ:

```yaml
labels:
  app: hello-world
```

ಆಗ:

```text
Pod → Running ✅

Service → Pod ಸಿಗಲ್ಲ ❌
```

ಅಂದರೆ Pod running ಇದ್ದರೂ Service traffic ಕಳುಹಿಸಲು ಸಾಧ್ಯವಾಗುವುದಿಲ್ಲ.

ಇದನ್ನು ನೆನಪಿಡಿ:

> **Service selector must match Pod labels.**

---

# 14. `imagePullSecrets`

ನಮ್ಮ image GHCRನಲ್ಲಿ ಇದೆ:

```text
ghcr.io/srujankn762/hello-world-image:latest
```

GHCR private ಆಗಿದ್ದರೆ Kubernetesಗೆ authentication ಬೇಕಾಗುತ್ತದೆ.

ಅದಕ್ಕಾಗಿ ನಾವು Secret create ಮಾಡಿದ್ದೇವೆ:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=srujankn762 \
  --docker-password='YOUR_GITHUB_PAT'
```

ನಂತರ Deploymentನಲ್ಲಿ:

```yaml
imagePullSecrets:
  - name: ghcr-secret
```

ಅಂತ attach ಮಾಡಿದ್ದೇವೆ.

ಅರ್ಥ:

> "GHCRನಿಂದ image pull ಮಾಡುವಾಗ `ghcr-secret` credentials ಬಳಸು."

---

# 15. `image`

```yaml
image: ghcr.io/srujankn762/hello-world-image:latest
```

ಇದು Kubernetes run ಮಾಡಬೇಕಾದ Docker image.

Flow:

```text
Kubernetes
    |
    | Pull image
    v
GHCR
    |
    v
hello-world-image:latest
    |
    v
Pod
```

---

# 16. `containerPort`

ನಮ್ಮ Deploymentನಲ್ಲಿ:

```yaml
ports:
  - containerPort: 8055
```

ನಿನ್ನ Dockerfileನಲ್ಲಿ:

```dockerfile
EXPOSE 8055

CMD ["gunicorn", "helloworld.wsgi:application", "--bind", "0.0.0.0:8055", "--workers", "3"]
```

ಅಂದರೆ Django/Gunicorn:

```text
0.0.0.0:8055
```

ನಲ್ಲಿ listen ಮಾಡುತ್ತಿದೆ.

ಆದ್ದರಿಂದ:

```text
containerPort = 8055
```

ಇಟ್ಟುಕೊಂಡಿದ್ದೇವೆ.

> `containerPort` ಅನ್ನು mainly container/application port ಅನ್ನು describe ಮಾಡಲು ಬಳಸುತ್ತೇವೆ. ಹೊರಗಿನಿಂದ access ಕೊಡಲು Service ಬೇಕು.

---

# 17. Service ಅಂದ್ರೆ ಏನು?

ಇದು ಬಹಳ important.

Podಗೆ ಒಂದು IP address ಇರುತ್ತದೆ.

ಉದಾಹರಣೆಗೆ:

```text
Pod A
10.1.0.15
```

Pod delete/recreate ಆದರೆ:

```text
Pod B
10.1.0.27
```

IP ಬದಲಾಗಬಹುದು.

ಆಗ client ಪ್ರತಿಬಾರಿ ಹೊಸ Pod IP ಹುಡುಕಬೇಕಾದರೆ ತುಂಬಾ inconvenient.

ಅದಕ್ಕಾಗಿ **Service**.

Service ಒಂದು stable network endpoint ಕೊಡುತ್ತದೆ.

```text
Client
   |
   v
Service
   |
   +---- Pod
   |
   +---- Pod
```

ಅಂದರೆ:

> **Deployment application Pods manage ಮಾಡುತ್ತದೆ.**
>
> **Service ಆ Podsಗೆ network access ಕೊಡುತ್ತದೆ.**

---

# 18. ನಮ್ಮ `service.yaml`

```yaml
apiVersion: v1
kind: Service

metadata:
  name: hello-world-service

spec:
  type: NodePort

  selector:
    app: hello-world

  ports:
    - protocol: TCP
      port: 8008
      targetPort: 8055
      nodePort: 30000
```

---

# 19. `kind: Service`

```yaml
kind: Service
```

Kubernetesಗೆ:

> "Service create ಮಾಡು."

ಅಂತ ಹೇಳುತ್ತದೆ.

---

# 20. Service `metadata`

```yaml
metadata:
  name: hello-world-service
```

Serviceನ ಹೆಸರು:

```text
hello-world-service
```

Check:

```bash
kubectl get services
```

---

# 21. `type: NodePort`

```yaml
type: NodePort
```

ಇದು Service ಅನ್ನು Kubernetes Nodeನ ಒಂದು port ಮೂಲಕ ಹೊರಗಿನಿಂದ access ಮಾಡಲು allow ಮಾಡುತ್ತದೆ.

ನಮ್ಮ caseನಲ್ಲಿ:

```text
localhost:30000
```

---

# 22. Service Selector

```yaml
selector:
  app: hello-world
```

Service:

> "app=hello-world label ಇರುವ Pods ಹುಡುಕು."

ನಮ್ಮ Pod:

```text
app=hello-world
```

ಆದ್ದರಿಂದ Service ನಮ್ಮ Pod ಅನ್ನು select ಮಾಡುತ್ತದೆ.

---

# 23. Service Ports — ಅತ್ಯಂತ Important

ನಮ್ಮ Service:

```yaml
port: 8008
targetPort: 8055
nodePort: 30000
```

ಇವು ಮೂರು ಬೇರೆ concepts.

---

## 23.1 `port: 8008`

ಇದು **Service port**.

ಅಂದರೆ Kubernetes cluster ಒಳಗೆ Service:

```text
hello-world-service:8008
```

ಅಂತ reachable ಆಗಿರುತ್ತದೆ.

ಇದು Django application port ಅಲ್ಲ.

---

## 23.2 `targetPort: 8055`

ಇದು:

> "Serviceಗೆ ಬಂದ traffic ಅನ್ನು Podನ ಯಾವ portಗೆ ಕಳುಹಿಸಬೇಕು?"

ಅನ್ನೋದನ್ನು ಹೇಳುತ್ತದೆ.

ನಮ್ಮ Django:

```text
Django/Gunicorn :8055
```

ಆದ್ದರಿಂದ:

```yaml
targetPort: 8055
```

Flow:

```text
Service :8008
      |
      | targetPort
      v
Pod :8055
      |
      v
Django
```

---

## 23.3 `nodePort: 30000`

ಇದು **ಹೊರಗಿನಿಂದ Kubernetes Nodeಗೆ access ಮಾಡುವ port**.

ನಮ್ಮ local Docker Desktop setupನಲ್ಲಿ:

```text
http://localhost:30000
```

ಬಳಸಬಹುದು.

NodePort ಸಾಮಾನ್ಯವಾಗಿ:

```text
30000 - 32767
```

rangeನಲ್ಲಿ ಇರುತ್ತದೆ.

---

# 24. Three Ports — Simple Memory Trick

ನಮ್ಮ projectನಲ್ಲಿ:

```text
30000 → 8008 → 8055
```

ಅರ್ಥ:

```text
30000 = NodePort
8008  = Service Port
8055  = Application / Pod Port
```

---

# 25. Full Request Flow

Browserನಲ್ಲಿ:

```text
http://localhost:30000
```

ಕೊಟ್ಟಾಗ:

```text
Browser
   |
   | :30000
   v
Kubernetes NodePort
   |
   | :30000
   v
Service
   |
   | :8008
   v
Service routing
   |
   | targetPort :8055
   v
Pod
   |
   | :8055
   v
Django/Gunicorn
```

Response ಮತ್ತೆ reverse directionನಲ್ಲಿ ಬರುತ್ತದೆ.

---

# 26. `port`, `targetPort`, `containerPort` Same ಇರಬೇಕಾ?

**ಇಲ್ಲ. ಯಾವಾಗಲೂ same ಇರಬೇಕೆಂದಿಲ್ಲ.**

ನಮ್ಮ setup:

```text
containerPort = 8055
targetPort    = 8055
port          = 8008
nodePort      = 30000
```

ಇದು perfectly valid.

Example:

```yaml
containerPort: 8055
```

Service:

```yaml
port: 8008
targetPort: 8055
nodePort: 30000
```

Flow:

```text
30000
  |
  v
8008
  |
  v
8055
```

---

# 27. Deployment vs Service

ಇದನ್ನು strong ಆಗಿ ನೆನಪಿಟ್ಟುಕೊಳ್ಳಿ.

## Deployment

**"ನನ್ನ application run ಆಗಬೇಕು."**

```text
Deployment
    |
    v
Pod
    |
    v
Container
```

## Service

**"ಆ applicationಗೆ network ಮೂಲಕ request ಹೇಗೆ ತಲುಪಬೇಕು?"**

```text
Client
   |
   v
Service
   |
   v
Pod
```

ಒಂದು lineನಲ್ಲಿ:

```text
Deployment = Application management
Service    = Network access
```

---

# 28. Commands

## Kubernetes context

```bash
kubectl config current-context
```

Docker Desktop Kubernetes ಬಳಸುತ್ತಿದ್ದರೆ:

```text
docker-desktop
```

---

## Cluster check

```bash
kubectl cluster-info
```

---

## Nodes

```bash
kubectl get nodes
```

---

## Deployment apply

```bash
kubectl apply -f deployment.yaml
```

---

## Deployments check

```bash
kubectl get deployments
```

Expected:

```text
hello-world   1/1   1   1
```

---

## Pods check

```bash
kubectl get pods
```

Expected:

```text
hello-world-xxxxx   1/1   Running
```

---

## Service apply

```bash
kubectl apply -f service.yaml
```

---

## Services check

```bash
kubectl get services
```

Expected:

```text
hello-world-service   NodePort   ...   8008:30000/TCP
```

---

# 29. Application Test

Browser:

```text
http://localhost:30000
```

ನಿನ್ನ API endpoint `/api/hello` ಆಗಿದ್ದರೆ:

```text
http://localhost:30000/api/hello
```

---

# 30. `ImagePullBackOff` ಬಂದರೆ

ನಮಗೆ ಹಿಂದೆ ಇದೇ ಸಮಸ್ಯೆ ಬಂದಿತ್ತು.

Check:

```bash
kubectl get pods
```

Pod:

```text
ImagePullBackOff
```

ಆಗ:

```bash
kubectl describe pod <pod-name>
```

ಮತ್ತು ಕೊನೆಯಲ್ಲಿ:

```text
Events:
```

ನೋಡಿ.

GHCR authentication problem ಇದ್ದರೆ:

```text
unauthorized
```

ಅಂತ ಬರಬಹುದು.

Check Secret:

```bash
kubectl get secrets
```

Expected:

```text
ghcr-secret
```

---

# 31. Pod Running ಆದರೆ Browser Work ಆಗದಿದ್ದರೆ

ಮೊದಲು:

```bash
kubectl get svc hello-world-service
```

ನಂತರ:

```bash
kubectl get endpoints hello-world-service
```

Endpoints empty ಆಗಿದ್ದರೆ Serviceಗೆ matching Pod ಸಿಗುತ್ತಿಲ್ಲ.

Labels check:

```bash
kubectl get pods --show-labels
```

Podನಲ್ಲಿ:

```text
app=hello-world
```

ಇರಬೇಕು.

Serviceನಲ್ಲಿ:

```yaml
selector:
  app: hello-world
```

ಇರಬೇಕು.

---

# 32. Logs ನೋಡಲು

```bash
kubectl logs <pod-name>
```

ಉದಾಹರಣೆ:

```bash
kubectl logs hello-world-xxxxx
```

ಇದರಿಂದ Django/Gunicorn application logs ನೋಡಬಹುದು.

---

# 33. Pod Details

```bash
kubectl describe pod <pod-name>
```

ಇದರಿಂದ:

- Image
- Container
- Ports
- Events
- Scheduling
- Errors

ಎಲ್ಲಾ ನೋಡಬಹುದು.

---

# 34. Service Details

```bash
kubectl describe service hello-world-service
```

ಇದರಿಂದ:

- Service type
- Ports
- Selector
- Endpoints

ಇತ್ಯಾದಿ ನೋಡಬಹುದು.

---

# 35. End-to-End Architecture

```text
                  GHCR
                   |
                   | Docker Image
                   v
             +-------------+
             | Deployment  |
             +-------------+
                   |
                   | creates
                   v
             +-------------+
             |    Pod      |
             |             |
             | label:      |
             | app=hello-world
             |             |
             | container    |
             | port: 8055  |
             +-------------+
                   ^
                   |
              targetPort
                 8055
                   |
             +-------------+
             |   Service   |
             |             |
             | port: 8008  |
             | selector:   |
             | app=hello-world
             +-------------+
                   ^
                   |
              NodePort
                30000
                   ^
                   |
                Browser
          localhost:30000
```

---

# 36. Most Important Concepts

## Deployment

> Applicationನ Pods manage ಮಾಡುತ್ತದೆ.

## Pod

> Containerized application run ಆಗುವ Kubernetes unit.

## Container

> ನಮ್ಮ Docker image run ಆಗುವ actual container.

## Label

> Podಗೆ ಹಾಕುವ key-value identifier.

Example:

```text
app=hello-world
```

## Selector

> Matching labels ಬಳಸಿ Pods ಹುಡುಕುತ್ತದೆ.

## Service

> Podsಗೆ stable network access ಕೊಡುತ್ತದೆ.

## `containerPort`

> Container/application ಬಳಸುವ port.

## `targetPort`

> Service traffic ಹೋಗಬೇಕಾದ Pod port.

## `port`

> Serviceನ internal port.

## `nodePort`

> Kubernetes Node ಮೇಲೆ external accessಗೆ ಬಳಸುವ port.

---

# 37. Final Configuration Table

| Component | ನಮ್ಮ Configuration | ಅರ್ಥ |
|---|---|---|
| Docker Image | `ghcr.io/srujankn762/hello-world-image:latest` | Kubernetes run ಮಾಡುವ image |
| Deployment | `hello-world` | Application manage ಮಾಡುತ್ತದೆ |
| Replicas | `1` | 1 Pod maintain ಮಾಡು |
| Pod Label | `app=hello-world` | Pod identifier |
| Deployment Selector | `app=hello-world` | Deploymentಗೆ Pod identify ಮಾಡಲು |
| Container Port | `8055` | Django/Gunicorn port |
| Service | `hello-world-service` | Network access |
| Service Type | `NodePort` | Node ಮೂಲಕ external access |
| Service Port | `8008` | Service port |
| Target Port | `8055` | Pod/application port |
| NodePort | `30000` | External Node port |
| Browser | `localhost:30000` | Local access |

---

# 38. One Final Memory Trick

ಇದನ್ನ ಮಾತ್ರ ನೆನಪಿಟ್ಟರೂ ಸಾಕು:

```text
Deployment
   ↓
Creates / manages
   ↓
Pod
   ↓
Runs
   ↓
Container
   ↓
Django :8055


Service
   ↓
Uses selector
   ↓
Finds Pod
   ↓
Forwards traffic
   ↓
targetPort :8055


Browser
   ↓
localhost:30000
   ↓
NodePort :30000
   ↓
Service :8008
   ↓
Pod :8055
   ↓
Django
```

### Super-short version

```text
Deployment → "App run ಮಾಡು"
Pod        → "App ಇಲ್ಲಿ run ಆಗುತ್ತಿದೆ"
Label      → "ಈ Pod ಯಾರು?"
Selector   → "ನನಗೆ ಬೇಕಾದ Pod ಹುಡುಕು"
Service    → "Podಗೆ stable network ಕೊಡು"
port       → "Service port"
targetPort → "Pod/App port"
nodePort   → "ಹೊರಗಿನಿಂದ ಬರುವ port"
```

**ನಮ್ಮ exact project flow:**

```text
localhost:30000
      ↓
Service:8008
      ↓
Pod:8055
      ↓
Django/Gunicorn
```
