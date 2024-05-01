from flask import Flask, render_template,redirect, url_for

app = Flask(
    __name__
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-site')
def add_site():
    return render_template('add_site.html')

@app.route('/assign-site')
def assign_site():
    return render_template('assign_site.html')

@app.route('/assets/images/<path:path>')
def asset_images_govuk(path):
    return redirect('/static/gov-uk-frontend/assets/images/' + path, code=301)

@app.route('/assets/fonts/<path:path>')
def asset_fonts(path):
    return redirect('/static/gov-uk-frontend/assets/fonts/' + path, code=301)


if __name__ == '__main__':
    app.run(debug=True)
