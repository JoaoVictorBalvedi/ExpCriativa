from flask import Blueprint, request, render_template, redirect, url_for

usuario = Blueprint("usuario", __name__, template_folder="templates")


users = {
"anne":"123",
}

users_adm = {
"thony":"123"
}


@usuario.route('/')
def index():
    return render_template("home.html")

@usuario.route("/login")
def login():
    return render_template("login.html")


@usuario.route("/validated_user", methods=['POST'])
def validated_user():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        print(user, password)
        if user in users and users[user] == password:
            return render_template('userpage.html')
        elif user in users_adm and users_adm[user] == password:
            return render_template('admpage.html')
        else:
            return '<h1>invalid credentials!</h1>'
    else:
        return render_template('login.html')

@usuario.route("/gestaouseradm")
def gestaouseradm():
    return render_template("gestaouseradm.html", users = users, users_adm = users_adm)

@usuario.route('/add_user', methods=['GET','POST'])
def add_users():
    global users
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        users[user] = password
    else:
        user = request.args.get('user', None)
        password = request.args.get('password', None)
        
    return redirect(url_for('usuario.gestaouseradm'))

@usuario.route('/del_user', methods=['GET', 'POST'])
def del_user():
    global users, users_adm
    if request.method == 'POST':
        user_data = request.form['user']
        user = user_data.split('|')[0]
        if user in users:
            users.pop(user)
        elif user in users_adm:
            users_adm.pop(user)
        else:
            return "Usuário não encontrado", 404
    else:
        user = request.args.get('user', None)
        if user in users:
            users.pop(user)
        elif user in users_adm:
            users_adm.pop(user)
        else:
            return "Usuário não encontrado", 404

    return redirect(url_for('usuario.gestaouseradm'))

@usuario.route('/att_user', methods=['GET', 'POST'])
def att_user():
    global users
    if request.method == 'POST':
        current_user = request.form['current_user']
        new_user = request.form['new_user']
        password = request.form['password']
        
        if current_user in users:
            users[new_user] = password
            if current_user != new_user:
                del users[current_user]
        elif current_user in users_adm:
            users_adm[new_user] = password
            if current_user != new_user:
                del users_adm[current_user]
        else:
            return "Usuário não encontrado", 404
    else:
        current_user = request.args.get('current_user', None)
        new_user = request.args.get('new_user', None)
        password = request.args.get('password', None)
        
        if current_user and new_user and password and current_user in users:
            users[new_user] = password
            if current_user != new_user:
                del users[current_user]
        elif current_user and new_user and password and current_user in users_adm:
            users_adm[new_user] = password
            if current_user != new_user:
                del users_adm[current_user]
        else:
            return "Usuário não encontrado ou dados inválidos", 404
        
    return redirect(url_for('usuario.gestaouseradm'))

