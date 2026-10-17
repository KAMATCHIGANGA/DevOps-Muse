# Starcourt — AWS Hosting & Infrastructure

## Overview

Starcourt is a Flask-based web application hosted on Amazon Web Services (AWS). The deployment uses a multi-tier architecture with a public web server, a private application server, and a managed PostgreSQL database.

The infrastructure is deployed in the **AWS Asia Pacific (Sydney) Region (`ap-southeast-2`)**.

## Architecture


                         Users
                           |
                           v
                    Internet Gateway
                           |
                           v
                +----------------------+
                | Public Subnet        |
                | Web EC2              |
                | Nginx :80            |
                +----------------------+
                           |
                     HTTP :5000
                           |
                           v
                +----------------------+
                | Private Subnet       |
                | App EC2              |
                | Flask + Gunicorn     |
                +----------------------+
                           |
                    PostgreSQL :5432
                           |
                           v
                +----------------------+
                | Amazon RDS            |
                | PostgreSQL            |
                | Private Database      |
                +----------------------+


## AWS Resources

AWS Region: Asia Pacific (Sydney) - ap-southeast-2
|
+-- Amazon VPC: starcourt-vpc (10.0.0.0/16)
    |
    +-- Public Subnet: starcourt-public-a
    |   |
    |   +-- Web EC2: starcourt-web-ec2 (t3.micro)
    |   |   +-- OS: Amazon Linux 2023
    |   |   +-- Web Server: Nginx
    |   |   +-- Role: Public HTTP entry point and reverse proxy
    |   |
    |   +-- Internet Gateway: starcourt-igw
    |       +-- Role: Internet connectivity for public resources
    |
    +-- Private Subnet: starcourt-private-a
    |   |
    |   +-- App EC2: starcourt-app-ec2 (t3.micro)
    |       +-- OS: Amazon Linux 2023
    |       +-- Application: Flask + Gunicorn
    |       +-- Process Manager: systemd
    |       +-- Role: Runs the Starcourt application
    |
    +-- Private Subnet: starcourt-private-b
    |   +-- Role: Additional private subnet
    |
    +-- NAT Gateway: starcourt-nat
    |   +-- Role: Outbound internet access for private resources
    |
    +-- Amazon RDS: starcourt-db
    |   +-- Engine: PostgreSQL
    |   +-- Port: 5432
    |   +-- Role: Application database
    |
    +-- Amazon CloudWatch Logs
        |
        +-- /starcourt/app/structured-logs
        +-- /starcourt/app/traces
        +-- /starcourt/app/service
        +-- /starcourt/web/nginx-access
        +-- /starcourt/web/nginx-error
        +-- Role: Centralized logs and troubleshooting


## Application Deployment

The Flask application is deployed on the private application EC2 instance and runs using Gunicorn under a systemd service.

- **Framework:** Flask
- **Application server:** Gunicorn
- **Web server:** Nginx
- **Database:** Amazon RDS for PostgreSQL
- **Operating system:** Amazon Linux 2023
- **Process management:** systemd

The systemd service manages the application process and is configured to restart the application following failures.

## Nginx Reverse Proxy

Nginx runs on the public web EC2 instance and forwards incoming HTTP requests to the Flask application on the private app EC2.

The reverse proxy configuration includes:

- Forwarding requests to the application server.
- Passing client and forwarded-protocol headers.
- Generating request IDs for request correlation.
- Recording access logs with HTTP status, request duration, and upstream response details.

This separates the public-facing web tier from the private application tier.

## Database Connectivity

Starcourt uses Amazon RDS for PostgreSQL to store application data.

- The database is deployed privately.
- The application connects to PostgreSQL on port `5432`.
- Security groups restrict database access to authorized application infrastructure.
- Database connection settings are supplied through environment variables rather than hardcoded into the application source code.

For local development and AI-agent integration, an SSH tunnel can forward a local port to the private RDS endpoint through the application EC2 instance.

This allows local tools to connect to the database without making the database publicly accessible.

## Logging and Observability

The deployment includes centralized logging using Amazon CloudWatch Logs and application-level instrumentation.

### Log collection

CloudWatch log groups are configured for:

- Application structured logs
- Application distributed traces
- Application service logs
- Nginx access logs
- Nginx error logs

### Structured logging

Application logs use JSON-formatted records containing fields such as timestamps, severity levels, messages, request identifiers, and trace context when available.

### Distributed tracing

OpenTelemetry instrumentation is used to capture application request spans and database-related spans.

Trace IDs and span IDs help connect related operations. Nginx request IDs are also propagated to the application to support cross-layer request correlation.

### Incident investigation

CloudWatch Logs Insights can be used to search log records, filter errors, inspect HTTP status codes, and correlate events using request identifiers and trace IDs.

## Security Considerations

- The application server is hosted in a private subnet without a public IP address.
- The RDS database is not intended to be publicly accessible.
- Security groups restrict communication between infrastructure components.
- Database credentials are supplied through a protected environment file.
- Private SSH keys and credentials are excluded from source control.
- Local database access uses SSH tunnelling rather than opening PostgreSQL directly to the internet.

## Verification Evidence

1. Live Starcourt website.
2. EC2 instance list.
3. VPC resource map.
4. RDS PostgreSQL details.
5. CloudWatch log groups.
6. Structured application logs.
7. Request-ID and trace correlation.
8. Successful database connectivity.