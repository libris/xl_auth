#!/usr/bin/env groovy

//noinspection GroovyAssignabilityCheck
pipeline {
    agent any
    stages {
        stage('Set Build Variables') {
            steps {
                script {

                    def getProjectVersion = { ->
                        return sh(
                            returnStdout: true,
                            script: 'echo $(node -e "console.log(require(\'./package.json\').version)")'
                        ).replace('\n', '')
                    }

                    def getBranchTypeAndName = { String fullBranchName ->

                        if (fullBranchName in ['develop', 'master']) {
                            return [fullBranchName, fullBranchName]
                        }

                        if (fullBranchName.matches(/(feature|bugfix)\/[.\d\-\w]+$/)) {
                            return [fullBranchName.split('/')[0],
                                    fullBranchName.split('/')[1].toLowerCase().replaceAll(/[^.\da-z]/, '.')]
                        }

                        if (fullBranchName.matches(/hotfix\/\d+(\.\d+){1,2}p\d+$/)) {
                            return fullBranchName.split('/') as List
                        }

                        if (fullBranchName.matches(/release\/\d+(\.\d+){1,2}([ab]\d+)?$/)) {
                            return fullBranchName.split('/') as List
                        }

                        throw new AssertionError("Enforcing Gitflow Workflow and SemVer. Ha!")
                    }

                    def getBuildVersion = { String fullBranchName, buildNumber ->
                        String projectVersion = getProjectVersion()
                        def branchTypeAndName = getBranchTypeAndName(fullBranchName)

                        switch (branchTypeAndName[0]) {
                            case 'master':
                                return projectVersion
                            case 'hotfix':
                                return "${branchTypeAndName[1]}-rc.${buildNumber}"
                            case 'develop':
                                return "${projectVersion}+develop.dev${buildNumber}"
                            case 'feature':
                                return "${projectVersion}+feature.${branchTypeAndName[1]}.dev${buildNumber}"
                            case 'bugfix':
                                return "${projectVersion}+bugfix.${branchTypeAndName[1]}.dev${buildNumber}"
                            case 'release':
                                assert branchTypeAndName[1] == projectVersion
                                return "${projectVersion}-rc.${buildNumber}"
                            default:
                                throw new AssertionError("Oops, Mats messed up! :(")
                        }
                    }

                    def getBuildType = { String fullBranchName ->
                        switch (getBranchTypeAndName(fullBranchName)[0]) {
                            case 'master':
                                return 'latest'
                            case 'release':
                                return 'next'
                            default:
                                return 'develop'
                        }
                    }

                    env.BUILD_VERSION = getBuildVersion(BRANCH_NAME as String, BUILD_NUMBER)
                    env.DOCKER_TAG = env.BUILD_VERSION.replace('+', '_')
                    env.BUILD_TYPE = getBuildType(BRANCH_NAME as String)
                    env.DOCKER_TAG_ALIAS = env.BUILD_TYPE != 'develop' ? env.BUILD_TYPE : null;

                    if (env.BUILD_TYPE == 'next') {
                        sh 'npm version $BUILD_VERSION'
                    }

                    stash 'pre_install_git_checkout'
                }
            }
        }
        stage('Install Dependencies') {
            steps {
                //noinspection GroovyAssignabilityCheck
                parallel(
                    'Npm install + build assets': {
                        sh 'npm install'
                        sh 'npm run build'
                    },
                    'Create virtualenv (py27)': {
                        sh 'mkdir -p /tmp/xl_auth'
                        sh 'scl enable python27 "virtualenv /tmp/xl_auth/py27venv"'
                        sh 'scl enable python27 "/tmp/xl_auth/py27venv/bin/pip install -r requirements/dev.txt"'
                    },
                    'Create virtualenv (py35)': {
                        sh 'mkdir -p /tmp/xl_auth'
                        sh 'scl enable rh-python35 "virtualenv /tmp/xl_auth/py35venv"'
                        sh 'scl enable rh-python35 "/tmp/xl_auth/py35venv/bin/pip install -r requirements/dev.txt"'
                    }
                )
            }
        }
        stage('Run Tests') {
            environment {
                FLASK_APP = 'autoapp.py'
            }
            steps {
                //noinspection GroovyAssignabilityCheck
                parallel(
                    'ESLint': {
                        sh 'npm run lint'
                    },
                    'flake8 (py27,py35)': {
                        script {
                            try {
                                sh 'scl enable python27 ". /tmp/xl_auth/py27venv/bin/activate && \
flask lint" | tee flake8.log && ( exit $PIPESTATUS )'
                                sh 'scl enable rh-python35 ". /tmp/xl_auth/py35venv/bin/activate && \
flask lint" | tee flake8.log && ( exit $PIPESTATUS )'
                            }
                            catch (Throwable e) {
                                sh 'scl enable python27 ". /tmp/xl_auth/py27venv/bin/activate && \
flake8_junit flake8.log flake8-junit.xml"'
                                junit 'flake8-junit.xml'
                                throw e
                            }
                        }
                    },
                    'pytest (py27)': {
                        script {
                            try {
                                sh 'scl enable python27 ". /tmp/xl_auth/py27venv/bin/activate && \
flask test --junit-xml=py27test-junit.xml"'
                            }
                            finally {
                                junit 'py27test-junit.xml'
                            }
                        }
                    },
                    'pytest (py35)': {
                        script {
                            try {
                                sh 'scl enable rh-python35 ". /tmp/xl_auth/py35venv/bin/activate && \
flask test --junit-xml=py35test-junit.xml"'
                            }
                            finally {
                                junit 'py35test-junit.xml'
                            }
                        }
                    }
                )
            }
        }
        stage('Build and Publish') {
            when {
                expression { env.BUILD_TYPE in ['next', 'latest'] }
            }
            environment {
                DOCKER_LOGIN = credentials('mblomdahl_docker')
            }
            steps {
                dir('_docker-build') {
                    unstash 'pre_install_git_checkout'
                    sh 'docker login -u $DOCKER_LOGIN_USR -p $DOCKER_LOGIN_PSW'
                    sh 'docker build -t mblomdahl/xl_auth:$DOCKER_TAG .'
                    sh 'docker save mblomdahl/xl_auth:$DOCKER_TAG | gzip - > xl_auth-$BUILD_VERSION.docker.tar.gz'
                    archiveArtifacts "mapbox-gl-circle-${BUILD_VERSION}.docker.tar.gz"

                    sh 'docker push mblomdahl/xl_auth:$DOCKER_TAG'
                    sh 'docker tag mblomdahl/xl_auth:$DOCKER_TAG mblomdahl/xl_auth:$DOCKER_TAG_ALIAS'
                    sh 'docker push mblomdahl/xl_auth:$DOCKER_TAG_ALIAS'
                    sh 'docker logout'
                    deleteDir()
                }
            }
        }
    }
    post {
        always {
            sh 'rm -rf /tmp/xl_auth'
            deleteDir()
        }
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed :('
        }
        changed {
            echo 'Things are different...'
        }
    }
}
