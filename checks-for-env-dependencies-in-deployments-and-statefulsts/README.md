# Webhook to automatically check if the env specified on the deloyment to be applied have their configmaps or secrets already in the cluster
## This utilises k8s MutatingWebhookConfiguration which listens or create or update operations on deployments and statefulsets and sends the information to be checked via webhook to the flask application to check if the dependecies are met.
# Deploy cert-manager using helm

```shell
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.3 \
  --set installCRDs=true
  --set prometheus.enabled=false \  # Example: disabling prometheus using a Helm parameter
  --set webhook.timeoutSeconds=4   # Example: changing the webhook timeout using a Helm parameter

```
- Note : Dont forget to set up Issuers or Cluster issuers
# Set up the certificate for our flask deployment
```commandline
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: selfsigned-issuer
  namespace: cert-notificiations
spec:
  selfSigned: {}

---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: my-selfsigned-ca
  namespace: cert-notificiations
spec:
  isCA: false
  dnsNames:
    - notifications.cert-notificiations.svc
    - notifications
    - notifications.cert-notificiations
  secretName: my-secret
  privateKey:
    algorithm: ECDSA
    size: 256
  issuerRef:
    name: selfsigned-issuer
    kind: Issuer
    group: cert-manager.io
```
# Build the image and push it into your docker registry

```docker
docker build -t <name of registry>/<image name>:<image tag> .
docker push <name of registry>/<image name>:<image tag>
```

# Make changes to the deployment yaml
```shell
- Edit the k8s/deployment.yaml and set image: <name of registry>/<image name>:<image tag> , set env JIRA_SERVER,JIRA_USERNAME,JIRA_API_TOKEN,JIRA_PROJECT_KEY
  and secretName: <name of the secret the you created earlier>
```
# Make changes to the MutatingWebhookConfiguration

- Get the ca.crt data from the certificate tls you created earlier and replace caBundle: in the mutation.yaml

# Finishing off

- Apply everything in the k8s folder after changes
```shell
kubectl apply -f k8s/
```