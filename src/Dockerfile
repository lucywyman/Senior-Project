FROM centos:7

MAINTAINER Justin Wolford, wolfordj@osuosl.org


ENV PASSWORD polymatheia
ENV HOST postgis
ENV USER polymatheia
ENV NAME  polymatheia
ENV ENVIRONMENTCONFIG True
ENV ENGINE django.contrib.gis.db.backends.postgis

EXPOSE 8000

RUN yum install -y python-devel python-setuptools postgresql-devel gcc curl

# Install the ius repository to install GDAL
RUN curl http://dl.iuscommunity.org/pub/ius/stable/CentOS/7/x86_64/ius-release-1.0-13.ius.centos7.noarch.rpm > /tmp/ius.rpm
RUN yum install -y /tmp/ius.rpm
RUN yum install -y gdal

RUN easy_install pip

WORKDIR /opt/polymatheia

COPY . /opt/polymatheia
RUN pip install .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
