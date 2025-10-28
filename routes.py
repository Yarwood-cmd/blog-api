from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, Post

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to the Blog API!',
        'endpoints': {
            'register': '/api/register',
            'login': '/api/login',
            'posts': '/api/posts'
        }
    }), 200

# User Registration
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

# User Login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Get all posts
@api.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat()
    } for post in posts]), 200

# Get single post
@api.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat()
    }), 200

# Create new post (requires authentication)
@api.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    
    post = Post(
        title=data['title'],
        content=data['content'],
        user_id=current_user_id
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'message': 'Post created successfully', 'id': post.id}), 201

# Update post (requires authentication)
@api.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'}), 200

# Delete post (requires authentication)
@api.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    
    if post.user_id != current_user_id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200


