# Cloud_Computing_Project (Serverless Real-Time Chat Application)

## Deployed Link
Deployed Live Demo: https://project-6c2cad9e-c127-49a4-aa1.ey.r.appspot.com/  


## Project Overview  

This repository contains a cloud-native, real-time customer chat application built as a proof-of-concept to modernize ShopWorld’s legacy, on-premises infrastructure.
Traditional on-premises setups relying on synchronous HTTP polling face massive CPU overhead, high latency, and eventual system outages during peak traffic on the website. This project demonstrates how migrating to a serverless, autoscaling cloud architecture permanently solves the infrastructure bottleneck while optimizing operational costs (FinOps).  



## System Architecture  

The application is deployed entirely within the Google Cloud Platform (GCP) Environment utilizing a fully managed, serverless stack designed to eliminate Kubernetes and virtual machine management overhead.

### Compute Platform:  

Hosted on Google App Engine (Standard Environment). It leverages dynamic scale-to-zero capabilities, meaning infrastructure costs are exclusively tied to actual incoming traffic.

### Edge Security & Routing:  

Traffic passes through Cloud Load Balancing and Cloud CDN to cache static assets at global edge nodes and minimize international latency. At the network perimeter, Cloud Armor acts as a Web Application Firewall (WAF) to mitigate potential DDoS attacks.

### Platforms:  

Cloud Platform is Google Cloud Platform and the Cloud Resource is App Engine.


## FinOps & Cost Optimization  

By shifting from traditional, always-on server infrastructure (such as standard Compute Engine instances and Cloud SQL) to an aggressive serverless framework, the baseline operational cost of this microservice was optimized from an estimated €119.58/month down to €2.91/month.  

## Credits  

Anirudh Gopishankar  

Hussein Monem  

Yohan Amaratunga  

Felipe Mancurti  
