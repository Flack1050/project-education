pipeline {
    agent any

    stages {
        stage('Branch Info') {
            steps {
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Build: ${env.BUILD_NUMBER}"
            }
        }

        stage('Test') {
            steps {
                echo "Hello from ${env.BRANCH_NAME}!"
            }
        }
    }
}
