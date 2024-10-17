# Influencer Engagement and Sponsorship Coordination Platform (IESCP)

### Overview
**IESCP** is a web-based platform designed to connect sponsors and influencers for advertising and promotion. Sponsors can create campaigns to advertise their products or services, while influencers can negotiate terms and get monetary benefits by accepting or rejecting ad requests. The platform includes role-based functionalities for Admins, Sponsors, and Influencers.

This project is built using:
- **Flask** for the backend
- **Jinja2 templates** + **Bootstrap** for the frontend
- **SQLite** for the database

All operations can be demonstrated locally on your machine.

### Features

1. **Roles:**
    - **Admin:**
      - Root access to monitor users, campaigns, and statistics.
      - Flag inappropriate campaigns and users.
    - **Sponsors:**
      - Create and manage campaigns.
      - Search for influencers and send ad requests.
      - Track campaign progress and manage individual ad requests.
    - **Influencers:**
      - Receive ad requests and negotiate terms.
      - Search public campaigns and accept/reject ad requests.
      - Maintain a public profile.

2. **Core Functionalities:**
    - **Login/Registration System**: Supports separate login forms for Admins, Sponsors, and Influencers.
    - **Admin Dashboard**: Displays platform statistics such as user activity, flagged items, campaigns, and ad requests.
    - **Campaign Management**: Allows sponsors to create, update, and delete campaigns.
    - **Ad Request Management**: Sponsors can create, modify, and delete ad requests, track payments, and monitor request statuses.
    - **Influencer & Campaign Search**: Sponsors can search for influencers based on niche, reach, and followers. Influencers can search for public campaigns.
    - **Negotiation**: Influencers can negotiate payment amounts for ad requests.

3. **Recommended Functionalities**:
    - API resources for interacting with users, ad requests, and campaigns.
    - Frontend validation using HTML5 and JavaScript.
    - Backend validation to ensure data integrity.
    - ChartJS for displaying statistics on the admin dashboard.

4. **Optional Functionalities**:
    - Aesthetic enhancements using CSS and Bootstrap for a responsive interface.
    - Authentication using Flask extensions such as `flask_login` or `flask_security`.
    - A mock payment portal for ad requests.

### Project Structure
```graphql
project/
│
├── app/
│   ├── static/              # CSS, JS, images
│   ├── templates/           # Jinja2 templates
│   ├── __init__.py          # Flask application instance
│   ├── models.py            # Database models (User, Campaign, AdRequest)
│   ├── routes.py            # All routes for the app (Admin, Sponsor, Influencer)
│   └── forms.py             # Flask-WTForms for forms validation
│
├── migrations/              # Database migrations
├── config.py                # Application configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md                # Project readme (this file)


