# Running statefulsets, Vault and Service Mesh on Amazon EKS cluster 

Make sure you have AWS access key & secret and aws cli working locally

To bring up the cluster, run the following terraform:
```
pushd eks-terraform
    terraform init
    terraform plan -out infra.pl
    terraform apply infra.pl
popd
```

Then generate the EKS cluster kubectl configuration
```
aws eks update-kubeconfig --name test-eks-cluster
kubectl get nodes
```

To deploy Vault we need to initialise the CA root and create a certificate for vault and store the vault cert + key in a configmap: 
```
pushd ssl 
    sh init_ssl.sh
    kubectl create secret tls vault-tls --cert=certs/vault.pem --key=certs/vault-key.pem
popd
```

Upload the ca cert into a configmap so we can use it for containers that need to talk to vault:
```
kubectl create configmap vault-ca-cert --from-file=vault-ca.pem=ssl/certs/ca.pem
```

Create the default storage class and deploy vault:
```
kubectl apply -f k8s/eks
kubectl apply -f k8s/vault
kubectl rollout status deployments/vault
```

When the rollout finishes, grab the K8S CA cert from the vault container and initialise vault:
```
VAULT_POD_NAME=$(kubectl get pods -l 'app=vault' -o jsonpath='{.items[0].metadata.name}')
kubectl exec -ti $VAULT_POD_NAME cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt > .kube-ca.pem
kubectl port-forward svc/vault 8200 &
make vault-init
export VAULT_CACERT=$PWD/ssl/certs/ca.pem
make vault-login
vault auth list
```

With vault up and running it's time to deploy Mongo:
```
kubectl apply -f k8s/mongo
kubectl rollout status statefulsets/mongo
```


### Service mesh
Use vault to generate certificates and configure LinkerD to use mTLS for pod to pod communication:
```
kubectl apply -f k8s/linkerd
kubectl apply -f k8s/echo-server
kubectl apply -f k8s/echo-client

kubectl rollout status deployments/echo-server
kubectl rollout status deployments/echo-client

CLIENT_POD_NAME=$(kubectl get pods -l 'app=echo-client' -o jsonpath='{.items[0].metadata.name}')
kubectl exec -ti $CLIENT_POD_NAME -c linkerd sh
curl -x http://localhost:4140 http://echo-server/
```

NB: After a vault restart it needs to be unsealed:
```
make vault-unseal
```
