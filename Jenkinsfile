pipeline {
  agent none
  stages {
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
            sh 'pytest'
          }
        }
        stage('Build RHEL7 Python 2.7') {
          agent {
            node {
              label 'python'
            }
          }
          steps {
            echo "Installing Insights..."
            sh 'pip install --user -e .'
            echo "Testing with Pytest..."
            sh 'pytest'
            echo "Testing with flake8..."   
            sh 'flake8'
            echo "Building Docs..."
            sh 'sphinx-build -W -b html -qa -E docs docs/_build/html'
          }
        }
        stage('Build RHEL7 Python 3.6') {
          agent {
            node {
              label 'python3'
            }
          }
          steps {
            echo "Installing Insights..."
            sh '/bin/python36 -m pip install --user -e .'
            echo "Testing with Pytest..."
            sh '/bin/python36 -m pytest'
            echo "Testing with flake8..."   
            sh '/bin/python36 -m flake8'
          }
        }
      }
    }
  }
}
