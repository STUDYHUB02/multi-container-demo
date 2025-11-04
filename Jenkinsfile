pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
        DOCKER_IMAGE = "studyhub02/flask-mysql-app"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/STUDYHUB02/multi-container-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest .'
            }
        }

        stage('Run Container for Testing') {
            steps {
                sh 'docker run -d --name test-container -p 5000:5000 $DOCKER_IMAGE:latest'
                sh 'sleep 10'
                sh 'curl -f http://localhost:5000/count || exit 1'
                sh 'docker stop test-container'
                sh 'docker rm test-container'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh 'echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin'
                sh 'docker push $DOCKER_IMAGE:latest'
            }
        }

        stage('Deploy to Local Server') {
            steps {
                sh '''
                docker stop flask_app || true
                docker rm flask_app || true
                docker pull $DOCKER_IMAGE:latest
                docker run -d --name flask_app -p 5000:5000 $DOCKER_IMAGE:latest
                '''
            }
        }
    }
}
