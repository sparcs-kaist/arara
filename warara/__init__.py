
def check_logged_in(request, r):
    if "arara_session_key" in request.session:
        sess = request.session["arara_session_key"]
        r['logged_in'] = True
    else:
        sess = ""
        r['logged_in'] = False

    return sess

