from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=3)  # 1: 高, 2: 中, 3: 低
    category = db.Column(db.String(50), nullable=True)

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    category_filter = request.args.get('category', '')
    
    query = Todo.query
    
    if search_query:
        query = query.filter(Todo.title.like(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Todo.category == category_filter)
        
    if sort_by == 'due_date':
        query = query.order_by(Todo.due_date.asc())
    elif sort_by == 'priority':
        query = query.order_by(Todo.priority.asc())
    else:
        query = query.order_by(Todo.created_at.desc())
        
    todos = query.all()
    categories = db.session.query(Todo.category).distinct().all()
    
    return render_template('index.html', 
                         todos=todos, 
                         search_query=search_query,
                         categories=categories,
                         current_category=category_filter,
                         sort_by=sort_by)

@app.route('/create', methods=['POST'])
def create():
    title = request.form.get('title')
    due_date_str = request.form.get('due_date')
    priority = request.form.get('priority', 3)
    category = request.form.get('category')
    
    if title:
        todo = Todo(
            title=title,
            priority=priority,
            category=category
        )
        if due_date_str:
            todo.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        db.session.add(todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:id>')
def toggle(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=5000)