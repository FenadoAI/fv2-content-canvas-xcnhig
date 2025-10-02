# Blogging Platform Implementation Plan

## Phase 1: Backend APIs

### Database Schema
1. **users collection**: _id, email, password_hash, name, role (admin/writer/reader), google_id, profile_pic, created_at
2. **articles collection**: _id, title, content, author_id, author_name, category, tags[], status (draft/published), likes_count, views_count, featured, created_at, updated_at, published_at
3. **comments collection**: _id, article_id, user_id, user_name, content, status (pending/approved/rejected), created_at
4. **likes collection**: _id, article_id, user_id, created_at
5. **settings collection**: _id, key, value (for about us, Instagram feed URL, etc.)

### API Endpoints

#### Auth APIs
- POST /api/auth/register (email, password, name)
- POST /api/auth/login (email, password) → JWT token
- POST /api/auth/google (google_token) → JWT token
- GET /api/auth/me (verify token)

#### User APIs
- GET /api/users (admin only) - list all users
- PUT /api/users/:id/role (admin only) - update user role
- GET /api/users/:id - get user profile

#### Article APIs
- POST /api/articles (writer/admin) - create article
- PUT /api/articles/:id (owner/admin) - update article
- DELETE /api/articles/:id (owner/admin) - delete article
- GET /api/articles - list articles (with filters: status, category, author)
- GET /api/articles/:id - get single article
- PUT /api/articles/:id/publish (owner/admin) - publish article
- POST /api/articles/:id/like - like/unlike article
- GET /api/articles/trending - get trending articles (by likes)
- GET /api/articles/featured - get featured articles

#### Comment APIs
- POST /api/comments (authenticated) - create comment
- GET /api/comments/:article_id - get approved comments for article
- PUT /api/comments/:id/approve (admin/author) - approve comment
- DELETE /api/comments/:id (admin/author) - delete comment
- GET /api/comments/pending (admin/author) - get pending comments

#### Settings APIs
- GET /api/settings/:key - get setting value
- PUT /api/settings/:key (admin) - update setting

## Phase 2: Frontend Pages

### Public Pages
1. **Home** (`/`)
   - Hero section
   - Featured articles
   - Trending articles (by likes)
   - Category filters
   - Instagram feed embed

2. **Article** (`/article/:id`)
   - Article content
   - Author info
   - Like button
   - Comments section
   - Related articles

3. **About Us** (`/about`)
   - Team information
   - Client information

### Auth Pages
4. **Sign Up** (`/signup`)
   - Email/password form
   - Google OAuth button

5. **Sign In** (`/signin`)
   - Email/password form
   - Google OAuth button

### Dashboard Pages
6. **Writer Dashboard** (`/dashboard/writer`)
   - My articles list
   - Create/edit article form
   - Pending comments on my articles

7. **Admin Dashboard** (`/dashboard/admin`)
   - All articles management
   - User management
   - All comments moderation
   - Settings management

## Phase 3: Testing & Deployment
- Test all APIs
- Build frontend
- Restart services
- Verify end-to-end flows

## Success Criteria
✓ Writer can publish an article
✓ Reader can sign up, like, comment
✓ Admin can moderate comments
✓ Instagram widget displays
✓ Trending articles shown on home
