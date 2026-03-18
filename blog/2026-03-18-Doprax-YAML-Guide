# Doprax.yaml Configuration Guide

The `doprax.yaml` file serves as the primary configuration blueprint for your application on the Doprax platform. By placing this file in your project's **root directory**, you can automate environment setup, define service architectures, and manage persistent storage.

## 1. Service Definitions
The `services` section is where you define the individual containers that make up your application.

* **Service Name:** A unique identifier for each component.
* **Image:** The specific Docker image to use (e.g., `python:3.10` or `nginx:latest`).
* **Build Context:** If building from source, specify the `context` (usually `.`) and the path to your `Dockerfile`.
* **Command:** The primary execution command that runs when the container starts (this overrides the default Docker CMD).

## 2. Ports and Networking
Define how traffic reaches your services.
* **Internal Port:** The port your application code listens on inside the container.
* **External Port:** (Optional) Mapping for specific public access.
* **Protocol:** Common options include `http` or `tcp`.

## 3. Environment Variables (`envs`)
Manage your application's configuration and security settings.
* **Static Values:** Hardcode non-sensitive values directly in the YAML.
* **Secrets:** For sensitive data (like API keys), use the Doprax dashboard to define variables that will be injected securely at runtime.

## 4. Persistent Storage (Volumes)
Standard container storage is temporary. To ensure data (like databases or user uploads) persists across deployments:
* **Mount Path:** Specify where the volume attaches inside the container (e.g., `/var/lib/mysql`).
* **Size:** Define the storage capacity (e.g., `1GB` or `5GB`).

## 5. Resource Management
Optimize performance by capping the hardware resources available to each service:
* **CPU:** Define the number of cores or CPU shares.
* **Memory:** Set the RAM limit (e.g., `512MB` or `2GB`).

## 6. Lifecycle Scripts
Automate tasks at specific stages of the deployment process:
* **Build Scripts:** Run during the image creation phase (e.g., `npm install`).
* **Run Scripts:** Execute immediately before the main application starts (e.g., `python manage.py migrate`).

## Example `doprax.yaml`
```yaml
services:
  web-app:
    image: python:3.9-slim
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - port: 8000
        protocol: http
    envs:
      - name: DEBUG
        value: "false"
    volumes:
      - name: app-storage
        path: /app/data
        size: 2GB
    scripts:
      run:
        - python manage.py migrate
