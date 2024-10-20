pipeline {
    agent any

    stages {
        stage('My-pipeline') {
            steps {
                echo '========start deploy to dev server========'
            }
        }

        stage('Checkout') {
            steps {
                script {
                    def workspaceDir = '/home/Project/Cloak'
                    sh "mkdir -p ${workspaceDir}"
                    dir("${workspaceDir}") {
                        checkout scm
                    }
                }
            }
        }

        stage('Delete Last Docker Compose') {
            steps {
                script {
                    dir('/home/Project/Cloak') {  // Добавляем dir
                        echo '========start delete last docker-compose========'
                        sh 'docker-compose --env-file /home/Project/Cloak_secrets/.env down -v'
                    }
                }
            }
        }

        stage('Build Docker Compose') {
            steps {
                script {
                    dir('/home/Project/Cloak') {  // Добавляем dir
                        echo '========start build docker-compose========'
                        sh 'cp /home/Project/Cloak_secrets/crontab /home/Project/Cloak/daily'
                        sh 'docker-compose build'
                    }
                }
            }
        }

        stage('Up Docker Compose') {
            steps {
                script {
                    dir('/home/Project/Cloak') {  // Добавляем dir
                        echo '========up docker-compose========'
                        sh 'docker-compose --env-file /home/Project/Cloak_secrets/.env up -d'
                    }
                }
            }
        }
    }
}
