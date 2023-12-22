
# How to delete a pod
k delete pod -n data-tooling colossal-ai-temp-a10g

kubectl apply -f ./local/k8s/experiment_pod.yaml 


k get pod -n data-tooling | grep colo
k describe pod -n data-tooling colossal-ai-temp-6577c8c-hllkj | grep Image


# Here is the pace to update the Doc to latest version
https://github.com/Ubix/ubix-deployments/blob/main/backoffice/data-tooling/colossal-ai/dev/values.yaml

https://github.com/Ubix/colossalai/actions
tags: colossalai-469,latest

# Manually start a tgi pod
k apply -f  ./local/k8s/experiment_tgi.yaml -n data-tooling

# Log in to one of the backend API pod
kubectl exec -ti -n data-tooling svc/colossal-ai-temp -- /bin/bash

# Check how many node we have
If we have several new pod was create, we need to take care if it's created by mistake, especially for GPU pod
kubectl get nodes --sort-by=.metadata.creationTimestamp


# Check if the node has GPU


# Check the current pod version
k describe pod  -n data-tooling colossal-ai-temp  | grep colo


# Edit the pod version
https://github.com/Ubix/ubix-deployments/blob/main/backoffice/data-tooling/colossal-ai/dev/values.yaml
kubectl set image -n data-tooling deployment/colossal-ai colossal-ai=882490700787.dkr.ecr.us-east-1.amazonaws.com/colossalai:645
kubectl scale deployment -n data-tooling  colossal-ai --replicas=0
kubectl scale deployment -n data-tooling  colossal-ai --replicas=1