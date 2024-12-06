This is the application to be used for ISCS 30.23. It is a Django app that uses MySQL as
its database. Owing to this, the steps taken to deploy to kubernetes can be found below.

# Containers

Docker was used in order to containerize the application: the first step in deploying to
kubernetes. A Dockerfile is created, which tells docker how the container should be
created imperatively, from dependencies to which port to expose (For this application, the
port is 8080). The docker container is then pushed to Dockerhub, which kubernetes uses in
order to create its pods.

Note that owing to Kubernetes Architecture, Django must be configured to accept MySQL. One
can turn to relevant documentation, however, the important note is that an IP address is
necessary for Django to make use of a MySQL server. As such, another pod to be deployed
should be a MySQL container, which can be pulled from Dockerhub as well.

In addition, the main docker container was built on a linux device. This matters because
Docker images can only run in the operating system that they were built on. Windows and
MacOS users must build their own docker containers in order to meaningfully test any
changes they may have.

# Kubernetes

For this project, the group relies on Google Cloud to host the Kubenetes Architecture.
Kubernetes, at its core, is a way to create scalable "servers" on the internet. Its main
strengths lie in its declarative nature, wherein one can write exactly how a pod should be
deployed, known as a manifest.

For this project, all manifests are held in the 'kubernetes-manifests/' folder.

# lazapee-manifest

WIP

# mySQL-manifest

WIP

# lazapee-service

WIP
