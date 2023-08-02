"""OAuth Client views."""


from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from ...utils import flash_errors
from .forms import EditForm, RegisterForm
from .models import Client

blueprint = Blueprint('oauth_client', __name__, url_prefix='/oauth/clients',
                      static_folder='../../static')


@blueprint.route('/')
@login_required
def home():
    """Client landing page."""
    if not current_user.is_admin:
        abort(403)

    clients = Client.query.all()

    return render_template('oauth/clients/home.html', clients=clients)


@blueprint.route('/register/', methods=['GET', 'POST'])
@login_required
def register():
    """Create new client."""
    if not current_user.is_admin:
        abort(403)

    register_form = RegisterForm(current_user, request.form)
    if register_form.validate_on_submit():
        user_id = None
        if register_form.user_id.data != -1:
            user_id = register_form.user_id.data
        Client.create_as(current_user,
                         name=register_form.name.data,
                         description=register_form.description.data,
                         user_id=user_id,
                         is_confidential=register_form.is_confidential.data,
                         redirect_uris=register_form.redirect_uris.data,
                         default_scopes=register_form.default_scopes.data,
                         created_by=current_user.id).save()
        flash(_('Client "%(name)s" created.', name=register_form.name.data), 'success')
        return redirect(url_for('oauth_client.home'))
    else:
        flash_errors(register_form)
    return render_template('oauth/clients/register.html', register_form=register_form)


@blueprint.route('/delete/<string:client_id>', methods=['GET', 'DELETE'])
@login_required
def delete(client_id):
    """Delete client."""
    if not current_user.is_admin:
        abort(403)

    client = Client.get_by_id(client_id)
    if not client:
        abort(404)
    else:
        name = client.name
        client.delete()
        flash(_('Successfully deleted OAuth2 Client "%(name)s".', name=name), 'success')
    return redirect(url_for('oauth_client.home'))


@blueprint.route('/edit/<string:client_id>', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    """Edit client details."""
    if not current_user.is_admin:
        abort(403)

    client = Client.get_by_id(client_id)
    if not client:
        abort(404)

    edit_form = EditForm(current_user, request.form)
    if edit_form.validate_on_submit():
        user_id = None
        if edit_form.user_id.data != -1:
            user_id = edit_form.user_id.data

        client.update_as(current_user,
                         name=edit_form.name.data, description=edit_form.description.data,
                         user_id=user_id,
                         is_confidential=edit_form.is_confidential.data,
                         redirect_uris=edit_form.redirect_uris.data,
                         default_scopes=edit_form.default_scopes.data).save()
        flash(_('Thank you for updating client details for "%(client_id)s".', client_id=client_id),
              'success')
        return redirect(url_for('oauth_client.home'))
    else:
        edit_form.set_defaults(client)
        flash_errors(edit_form)
        return render_template('oauth/clients/edit.html', edit_form=edit_form, client=client)
