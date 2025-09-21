from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import uuid
from dotenv import load_dotenv
from ai_service import generate_caption_and_hashtags, generate_product_description, analyze_image_for_content

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create upload directories
os.makedirs('static/uploads/posts', exist_ok=True)
os.makedirs('static/uploads/products', exist_ok=True)
os.makedirs('static/uploads/profiles', exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'artisan' or 'buyer'
    bio = db.Column(db.Text)
    region = db.Column(db.String(100))
    craft_type = db.Column(db.String(100))
    profile_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    products = db.relationship('Product', backref='artisan', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy='dynamic')
    
    # Helper methods for following
    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
    
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
    
    def is_following(self, user):
        return self.following.filter_by(followed_id=user.id).first() is not None
    
    def followers_count(self):
        return self.followers.count()
    
    def following_count(self):
        return self.following.count()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.Text)
    hashtags = db.Column(db.Text)
    story = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    # Helper methods
    def likes_count(self):
        return self.likes.count()
    
    def comments_count(self):
        return self.comments.count()
    
    def is_liked_by(self, user):
        return self.likes.filter_by(user_id=user.id).first() is not None

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id'),)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id'),)

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/discover')
def discover():
    return render_template('discover.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not username or not email or not password or not role:
            return jsonify({'error': 'All fields are required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User()
        user.username = username
        user.email = email
        user.password_hash = generate_password_hash(password)
        user.role = role
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('feed')}), 200
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('feed')}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('feed.html', posts=posts)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    products = Product.query.filter_by(user_id=user.id).order_by(Product.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts, products=products)

# API Routes for AJAX interactions
@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    if current_user.role != 'artisan':
        return jsonify({'error': 'Only artisans can create posts'}), 403
    
    # Handle both JSON and form data
    if request.content_type and 'application/json' in request.content_type:
        data = request.get_json()
        image_url = data.get('image_url')
        caption = data.get('caption', '')
        hashtags = data.get('hashtags', '')
        story = data.get('story', '')
    else:
        # Handle form data with file upload
        caption = request.form.get('caption', '')
        hashtags = request.form.get('hashtags', '')
        story = request.form.get('story', '')
        
        # For now, use a placeholder image URL
        # In production, you'd upload the file to a storage service
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            # Save to static/uploads/posts directory
            upload_dir = os.path.join(app.static_folder, 'uploads', 'posts')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
            filename = str(uuid.uuid4()) + '.' + file_ext
            filepath = os.path.join(upload_dir, filename)
            image_file.save(filepath)
            
            # Generate URL for the image
            image_url = url_for('static', filename=f'uploads/posts/{filename}')
        else:
            return jsonify({'error': 'Image is required'}), 400
    
    if not image_url:
        return jsonify({'error': 'Image URL is required'}), 400
    
    post = Post(
        user_id=current_user.id,
        image_url=image_url,
        caption=caption,
        hashtags=hashtags,
        story=story
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Post created successfully',
        'post_id': post.id
    }), 201

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        liked = True
    
    db.session.commit()
    like_count = Like.query.filter_by(post_id=post_id).count()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'like_count': like_count
    })

@app.route('/api/posts/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def handle_comments(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Comment content is required'}), 400
        
        comment = Comment(
            user_id=current_user.id,
            post_id=post_id,
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'username': current_user.username,
                'created_at': comment.created_at.isoformat()
            }
        }), 201
    
    # GET comments
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify({
        'comments': [{
            'id': c.id,
            'content': c.content,
            'username': c.user.username,
            'created_at': c.created_at.isoformat()
        } for c in comments]
    })

@app.route('/api/follow/<int:user_id>', methods=['POST'])
@login_required
def toggle_follow(user_id):
    if current_user.role != 'buyer':
        return jsonify({'error': 'Only buyers can follow artisans'}), 403
    
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    target_user = User.query.get_or_404(user_id)
    if target_user.role != 'artisan':
        return jsonify({'error': 'Can only follow artisans'}), 400
    
    existing_follow = Follow.query.filter_by(follower_id=current_user.id, followed_id=user_id).first()
    
    if existing_follow:
        db.session.delete(existing_follow)
        following = False
    else:
        new_follow = Follow(follower_id=current_user.id, followed_id=user_id)
        db.session.add(new_follow)
        following = True
    
    db.session.commit()
    follower_count = Follow.query.filter_by(followed_id=user_id).count()
    
    return jsonify({
        'success': True,
        'following': following,
        'follower_count': follower_count
    })

# Marketplace Routes
@app.route('/marketplace')
@login_required
def marketplace():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.title.contains(search) | Product.description.contains(search))
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('marketplace.html', products=products, category=category, search=search)

@app.route('/api/products', methods=['POST'])
@login_required
def create_product():
    if current_user.role != 'artisan':
        return jsonify({'error': 'Only artisans can create products'}), 403
    
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    image_url = data.get('image_url', '').strip()
    category = data.get('category', '').strip()
    
    if not all([title, description, image_url]) or price is None:
        return jsonify({'error': 'All fields are required'}), 400
    
    try:
        price = float(price)
        if price <= 0:
            return jsonify({'error': 'Price must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid price format'}), 400
    
    product = Product(
        user_id=current_user.id,
        title=title,
        description=description,
        price=price,
        image_url=image_url,
        category=category
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'created_at': product.created_at.isoformat()
        }
    }), 201

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if current_user.role != 'buyer':
        return jsonify({'error': 'Only buyers can add items to cart'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    if product.user_id == current_user.id:
        return jsonify({'error': 'Cannot add your own product to cart'}), 400
    
    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing_item:
        existing_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'success': True,
        'message': 'Product added to cart',
        'cart_count': cart_count
    })

@app.route('/api/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id):
    if current_user.role != 'buyer':
        return jsonify({'error': 'Only buyers can add items to wishlist'}), 403
    
    product = Product.query.get_or_404(product_id)
    
    if product.user_id == current_user.id:
        return jsonify({'error': 'Cannot add your own product to wishlist'}), 400
    
    existing_item = WishlistItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing_item:
        return jsonify({'error': 'Product already in wishlist'}), 400
    
    wishlist_item = WishlistItem(user_id=current_user.id, product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Product added to wishlist'
    })

@app.route('/cart')
@login_required
def view_cart():
    if current_user.role != 'buyer':
        return redirect(url_for('feed'))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

# Search and Discovery
@app.route('/api/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # 'artisans', 'products', 'all'
    
    results = {'artisans': [], 'products': []}
    
    if query:
        if search_type in ['artisans', 'all']:
            artisans = User.query.filter(
                User.role == 'artisan',
                (User.username.contains(query) | 
                 User.craft_type.contains(query) | 
                 User.region.contains(query))
            ).limit(10).all()
            
            results['artisans'] = [{
                'id': u.id,
                'username': u.username,
                'craft_type': u.craft_type,
                'region': u.region,
                'profile_image': u.profile_image
            } for u in artisans]
        
        if search_type in ['products', 'all']:
            products = Product.query.filter(
                Product.title.contains(query) | 
                Product.description.contains(query) |
                Product.category.contains(query)
            ).limit(10).all()
            
            results['products'] = [{
                'id': p.id,
                'title': p.title,
                'price': p.price,
                'image_url': p.image_url,
                'artisan': p.artisan.username
            } for p in products]
    
    return jsonify(results)

# AI-powered Content Generation Routes
@app.route('/api/ai/generate-caption', methods=['POST'])
@login_required
def ai_generate_caption():
    if current_user.role != 'artisan':
        return jsonify({'error': 'Only artisans can use AI content generation'}), 403
    
    data = request.get_json()
    image_description = data.get('image_description', '')
    craft_type = current_user.craft_type
    
    if not image_description:
        return jsonify({'error': 'Image description is required'}), 400
    
    result = generate_caption_and_hashtags(image_description, craft_type)
    
    return jsonify({
        'success': True,
        'caption': result['caption'],
        'hashtags': result['hashtags'],
        'story': result['story']
    })

@app.route('/api/ai/generate-product-description', methods=['POST'])
@login_required
def ai_generate_product_description():
    if current_user.role != 'artisan':
        return jsonify({'error': 'Only artisans can use AI content generation'}), 403
    
    data = request.get_json()
    title = data.get('title', '')
    basic_description = data.get('basic_description', '')
    price = data.get('price')
    craft_type = current_user.craft_type
    
    if not title or not basic_description:
        return jsonify({'error': 'Title and basic description are required'}), 400
    
    enhanced_description = generate_product_description(title, basic_description, craft_type, price)
    
    return jsonify({
        'success': True,
        'description': enhanced_description
    })

@app.route('/api/ai/analyze-image', methods=['POST'])
@login_required
def ai_analyze_image():
    if current_user.role != 'artisan':
        return jsonify({'error': 'Only artisans can use AI image analysis'}), 403
    
    data = request.get_json()
    base64_image = data.get('base64_image', '')
    
    if not base64_image:
        return jsonify({'error': 'Base64 image data is required'}), 400
    
    analysis = analyze_image_for_content(base64_image)
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)