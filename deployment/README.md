# NFC Reader/Writer System - Deployment Guide

This directory contains deployment packages and configurations for the NFC Reader/Writer System.

## Available Deployments

### Server Deployments
- **Docker**: Containerized deployment with Docker Compose
- **Kubernetes**: Production-ready Kubernetes manifests
- **Systemd**: Linux service deployment
- **AWS**: AWS ECS/EKS deployment configurations
- **Manual**: Manual deployment scripts

### Android App Deployments
- **APK**: Debug and release APK builds
- **Play Store**: Google Play Store deployment configuration
- **F-Droid**: F-Droid repository deployment
- **CI/CD**: Automated build and deployment pipelines

## Quick Start

### Server
```bash
# Docker deployment (recommended for development)
cd deployment/docker
docker-compose up -d

# Production deployment
cd deployment/kubernetes
kubectl apply -f manifests/

# Local systemd service
cd deployment/systemd
sudo ./install.sh
```

### Android App
```bash
# Build debug APK
cd android
./gradlew assembleDebug

# Build release APK (requires signing)
./gradlew assembleRelease

# Deploy to Play Store (CI/CD)
# See deployment/android/play-store/README.md
```

## Environment Configuration

Each deployment method includes environment configuration templates:
- `.env.example` files for configuration
- Secrets management instructions
- Database setup guides
- SSL/TLS certificate configuration

## Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Android App   │────│   Load Balancer │
└─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   NFC Server    │
                       │   (FastAPI)     │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
```

## Security Considerations

- All deployments include HTTPS/TLS configuration
- Database credentials are managed via secrets
- API authentication and rate limiting enabled
- Regular security updates and vulnerability scanning

## Monitoring and Logging

- Prometheus metrics collection
- Grafana dashboards
- Centralized logging with ELK stack
- Health check endpoints

For detailed instructions, see the README.md file in each deployment subdirectory.
