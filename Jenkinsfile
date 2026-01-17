pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.12'
        VENV_NAME = 'venv'
        APP_PORT = '8000'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                bat '''
                    python -m venv %VENV_NAME%
                    call %VENV_NAME%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip setuptools wheel
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing project dependencies...'
                bat '''
                    call %VENV_NAME%\\Scripts\\activate.bat
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                bat '''
                    call %VENV_NAME%\\Scripts\\activate.bat
                    python -m pytest tests/ --junitxml=test-results.xml || exit 0
                '''
            }
            post {
                always {
                    // Publish test results
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }
        
        stage('Code Quality Check') {
            steps {
                echo 'Running code quality checks...'
                bat '''
                    call %VENV_NAME%\\Scripts\\activate.bat
                    pip install pylint flake8 || exit 0
                    pylint app.py --exit-zero > pylint-report.txt || exit 0
                    flake8 app.py --exit-zero > flake8-report.txt || exit 0
                '''
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { fileExists('Dockerfile') }
            }
            steps {
                echo 'Building Docker image...'
                script {
                    bat '''
                        docker build -t hotel-price-prediction:latest .
                        docker tag hotel-price-prediction:latest hotel-price-prediction:%BUILD_NUMBER%
                    '''
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to staging environment...'
                bat '''
                    call %VENV_NAME%\\Scripts\\activate.bat
                    taskkill /F /IM python.exe /FI "WINDOWTITLE eq Flask*" || exit 0
                    start /B python app.py
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health check...'
                script {
                    sleep(time: 10, unit: 'SECONDS')
                    bat '''
                        curl -f http://localhost:%APP_PORT% || exit 1
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            emailext (
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                    <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        failure {
            echo 'Pipeline failed!'
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                    <p>Check console output at <a href='${env.BUILD_URL}'>${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                recipientProviders: [[$class: 'DevelopersRecipientProvider']]
            )
        }
        always {
            echo 'Cleaning up...'
            cleanWs()
        }
    }
}
