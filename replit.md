# ArtConnect - AI-Powered Social Marketplace for Local Artisans

## Overview
ArtConnect is a full-stack web application that combines social media features with an AI-powered marketplace for local artisans. Built with Flask (Python) backend and modern HTML/CSS/JavaScript frontend, inspired by Instagram + Etsy.

## Project Status
✅ **Complete** - All core features implemented and functional
- Authentication system with Artisan/Buyer roles
- Social media feed with posts, likes, comments, following
- AI-powered content generation using Google Gemini
- Marketplace with product listings and shopping cart
- Search and discovery features
- Responsive Instagram-inspired UI

## Key Features Implemented

### 1. Authentication System
- User registration and login with role selection (Artisan/Buyer)
- Session management with Flask-Login
- Role-based access control for features

### 2. Social Media Features
- Instagram-style feed showing artisan posts
- Like and comment functionality
- Follow/unfollow system for buyers to follow artisans
- Real-time UI updates for social interactions

### 3. AI Integration (Google Gemini)
- **Caption Generation**: AI suggests engaging captions and hashtags for posts
- **Product Descriptions**: AI generates compelling marketplace descriptions
- **Image Analysis**: AI analyzes uploaded artwork to suggest content
- **Storytelling**: AI creates background stories about crafts

### 4. Marketplace
- Product listing system for artisans
- Shopping cart and wishlist functionality
- Category filtering and search
- Price display and artisan attribution

### 5. User Profiles
- Comprehensive artisan profiles with bio, region, craft type
- Portfolio display with posts and products
- Follower/following counts and statistics

### 6. Search & Discovery
- Search artisans by craft type, location, keywords
- Product search across titles and descriptions
- Filter by categories and regions

## Technical Architecture

### Backend (Flask/Python)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite for development (easily upgradeable to PostgreSQL)
- **Authentication**: Flask-Login with secure password hashing
- **AI Service**: Google Gemini integration for content generation
- **API**: RESTful endpoints for all functionality

### Frontend
- **UI Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with Fetch API for AJAX interactions
- **Design**: Instagram-inspired clean, minimal interface
- **Icons**: Font Awesome for consistent iconography

### Database Schema
- **Users**: id, username, email, password_hash, role, bio, region, craft_type
- **Posts**: id, user_id, image_url, caption, hashtags, story, created_at
- **Products**: id, user_id, title, description, price, image_url, category
- **Likes**: user_id, post_id (unique constraint)
- **Comments**: id, user_id, post_id, content, created_at
- **Follow**: follower_id, followed_id (unique constraint)
- **Cart/Wishlist**: user_id, product_id relationships

## Key API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Social Features
- `POST /api/posts` - Create new post
- `POST /api/posts/<id>/like` - Toggle like on post
- `GET/POST /api/posts/<id>/comments` - Handle comments
- `POST /api/follow/<user_id>` - Toggle follow relationship

### Marketplace
- `GET /marketplace` - Browse products with filtering
- `POST /api/products` - Create product listing
- `POST /api/cart/add/<product_id>` - Add to cart
- `POST /api/wishlist/add/<product_id>` - Add to wishlist

### AI Features
- `POST /api/ai/generate-caption` - AI caption generation
- `POST /api/ai/generate-product-description` - AI product descriptions
- `POST /api/ai/analyze-image` - AI image analysis

### Search
- `GET /api/search` - Search artisans and products

## Environment Setup
- **Python**: 3.11 with Flask ecosystem
- **Dependencies**: Flask, SQLAlchemy, Flask-Login, google-genai, Pillow
- **Secrets**: GEMINI_API_KEY (for AI features), SESSION_SECRET
- **Port**: 5000 (configured for Replit hosting)

## Recent Changes (September 20, 2025)
- Implemented complete Flask backend with all core functionality
- Created responsive frontend with Instagram-inspired design
- Integrated Google Gemini AI for content generation features
- Added comprehensive social features (likes, comments, following)
- Built marketplace with cart and wishlist functionality
- Implemented search and discovery features
- Added role-based access control throughout application
- Created all necessary database models and relationships

## User Preferences
- Preferred AI: Google Gemini (switched from OpenAI per user request)
- UI Style: Instagram-inspired, clean and minimal
- Focus: Social marketplace combining creativity with commerce
- Target Users: Local artisans and buyers interested in handcrafted items

## Next Phase Enhancements (Future)
- Real-time notifications system
- Payment gateway integration
- Advanced AI recommendation system
- Admin dashboard for content moderation
- Image enhancement features
- Multi-language support
- Mobile app development
- Advanced analytics and insights

## Deployment
- Configured for Replit hosting with Flask development server
- Ready for production deployment with WSGI server
- Database can be upgraded to PostgreSQL for production scale
- All static assets properly organized and cached