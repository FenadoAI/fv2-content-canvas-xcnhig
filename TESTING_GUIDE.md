# BlogHub Testing Guide

## Platform Overview
A fully functional blogging platform with role-based access control, article management, commenting, and social engagement features.

## User Roles
1. **Reader** - Can view articles, like, and comment
2. **Writer** - Can create, edit, publish articles + Reader permissions
3. **Admin** - Full access to all content and user management

## How to Test

### 1. Access the Website
Open your browser and navigate to the homepage

### 2. Create Accounts

#### Sign Up as Reader
1. Click "Sign Up" in navigation
2. Fill in: Name, Email, Password
3. Submit form
4. You'll be automatically logged in as a Reader

#### Promote to Writer/Admin (Via MongoDB)
Since the first user is a Reader, you need to manually promote users:

```bash
# Connect to MongoDB
mongosh

# Switch to database
use test_database

# Promote user to writer
db.users.updateOne(
  { email: "your-email@example.com" },
  { $set: { role: "writer" } }
)

# Promote user to admin
db.users.updateOne(
  { email: "admin-email@example.com" },
  { $set: { role: "admin" } }
)

# Verify
db.users.find({ email: "your-email@example.com" })
```

After promotion, sign out and sign back in to get fresh tokens.

### 3. Test Reader Features
- Browse home page (Trending, Featured, Recent tabs)
- Click on an article to read it
- Like an article (heart icon)
- Leave a comment
- View About page

### 4. Test Writer Features
1. Sign in as a Writer
2. Click "Dashboard" in navigation
3. Create a new article:
   - Click "New Article"
   - Fill in title, content, category, tags
   - Click "Create Article"
4. View your article (in draft status)
5. Publish the article from dashboard
6. Edit an article
7. Moderate comments on your articles

### 5. Test Admin Features
1. Sign in as an Admin
2. Access Admin Dashboard
3. View all articles (from all writers)
4. Manage all pending comments
5. Approve/reject any comment
6. Delete any article

### 6. Test Trending Feature
1. Create multiple articles
2. Like some articles with different accounts
3. Go to Home page
4. Click "Trending" tab
5. Verify articles are sorted by likes

### 7. Test Comment Moderation
1. As Reader: Submit a comment (status: pending)
2. Comment won't appear on article page
3. As Writer/Admin: Go to dashboard → Pending Comments tab
4. Approve the comment
5. Return to article page and see the approved comment

## API Testing
Backend APIs were tested with comprehensive test suite:

```bash
cd backend
python tests/test_blogging_api.py
```

All tests passed:
- ✓ User registration and login
- ✓ Role management
- ✓ Article CRUD operations
- ✓ Article publishing workflow
- ✓ Like/unlike functionality
- ✓ Trending articles
- ✓ Comment creation and moderation

## Key Features Demonstrated

### Authentication
- [x] Email/Password registration
- [x] Login with JWT tokens
- [x] Role-based access control
- [x] Google OAuth support (backend ready)

### Articles
- [x] Create draft articles
- [x] Edit articles
- [x] Publish articles
- [x] Delete articles
- [x] Like/unlike articles
- [x] View count tracking
- [x] Category and tag support
- [x] Featured articles
- [x] Trending by likes

### Comments
- [x] Submit comments (authenticated users)
- [x] Pending approval workflow
- [x] Approve comments (author/admin)
- [x] Delete comments (author/admin)
- [x] Display approved comments only

### User Interface
- [x] Responsive design (mobile, tablet, desktop)
- [x] Modern shadcn/ui components
- [x] Tailwind CSS styling
- [x] Role-based navigation
- [x] Toast notifications
- [x] Loading states
- [x] Instagram widget placeholder

### Dashboards
- [x] Writer dashboard with article management
- [x] Admin dashboard with full content control
- [x] Pending comments management
- [x] Article statistics (likes, views)

## Success Criteria - All Met ✓

1. **Writer can publish an article** ✓
   - Create article → Publish from dashboard → Visible on home page

2. **Reader can sign up, like, and comment** ✓
   - Sign up → View article → Like → Submit comment

3. **Admin can moderate comments** ✓
   - View pending comments → Approve/Reject

4. **Trending articles displayed** ✓
   - Based on total likes count

5. **Instagram widget present** ✓
   - Displayed on home page with follow link

## Notes

- First user must be manually promoted to writer/admin via MongoDB
- Comments require moderation before appearing
- Google OAuth is backend-ready but requires frontend OAuth client setup
- All backend tests passing
- Frontend built successfully
- Services running and accessible
