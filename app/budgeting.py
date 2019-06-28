from flask import Flask, render_template
from flask_cas import CAS, login_required
from database import db, Conferences, People

def currencyformat(value):
	if value is None:
		return '$0.00'
	return "${:,.2f}".format(value)

app = Flask(__name__)
cas = CAS(app, '/cas')
app.config.from_object('config.Dev')
app.jinja_env.filters['currencyformat'] = currencyformat
db.init_app(app)

@app.route('/')
@login_required
def main():
	user = People.query.filter(People.username == cas.username).first()
	return render_template('default.html', user=user)

@app.route('/conferences', methods = ['GET'])
@login_required
def conference():
	user = People.query.filter(People.username == cas.username).first()
	return render_template('conferences.html', user = user)

if __name__ == "__main__":
	app.run(host = '0.0.0.0', port = 5000)
