# Kubernetes + Argo CD + PostgreSQL — Learning Project

ಈ READMEನಲ್ಲಿ ನಾವು ಇಲ್ಲಿವರೆಗೆ build ಮಾಡಿದ complete setup, concepts, commands ಮತ್ತು architecture ಅನ್ನು Kannada + English mixನಲ್ಲಿ document ಮಾಡಿದ್ದೇವೆ.

## 1. Project Goal

ನಮ್ಮ Django `hello-world` backend ಅನ್ನು Docker image ಆಗಿ build ಮಾಡಿ, GHCRಗೆ push ಮಾಡಿ, Kubernetesನಲ್ಲಿ Deployment + Service ಮೂಲಕ run ಮಾಡಿ, PostgreSQL ಅನ್ನು Kubernetesನಲ್ಲಿ deploy ಮಾಡಿ, Django → PostgreSQL connection ಮಾಡಿಸಿ, persistent storage ಬಳಸಿಸಿ, Argo CD ಮೂಲಕ GitOps deployment ಮಾಡುವುದು. ಮುಂದೆ Jenkins ಮೂಲಕ CI automation ಸೇರಿಸುವುದು.

```text
Developer
   ↓
GitHub
   ├── application code
   └── k8s manifests
          ↓
       Argo CD
          ↓
     Kubernetes
       ├── Django Pod
       │      ↓
       │  postgres-service
       │      ↓
       └── PostgreSQL Pod
              ↓
            PVC
```

## 2. Docker Application

ನಮ್ಮ Dockerfileನಲ್ಲಿ Django/Gunicorn `8055` portನಲ್ಲಿ listen ಮಾಡುತ್ತದೆ:

```dockerfile
FROM python:3.12-slim AS base

WORKDIR /srujan

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     libpq-dev     && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /srujan
RUN pip install -r requirements.txt

COPY . /srujan

EXPOSE 8055

CMD ["gunicorn", "helloworld.wsgi:application", "--bind", "0.0.0.0:8055", "--workers", "3"]
```

`EXPOSE 8055` container ಒಳಗಿನ application port. ಇದು ಸ್ವತಃ Macನಲ್ಲಿ port publish ಮಾಡುವುದಿಲ್ಲ; Kubernetes Service routing ಮಾಡುತ್ತದೆ.

## 3. `.dockerignore`

Kubernetes manifests Docker image runtimeಗೆ ಬೇಕಾಗಿಲ್ಲ:

```dockerignore
k8s/
.git/
.github/
.gitignore
__pycache__/
*.py[cod]
venv/
.venv/
env/
.env
.env.*
.vscode/
.idea/
.DS_Store
.pytest_cache/
.coverage
htmlcov/
```

GitHubನಲ್ಲಿ `k8s/` ಇರಬೇಕು, ಆದರೆ Docker imageನಲ್ಲಿ ಬೇಡ.

## 4. Docker Image Versioning

ನಾವು `latest` ಜೊತೆಗೆ versioned tag ಬಳಸಿದೆವು:

```text
ghcr.io/srujankn762/hello-world-image:v2
```

Build:

```bash
docker build -t ghcr.io/srujankn762/hello-world-image:v2 .
```

Push:

```bash
docker push ghcr.io/srujankn762/hello-world-image:v2
```

Kubernetesನಲ್ಲಿ verify:

```bash
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].image}{"\n"}'
```

`v2` running ಎಂದು confirm ಮಾಡಿದೆವು.

## 5. Kubernetes Namespace

Argo CDಗಾಗಿ dedicated namespace:

```bash
kubectl create namespace argocd
```

Namespace ಅಂದ್ರೆ cluster ಒಳಗಿನ logical boundary. ಇದು separate cluster ಅಥವಾ machine ಅಲ್ಲ. Resources organize ಮಾಡಲು ಮತ್ತು RBAC/access control ಸುಲಭ ಮಾಡಲು ಉಪಯೋಗಿಸುತ್ತೇವೆ.

## 6. Deployment

Application Deployment desired state manage ಮಾಡುತ್ತದೆ:

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
      containers:
        - name: hello-world
          image: ghcr.io/srujankn762/hello-world-image:v2
          ports:
            - containerPort: 8055
```

`replicas: 1` ಅಂದ್ರೆ one Pod desired.

## 7. Labels and Selectors

Pod template label:

```yaml
labels:
  app: hello-world
```

Deployment selector:

```yaml
matchLabels:
  app: hello-world
```

Service selector:

```yaml
selector:
  app: hello-world
```

ಅಂದರೆ Service ಸರಿಯಾದ Pod ಅನ್ನು label ಮೂಲಕ find ಮಾಡುತ್ತದೆ.

```text
Pod label app=hello-world
       ↑
       ├── Deployment selector
       └── Service selector
```

Selector mismatch ಆದರೆ Serviceಗೆ endpoints ಸಿಗುವುದಿಲ್ಲ.

## 8. Django Service

ನಮ್ಮ application Service NodePort:

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

Port meanings:

- `containerPort: 8055` → Django/Gunicorn container port
- `targetPort: 8055` → Service traffic ಯಾವ Pod portಗೆ ಹೋಗಬೇಕು
- `port: 8008` → Service port
- `nodePort: 30000` → Node level external/local access

Flow:

```text
Client
  ↓ :30000
NodePort
  ↓ :8008
Service
  ↓ :8055
Django Pod
```

ಈ ports same ಇರಬೇಕೆಂಬ rule ಇಲ್ಲ.

## 9. NodePort vs ClusterIP

Django user-facing applicationಗೆ:

```text
NodePort
```

ಬಳಸಿದೆವು.

PostgreSQL internal database ಆದ್ದರಿಂದ:

```text
ClusterIP
```

ಬಳಸಿದೆವು.

```text
User
 ↓
Django NodePort
 ↓
Django Pod

Django Pod
 ↓
Postgres ClusterIP
 ↓
Postgres Pod
```

Database ಅನ್ನು external usersಗೆ expose ಮಾಡಬೇಕಾದ ಅಗತ್ಯ ಇಲ್ಲ.

## 10. PostgreSQL Deployment

PostgreSQL container ಸಾಮಾನ್ಯವಾಗಿ `5432`ನಲ್ಲಿ listen ಮಾಡುತ್ತದೆ:

```yaml
ports:
  - containerPort: 5432
```

ಇದು PostgreSQL Pod/container port.

## 11. Persistent Storage

PostgreSQL data Pod lifetimeಗೆ tied ಆಗಬಾರದು. ಆದ್ದರಿಂದ PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Check:

```bash
kubectl get pvc
```

ನಮಗೆ `Bound`, `1Gi`, `RWO`, `hostpath` ಬಂದಿತ್ತು.

- PVC = storage request
- PV = provisioned storage
- `hostpath` = Docker Desktop/local-backed storage provisioner in this local setup
- Service storage ಅಲ್ಲ; Service networkingಗಾಗಿ

Flow:

```text
PostgreSQL Pod
   ↓
PVC
   ↓
PV
   ↓
Docker Desktop/local-backed storage
```

## 12. `volumes` vs `volumeMounts`

Container ಒಳಗಿನ PostgreSQL data directory:

```yaml
volumeMounts:
  - name: postgres-storage
    mountPath: /var/lib/postgresql/data
```

`mountPath` ಅಂದ್ರೆ **container ಒಳಗಿನ path**.

`volumes` ಹೇಳುವುದು ಯಾವ storage attach ಮಾಡಬೇಕು:

```yaml
volumes:
  - name: postgres-storage
    persistentVolumeClaim:
      claimName: postgres-pvc
```

Memory trick:

```text
volumes      → ಯಾವ storage?
volumeMounts → container ಒಳಗೆ ಎಲ್ಲಿ?
```

## 13. PostgreSQL Secret

Password ಅನ್ನು GitHub YAMLನಲ್ಲಿ hardcode ಮಾಡಲಿಲ್ಲ. Clusterನಲ್ಲಿ Secret create ಮಾಡಿದೆವು:

```bash
kubectl create secret generic postgres-secret   --from-literal=POSTGRES_DB=hello_world   --from-literal=POSTGRES_USER=postgres   --from-literal=POSTGRES_PASSWORD='<your-password>'
```

Actual password GitHubಗೆ commit ಮಾಡಬಾರದು.

Productionನಲ್ಲಿ External Secrets, cloud secret managers, Vault, Sealed Secrets ಮುಂತಾದ approaches ಬಳಸಬಹುದು.

## 14. PostgreSQL Service

ನಮ್ಮ current PostgreSQL Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5445
      targetPort: 5432
```

ಇಲ್ಲಿ:

```text
Service port = 5445
targetPort   = 5432
```

Flow:

```text
Django
  ↓
postgres-service:5445
  ↓
Kubernetes Service
  ↓
PostgreSQL Pod:5432
```

`5432` PostgreSQL actual container listening port. `5445` ನಮ್ಮ Service-facing port.

## 15. Why `targetPort`?

`port` ಮತ್ತು `targetPort` different ಆಗಬಹುದು.

```yaml
port: 5445
targetPort: 5432
```

ಅರ್ಥ:

```text
Client → Service:5445 → Pod:5432
```

`targetPort` = traffic destination inside selected Pod.

## 16. Endpoint Verification

ನಾವು:

```bash
kubectl get endpoints postgres-service
```

ಮಾಡಿದಾಗ:

```text
postgres-service   10.1.0.163:5432
```

ಬಂದಿತ್ತು.

ಇದರಿಂದ Service selector PostgreSQL Pod ಅನ್ನು successfully select ಮಾಡುತ್ತಿದೆ ಎಂದು confirm ಆಯಿತು.

Pod IP hardcode ಮಾಡಬಾರದು; Service name ಬಳಸಬೇಕು.

Modern Kubernetesನಲ್ಲಿ EndpointSlice ಕೂಡ ನೋಡಬಹುದು:

```bash
kubectl get endpointslice   -l kubernetes.io/service-name=postgres-service
```

## 17. Django PostgreSQL Configuration

`helloworld/settings.py`:

```python
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
```

`requirements.txt`ನಲ್ಲಿ:

```text
psycopg2-binary>=2.9
```

ಇದೆ.

## 18. Django Environment Variables

Application Deploymentನಲ್ಲಿ:

```yaml
env:
  - name: DB_NAME
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: POSTGRES_DB

  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: POSTGRES_USER

  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: postgres-secret
        key: POSTGRES_PASSWORD

  - name: DB_HOST
    value: postgres-service

  - name: DB_PORT
    value: "5445"
```

Runtime connection:

```text
DB_HOST = postgres-service
DB_PORT = 5445
DB_NAME = hello_world
DB_USER = postgres
DB_PASSWORD = Kubernetes Secret
```

So:

```text
Django Pod
   ↓
postgres-service:5445
   ↓
Service targetPort 5432
   ↓
PostgreSQL Pod:5432
```

## 19. DBeaver Connection

PostgreSQL Service `ClusterIP`, ಆದ್ದರಿಂದ Macನಿಂದ direct access ಇಲ್ಲ.

Local port-forward:

```bash
kubectl port-forward svc/postgres-service 5445:5445
```

DBeaver:

```text
Host:     localhost
Port:     5445
Database: hello_world
Username: postgres
Password: <postgres-secret password>
```

Flow:

```text
DBeaver
localhost:5445
   ↓
Service:5445
   ↓
PostgreSQL Pod:5432
```

Port-forward terminal running ಇರಬೇಕು.

## 20. Employee CRUD API

Employee model:

```python
from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
```

Serializer:

```python
from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
```

ViewSet:

```python
from rest_framework.viewsets import ModelViewSet
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
```

Routes:

```text
GET     /api/employees/
POST    /api/employees/
GET     /api/employees/1/
PUT     /api/employees/1/
PATCH   /api/employees/1/
DELETE  /api/employees/1/
```

## 21. Migrations

Create migration files:

```bash
python manage.py makemigrations
```

Apply to database:

```bash
python manage.py migrate
```

Important:

```text
makemigrations → migration file
migrate        → actual DB schema update
```

Kubernetes example:

```bash
kubectl exec -it <hello-world-pod> --   python manage.py migrate
```

## 22. Argo CD Setup

Fresh Argo CD namespace:

```bash
kubectl create namespace argocd
```

Installed Argo CD manifests.

Normal apply had CRD annotation-size issue, so server-side apply worked:

```bash
kubectl apply -n argocd   --server-side   --force-conflicts   -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Check:

```bash
kubectl get pods -n argocd
```

All Argo CD components became Running.

## 23. Argo CD Port Forward

Argo CD server uses HTTPS service port `443`.

We used:

```bash
kubectl port-forward svc/argocd-server -n argocd 8800:443
```

Meaning:

```text
localhost:8800
    ↓
Argo CD Service:443
```

`8800` is local port-forward port. `443` is Argo CD Service port.

## 24. Argo CD Application

Git repository:

```text
https://github.com/srujankn762/system_design_concepts.git
```

Manifest path:

```text
helloworld/k8s
```

Destination:

```text
https://kubernetes.default.svc
```

Namespace:

```text
default
```

Application:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application

metadata:
  name: hello-world

spec:
  project: default

  source:
    repoURL: https://github.com/srujankn762/system_design_concepts.git
    path: helloworld/k8s
    targetRevision: HEAD

  destination:
    server: https://kubernetes.default.svc
    namespace: default
```

Argo CD showed `Healthy` and `Synced`.

## 25. GitOps

Git is the desired state.

```text
GitHub
   ↓
Argo CD
   ↓
Kubernetes
```

If Git says:

```yaml
replicas: 2
```

Argo CD makes Kubernetes converge toward 2 Pods.

If Git says:

```yaml
image: ...:v2
```

Argo CD deploys that desired image.

## 26. Auto Sync

Manual sync:

```text
Git change
   ↓
Argo CD detects OutOfSync
   ↓
User clicks Sync
```

Auto sync:

```text
Git change
   ↓
Argo CD detects
   ↓
Automatic Sync
   ↓
Kubernetes updated
```

## 27. Code Change vs Manifest Change

This distinction is critical.

Changing `deployment.yaml` or `service.yaml` changes Kubernetes desired state.

Changing Python code does NOT itself build a new Docker image.

Proper CI/CD flow:

```text
Code change
   ↓
Docker build
   ↓
New image v3
   ↓
GHCR
   ↓
deployment.yaml image → v3
   ↓
Git push
   ↓
Argo CD
   ↓
Kubernetes
```

Argo CD is not a Docker image builder.

## 28. GHCR `imagePullSecrets`

For private GHCR images:

```yaml
imagePullSecrets:
  - name: ghcr-secret
```

The Kubernetes Secret stores credentials needed to pull the private image.

When the GHCR PAT changed, we updated `ghcr-secret`.

## 29. Current Architecture

```text
                         GitHub
                           |
                           v
                        Argo CD
                           |
                           v
                    Kubernetes Cluster
                           |
              +------------+------------+
              |                         |
              v                         v
       hello-world Pod            postgres Pod
              |                         |
        Django :8055              Postgres :5432
              |                         |
              v                         |
      hello-world Service                |
          NodePort                       |
          :30000                         |
                                        |
                         postgres-service:5445
                                  |
                                  v
                           targetPort :5432
                                  |
                                  v
                               PostgreSQL
                                  |
                                  v
                              postgres-pvc
                                  |
                                  v
                           Persistent Storage
```

## 30. Important Port Summary

| Component | Port | Meaning |
|---|---:|---|
| Django container | 8055 | Gunicorn/Django listening port |
| Django Service | 8008 | Service port |
| Django NodePort | 30000 | External/local node access |
| PostgreSQL container | 5432 | PostgreSQL actual listening port |
| PostgreSQL Service | 5445 | Internal Service port |
| PostgreSQL targetPort | 5432 | Pod/container destination |
| DBeaver local | 5445 | Local port-forward port |
| Argo CD server | 443 | Argo CD HTTPS service port |
| Argo CD local | 8800 | Local port-forward port |

## 31. Useful Commands

```bash
kubectl get pods
kubectl get deployments
kubectl get services
kubectl get pvc
kubectl get secrets
kubectl get endpoints postgres-service
kubectl get endpointslice -l kubernetes.io/service-name=postgres-service
kubectl get pods -n argocd
```

## 32. Current Status

We have completed:

- Dockerized Django application
- `.dockerignore`
- GHCR image `v2`
- Kubernetes Deployment
- Django NodePort Service
- PostgreSQL Deployment
- PostgreSQL ClusterIP Service
- PostgreSQL Secret
- PostgreSQL PVC
- Django → PostgreSQL connection
- Employee CRUD API
- Argo CD fresh installation
- Argo CD GitHub Application
- GitOps deployment
- DBeaver access using port-forward

## 33. Next: Jenkins CI

Planned pipeline:

```text
Developer
   |
   | git push
   v
GitHub
   |
   | webhook
   v
Jenkins
   |
   +--> Tests
   |
   +--> Docker build
   |
   +--> Push image to GHCR
   |
   +--> Update image tag in deployment.yaml
   |
   +--> Git push
             |
             v
          Argo CD
             |
             v
        Kubernetes
```

### Jenkins = CI

Jenkins handles:

```text
Build
Test
Docker image build
Image push
```

### Argo CD = CD / GitOps

Argo CD handles:

```text
Read Git
Compare desired state
Sync Kubernetes
```

This gives us a clean CI/CD separation.
