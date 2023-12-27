from flask import Flask, request, jsonify
from kubernetes import client, config
from flask_sslify import SSLify
app = Flask(__name__)
sslify = SSLify(app)
# Load the Kubernetes configuration
config.load_incluster_config()

# Create a Kubernetes API client
api_client = client.CoreV1Api()


def check_secret_exists(secret_name, namespace):
    try:
        # Check if the secret exists in the specified namespace
        api_client.read_namespaced_secret(secret_name, namespace)
        return True
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return False
        else:
            raise


@app.route('/verify-secrets', methods=['POST'])
def verify_secrets():
    # Parse the incoming request to extract the deployment object
    deployment = request.json['request']['object']

    # Check if the deployment has environment variables with values from secretKeyRef
    if 'env' in deployment['spec']['template']['spec']['containers'][0]:
        env_vars = deployment['spec']['template']['spec']['containers'][0]['env']
        secret_refs = [env_var['valueFrom']['secretKeyRef']['name'] for env_var in env_vars if
                       'secretKeyRef' in env_var.get('valueFrom', {})]

        # Check if the referenced secrets exist in the Kubernetes cluster
        secrets_exist = all(
            check_secret_exists(secret_ref, deployment['metadata']['namespace']) for secret_ref in secret_refs)

        # Return the verification result
        if secrets_exist:
            # Do something if all secrets exist
            return jsonify({"apiVersion": "admission.k8s.io/v1","kind": "AdmissionReview","response": {"uid": request.json['request']['uid'],"allowed": True}}), 200
        else:
            return jsonify({"status": "failure", "message": "Secret doesnt exists"}), 400
    else:
        return jsonify({"apiVersion": "admission.k8s.io/v1", "kind": "AdmissionReview","response": {"uid": request.json['request']['uid'], "allowed": True}}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,ssl_context=('/app/certs/tls.crt', '/app/certs/tls.key'))