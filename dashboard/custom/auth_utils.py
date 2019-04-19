from firebase_admin import auth


def is_authenticated(request):
    try:
        token = request.session['tk']
    except KeyError:
        return False

    try:
        _ = auth.verify_id_token(token)
    except ValueError:
        return False

    return True
