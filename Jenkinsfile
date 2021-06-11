#!/usr/bin/env groovy

//noinspection GroovyAssignabilityCheck
pipeline {
    agent { label 'build-agent-01' }
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

                        if (fullBranchName.matches(/^(feature|bugfix)\/[.\d\-\w]+$/)) {
                            return [fullBranchName.split('/')[0],
                                    fullBranchName.split('/')[1].toLowerCase().replaceAll(/[^.\da-z]/, '.')]
                        }

                        if (fullBranchName.matches(/^hotfix\/\d+(\.\d+){1,2}p\d+$/)) {
                            return fullBranchName.split('/') as List
                        }

                        if (fullBranchName.matches(/^release\/\d+(\.\d+){1,2}([ab]\d+)?$/)) {
                            return fullBranchName.split('/') as List
                        }

                        if (fullBranchName.matches(/^PR-\d+-?(merge|head)?$/)) {
                            return ['PR', fullBranchName.split('-', 2)[1].replaceAll(/-/, '.')]
                        }

                        error "Enforcing Gitflow Workflow and SemVer on '${fullBranchName}'. Ha!"
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
                            case 'PR':
                                return "${projectVersion}+PR.${branchTypeAndName[1]}.${buildNumber}"
                            default:
                                error "Oops, we messed up! :("
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

                    env.VENV_ROOT = "/tmp/xl_auth/${env.BUILD_VERSION}"
                    sh 'mkdir -p $VENV_ROOT'
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
                    'Create virtualenv (py36)': {
                        sh 'scl enable rh-python36 "virtualenv $VENV_ROOT/py36venv"'
                        sh 'scl enable rh-python36 ". $VENV_ROOT/py36venv/bin/activate && python -m pip install -U pip"'
                        sh 'scl enable rh-python36 "$VENV_ROOT/py36venv/bin/pip --cache-dir ~/.cache/pip36/$EXECUTOR_NUMBER install -r requirements/dev.txt"'
                    }
                )
            }
            post {
                success {
                    sh 'scl enable rh-python36 ". $VENV_ROOT/py36venv/bin/activate && \
FLASK_APP=autoapp.py flask translate"'
                }
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
                    'flake8 (py27,py36)': {
                        script {
                            try {
                                sh 'scl enable rh-python36 ". $VENV_ROOT/py36venv/bin/activate && \
flask lint" | tee flake8.log && ( exit $PIPESTATUS )'
                            }
                            catch (Throwable e) {
                                junit 'flake8-junit.xml'
                                throw e
                            }
                        }
                    },
                    'pytest (py36)': {
                        script {
                            try {
                                sh 'scl enable rh-python36 ". $VENV_ROOT/py36venv/bin/activate && \
flask test --junit-xml=py36test-junit.xml"'
                            }
                            finally {
                                junit 'py36test-junit.xml'
                            }
                        }
                    }
                )
            }
        }
    }
    post {
        always {
            sh 'rm -rf $VENV_ROOT'
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
