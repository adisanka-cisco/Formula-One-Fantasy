# k3s Lab Deployment Notes

These commands are written for the two demo VMs:

```text
app1: 198.18.149.114, real IP 192.168.249.114
app2: 198.18.149.100, real IP 192.168.249.100
```

## 1. Install k3s

On `app1`:

```bash
curl -sfL https://get.k3s.io | sh -s - server --node-name app1
sudo cat /var/lib/rancher/k3s/server/node-token
```

On `app2`, replace `<TOKEN>` with the token from `app1`:

```bash
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.249.114:6443 K3S_TOKEN=<TOKEN> sh -s - agent --node-name app2
```

On `app1`:

```bash
sudo kubectl label node app1 role=formula-primary --overwrite
sudo kubectl label node app2 role=formula-backup --overwrite
sudo kubectl get nodes -o wide
```

## 2. Install CloudNativePG

```bash
kubectl apply --server-side -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.25/releases/cnpg-1.25.0.yaml
kubectl wait --for=condition=Available deployment/cnpg-controller-manager -n cnpg-system --timeout=180s
```

## 3. Build and Import Images

Build from the repository root:

```bash
docker build -t formula-api:latest -f backend/Dockerfile backend
docker build -t formula-ai-assistant:latest -f ai-assistant/Dockerfile ai-assistant
docker build -t formula-worker:latest -f worker/Dockerfile .
docker build -t formula-frontend:latest -f frontend/Dockerfile frontend
```

For k3s/containerd on both nodes, either push these images to a registry or import them into k3s:

```bash
docker save formula-api:latest formula-ai-assistant:latest formula-worker:latest formula-frontend:latest -o formula-images.tar
sudo k3s ctr images import formula-images.tar
```

Repeat the import on `app2` if you do not use a registry.

## 4. Deploy the App

Copy `k8s/base/secrets.example.yaml` to a private secrets file and replace all `change-me` values.

```bash
kubectl apply -k k8s/base
kubectl get pods -A -o wide
```

The app ingress host is `formula.local`. Add this to your local hosts file for testing:

```text
198.18.149.114 formula.local
```

Then open:

```text
http://formula.local
```

## 5. Useful Checks

```bash
kubectl get nodes -o wide
kubectl get pods -n formula-one-fantasy -o wide
kubectl get cluster -n database
kubectl get pods -n database -o wide
kubectl logs -n formula-one-fantasy deploy/formula-api
kubectl logs -n formula-one-fantasy deploy/formula-frontend
```
