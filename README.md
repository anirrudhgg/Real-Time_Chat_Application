# Serverless Real-Time Chat Application

A chat with disappearing messages, built with Flask and deployed on Google App Engine. It was the proof of concept in a Cloud Computing group project, where we proposed moving a fictional retailer's (ShopWorld) customer chat from on-premises servers to a serverless cloud architecture.

**Live demo:** https://project-6c2cad9e-c127-49a4-aa1.ey.r.appspot.com/

## Features

- Post messages that disappear after 10 or 30 seconds, or stay permanently
- Each message shows a live countdown until it disappears
- Server-side validation: required fields, length limits and allowed timers, with clear error messages
- Messages are rendered as text, never as HTML, so a message cannot inject scripts into other users' browsers
- The number of stored messages is capped, so memory use stays bounded

## What is deployed vs. what we designed

| | Deployed proof of concept (this repo) | Target architecture (Phase 2, in the presentation) |
|---|---|---|
| Compute | App Engine Standard, scales to zero | App Engine Standard |
| Data | In-memory list on one instance | Firestore (NoSQL, real-time) |
| Updates | Browser polls `/messages` every second | Real-time push (WebSockets / Firestore listeners) |
| Edge | App Engine's default front end | Cloud Load Balancing, Cloud CDN, Cloud Armor (WAF/DDoS) |
| Auth | None | Firebase Authentication |

The presentation (`Cloud_ppt.pptx`) explains the target design and the cost comparison.

## Cost estimate

Using the Google Cloud pricing calculator, we estimated about **€119.58/month** for an always-on setup (Compute Engine + Cloud SQL) and about **€2.91/month** for the serverless design, both assuming 30 GB of storage. The calculator links are in the presentation.

## Running locally

Requires Python 3.10+.

```
pip install -r requirements.txt
python main.py                          # http://127.0.0.1:8080
python -m unittest discover tests -v    # run the 7 tests
```

## Deploying to App Engine

With the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and a project selected:

```
gcloud app deploy
```

`app.yaml` runs the app with gunicorn on the Python 3.12 runtime and limits it to **one instance**, because messages live in that instance's memory.

## Limitations

- Messages are lost whenever the instance restarts or scales to zero. Firestore would fix this and allow more than one instance.
- Polling every second is simple but wasteful compared with real-time push.
- There is no login, so anyone can post under any name.

## API

| Method | Path | Body / response |
|---|---|---|
| GET | `/` | The chat page |
| POST | `/send` | `{"name": "...", "text": "...", "timer": 0 \| 10 \| 30}` → 200, or 400 with `{"error": "..."}` |
| GET | `/messages` | `[{"name", "text", "left"}]` for all messages that have not expired |

## Team

- Anirudh Gopishankar
- Hussein Monem
- Yohan Amaratunga
- Felipe Mancurti
