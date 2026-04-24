# AWS Music Subscription App

This project is a cloud-based music subscription web application built using AWS services.

## AWS Services Used

- Amazon S3
- Amazon DynamoDB
- Amazon EC2
- Amazon ECS
- Amazon API Gateway
- AWS Lambda

## Project Structure

```text
frontend/   Frontend HTML, CSS, and JavaScript
backend/    Backend team workspace

## API Contract

The frontend expects the backend to provide these endpoints:

- `POST /login`
- `POST /register`
- `GET /music/search?title=&artist=&year=&album=`
- `GET /subscriptions?email=`
- `POST /subscriptions`
- `DELETE /subscriptions`

The backend base URL should be configured in:

```text
frontend/js/config.js
