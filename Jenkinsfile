def agentLabel
if ( env.BRANCH_NAME == 'master') {
  agentLabel = 'prod'
} else if ( env.BRANCH_NAME == 'release') {
  agentLabel = 'stg'
} else {
  agentLabel = 'dev'
}

pipeline {
  agent {
    label agentLabel
  }
  stages {
    stage('Source Code') {
      steps {
        sh '''cd /data/code/resolver
              git branch
              hostname
              git pull'''
      }
    }

    stage('Build') {
      steps {
        sh '''cd /data/code/resolver
              docker build --no-cache -t resolver:${env.BUILD_NUMBER} .'''
      }
    }

    stage('Deploy') {
      when {
        expression {
          env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'release'
        }
      }
      steps {
        sh '''id
              hostname
              cd /data/code/resolver
              docker run -it -d -p 9936:80 --name resolver resolver:${env.BUILD_NUMBER}'''
      }
    }

  }
}