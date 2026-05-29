pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "mlops-new-495606"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages {

        stage('Clone Repo') {
            steps {
                echo 'Cloning repository...'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        credentialsId: 'GitHub-Token',
                        url: 'https://github.com/Vijaylekha25/MLOPS-PROJECT-1.git'
                    ]]
                )
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh '''#!/bin/bash
                python3 -m venv ${VENV_DIR}
                ${VENV_DIR}/bin/pip install --upgrade pip
                ${VENV_DIR}/bin/pip install -e .
                '''
            }
        }

        stage('Build & Push Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh '''#!/bin/bash
                    set -e

                    export PATH=$PATH:${GCLOUD_PATH}

                    echo "Authenticating GCP..."
                    gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS

                    gcloud config set project ${GCP_PROJECT}

                    gcloud auth configure-docker --quiet

                    echo "Building Docker image..."
                    docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                    echo "Pushing Docker image..."
                    docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                    '''
                }
            }
        }
    }
}