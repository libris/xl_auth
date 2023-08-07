"""Test listing grants."""


from flask import url_for


def test_superuser_can_list_existing_grant(superuser, grant, testapp):
    """List existing grants."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # Clicks Grant button
    # res = res.click(href=url_for('oauth_grant.home'))
    # FIXME: No nav link yet
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('oauth_grant.home'))) == []

    res = testapp.get('/oauth/grants/')

    # The grant is listed under existing grants
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(grant.user.email))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(grant.client.name))) == 1


def test_user_cannot_list_existing_grant(user, testapp):
    """Attempt to list existing grants."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # No Grant home link for regular users
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('oauth_grant.home'))) == []

    # Try to go there directly
    testapp.get(url_for('oauth_grant.home'), status=403)
