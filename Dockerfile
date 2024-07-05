FROM registry.access.redhat.com/ubi8/ubi-minimal:latest
RUN microdnf update -y && microdnf -y install which procps-ng git libffi-devel file xz bzip2 tar zip python3.11 python3.11-pip && microdnf clean all
RUN python3 -m pip install --no-cache-dir --upgrade pip
COPY . /src
RUN python3 -m pip install --no-cache-dir /src
