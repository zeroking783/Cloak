pipeline {
    agent any

    stages {
        stage('My-pipeline') {
            steps {
                echo '========start deploy to dev server========'
            }
        }

        stage('delete last docker-compose') {
            steps {
                echo '========start delete last docker-compose========'
                sh 'docker-compose down -v'
            }
        }

        stage('build docker-compose') {
            steps {
                echo '========start build docker-compose========'
                sh 'cp /home/Project/Cloak_secrets/crontab /home/Project/Cloak/daily'
                sh 'docker-compose build'
            }
        }

        stage('up docker-compose') {
            steps {
                echo '========up docker-compose========'
                sh 'docker-compose --env-file /home/Project/Cloak_secrets/.env up -d'
            }
        }
    }
}