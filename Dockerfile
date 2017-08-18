FROM docker.io/projectatomic/atomicapp
RUN yum install -y python-devel python-pip file zip tar gzip gcc && yum clean all
COPY . /src
RUN pip install /src
