# Jenkins CI/CD Setup

ಈ projectನಲ್ಲಿ Jenkins ಅನ್ನು CI/CD pipeline automate ಮಾಡಲು ಬಳಸಿದ್ದೇವೆ.

## Jenkins Docker Setup

```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts-jdk21
```

Jenkins UI: `http://localhost:8080`

`jenkins_home` volume Jenkins configuration, jobs ಮತ್ತು plugins persist ಮಾಡುತ್ತದೆ.

## Docker Access

Jenkins containerಗೆ Docker daemon access ಕೊಡಲು `/var/run/docker.sock` mount ಮಾಡಿದ್ದೇವೆ.

```text
Jenkins Container
       |
       v
Docker Socket
       |
       v
Docker Desktop
```

Productionನಲ್ಲಿ Jenkins controllerಗೆ Docker socket mount ಮಾಡುವುದನ್ನು ಸಾಮಾನ್ಯವಾಗಿ avoid ಮಾಡುತ್ತಾರೆ; isolated agents ಮತ್ತು BuildKit/Kaniko ಮುಂತಾದ approaches safer.

## Jenkins Credentials

### GHCR

```text
ID: ghcr-credentials
```

Docker image ಅನ್ನು GHCRಗೆ push ಮಾಡಲು ಬಳಸುತ್ತೇವೆ.

### GitHub

```text
ID: github-git-credentials
```

Kubernetes manifest update ಮಾಡಿದ ನಂತರ GitHubಗೆ push ಮಾಡಲು ಬಳಸುತ್ತೇವೆ.

GitHub Classic PAT permissions:

```text
repo
write:packages
```

PAT ಅನ್ನು Jenkinsfileನಲ್ಲಿ hard-code ಮಾಡಬಾರದು.

## Jenkinsfile

Location:

```text
helloworld/Jenkinsfile
```

Pipeline:

```text
Checkout
   ↓
Get Commit ID
   ↓
Docker Build
   ↓
Docker Push
   ↓
Update Kubernetes Manifest
   ↓
Git Push
```

## Checkout

```groovy
stage('Checkout') {
    steps {
        checkout scm
    }
}
```

Repository:
`https://github.com/srujankn762/system_design_concepts.git`

Branch: `main`

## Commit ID as Docker Tag

```groovy
env.COMMIT_ID = sh(
    script: 'git rev-parse --short=4 HEAD',
    returnStdout: true
).trim()
```

Example:

```text
Git commit: 1973abcd...
Image: ghcr.io/srujankn762/hello-world-image:1973
```

This makes the Docker image traceable to the Git commit.

## Docker Build

Jenkins `helloworld` directory ಒಳಗೆ Docker image build ಮಾಡುತ್ತದೆ.

```groovy
stage('Docker Build') {
    steps {
        dir('helloworld') {
            sh '''
                docker build \
                  -t ghcr.io/srujankn762/hello-world-image:${COMMIT_ID} \
                  .
            '''
        }
    }
}
```

## Docker Push

The image is pushed to GHCR:

```text
ghcr.io/srujankn762/hello-world-image:<commit-id>
```

Flow:

```text
Jenkins
   ↓
docker login ghcr.io
   ↓
docker push
   ↓
GHCR
```

## Kubernetes Manifest Update

Jenkins automatically updates:

```text
helloworld/k8s/deployment.yaml
```

Example:

```yaml
image: ghcr.io/srujankn762/hello-world-image:v2
```

becomes:

```yaml
image: ghcr.io/srujankn762/hello-world-image:1973
```

Then Jenkins commits and pushes the manifest change:

```bash
git add helloworld/k8s/deployment.yaml
git commit -m "ci: deploy 1973"
git push
```

## Jenkins → Argo CD

Jenkins does not directly deploy to Kubernetes.

```text
Jenkins
   ↓
Update deployment.yaml
   ↓
GitHub
   ↓
Argo CD
   ↓
Kubernetes
```

Argo CD configuration:

```text
Repository: https://github.com/srujankn762/system_design_concepts.git
Branch: main
Path: helloworld/k8s
```

When the image tag changes in Git, Argo CD detects the desired-state change and synchronizes Kubernetes.

## Complete Flow

```text
Developer
    |
    | git push
    v
GitHub
    |
    v
Jenkins
    |
    ├── Checkout
    ├── Get Commit ID
    ├── Docker Build
    ├── Docker Push
    |       ↓
    |      GHCR
    |
    ├── Update deployment.yaml
    |
    └── Git Push
            ↓
          GitHub
            ↓
         Argo CD
            ↓
        Kubernetes
```

## Current Status

The Jenkins pipeline currently:

- Checks out code from GitHub
- Generates a commit-based image tag
- Builds the Docker image
- Pushes the image to GHCR
- Updates `deployment.yaml`
- Pushes the manifest change back to GitHub
- Allows Argo CD to deploy the Git change to Kubernetes

## Next Improvement

Configure a GitHub webhook:

```text
git push
   ↓
GitHub Webhook
   ↓
Jenkins automatically starts
```

This removes the need to manually click **Build Now**.