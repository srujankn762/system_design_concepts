pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: kaniko
      image: gcr.io/kaniko-project/executor:v1.23.2-debug
      command:
        - /busybox/sh
      args:
        - -c
        - cat
      tty: true
      volumeMounts:
        - name: kaniko-config
          mountPath: /kaniko/.docker
  volumes:
    - name: kaniko-config
      emptyDir: {}
'''
        }
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Get Commit ID') {
            steps {
                script {
                    env.COMMIT_ID = sh(
                        script: 'git rev-parse --short=4 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Commit ID: ${env.COMMIT_ID}"
                }
            }
        }

        stage('Build and Push Image') {
            steps {
                container('kaniko') {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'ghcr-credentials',
                            usernameVariable: 'GHCR_USER',
                            passwordVariable: 'GHCR_TOKEN'
                        )
                    ]) {
                        sh '''
                            printf '{"auths":{"ghcr.io":{"username":"%s","password":"%s"}}}' \\
                              "$GHCR_USER" "$GHCR_TOKEN" \\
                              > /kaniko/.docker/config.json

                            /kaniko/executor \\
                              --context "$WORKSPACE/helloworld" \\
                              --dockerfile "$WORKSPACE/helloworld/Dockerfile" \\
                              --destination "ghcr.io/srujankn762/hello-world-image:${COMMIT_ID}"
                        '''
                    }
                }
            }
        }

        stage('Update Kubernetes Manifest') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credentials',
                        usernameVariable: 'GH_USER',
                        passwordVariable: 'GH_TOKEN'
                    )
                ]) {
                    sh '''
                        sed -i "s|image: ghcr.io/srujankn762/hello-world-image:.*|image: ghcr.io/srujankn762/hello-world-image:${COMMIT_ID}|" \
                            helloworld/k8s/deployment.yaml

                        git config user.name "jenkins"
                        git config user.email "jenkins@localhost"

                        git add helloworld/k8s/deployment.yaml

                        git commit -m "ci: deploy ${COMMIT_ID}" || echo "No manifest changes"

                        git push https://${GH_USER}:${GH_TOKEN}@github.com/srujankn762/system_design_concepts.git HEAD:main
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Image pushed successfully:"
            echo "ghcr.io/srujankn762/hello-world-image:${COMMIT_ID}"
        }

        failure {
            echo "Build or push failed."
        }
    }
}
