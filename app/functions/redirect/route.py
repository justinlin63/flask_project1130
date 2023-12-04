from .use_model import *
from . import redirect_blueprint


@redirect_blueprint.route('/<info>')
def redirect_info(info):
    info = str(info)
    return render_template('redirect.html', home_bool=1, info=info)
