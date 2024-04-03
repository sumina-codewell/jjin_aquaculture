from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) #pwd 역할
print(basedir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'posts.db')
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100))
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    mood = db.Column(db.String(20))
    comments = db.relationship('Comment', backref='post', lazy=True) # 게시글과 댓글의 관계

# 댓글 모델
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
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
    posts = Post.query.all()
    return render_template('jjookkumi.html', posts=posts)

# 게시글작성 라우트
@app.route('/write_post', methods=['POST'])
def write_post():
    anonymous_nickname = request.form['nickname']
    post_title = request.form['title']
    post_content = request.form['content']
    mood_emoji = request.form['mood']

    new_post = Post(nickname=anonymous_nickname, title=post_title,
                    content=post_content, mood=mood_emoji)

    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for('index'))

# 댓글 작성 라우트
@app.route('/write_comment/<int:post_id>', methods=['POST'])
def write_comment(post_id):
    post = Post.query.get_or_404(post_id)
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
