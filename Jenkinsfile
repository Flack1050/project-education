pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = 'notes-frontend'
        BACKEND_IMAGE = 'notes-backend'

        GHCR_REGISTRY = 'ghcr.io'
        GHCR_NAMESPACE = 'flack1050'

        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    parameters {
        choice(
            name: 'BUILD_TARGET',
            choices: ['all', 'frontend', 'backend'],
            description: 'Choose what to build'
        )
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository was cloned successfully'
            }
        }

        stage('Environment') {
            steps {
                sh '''
                    echo "Frontend image: $FRONTEND_IMAGE"
                    echo "Backend image: $BACKEND_IMAGE"
                    echo "Image tag: $IMAGE_TAG"
                    echo "Build number: $BUILD_NUMBER"
                    echo "Build target: $BUILD_TARGET"
                '''
            }
        }

        stage('Check Docker') {
            steps {
                sh 'docker --version'
                sh 'docker compose version'
            }
        }

        stage('Build Frontend') {
            when {
                expression {
                    params.BUILD_TARGET == 'all' ||
                    params.BUILD_TARGET == 'frontend'
                }
            }

            steps {
                sh '''
                    docker build \
                        -t $GHCR_REGISTRY/$GHCR_NAMESPACE/$FRONTEND_IMAGE:$IMAGE_TAG \
                        ./frontend
                '''
            }
        }

        stage('Build Backend') {
            when {
                expression {
                    params.BUILD_TARGET == 'all' ||
                    params.BUILD_TARGET == 'backend'
                }
            }

            steps {
                sh '''
                    docker build \
                        -t $GHCR_REGISTRY/$GHCR_NAMESPACE/$BACKEND_IMAGE:$IMAGE_TAG \
                        ./backend
                '''
            }
        }

        stage('Login to GHCR') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-ghcr',
                        usernameVariable: 'GHCR_USERNAME',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login $GHCR_REGISTRY \
                            -u "$GHCR_USERNAME" \
                            --password-stdin
                    '''
                }
            }
        }

        stage('Push Frontend') {
            when {
                expression {
                    params.BUILD_TARGET == 'all' ||
                    params.BUILD_TARGET == 'frontend'
                }
            }

            steps {
                sh '''
                    docker push \
                        $GHCR_REGISTRY/$GHCR_NAMESPACE/$FRONTEND_IMAGE:$IMAGE_TAG
                '''
            }
        }

        stage('Push Backend') {
            when {
                expression {
                    params.BUILD_TARGET == 'all' ||
                    params.BUILD_TARGET == 'backend'
                }
            }

            steps {
                sh '''
                    docker push \
                        $GHCR_REGISTRY/$GHCR_NAMESPACE/$BACKEND_IMAGE:$IMAGE_TAG
                '''
            }
        }
    }

    post {
        success {
            echo 'CI pipeline completed successfully!'
        }

        failure {
            echo 'CI pipeline failed!'
        }

        always {
            echo 'Pipeline finished'
        }
    }
}
