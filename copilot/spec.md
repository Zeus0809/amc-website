# Arlington Men's Circle Website - Technical Specification

## Project Overview

**Project Name:** Arlington Men's Circle Website  
**Purpose:** Private event RSVP website to replace Meetup functionality  
**Target Users:** 9-50 members, age 25-35, tech-savvy  
**Primary Goal:** Cost-effective ($40/month → ~$5/month) private group event management  

## Core Requirements

### MVP Functional Requirements
- **Authentication:** Individual user accounts (username/password)
- **Event Management:** Display upcoming events, prevent RSVP to past events
- **RSVP System:** Simple yes/no RSVP with email confirmation
- **About Page:** Static group description and purpose
- **Mobile-First:** Primary usage on mobile devices

### MVP Non-Functional Requirements
- **Scalability:** Support up to 50 concurrent users
- **Performance:** Fast loading on mobile networks
- **Security:** Private group access only
- **Cost:** Minimize hosting costs
- **Maintenance:** Simple to update events (manual for MVP)

### Post-MVP Features (Phase 2)
- Photo gallery with upload functionality
- Event detail pages with attendee lists
- Admin interface for event creation
- Advanced RSVP options (maybe/not attending)
- S3 file storage and advanced deployment options

## Technical Stack

### Frontend
- **Languages:** HTML5, CSS3, minimal JavaScript
- **Approach:** Server-side rendered pages (Flask templates)
- **Styling:** Custom CSS with mobile-first responsive design
- **JavaScript:** Minimal for form validation, photo modals, session handling

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite (development and MVP) → PostgreSQL (future scaling)
- **Authentication:** Flask-Login with session management
- **Email:** Flask-Mail with console output (MVP) → AWS SES (production)

### Infrastructure (AWS)
- **Hosting:** AWS EC2 instance (t3.micro) - Linux server
- **Database:** SQLite on EC2 instance (simple, file-based)
- **Email:** Console logging (MVP) → Amazon SES (Phase 2)
- **File Storage:** Local storage on EC2 (static assets only)
- **Web Server:** Apache HTTP Server + mod_wsgi
- **SSL:** HTTP initially → Let's Encrypt (Phase 2)

## Configuration Flexibility Requirements

**IMPORTANT FOR IMPLEMENTATION:** The Flask application must be designed with configuration flexibility to easily switch between different AWS deployment options without code changes. The host may decide to change infrastructure approaches during or after development.

### Required Flexibility:
- **Database Switching:** Easy migration between SQLite (MVP) → PostgreSQL on EC2 → Amazon RDS
- **Email Backend:** Switch between console logging and AWS SES without code changes
- **Deployment Methods:** Support EC2 (Apache), with future Elastic Beanstalk capability
- **Environment Configuration:** Development and production configs via environment variables
- **File Storage Options:** Prepared for future S3 integration without code changes

### Implementation Approach:
- Use Flask configuration classes for different environments
- Abstract email operations (console vs SES)
- Environment variable driven configuration
- Database connection strings configurable via environment
- Single codebase deployable with different configurations

This ensures the MVP can start simple (SQLite + console emails) and scale to full AWS services (PostgreSQL + SES) without requiring code modifications.

## Design System

### Brand Colors
- **Primary Orange:** #ef8f36
- **Black:** #000000
- **White:** #ffffff

### Typography
- **Primary Font:** Roboto (clean, sans-serif)
- **Fallback:** system fonts (Arial, Helvetica)

### Design Principles
- **Style:** Clean, minimalistic
- **Mobile-First:** Touch-friendly (44px+ touch targets)
- **Layout:** Card-based design for events
- **Navigation:** Simple hamburger menu or bottom nav

## Database Configuration

### MVP Approach: SQLite on EC2 (Simple, Fast Development)
```bash
# No installation needed - SQLite is file-based
# Database file: /var/www/amc-website/instance/amc_website.db
```

**MVP Benefits:**
- Zero setup - works immediately
- No additional AWS costs
- Perfect for 9-50 users
- Easy backup (just copy the .db file)
- Fast development and deployment

**When to migrate:**
- When you need >100 concurrent users
- When you want professional database management
- When you add complex queries/reporting

### Future: PostgreSQL Options
Will be available via configuration switching without code changes:

#### Option A: PostgreSQL on EC2
- Manual setup and maintenance
- No additional AWS costs
- Good for medium scale

#### Option B: Amazon RDS  
- Managed service with backups
- Additional cost (~$15-20/month)
- Better for production scaling

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Events Table
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    date_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    max_attendees INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### RSVPs Table
```sql
CREATE TABLE rsvps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    event_id UUID REFERENCES events(id),
    status VARCHAR(20) DEFAULT 'attending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id)
);
```

**MVP Database Schema Notes:**
- **No Photos table for MVP** - Will be added in Phase 2
- **Simple RSVP status** - Only 'attending' for MVP (future: maybe/not_attending)
- **SQLite compatibility** - UUIDs handled via Python uuid.uuid4() in MVP
- **Future PostgreSQL** - Will use native gen_random_uuid()

**Benefits of UUIDs:**
- **Security:** No sequential ID enumeration attacks
- **Privacy:** User IDs aren't guessable (can't iterate through /users/1, /users/2, etc.)
- **Scalability:** No ID collision issues when merging databases
- **Distribution:** Works well with multiple servers/regions

**Note for SQLite (Development):**
- SQLite doesn't have native UUID generation
- Will use Python's `uuid.uuid4()` in the Flask app
- PostgreSQL production will use `gen_random_uuid()`

## Application Structure

```
amc-website/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── config.py             # Configuration settings
├── amc_website.wsgi      # WSGI file for Apache
├── instance/
│   └── amc_website.db    # SQLite database (MVP)
├── static/
│   ├── css/
│   │   └── main.css      # Main stylesheet (mobile-first)
│   ├── js/
│   │   └── main.js       # Minimal JavaScript
│   └── images/
│       └── logo.jpeg     # AMC logo
├── templates/
│   ├── base.html         # Base template
│   ├── login.html        # Login form
│   ├── events.html       # Main events page
│   └── about.html        # About page
├── models/
│   ├── __init__.py
│   ├── user.py           # User model
│   ├── event.py          # Event model
│   └── database.py       # Database setup
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   └── events.py         # Event-related routes
└── utils/
    ├── __init__.py
    ├── email.py          # Email utilities (console/SES)
    └── helpers.py        # General utilities
```

## Page Specifications

### 1. Login Page (`/login`)
**Purpose:** Authenticate users before accessing content  
**Components:**
- AMC logo
- Username/password form
- Error messages
- Clean, centered design

**Features:**
- Session management
- Password validation
- Redirect to events page after login

### 2. Events Page (`/events`) - Main Dashboard
**Purpose:** Display all upcoming events and handle RSVPs  
**Components:**
- Navigation header with logout
- Event cards showing:
  - Event title
  - Date/time
  - Location
  - Current attendee count
  - RSVP button (if not already RSVP'd)
  - "Already attending" status (if RSVP'd)
- Past events section (collapsed by default)

**Features:**
- Mobile-optimized card layout
- One-click RSVP functionality
- Email confirmation on RSVP
- Visual distinction for past events
- Prevent RSVP to past events

### 3. About Page (`/about`)
**Purpose:** Information about Arlington Men's Circle  
**Components:**
- Group description
- Mission/purpose
- Static group photos (embedded in page)
- Contact information (optional)

**Features:**
- Simple, responsive text layout
- Static images (no upload functionality for MVP)

## User Flows

### Authentication Flow
1. User visits site → redirected to login
2. Enter credentials → session created
3. Access events page → browse and RSVP
4. Logout → session destroyed

### RSVP Flow (MVP)
1. View events page → see upcoming events
2. Click RSVP button → immediate confirmation
3. Email sent to user confirming RSVP
4. Button changes to "Already attending"
5. Attendee count updates on page

### Admin Flows (Manual for MVP)
1. Admin manually adds events via database/config
2. Admin manually manages users via database
3. Email confirmations logged to console (MVP) or sent via SES

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout user

### Events
- `GET /` or `/events` - Main events page (homepage)
- `POST /events/<id>/rsvp` - RSVP to event (AJAX)

### Pages
- `GET /about` - About page

### Future (Phase 2)
- `GET /events/<id>` - Event detail pages
- `POST /admin/events` - Create event
- `GET /gallery` - Photo gallery

## Deployment Strategy

### Development Setup
1. Python virtual environment
2. SQLite database
3. Local Flask development server
4. Environment variables for AWS credentials

### Production Deployment (AWS EC2)

#### MVP Setup (Simple and Fast)
1. **EC2 Instance:** t3.micro (1 vCPU, 1GB RAM) - Ubuntu 22.04 LTS
2. **Database:** SQLite database file on EC2
3. **Web Server:** Apache HTTP Server with mod_wsgi for Flask
4. **File Storage:** Local filesystem on EC2 (static assets only)
5. **Email:** Console logging initially → AWS SES later
6. **SSL:** HTTP initially → Let's Encrypt in Phase 2

#### EC2 Setup Steps (Simplified)
```bash
# 1. Launch EC2 instance (Ubuntu 22.04 LTS)
# 2. Install dependencies
sudo apt update
sudo apt install apache2 python3 python3-pip libapache2-mod-wsgi-py3

# 3. Clone and setup Flask app
git clone <repository>
cd amc-website
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Create SQLite database
flask db init
flask db migrate
flask db upgrade

# 5. Configure Apache Virtual Host (simplified)
sudo nano /etc/apache2/sites-available/amc-website.conf

# 6. Enable site and restart
sudo a2ensite amc-website.conf
sudo a2enmod wsgi
sudo systemctl restart apache2
```

### Alternative: Managed Services
- **Elastic Beanstalk:** For future scaling when needed
- **Lambda + RDS:** Serverless option for Phase 2
- **ECS/Fargate:** Container-based deployment for Phase 2

## Apache Configuration (Simplified for MVP)

### Basic Virtual Host Configuration (`/etc/apache2/sites-available/amc-website.conf`)
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /var/www/amc-website
    
    WSGIDaemonProcess amc_website python-path=/var/www/amc-website python-home=/var/www/amc-website/venv
    WSGIProcessGroup amc_website
    WSGIScriptAlias / /var/www/amc-website/amc_website.wsgi
    
    <Directory /var/www/amc-website>
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    # Serve static files directly with Apache
    Alias /static /var/www/amc-website/static
    <Directory /var/www/amc-website/static>
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/amc_website_error.log
    CustomLog ${APACHE_LOG_DIR}/amc_website_access.log combined
</VirtualHost>
```

### WSGI Configuration (`amc_website.wsgi`)
```python
#!/usr/bin/python3
import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, "/var/www/amc-website/")

# Activate virtual environment
activate_this = '/var/www/amc-website/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application

if __name__ == "__main__":
    application.run()
```

## Security Considerations

### Authentication
- Password hashing (bcrypt/scrypt)
- Session management with secure cookies
- CSRF protection on forms
- Rate limiting on login attempts

### Data Protection
- HTTPS only (AWS Certificate Manager)
- Environment variables for secrets
- Database connection encryption
- Input validation and sanitization

### Access Control
- Login required for all content
- User session validation
- No public endpoints except login

## Performance Optimizations

### Frontend
- Minified CSS/JS
- Optimized images (WebP format)
- Mobile-first responsive design
- Minimal JavaScript payload

### Backend
- Database query optimization
- Session storage (Redis for scaling)
- Caching static content
- Image compression for uploads

### Infrastructure
- CloudFront CDN for static assets
- RDS connection pooling
- Auto-scaling groups (if needed)

## Testing Strategy

### Unit Tests
- User authentication
- RSVP logic
- Email sending
- Database operations

### Integration Tests
- Full user flows
- Form submissions
- Email delivery
- File uploads

### Manual Testing
- Mobile device testing
- Cross-browser compatibility
- Accessibility compliance
- Performance testing

## Maintenance & Operations

### Content Management
- Admin interface for creating events
- Photo upload system
- User account management
- Backup procedures

### Monitoring
- Application health checks
- Error logging
- Performance metrics
- Cost monitoring

### Updates
- Regular security updates
- Feature enhancements
- AWS service updates
- Database maintenance

## Future Enhancements

### Phase 2 Features
- Event creation interface for organizers
- Photo upload by members
- Event comments/discussions
- Member profiles

### Phase 3 Features
- Event categories
- Recurring events
- Push notifications
- Mobile app (React Native)

### Integration Possibilities
- Calendar integration (Google Calendar)
- Social media sharing
- Payment processing (for paid events)
- SMS notifications

## Budget Estimates

### AWS Monthly Costs (50 users, 4 events/month)

#### MVP Setup (Ultra Cost-Effective)
- **EC2 t3.micro:** $0-8/month (free tier eligible for 12 months)
- **Elastic IP:** $0 (when attached to running instance)
- **Data Transfer:** $1-2/month
- **Email (console):** $0/month
- **Total MVP:** ~$1-10/month (after free tier: ~$8-12/month)

#### Future Production Setup
- **EC2 t3.micro:** $8-12/month
- **SES (email):** $1-2/month
- **SSL (Let's Encrypt):** $0/month
- **PostgreSQL upgrade:** $0 (still on EC2)
- **Total Production:** ~$9-14/month

#### Comparison with Current
- **Meetup:** $40/month
- **MVP:** $1-10/month (75-97% cost reduction)
- **Production:** $9-14/month (65-77% cost reduction)

## Success Metrics

### Technical Metrics
- Page load times < 2 seconds
- 99.9% uptime
- Zero security incidents
- Mobile performance scores > 90

### Business Metrics
- Cost reduction from $40/month to <$30/month
- User adoption rate > 90%
- RSVP conversion rate > 80%
- Member satisfaction survey scores

## Timeline Considerations

### MVP Development (Target: August 21)
- **Week 1 (Aug 16-18):** Backend setup, authentication, database models
- **Week 2 (Aug 19-21):** RSVP system, email integration, basic styling, deployment

### Simplified MVP Scope
- **Day 1-2:** Flask app structure, user authentication, SQLite setup
- **Day 3-4:** Event display, RSVP functionality, email confirmations
- **Day 5:** Mobile styling, AWS deployment, testing

### Post-MVP Iterations (Phase 2)
- **Month 1:** Photo gallery, event detail pages, SSL setup
- **Month 2:** Admin interface, PostgreSQL migration, advanced features
- **Month 3:** Performance optimization, monitoring, scaling preparation

---

*This specification serves as the blueprint for developing the Arlington Men's Circle MVP website. The focus is on delivering core event RSVP functionality quickly and cost-effectively, with a clear path for future feature expansion. All technical decisions prioritize simplicity and rapid deployment while maintaining flexibility for growth.*
