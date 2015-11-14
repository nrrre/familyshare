#encoding:utf-8

import MySQLdb
import MySQLdb.cursors
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
# import sae.const

import sys
reload(sys)
sys.setdefaultencoding('utf8')


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='hahah-2333'
))
MYSQL_DB = 'family'      # 数据库名
MYSQL_USER = 'root'    # 用户名
MYSQL_PASS = '2333'    # 密码
MYSQL_HOST = 'localhost'    # 主库域名（可读写）
MYSQL_PORT = 3306


def connect_db():
    """Connects to the specific database."""
    conn = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB, \
        port=int(MYSQL_PORT), charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
    return conn


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db


@app.teardown_request
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()


@app.route('/testt')
def test():
    db = get_db()
    cur = db.cursor()
    cur.execute('select * from testt')
    create_dates = cur.fetchall()
    print create_dates
    return create_dates

@app.route('/')
def show_entries():
    if session.get('logged_in'):
        db = get_db()
        cur = db.cursor()
        cur.execute('select * from share,user where share.user_id=user.id order by share.id desc')
        entries = cur.fetchall()

        for entry in entries:
            cur.execute('select * from reply where share_id=%d order by id' % entry['id'])
            replys = cur.fetchall()
            if replys:
                for reply in replys:
                    cur.execute('select nickname from user where id=%d' % int(reply['user_id']))
                    nickname = cur.fetchall()[0]['nickname']
                    reply['nickname'] = nickname
                entry['replys'] = replys

        return render_template('show_entries.html', entries=entries)
    else:
        return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.cursor()
    cur.execute('insert into share (user_id, content) values ("%d", "%s")' % \
               (int(session['user']),
                request.form['text'].encode('utf8')))
    db.commit()
    flash('您的分享已经成功发布！')
    return redirect(url_for('show_entries'))

@app.route('/reply/<int:share_id>', methods=['POST'])
def reply(share_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.cursor()
    cur.execute('insert into reply (content, share_id, user_id) values ("%s", "%d", "%d")' % \
        (request.form['reply_content'],
        share_id,
        int(session['user'])))
    db.commit()
    flash('回复成功！')
    return redirect(url_for('show_entries'))

@app.route('/del/<int:share_id>')
def delete(share_id):
    db = get_db()
    cur = db.cursor()
    cur.execute('select user_id from share where id = %d' % share_id)
    share = cur.fetchall()
    if session['user'] == int(share[0]['user_id']):
        cur.execute('delete from share where id = %d' % share_id)
        db.commit()
        cur.execute('delete from reply where share_id = %d' % share_id)
        db.commit()
        flash('已成功删除您的分享！')
        return redirect(url_for('show_entries'))
    else:
        flash('您不能删除他人的分享！')
        return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute('select passwd, id from user where username="%s"' % \
            request.form['username'])
        user_info = cur.fetchone()
        if user_info:
            if user_info['passwd'] == request.form['password']:
                session['logged_in'] = True
                session['user'] = user_info['id']
                flash('You were logged in')
                return redirect(url_for('show_entries'))
            else:
                error = '密码错误！'
        else:
            error = '用户名错误！'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
