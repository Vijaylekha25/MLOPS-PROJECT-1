pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "mlops-new-495606"
        GCP_REGION = "us-central1"
        SERVICE_NAME = "ml-project"
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
                        
                        docker build -t gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:latest .
                        docker push gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:latest
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
                        
                        gcloud run deploy ${SERVICE_NAME} \
                          --image=gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:latest \
                          --platform=managed \
                          --region=${GCP_REGION} \
                          --allow-unauthenticated \
                          --memory=2Gi \
                          --cpu=1 \
                          --timeout=3600 \
                          --quiet
                        
                        echo "Deployment successful!"
                        gcloud run services describe ${SERVICE_NAME} --platform managed --region ${GCP_REGION}
                        '''
                    }
                }
            }
        }
    }
}
