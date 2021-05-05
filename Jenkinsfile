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
            echo "Setup testing environment..."
            sh """
                yum install -y https://archives.fedoraproject.org/pub/archive/epel/6/x86_64/epel-release-6-8.noarch.rpm &&
                yum install -y python-pip.noarch python-virtualenv.noarch &&
                mkdir pip_packages && cd pip_packages && xargs -n 1 curl -L -O < ../insights-core/requirements_with_links.txt && cd ../ &&
                cat requirements_with_links.txt | awk -F '/' '{print $8}' | sed 's/.tar.gz//g;s/.zip//g;s/-\\([0-9]\\)/==\\1/g' > requirements_without_links.txt &&
                virtualenv insights-core/venv &&
                source insights-core/venv/bin/activate &&
                pip install pip_packages/setuptools* &&
                pip install pip_packages/{pbr*,pytest-runner*} &&
                pip install -v -r requirements_without_links.txt --no-index --find-links=./pip_packages/;
            """
            echo "Testing with Pytest..."
            sh """
                source insights-core/venv/bin/activate
                pytest
            """

            echo "Testing with Linter..."
            sh """
                source insights-core/venv/bin/activate
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
