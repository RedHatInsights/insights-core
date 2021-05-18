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
                pip install /pip_packages/pip-9.0.3-py2.py3-none-any.whl
                pip install -r /var/lib/jenkins/ci_requirements.txt -f /pip_packages
                pip install -e .[testing] -f /pip_packages
                pytest
            """
            echo "Testing with Linter..."
            sh """
                virtualenv .lintenv
                source .lintenv/bin/activate
                pip install /pip_packages/pip-9.0.3-py2.py3-none-any.whl
                pip install -r /var/lib/jenkins/ci_requirements.txt -f /pip_packages
                pip install -e .[linting] -f /pip_packages
                flake8
            """
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
                pytest
            """
            echo "Testing with Linter..."
            sh """
                virtualenv .lintenv
                source .lintenv/bin/activate
                pip install -e .[linting]
                flake8
            """
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
                /bin/python3 -m venv .testenv
                source .testenv/bin/activate
                pip install -e .[testing]
                pytest
            """
            echo "Testing with Linter..."
            sh """
                /bin/python3 -m venv .lintenv
                source .lintenv/bin/activate
                pip install -e .[linting]
                flake8
            """
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
            /bin/python3 -m venv .docenv
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
