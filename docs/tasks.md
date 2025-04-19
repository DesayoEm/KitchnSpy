Project Workflow

## Tech Stack
-  **Python**
-  **BeautifulSoup + Requests** - for KitchenAid official UK site
-  **FastAPI** – for API endpoints, manual triggers
-  **smtplib** – native email notifications
-  **Matplotlib** - for price trend visualization
-  **schedule / background tasks** – optional for periodic scrapes
-  **SQlite** – for logging data

## Goal
Track three specific KitchenAid products on the official site:
-  **Mixer Design Series 4.7L Evergreen Artisan (5KSM180WS)**
-  **Mixer Tilt-Head 4.3L Classic White (5K45SS)**
-  **Mini Food Chopper 830ml White (5KFC3516)**
-  **Glass Mixing Bowl 4.7 L (5KSM5GB)** 

Send an **email notification** when:
-   Price changes

Plot price changes over time using Matplotlib:
-  Historical price tracking visualization


### 1. Setup & Configuration
- [x] Create project structure
- [x] Initialize Python virtual environment
- [x] Install required packages
- [x] Setup FastAPI application structure
- [x] Create configuration files for products and URLs

### 2. Web Scraping Implementation
- [x] Analyze KitchenAid UK website structure
- [x] Inspect HTML elements for price information
- [ ] Identify product availability indicators
- [x] Implement BeautifulSoup + Requests scraper
- [x] Set up proper headers to mimic browser behavior
- [x] Implement error handling for network issues
- [x] Extract all relevant product information (price, availability, etc.)
- [ ] Implement data validation and cleaning


### 3. Data Management
- [ ] Design data model for product information
- [ ] Implement SQlite logging 
- [ ] Create data validation and cleaning functions

### 4. API Development
- [ ] Create FastAPI main application
- [ ] Implement scraping endpoints
- [ ] Create status and history endpoints
- [ ] Add product management endpoints
- [ ] Setup error handling and logging

### 5. Notification System
- [ ] Configure SMTP settings
- [ ] Create email template for notifications
- [ ] Implement notification sending logic
- [ ] Add price threshold checking functionality

### 6. Visualization with Matplotlib
- [ ] Create data processing functions for visualization
- [ ] Implement time-series price tracking charts
- [ ] Build retailer comparison visualizations
- [ ] Setup visualization generation endpoints
- [ ] Create functionality to save/export visualizations

### 7. Scheduling & Automation
- [ ] Implement background task scheduler
- [ ] Create periodic scraping functionality
- [ ] Setup error recovery mechanisms
- [ ] Add logging for automated processes

### 9. Deployment & Documentation
- [ ] Document API endpoints
- [ ] Create usage instructions
- [ ] Setup deployment configuration
- [ ] Create backup and maintenance procedures

##  Weekly Milestones

### Week 1: Setup & Learning
- [x] Complete project structure and environment setup
- [x] Analyze KitchenAid UK website structure
- [ ] Setup basic data logging structure

### Week 2-3: Implementation
- [x] Implement BeautifulSoup scraper for KitchenAid UK
- [ ] Create price tracking for all four products
- [ ] Implement FastAPI application and core endpoints
- [ ] Setup notification system

### Week 4: Visualization & Polish
- [ ] Implement Matplotlib visualizations
- [ ] Add scheduling functionality
- [ ] Complete testing and documentation