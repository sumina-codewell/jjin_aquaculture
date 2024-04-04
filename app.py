from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os

#이미지 업로드하려면 이거 써야됨.
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'image')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 폴더 없으면 생성함. 
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    
basedir = os.path.abspath(os.path.dirname(__file__)) #pwd 역할
print(basedir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'jkmi.db')
db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Method POST 방식과 명칭 헷갈림 지양함. 
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100))
    title = db.Column(db.String(50))
    content = db.Column(db.Text)
    mood = db.Column(db.String(20))
    image_filename = db.Column(db.String(100), nullable=True)
    comments = db.relationship('Comment', backref='article', lazy=True) # 게시글과 댓글의 관계

# 댓글 모델
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    comment_pw = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()

# 게시글 및 댓글 조회 라우트(Modal)
@app.route('/')
def main():
    # 여기에 데이터베이스에서 게시글을 조회하는 코드를 추가할 수 있습니다.
    articles = Article.query.all()
    return render_template('jjookkumi.html', posts=articles)

# 게시글 작성 라우트
@app.route('/write_article', methods=['POST'])
def write_article():
    anonymous_nickname = request.form['nickname']
    article_title = request.form['title']
    article_content = request.form['content']
    mood_emoji = request.form['mood']
    image = request.files['image']

    # 기존 게시글 처리 로직
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(file_path)
            # 이미지 파일명을 데이터베이스에 저장
        new_article = Article(nickname = anonymous_nickname, title=article_title, content=article_content, mood=mood_emoji, image_filename=filename)
    else:
        # 이미지 없이 게시글 처리 로직
        new_article = Article(nickname=anonymous_nickname, title=article_title,
                    content=article_content, mood=mood_emoji)

    db.session.add(new_article)
    db.session.commit()

    return redirect(url_for('main'))

# 댓글 작성 라우트
@app.route('/write_comment/<int:post_id>', methods=['POST'])
def write_comment(post_id):
    post = Article.query.get_or_404(post_id)
    comment_content = request.form['comment_content']
    comment_author = request.form['comment_author']
    new_comment = Comment(content=comment_content, author=comment_author, post=post)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('main'))

#reply 페이지 이동 라우트
@app.route("/reply/")
def reply():
    return render_template('suminreply2.html')


if __name__ == '__main__':
    app.run(debug=True)
