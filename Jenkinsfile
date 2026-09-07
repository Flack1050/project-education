pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = 'notes-frontend-ci'
        BACKEND_IMAGE = 'notes-backend-ci'
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
            steps {
                sh 'docker build -t $FRONTEND_IMAGE:$IMAGE_TAG ./frontend'
            }
        }

        stage('Build Backend') {
            steps {
                sh 'docker build -t $BACKEND_IMAGE:$IMAGE_TAG ./backend'
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
