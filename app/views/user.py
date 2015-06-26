from flask import redirect, url_for, request, g, render_template
from flask.ext.login import LoginManager, login_user, logout_user, current_user
import ldap

from app import telomere
from app.model.user import User

login_manager = LoginManager()
login_manager.init_app(telomere)
login_manager.login_view = "login" 
 
@login_manager.user_loader
def load_user(userId):
    return User.query.filter_by(id=userId).first()
 
@telomere.before_request
def get_current_user():
    g.user = current_user

@telomere.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@telomere.route("/login",methods=["GET", "POST"])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if validateLDAP(username,password):
            user = User.query.filter_by(username=username).first()
 
            if not user:
                user = User(username)
                db.session.add(user)
                db.session.commit()

            login_user(user)
            return redirect(url_for('index'))

    return render_template('user/login.html')

def validateLDAP(username,password):
    ld = ldap.initialize(telomere.config['LDAP_URL'])
    try:
        ld.simple_bind_s(
            'uid={0},{1}'.format(username, telomere.config['LDAP_BASEDN']),
            password
        )
        print "Validated user"
        return True
    except ldap.LDAPError, e:
        print "authentication error"
        print e
        return False

