FROM centos:7
RUN yum install -y python-devel file zip gcc libffi-devel && yum clean all
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py
COPY . /src
RUN pip install /src
