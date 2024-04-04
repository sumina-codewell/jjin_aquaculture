from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import datetime
from werkzeug.utils import secure_filename
import unicodedata

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

#한국어 파일명 작업
def secure_filename_with_unicode(filename):
    file, ext = os.path.splitext(filename)
    file = file.replace(' ', '_')  # 공백을 밑줄로 대체
    file = ''.join(e for e in file if e.isalnum() or e in {'_', '-'})
    return f"{file}{ext}"

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
    comment_pw = db.Column(db.Integer)

with app.app_context():
    db.create_all()

# 게시글 및 댓글 조회 라우트(Modal)
@app.route('/')
def main():
    # 여기에 데이터베이스에서 게시글을 조회하는 코드를 추가할 수 있습니다.
    articles = Article.query.all()
    return render_template('jjookkumi.html', articles=articles)

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
        filename = secure_filename_with_unicode(image.filename)
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

# 게시글 상세 
@app.route('/article/<int:article_id>')
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article_detail.html', article=article)

# 댓글 작성 라우트
@app.route('/write_comment/<int:article_id>', methods=['POST'])
def write_comment(article_id):
    article = Article.query.get_or_404(article_id)
    comment_content = request.form['comment_content']
    comment_author = request.form['comment_author']
    comment_pw = request.form['comment_pw'] 
    # 현재 시간을 생성 시간으로 설정
    now = datetime.datetime.now()
    new_comment = Comment(content=comment_content, author=comment_author, article=article, created_at=now, comment_pw=comment_pw)
    
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('article_detail', article_id=article_id))

# 댓글 수정 라우트
@app.route('/edit_comment/<int:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    data = request.json
    comment_pw = data.get('comment_pw')
    comment_content = data.get('comment_content') 
    comment = Comment.query.get_or_404(comment_id)
    
    # 비밀번호가 일치할 때만 댓글 수정을 허용
    if comment.comment_pw == int(comment_pw):
        comment.content = comment_content
        db.session.commit()

        return jsonify({'message': '댓글이 수정되었습니다.'}), 200
    else:
        return jsonify({'error': '잘못된 비밀번호입니다.'}), 403

# 댓글 삭제 라우트
@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment_pw = request.form['comment_pw']
    # 비밀번호가 일치할 때만 댓글 삭제를 허용
    if comment.comment_pw == int(comment_pw):
        db.session.delete(comment)
        db.session.commit()
        return "<script>alert('댓글이 삭제되었습니다.'); window.location.href = document.referrer;</script>"
    else:
        return "<script>alert('잘못된 비밀번호입니다.'); window.location.href = document.referrer;</script>"

#reply 페이지 이동 라우트
@app.route("/reply/")
def reply():
    return render_template('suminreply2.html')


if __name__ == '__main__':
    app.run(debug=True)
