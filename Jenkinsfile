pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "mlops-new-495606"
        GCP_REGION = "us-central1"
        SERVICE_NAME = "ml-project"
        SERVICE_ACCOUNT = "mlops-project-1@mlops-new-495606.iam.gserviceaccount.com"
        IMAGE_NAME = "gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:latest"
    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins...............'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'Github-Token', url: 'https://github.com/Vijaylekha25/MLOPS-PROJECT-1.git']])
                }
            }
        }

         stage('Setting up our Virtual Environment and Installing dependancies'){
            steps{
                script{
                    echo 'Setting up our Virtual Environment and Installing dependancies...............'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install gunicorn
                    '''
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR'){
            steps{
                withCredentials([file(credentialsId : 'GCP-KEY' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Building and Pushing Docker Image to GCR.................'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker gcr.io --quiet
                        
                        # Build with detailed output
                        docker build -t ${IMAGE_NAME} .
                        
                        # Verify image created
                        docker images | grep ml-project
                        
                        # Push to GCR
                        docker push ${IMAGE_NAME}
                        
                        echo "✓ Image pushed to GCR: ${IMAGE_NAME}"
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId : 'GCP-KEY' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Deploy to Google Cloud Run.................'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        
                        # Delete old revisions to save space
                        gcloud run revisions list --service=${SERVICE_NAME} --region=${GCP_REGION} --format='value(name)' --limit=10 | tail -n +4 | xargs -I {} gcloud run revisions delete {} --region=${GCP_REGION} --quiet || true
                        
                        # Deploy with optimized parameters
                        gcloud run deploy ${SERVICE_NAME} \
                          --image=${IMAGE_NAME} \
                          --platform=managed \
                          --region=${GCP_REGION} \
                          --allow-unauthenticated \
                          --memory=2Gi \
                          --cpu=1 \
                          --timeout=3600 \
                          --max-instances=10 \
                          --min-instances=1 \
                          --cpu-boost 
                          --session-affinity \
                          --service-account=${SERVICE_ACCOUNT} \
                          --project=${GCP_PROJECT} \
                          --quiet
                        
                        # Get service URL
                        SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT} --format='value(status.url)')
                        echo "✓ Service deployed: ${SERVICE_URL}"
                        echo "✓ Health check: ${SERVICE_URL}/health"
                        '''
                    }
                }
            }
        }

        stage('Verify Deployment'){
            steps{
                withCredentials([file(credentialsId : 'GCP-KEY' , variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                    script{
                        echo 'Verifying deployment.................'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        
                        # Wait for service to be ready
                        echo "Waiting for service to stabilize..."
                        sleep 10
                        
                        # Get service details
                        gcloud run services describe ${SERVICE_NAME} --region=${GCP_REGION} --format='table(
                          status.url,
                          status.conditions[0].type,
                          status.conditions[0].status,
                          metadata.generation
                        )'
                        
                        # Get latest revision
                        gcloud run revisions list --service=${SERVICE_NAME} --region=${GCP_REGION} --limit=1 --format='table(
                          name,
                          status.conditions[0].type,
                          status.conditions[0].status
                        )'
                        
                        echo "✓ Deployment verification complete"
                        '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✓ Pipeline completed successfully!'
        }
        failure {
            echo '✗ Pipeline failed!'
            sh '''
            echo "Checking Cloud Run logs for errors..."
            gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ml-project" \
              --project=${GCP_PROJECT} --limit=20 --format="table(timestamp, textPayload)" || true
            '''
        }
    }
}
