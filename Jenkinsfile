pipline{
    agent any

    stages{
        stage("Cloning Github repo to Jenkins"){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins.......................'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'GitHub-Token', url: 'https://github.com/Vijaylekha25/MLOPS-PROJECT-1.git']])
                }
            }
        }
    }
}