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

The mySQL manifest has three sections: the service, the PersistentVolumeClaim, and the
mysql StatefulSet proper. This manifest will deploy one mySQL pod with a ClusterIP
service, alongside a PersistentVolumeClaim. You can consider the PersistentVolumeClaim as
a way to introduce a static directory to store data: normally, data in Kubenetes can
disappear as pods fail and get replaced. The Persistent Volume keeps the data safe, even
if the pods fail.

The ClusterIP service allows MySQL to interface with other pods. Think of it as exposing a
port for access. In this case, it exposes port 3306.

the mySQL pod proper is a StatefulSet, a type of Pod meant to ensure consistency. It
essentially fixes the name of a pod to be "mysql-x", where x is a number from 0 onwards.

## Django and Services

As mentioned prior, Pods can only interface with each other via services. This means that
the Django settings file must be edited. Normally, the django database settings look
something like this:

'''
DATABASES = {
"default": {
"ENGINE": "django.db.backends.mysql",
"NAME": "lazapeedata",
"USER": "root",
"PASSWORD": "admin",
"HOST": "localhost",
}
}
'''

This, however, will not work: because MySQL is not local at all. Instead, you need to
specify the host and the port:
DATABASES = {
"default": {
"ENGINE": "django.db.backends.mysql",
"NAME": "lazapeedata",
"USER": "root",
"PASSWORD": "admin",
"HOST": "mysql",
"PORT": "3306",
}
}

This way, Django can interface with the MySQL pod.

(You may notice that the password is put there for everyone to see. You really shouldn't
do that! You can use Kubernetes' Secrets function, but that's a bit out of scope for this
demonstration.)

# lazapee-service

WIP

# deployment

After all manifests are written, the following command must be run:
'''
gcloud container clusters create {{cluster name}} --num-nodes 1 --zone asia-west1
--enable-ip-alias
'''

This will create the cluster in the console. Afterwards, you can use kubectl to apply your
manifests:

'''
kubectl apply -f {{manifest name}}
'''

This should deploy the following:

- a MySQL instance;
- The lazapee django application; (CAUTION: read Post-Deployment before deploying this!)
- a lazapee LoadBalancer service;
- a MySQL ClusterIP instance;
- a PersistentVolumeClaim named "mysql-pv-claim"

# Post-Deployment

There are some minor details we may have to handle first, before anything happens.

1. Create a database.
   NOTE: this must be done before deploying the lazapee instance, or else it is possible that
   the lazapee deployment will attempt to migrate without any database.

The migrate function of django requires a database to already be present. As such, you
must first enter the mysql pod and interface with it:

'''
kubectl exec -it {pod-name} -- /bin/bash
mysql -u root -p
'''
From here, create a database called 'lazapeedata'. Exit afterwards.

2. Autoscaling

The lazapee-manifest defines only one pod to be created. You can change this and add
autoscaling via the command:
"kubectl autoscale deployment web --max 4 --min 1 --cpu-percent 1"

This will create a HorizontalPodAutoscaler object which will create and destroy pods based
on how much traffic there is.
