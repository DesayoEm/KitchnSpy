# KitchnSpy

**KitchnSpy** is a price tracking and monitoring system built with FastAPI, MongoDB, and Celery.  
It scrapes selected KitchenAid products, logs historical price changes, and notifies subscribers via email when prices change or products are removed.

> *Built with caffeine and the desperate hope of justifying that gorgeous Evergreen Artisan mixer, or maybe the classic white tilt-head... or both?*

---

## Tech Stack

- **FastAPI** – API layer 
- **MongoDB** – DB storage
- **Celery + Redis** – Handles database queues, background scraping and notifications
- **BeautifulSoup** – HTML parsing engine for scraping web pages

---

## Features

-  **Email Alerts** – Subscribe to products and receive notifications on price drops
-  **Historical Tracking** – Logs each price change as a timestamped event
-  **Graphing** – Visualize usingStreamlit

