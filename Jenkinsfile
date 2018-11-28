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
                pip install "pycparser<=2.18"
                pip install "pyOpenSSL<=17.5.0"
                pip install -e .[linting]
                flake8
            """
            s3Upload (
              consoleLogLevel: 'INFO',
              dontWaitForConcurrentBuildCompletion: false,
              entries: [[
                bucket: 'insights-core-jenkins-reports',
                managedArtifacts: true,
                selectedRegion: 'us-east-1',
                sourceFile: '**/test-reports/*.html']],
              profileName: 'Report Bucket')
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
            publishHTML (target: [
              allowMissing: false,
              alwaysLinkToLastBuild: false,
              keepAll: true,
              reportDir: 'test-reports',
              reportFiles: 'py27-report.html',
              reportName: 'Python 2.7 Test Report'
            ])
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
            publishHTML (target: [
              allowMissing: false,
              alwaysLinkToLastBuild: false,
              keepAll: true,
              reportDir: 'test-reports',
              reportFiles: 'py3-report.html',
              reportName: 'Python 3 Test Report'
            ])
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
          label 'python'
        }
      }
      steps {
        echo "Building Docs..."
        sh """
            virtualenv .docenv
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
}
