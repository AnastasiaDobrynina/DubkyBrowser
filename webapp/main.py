from flask import Flask, render_template, request, redirect, flash, session, url_for
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

API_URL = "http://localhost:8000"


@app.route('/')
def home():
    return render_template('index.html',
                           current_user=session)


@app.route('/search')
def search_page():
    return render_template('search.html',
                           current_user=session)

@app.route('/res', methods=['GET', 'POST'])
def search_res():
    if request.method == 'POST':
        query_data = {
            "query": request.form['text-q'],
            "quantity": request.form['quantity'],
            "search_type": request.form['type']
        }
        print(query_data)
        response = requests.post(f"{API_URL}/search", json=query_data)
        print(response)
        if response.status_code == 200:
            print('запрос корректный')
            return render_template('search.html',
                                   data=response.json(),
                                   current_user=session)
        else:
            flash(response.json().get("detail", "Корректно заполните все полч"), "danger")
    print('я не делаю запрос')
    return render_template('search.html',
                           current_user=session)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            "login": request.form['login'],
            "name": request.form['name'],
            "password": request.form['password'],
            "gender": request.form.get('gender') if request.form.get('gender') else None,
            "age": request.form.get('age') if request.form.get('age') else None
        }
        response = requests.post(f"{API_URL}/register", json=user_data)
        if response.status_code == 200:
            return redirect(url_for('login'))
        else:
            flash(response.json().get("detail", "Error during registration"), "danger")
    return render_template('register.html',
                           current_user=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credentials = {
            "login": request.form['login'],
            "password": request.form['password']
        }
        response = requests.post(f"{API_URL}/login", json=credentials)
        if response.status_code == 200:
            session['user_login'] = request.form['login']
            return redirect(url_for('profile'))
        else:
            flash(response.json().get("detail", "Invalid login or password"), "danger")
    return render_template('login.html')


@app.route('/profile')
def profile():
    user_login = session.get('user_login')
    if not user_login:
        flash("Please log in to view your profile", "warning")
        return redirect(url_for('login'))

    response = requests.get(f"{API_URL}/profile/{user_login}")
    if response.status_code == 200:
        print(response.json())
        return render_template('personal_page.html',
                                current_user=session,
                                user_data=response.json(),
                                auth=True)
    else:
        flash("Failed to load profile", "danger")
        return redirect(url_for('login',
                                current_user=session))


@app.route('/logout')
def logout():
    session.pop('user_login', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
