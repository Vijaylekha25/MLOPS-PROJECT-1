pipline{
    agent any

    stages{
        stages("Cloning Github repo to Jenkins"){
            step{
                script{
                    echo 'Cloning Github repo to Jenkins...........'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Vijaylekha25/MLOPS-PROJECT-1']])
                }
            }
        }
    }
}