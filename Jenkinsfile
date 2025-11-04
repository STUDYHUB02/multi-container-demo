pipeline {
  agent any

  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKER_IMAGE = "studyhub02/flask-mysql-app"
    TEST_NETWORK = "ci_test_net"
    MYSQL_CONTAINER = "ci_test_mysql"
    APP_CONTAINER = "ci_test_app"
  }

  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  stages {

    stage('Build Docker Image') {
      steps {
        sh '''
          echo "Building Docker image: ${DOCKER_IMAGE}:latest"
          docker build -t ${DOCKER_IMAGE}:latest .
        '''
      }
    }

    stage('Integration Smoke Test') {
      steps {
        script {
          // Run the CI integration script using bash (to allow pipefail)
          sh '''bash <<'BASH'
set -euo pipefail

# ensure previous test artifacts removed
docker rm -f ${APP_CONTAINER} ${MYSQL_CONTAINER} >/dev/null 2>&1 || true
docker network rm ${TEST_NETWORK} >/dev/null 2>&1 || true

echo "Creating test network ${TEST_NETWORK}"
docker network create ${TEST_NETWORK}

echo "Starting MySQL for CI test..."
docker run -d --name ${MYSQL_CONTAINER} --network ${TEST_NETWORK} \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=testdb \
  -e MYSQL_USER=testuser \
  -e MYSQL_PASSWORD=testpass \
  --health-cmd='mysqladmin ping -h localhost -u root -prootpass' \
  --health-interval=5s --health-retries=10 mysql:8 --default-authentication-plugin=mysql_native_password

echo "Waiting for MySQL to be healthy (max ~60s)..."
RETRY=0
until [ "$(docker inspect -f '{{.State.Health.Status}}' ${MYSQL_CONTAINER} 2>/dev/null || echo unknown)" = "healthy" ]; do
  sleep 3
  RETRY=$((RETRY+1))
  if [ "$RETRY" -gt 20 ]; then
    echo "MySQL did not become healthy in time. Logs:"
    docker logs ${MYSQL_CONTAINER} --tail 200 || true
    exit 1
  fi
done
echo "MySQL is healthy."

echo "Running Flask app container connected to test MySQL..."
docker run -d --name ${APP_CONTAINER} --network ${TEST_NETWORK} -p 5100:5000 \
  -e DB_HOST=${MYSQL_CONTAINER} -e DB_USER=testuser -e DB_PASS=testpass -e DB_NAME=testdb \
  ${DOCKER_IMAGE}:latest

echo "Waiting for Flask app to start (sleep 6s)..."
sleep 6

echo "Smoke testing /count endpoint..."
if ! curl -sSf http://localhost:5100/count -m 10 ; then
  echo "Smoke test failed. App logs:"
  docker logs ${APP_CONTAINER} --tail 200 || true
  exit 1
fi
echo "Smoke test passed."

# cleanup test containers but keep image
docker rm -f ${APP_CONTAINER} ${MYSQL_CONTAINER} >/dev/null 2>&1 || true
docker network rm ${TEST_NETWORK} >/dev/null 2>&1 || true

BASH
'''
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            echo "Logging into Docker Hub as $DH_USER"
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${DOCKER_IMAGE}:latest
            docker logout
          '''
        }
      }
    }

    stage('Deploy to Local Server') {
      steps {
        sh '''
          echo "Deploying image locally as 'flask_app' (port 5000)..."
          docker rm -f flask_app >/dev/null 2>&1 || true
          docker pull ${DOCKER_IMAGE}:latest
          docker run -d --name flask_app -p 5000:5000 ${DOCKER_IMAGE}:latest
          echo "Deployed. Will sleep 2s then verify /count..."
          sleep 2
          curl -sSf http://localhost:5000/count || (echo "Deployment verification failed" && exit 1)
          echo "Deployment verification OK."
        '''
      }
    }
  }

  post {
    always {
      sh '''
        docker rm -f ${APP_CONTAINER} ${MYSQL_CONTAINER} >/dev/null 2>&1 || true
        docker network rm ${TEST_NETWORK} >/dev/null 2>&1 || true
      '''
      cleanWs()
    }
    success {
      echo 'Pipeline completed successfully.'
    }
    failure {
      echo 'Pipeline failed — check console output for details.'
    }
  }
}
