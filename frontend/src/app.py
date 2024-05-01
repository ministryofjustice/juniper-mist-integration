from flask import Flask, render_template,redirect, url_for

app = Flask(
    __name__
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/images/govuk-crest-2x.png')
def subpage():
    return redirect('http://localhost:5000/static/gov-uk-frontend/assets/images/govuk-crest-2x.png', code=301)


if __name__ == '__main__':
    app.run(debug=True)
