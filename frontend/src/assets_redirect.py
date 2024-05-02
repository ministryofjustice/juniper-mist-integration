from flask import Blueprint

redirects_blueprint = Blueprint('redirects',__name__)


@redirects_blueprint.route('/images/<path:path>')
def asset_images_govuk(path):
    return redirect('/static/gov-uk-frontend/assets/images/' + path, code=301)

@redirects_blueprint.route('/fonts/<path:path>')
def asset_fonts(path):
    return redirect('/static/gov-uk-frontend/assets/fonts/' + path, code=301)
