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


with app.app_context():
    db.create_all()

# Modal
@app.route('/')
def main():
    # 여기에 데이터베이스에서 게시글을 조회하는 코드를 추가할 수 있습니다.
    posts = Post.query.all()
    return render_template('jjookkumi.html', posts=posts)


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

#reply

@app.route("/reply/")
def reply():
    return render_template('suminreply2.html')


if __name__ == '__main__':
    app.run(debug=True)
