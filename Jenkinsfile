pipeline {
  agent any
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
docker build --no-cache -t resolver:${env.BUILD_ID} .'''
      }
    }

    stage('Deploy') {
      steps {
        sh '''id
hostname
cd /data/code/resolver
docker run -it -d -p 9936:80 --name resolver resolver:${env.BUILD_ID}'''
      }
    }

  }
}