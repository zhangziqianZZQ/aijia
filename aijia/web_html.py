from flask import current_app,make_response,Blueprint
from flask_wtf import csrf

html = Blueprint('web_html',__name__)

@html.route("/<re('.*'):html_file_name>")
def get_html(html_file_name):
    if not html_file_name:
        html_file_name = 'index.html'
    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name
    csrf_token = csrf.generate_csrf()
    resp = make_response(current_app.send_static_file(html_file_name))
    resp.set_cookie('csrf_token',csrf_token)
    return resp