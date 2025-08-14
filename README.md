# Flask User Management System

A comprehensive user management system built with Flask that provides functionality to add new users and limit their access based on roles and permissions.

## Features

- **User Management**: Add, edit, delete, and list users
- **Role-Based Access Control**: Predefined roles (Admin, Editor, Viewer)
- **Permission Management**: Granular permissions assigned to roles
- **Authentication**: User login and session management
- **Responsive UI**: Bootstrap 5 based responsive design

## Default Accounts

The system is initialized with one admin user:
- Username: `admin`
- Password: `admin`

## Roles and Permissions

The system comes with three predefined roles:

1. **Admin**
   - Full access to all features
   - All permissions granted

2. **Editor**
   - Can view the dashboard and user list
   - Cannot manage users or roles

3. **Viewer**
   - Can only view the dashboard
   - Minimal system access

Available permissions:
- `users.view`: View the user list
- `users.create`: Create new users
- `users.edit`: Edit existing users
- `users.delete`: Delete users
- `roles.manage`: Manage role permissions
- `dashboard.view`: View the main dashboard
- `settings.edit`: Edit application settings

## Installation and Setup

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python app.py
```

4. Access the application at `http://localhost:5000`

## Development

This project uses:
- Flask for the web framework
- SQLAlchemy for database ORM
- Flask-Login for authentication
- Flask-WTF for form handling
- Bootstrap 5 for frontend UI

## Security Notes

- This application uses Microsoft Sql Server for data storage
- Passwords are hashed using bcrypt before storage
- Set a strong SECRET_KEY in environment variables for production use
