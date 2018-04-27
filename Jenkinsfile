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
               pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'importlib' 'Jinja2==2.9.6'
               """
            echo "Testing with Pytest..."
            sh 'source bin/activate && pytest'
            echo "Testing Syntax..."   
            sh 'source bin/activate && flake8'
            echo "Building Docs..."
            sh 'source bin/activate && sphinx-build -W -b html -qa -E docs docs/_build/html'
          }
        }
        stage('Build RHEL7 Python 2.7') {
          agent {
            node {
              label 'python'
            }
          }
          steps {
            echo "Building environment..."
            sh """
               virtualenv .
               source bin/activate
               pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'importlib' 'Jinja2==2.9.6'
               """
            echo "Testing with Pytest..."
            sh 'source bin/activate && pytest'
            echo "Testing Syntax..."   
            sh 'source bin/activate && flake8'
            echo "Building Docs..."
            sh 'source bin/activate && sphinx-build -W -b html -qa -E docs docs/_build/html'
          }
        }
      }
    /*    stage('Build RHEL7 Python 3.6') {
          agent {
            node {
              label 'python3'
            }
          }
          steps {
            echo "Building environment..."
            sh """
               virtualenv -p python36 .
               source bin/activate
               pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'Jinja2==2.9.6'
               """
            echo "Testing with Pytest..."
            sh 'source bin/activate && pytest'
            echo "Testing Syntax..."   
            sh 'source bin/activate && flake8'
            echo "Building Docs..."
            sh 'source bin/activate && sphinx-build -W -b html -qa -E docs docs/_build/html'
          }
    } */
  }
}
}
