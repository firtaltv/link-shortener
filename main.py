from flask import Flask, request, render_template
import hashlib
import flask
import redis
from wtforms import Form, StringField
from wtforms.validators import DataRequired
from werkzeug.exceptions import abort

app = Flask(__name__)
redis_db = redis.Redis()


class UrlInputForm(Form):
    inputField = StringField(label="Paste here", validators=[DataRequired()])


def random_slug(link: str):
    encoded = link.encode()
    hash_object = hashlib.sha256(encoded)
    return hash_object.hexdigest()[2:13:2]


@app.route('/', methods=['post', 'get'])
def index():
    form = UrlInputForm(request.form)
    if request.method == "POST" and form.validate():
        slug = random_slug(form.inputField.data)
        if redis_db.get(slug):
            redis_db.expire(slug, 3600)
        else:
            redis_db.set(slug, form.inputField.data)
            redis_db.expire(slug, 3600)
        return flask.redirect(f'http://127.0.0.1:5000/shortened/{slug}')
    return render_template('index.html', form=form)


@app.route('/shortened/<slug>/')
def shortened(slug):
    link_to = redis_db.get(slug)
    url = f'http://127.0.0.1:5000/{slug}'
    if link_to:
        return render_template('shortened.html', data={'link_to': link_to.decode('utf-8'), 'url': url})
    else:
        abort(404)


@app.route('/<slug>/')
def redirect(slug):
    link_to = redis_db.get(slug)
    if link_to:
        return flask.redirect(link_to.decode('utf-8'))
    else:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
    # random_slug("https://www.javatpoint.com/django-model")
