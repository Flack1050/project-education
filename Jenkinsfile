pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Repository was cloned successfully'
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
                sh 'docker build -t notes-frontend-ci ./frontend'
            }
        }

        stage('Build Backend') {
            steps {
                sh 'docker build -t notes-backend-ci ./backend'
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
