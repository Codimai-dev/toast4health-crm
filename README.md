# CRM System - Flask Web Application

A comprehensive Customer Relationship Management (CRM) system built with Flask, designed for managing B2C/B2B leads, customers, bookings, employees, expenses, and channel partners.

## 🚀 Features

### Core Modules
- **Authentication & Authorization**: Role-based access control (ADMIN, SALES, OPS, FINANCE, VIEWER)
- **Dashboard**: Real-time statistics, charts, and activity timeline
- **B2C Lead Management**: Lead tracking with follow-up system
- **B2B Lead Management**: Organization-focused lead tracking
- **Customer Management**: Customer profiles with booking history
- **Booking Management**: Service bookings with financial calculations
- **Employee Management**: Staff profiles with assignment tracking
- **Expense Management**: Expense tracking and categorization
- **Channel Partner Management**: Partner relationship management
- **Settings Management**: Configurable system settings

### Technical Features
- **Responsive Design**: Bootstrap 5 UI with mobile-first approach
- **Database**: SQLite with SQLAlchemy ORM and Flask-Migrate
- **Security**: Password hashing, CSRF protection, session management
- **Import/Export**: XLSX/CSV data import and export functionality
- **REST API**: JSON API with token authentication
- **Charts & Analytics**: Interactive charts with Chart.js
- **Audit Logging**: Track all CRUD operations
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Server-side pagination for large datasets

## 📋 Prerequisites

- Python 3.11+
- pip (Python package manager)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd CRM
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=sqlite:///crm.db
```

### 5. Database Setup
```bash
# Initialize database
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade

# Seed the database with initial data
flask seed
```

### 6. Run the Application
```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`

## 🔐 Default Credentials

After running `flask seed`, use these credentials to login:

- **Email**: admin@example.com
- **Password**: Admin@12345
- **Role**: ADMIN

## 📁 Project Structure

```
CRM/
├── app/                          # Main application package
│   ├── auth/                     # Authentication blueprint
│   ├── dashboard/                # Dashboard blueprint
│   ├── leads_b2c/               # B2C leads management
│   ├── leads_b2b/               # B2B leads management
│   ├── customers/               # Customer management
│   ├── bookings/                # Booking management
│   ├── employees/               # Employee management
│   ├── expenses/                # Expense management
│   ├── channel_partners/        # Channel partner management
│   ├── settings/                # Settings management
│   ├── api/                     # REST API endpoints
│   ├── static/                  # Static files (CSS, JS, images)
│   ├── templates/               # Jinja2 templates
│   ├── utils/                   # Utility modules
│   ├── __init__.py             # App factory
│   ├── models.py               # Database models
│   ├── cli.py                  # CLI commands
│   └── errors.py               # Error handlers
├── migrations/                  # Database migrations
├── tests/                      # Unit tests
├── instance/                   # Instance-specific files
├── config.py                   # Configuration settings
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 💾 Database Models

### User Management
- **User**: System users with role-based permissions

### Lead Management
- **B2CLead**: Individual customer leads
- **B2BLead**: Business/organization leads
- **FollowUp**: Follow-up activities for leads

### Customer & Booking Management
- **Customer**: Customer profiles
- **Booking**: Service bookings with financial data
- **Employee**: Staff members who can be assigned to bookings

### Financial Management
- **Expense**: Expense tracking and categorization

### System Management
- **ChannelPartner**: Business partners
- **Setting**: Configurable system settings
- **AuditLog**: System activity logging

## 🎯 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full system access, user management, settings |
| **SALES** | Lead management, customer management, bookings |
| **OPS** | Operations, employee management, bookings |
| **FINANCE** | Financial data, expenses, revenue reports |
| **VIEWER** | Read-only access to most data |

## 🔧 CLI Commands

```bash
# Seed database with initial data
flask seed

# Import data from XLSX file
flask import-xlsx path/to/file.xlsx

# Create a new user
flask create-user

# List all users
flask list-users

# Reset database (WARNING: Deletes all data)
flask reset-db
```

## 📊 Dashboard Features

- **Real-time Statistics**: Lead counts, revenue, expenses
- **Interactive Charts**: Lead status distribution, revenue trends
- **Activity Timeline**: Recent system activities
- **Follow-up Reminders**: Upcoming and overdue follow-ups
- **Quick Actions**: Fast access to common operations

## 🔌 API Endpoints

The system provides a REST API with the following endpoints:

- `POST /api/auth/token` - Get authentication token
- `GET /api/leads-b2c` - List B2C leads
- `POST /api/leads-b2c` - Create B2C lead
- `GET /api/leads-b2c/{id}` - Get specific B2C lead
- `PUT /api/leads-b2c/{id}` - Update B2C lead
- `DELETE /api/leads-b2c/{id}` - Delete B2C lead

Similar endpoints exist for all major entities (B2B leads, customers, bookings, etc.).

### API Authentication
```bash
# Get token
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin@12345"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/leads-b2c
```

## 📈 Import/Export

### Supported Formats
- **Import**: XLSX files with predefined templates
- **Export**: CSV and XLSX formats for all data

### Import Templates
The system supports importing from XLSX files with these sheet names:
- `B2C Leads Master` - B2C lead data
- `B2B Lead Master` - B2B lead data
- `CustomerMaster` - Customer data
- `BookingMaster` - Booking data
- `EmployeesMaster` - Employee data
- `Expense Master` - Expense data
- `Channel Partner` - Channel partner data

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 🚀 Deployment

### Production Configuration

1. Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=your-production-database-url
```

2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

3. Configure a reverse proxy (nginx) and SSL certificate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 📋 Todo / Roadmap

- [ ] Advanced reporting and analytics
- [ ] Email notification system
- [ ] Mobile application
- [ ] Advanced workflow automation
- [ ] Integration with external systems (CRMs, accounting software)
- [ ] Multi-language support
- [ ] Advanced search with Elasticsearch
- [ ] Real-time notifications with WebSockets