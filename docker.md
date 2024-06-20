# Mailman3 Exporter for Prometheus (docker)

> Don't forget `--web.listen`

## Build image

```shell
docker build -t {image_name}:{version} .
```

## Run

```shell
docker run --rm -p 9934:9934 --name mailman3_exporter {image_name}:{version} --mailman.user {mailman_user} --mailman.password {mailman_password} --mailman.address {mailman_address} --web.listen 0.0.0.0:9934
```

The metrics are accessible at `http://127.0.0.1:9934`

## Publish image

### Tag version

```shell
docker tag {image_name}:{version} {docker_username}/{image_name}:{version}
```

### Push image

```shell
docker push {docker_username}/{image_name}:{version}
```

## k8s

```yml
# Mailman 3 prometheus exporter
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mailman-prometheus-exporter-deployment
  labels:
    app: mailman-prometheus-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mailman-prometheus-exporter
  template:
    metadata:
      labels:
        app: mailman-prometheus-exporter
    spec:
      containers:
        - name: mailman-prometheus-exporter
          image: docker.io/{docker_username}/{image_name}:{version}
          resources:
            limits:
              memory: "2Gi"
              cpu: "2"
          args: ["--mailman.user", "$(MAILMAN_USER)", "--mailman.password", "$(MAILMAN_PASSWORD)", "--mailman.address", "http://mailman-core:8001", "--web.listen", "0.0.0.0:9934"]
          ports:
            - containerPort: 9934
              name: metrics
          env:
            - name: MAILMAN_USER
              valueFrom:
                secretKeyRef:
                  name: mailman-core-secret
                  key: mailman-rest-user
            - name: MAILMAN_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mailman-core-secret
                  key: mailman-rest-password
---
# Mailman 3 prometheus exporter service
apiVersion: v1
kind: Service
metadata:
  name: mailman-prometheus-exporter
  namespace: mailing-list
spec:
  type: NodePort
  ports:
    - name: metrics
      port: 9934
      targetPort: 9934
      nodePort: 30705
  selector:
    app: mailman-prometheus-exporter

```