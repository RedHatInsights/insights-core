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
            echo "Building environment..."
            sh """
               virtualenv .
               source bin/activate
               pip install 'flake8==3.3.0'
               """
            echo "Testing with Pytest..."
            sh 'bin/pytest'
            echo "Testing Syntax..."   
            sh 'bin/flake8 --config=.flake8'
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
            echo "Testing Syntax..."   
            sh 'flake8 --config=.flake8'
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
            sh 'pip install --user -e .'
            echo "Testing with Pytest..."
            sh 'pytest'
            echo "Testing Syntax..."   
            sh 'flake8 -config=.flake8'
          }
        }
      }
    }
  }
}
