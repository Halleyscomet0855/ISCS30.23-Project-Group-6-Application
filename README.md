This is the application to be used for ISCS 30.23. It is a Django app that uses MySQL as
its database. Owing to this, the steps taken to deploy to kubernetes can be found below.

# Dependencies

The following must be installed to deploy this app:

- docker
- gcloud
- kubectl

Please follow the instructions for your operating system.

# Pre-deployment

Before everything, first create your cluster:

```
gcloud container clusters create {{cluster name}} --num-nodes 1 --zone asia-east1
--enable-ip-alias
```

Each node will take up ~300GB, so make sure your account has enough space!

Now, do the following:

1. In the google cloud console, search for IP Addresses, and click on the one under VPC
   Network.
2. Click "Reserve a Static Address." Input a name for your address (ex. lazapee-ip), and
   change the area to asia-west1. Click reserve afterwards.
3. Copy-Paste the resulting address. Go to service-lazapee.yaml.
4. Uncomment the loadBalancerIP line. Paste the IP address there.
5. Head to your django settings' file. Add your IP address to the allowed_hosts list.

This is done in order to allow for the IP to access the django app. Without this, you will
get an error as django will block any IP that is not in the allowed_hosts list from
accessing the app.

Alternatively, you can also skip reserving a static address. Deploy the service-lazapee
file first (See [# Deployment]), then run 'kubectl get services'. You may have to wait a
little bit until the column called External IP is filled in with an IP. Copy-paste this IP
to the allowed_hosts list.

Now that that's done, run the following command to build the image:

```
docker build -t {DockerhubUsername}/lazapee:0.1 .
```

This will build the docker image based off of the Dockerfile (which is an imperative list
of commands that set up the image). Afterwards, push the image:

```
docker push -t {DockerhubUsername}/lazapee:0.1
```

Finally, edit the lazapee-deployment manifest such that beside the container tag, it has your specific
image. Currently it's using halleyscomet0855/lazapee:1.0, but you should change it to your
own image. Kubernetes will be pulling this image from Dockerhub, so make sure this is
changed!

Before we continue, let's discuss first each manifest in order to understand what we're
working with here:

# lazapee-manifest

In this Kubernetes manifest it defines a Deployment resource, which ensures the continuous running and management of a containerized application. The Deployment of the application named Lazapee, is specified under the metadata section. It will create and maintain three replicas of a Pod, as indicated in the replicas field of the spec section. The Deployment uses a selector to match Pods with the label app: Lazapee, ensuring it manages only those Pods.

Each Pod is defined by the template field, which includes metadata that labels the Pods with "app: Lazapee" for identification. Inside each Pod, there is a single container named my-container, which uses the image "halleyscomet0855/lazapee". The container exposes port 8080 for the application to listen on. Kubernetes will ensure that three replicas of this Pod are always running, and it will replace any failed Pods to maintain the desired state.

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

```python
DATABASES = {
    "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "lazapeedata",
    "USER": "root",
    "PASSWORD": "admin",
    "HOST": "localhost",
    }
}
```

This, however, will not work: because MySQL is not local at all. Instead, you need to
specify the host and the port:

```python
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
```

This way, Django can interface with the MySQL pod.

(You may notice that the password is put there for everyone to see. You really shouldn't
do that! You can use Kubernetes' Secrets function, but that's a bit out of scope for this
demonstration.)

# lazapee-service

Shown below is the contents of service-lazapee.yaml.

```kubernetes
apiVersion: v1
kind: Service
metadata:
  name: service-lazapee
spec:
  type: LoadBalancer
  # loadBalancerIP: xx.xx.xxx
  selector:
    app: lazapee
  ports:
    - name: service-lazapee
      port: 8080
      targetPort: 8080
```

Services, as mentioned before, allow pods to interface with each other.
LoadBalancer allows external traffic to be routed to the targetPort. This is in contrast
to a ClusterIP, which only allows pod-to-pod traffic.

# Deployment

After the cluster has been set up, you can use kubectl to apply your manifests:

```
kubectl apply -f {{manifest name}}
```

This should deploy the following:

- a MySQL instance;
- The lazapee django application;
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

```
kubectl exec -it {pod-name} -- /bin/bash
mysql -u root -p
```

From here, create a database called 'lazapeedata'. Exit afterwards.

Afterwards, migrate the database:

```
kubectl exec {application-pod-name} -- python manage.py migrate
```

This should get the database all setup.

2. Autoscaling

The lazapee-manifest defines three pods to be created. In order to autoscale, do the
following:

a. change spec.replicas to 1 instead of 3 in lazapee-deployment.yaml.

b. run the following command:

```
"kubectl autoscale deployment web --max 4 --min 1 --cpu-percent 1"
```

This will create a HorizontalPodAutoscaler object which will create and destroy pods based
on how much traffic there is.
