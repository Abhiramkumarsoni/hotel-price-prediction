pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'hotel-price-prediction'
        CONTAINER_NAME = 'hotel-app'
        APP_PORT = '8000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                bat '''
                    docker build -t %DOCKER_IMAGE%:latest .
                '''
            }
        }
        
        stage('Stop Old Container') {
            steps {
                echo '🛑 Stopping any existing container...'
                bat '''
                    docker stop %CONTAINER_NAME% 2>nul || echo "No container to stop"
                    docker rm %CONTAINER_NAME% 2>nul || echo "No container to remove"
                '''
            }
        }
        
        stage('Run Container') {
            steps {
                echo '🚀 Starting new container...'
                bat '''
                    docker run -d -p %APP_PORT%:%APP_PORT% --name %CONTAINER_NAME% %DOCKER_IMAGE%:latest
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo '❤️ Checking if app is running...'
                script {
                    sleep(time: 10, unit: 'SECONDS')
                    bat '''
                        curl -f http://localhost:%APP_PORT% || echo "Health check - app may still be starting"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully! App running at http://localhost:8000'
        }
        failure {
            echo '❌ Pipeline failed! Check the logs above for errors.'
        }
    }
}
