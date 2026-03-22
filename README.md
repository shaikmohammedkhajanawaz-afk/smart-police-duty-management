# Intelligent Police Duty Roster & Smart Management System

A full-stack web application for managing police duty rosters with AI-powered allocation, real-time alerts, and comprehensive analytics.

## Features

- **Smart Duty Allocation Engine**: AI algorithms for fair duty assignment considering availability, rank, and workload balance.
- **Smart Alerts & Alarm System**: Notifications for shifts, emergencies, and schedule changes.
- **Admin & Officer Dashboards**: Role-based access for managing schedules and viewing duties.
- **Secure Authentication**: Login system with role-based access control.
- **Analytics & Reporting**: Charts and insights for duty distribution and performance.

## Tech Stack

- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite (can be changed to MySQL)
- **Styling**: Bootstrap 5, Custom CSS
- **Charts**: Chart.js

## Installation

1. **Clone the repository** (or set up the files as above).

2. **Install Python dependencies**:
   ```
   cd backend
   py -m pip install -r requirements.txt
   ```

3. **Run the backend**:
   ```
   py app.py
   ```
   The server will start on http://localhost:5000

4. **Open the frontend**:
   Open `frontend/index.html` in a web browser.

## Usage

- **Login** as admin (username: admin, password: admin123) or officer (username: officer, password: officer123).
- **Admin**: Create schedules, view analytics, manage officers.
- **Officer**: View assigned duties, mark attendance, receive alerts.

## API Endpoints

- `POST /login`: Authenticate user
- `GET /officers`: Get list of officers
- `GET /duties/<officer_id>`: Get duties for an officer
- `POST /assign-duty`: Assign a duty
- `GET /analytics`: Get duty analytics
- `POST /mark-attendance`: Mark attendance
- `GET /alerts/<officer_id>`: Get alerts for an officer

## Future Enhancements

- Real-time notifications (email/SMS)
- Advanced AI for predictive scheduling
- Mobile app
- Integration with GPS for location-based alerts
- Multi-language support

## License

This project is for demonstration purposes.