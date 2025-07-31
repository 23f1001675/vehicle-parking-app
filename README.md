# Vehicle Parking Management System

## Project Overview
The Vehicle Parking Management System is a web-based application that allows users to reserve, book, and manage parking spots while providing administrators with tools to manage parking lots and monitor system statistics. The project includes:

- **Frontend**: Built with Vue.js (Vite) for responsive user interaction.  
- **Backend**: Developed using Flask with JWT authentication, SQLAlchemy ORM, and Celery for asynchronous background jobs.  
- **Asynchronous Jobs**:
  - Export user reservations to CSV (user-triggered).
  - Send daily reminders to users via email if they have not booked or if a new lot is added.
  - Generate and send monthly activity reports via email.  
- **Performance**: Flask-Caching with Redis for performance optimization.  
- **Email Service**: Configured with MailHog for local development.

---

## Features
- User registration and login with JWT authentication.
- Admin and user roles with access restrictions.
- Parking lot and parking spot management.
- Reservation booking and history tracking.
- CSV export of reservation history (asynchronous).
- Automated daily reminders for users.
- Automated monthly activity reports delivered via email.
- Cached API responses to improve performance.

---

## Technologies Used
- **Backend**: Flask, Flask-JWT-Extended, Flask-CORS, Flask-Caching, SQLAlchemy  
- **Frontend**: Vue.js with Vite and Axios  
- **Database**: SQLite (file-based database for simplicity)  
- **Asynchronous Jobs**: Celery + Redis  
- **Mailing**: MailHog (development mail server)  
- **Other Tools**: Docker (optional for MailHog), Jinja2 for HTML reports  

---

## Database Schema
- **Users**: `id`, `name`, `email`, `password_hash`, `role`, `pincode`, `date_created`  
- **ParkingLots**: `id`, `city`, `address`, `pincode`, `price`, `number_of_spots`, `date_created`  
- **ParkingSpots**: `id`, `lot_id (FK)`, `status`  
- **Reservations**: `id`, `spot_id (FK)`, `user_id (FK)`, `vehicle_number`, `booked_at`, `parking_timestamp`, `leaving_timestamp`, `parking_cost`

---

## Installation and Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Redis (running on localhost:6379)
- MailHog (running on localhost:1025 for SMTP, localhost:8025 for MailHog web UI)

### Backend Setup
```bash
cd flask-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run database migrations (if using SQLite):
```bash
flask db upgrade
```

Start Flask backend:
```bash
flask run
```

Start Celery worker and scheduler:
```bash
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```

### Frontend Setup
```bash
cd vue-frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000` and backend on `http://localhost:5000`.

---

## MailHog Setup
To capture emails locally:
```bash
# Install MailHog
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
./MailHog_linux_amd64
```

- Access Mailhog Web UI: `http://localhost:8025`
- SMTP Server: `localhost:1025`

---

## API Endpoints
- **Auth**: `/api/auth/register`, `/api/auth/login`
- **Admin**: `/api/admin/*` (lot management, statistics)
- **User**: `/api/user/*` (reservations, export, reminders, reports)

---

## Running the Full Application
1. Start Redis server.
2. Start MailHog for emails.
3. Run Flask backend (`flask run`).
4. Start Celery worker and beat for background jobs.
5. Start Vue frontend (`npm run dev`).
6. Access app from browser at `http://localhost:3000`.

---

## Project Structure
```
vehicle-parking-app/
│── flask-backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   ├── jobs/
│   ├── mailer.py
│   └── requirements.txt
│── vue-frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│── README.md
```
