import pickle

def check_logged_in(request):
    r = {}
    if "arara_session_key" in request.session:
        sess = request.session['arara_session_key']
        r['logged_in'] = True
        r['username'] = request.session.get('arara_username', 0);
    else:
        sess = ""
        r['logged_in'] = False
        r['id'] = ""

    return sess, r

