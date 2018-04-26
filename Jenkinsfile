pipeline {
  agent none
  stages {
    stage('Build RHEL6') {
      agent {
        node {
          label 'python26'
        }
      }
      steps {
        sh """
           virtualenv .
           source bin/activate
           pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'importlib' 'Jinja2==2.9.6'
           pytest
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
        sh """
           virtualenv .
           source bin/activate
           pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'importlib' 'Jinja2==2.9.6'
           pytest
           flake8
        """
      }
    }
    stage('Build RHEL7 Python 3.6') {
      agent {
        node {
          label 'python36'
        }
      }
      steps {
        sh """
           virtualenv -p python36 .
           source bin/activate
           pip install 'flake8==3.3.0' 'coverage==4.3.4' 'pytest==3.0.6' 'pytest-cov==2.4.0' 'futures==3.0.5' 'requests==2.13.0' 'six' 'wheel' 'pyyaml>=3.10,<=3.12' 'pyOpenSSL' 'Jinja2==2.9.6'
           pytest
           flake8
        """
      }
    }
  }
}
