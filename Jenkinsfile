@Library('fh-pipeline-library')_

pipeline {
  agent none
  stages {
    stage('Trust') {
      steps {
        enforceTrustedApproval('RedHatInsights')
      }
    }
    stage('Build and Test Insights Core') {
      parallel {
        stage('Build RHEL6') {
          agent {
            node {
              label 'python26'
            }
          }
          steps {
            echo "Testing with Pytest..."
            sh """
                virtualenv .testenv
                source .testenv/bin/activate
                pip install "idna<=2.7"
                pip install "pycparser<=2.18"
                pip install "pyOpenSSL<=17.5.0"
                pip install -e .[testing]
                pip install "pytest-html==1.13.0"
                pytest --html=test-reports/py26-report.html --self-contained-html
            """
            echo "Testing with Linter..."
            sh """
                virtualenv .lintenv
                source .lintenv/bin/activate
                pip install "idna<=2.7"
                pip install "pycparser<=2.18"
                pip install "pyOpenSSL<=17.5.0"
                pip install -e .[linting]
                flake8
            """
            withAWS(credentials:'bucket_access', region:'us-east-1') {
              s3Upload (
                bucket:"insights-core-jenkins-reports",
                path:"${env.BRANCH_NAME}-${BUILD_ID}/",
                includePathPattern:'**/*.html',
                workingDir:'test-reports',
                metadatas:[
                  "Change_Author:${env.CHANGE_AUTHOR}",
                  "Change_Author_Email:${env.CHANGE_AUTHOR_EMAIL}"
               ]
              )
            }
          }
        }
        stage('Build RHEL7 Python 2.7') {
          agent {
            node {
              label 'python'
            }
          }
          steps {
            echo "Testing with Pytest..."
            sh """
                virtualenv .testenv
                source .testenv/bin/activate
                pip install -e .[testing]
                pip install "pytest-html==1.19.0"
                pytest --html=test-reports/py27-report.html --self-contained-html
            """
            echo "Testing with Linter..."
            sh """
                virtualenv .lintenv
                source .lintenv/bin/activate
                pip install -e .[linting]
                flake8
            """
            withAWS(credentials:'bucket_access', region:'us-east-1') {
              s3Upload (
                bucket:"insights-core-jenkins-reports",
                path:"${env.BRANCH_NAME}-${BUILD_ID}/",
                includePathPattern:'**/*.html',
                workingDir:'test-reports',
                metadatas:[
                  "Change_Author:${env.CHANGE_AUTHOR}",
                  "Change_Author_Email:${env.CHANGE_AUTHOR_EMAIL}"
               ]
              )
            }
          }
        }
        stage('Build RHEL7 Python 3.6') {
          agent {
            node {
              label 'python3'
            }
          }
          steps {
            echo "Testing with Pytest..."
            sh """
                /bin/python36 -m venv .testenv
                source .testenv/bin/activate
                pip install -e .[testing]
                pip install "pytest-html==1.19.0"
                pytest --html=test-reports/py3-report.html --self-contained-html
            """
            echo "Testing with Linter..."
            sh """
                /bin/python36 -m venv .lintenv
                source .lintenv/bin/activate
                pip install -e .[linting]
                flake8
            """
            withAWS(credentials:'bucket_access', region:'us-east-1') {
              s3Upload (
                bucket:"insights-core-jenkins-reports",
                path:"${env.BRANCH_NAME}-${BUILD_ID}/",
                includePathPattern:'**/*.html',
                workingDir:'test-reports',
                metadatas:[
                  "Change_Author:${env.CHANGE_AUTHOR}",
                  "Change_Author_Email:${env.CHANGE_AUTHOR_EMAIL}"
               ]
              )
            }
          }
        }
      }
    }
    stage('Nofity Github - Code Check Passed') {
      steps {
        githubNotify description: 'Code Checks Passed', status: 'SUCCESS'
      }
    }
    stage('Test Docs') {
      agent {
        node {
          label 'python3'
        }
      }
      steps {
        echo "Building Docs..."
        sh """
            /bin/python36 -m venv .docenv
            source .docenv/bin/activate
            pip install -e .[docs]
            sphinx-build -W -b html -qa -E docs docs/_build/html
        """
      } 
    }
    stage('Nofity Github - Docs Check Passed') {
      steps {
        githubNotify description: 'Code Checks and Docs Generation Passed', status: 'SUCCESS'
      }
    }
  }
  post {
    always {
      pullRequest.comment """
                          Jenkins reports located at:
                          https://insights-core-jenkins-reports.s3.amazonaws.com/${env.BRANCH_NAME}-${env.BUILD_ID}/py26-report.html
                          https://insights-core-jenkins-reports.s3.amazonaws.com/${env.BRANCH_NAME}-${env.BUILD_ID}/py27-report.html
                          https://insights-core-jenkins-reports.s3.amazonaws.com/${env.BRANCH_NAME}-${env.BUILD_ID}/py3-report.html
                          """
    }
  }
}
