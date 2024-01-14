from flask import render_template, session
from backend import app, GLOBAL_VARS
from backend.forms.common import LoadMoreForm
from backend.routes_functions import flash_messages_and_load_more, check_uid, asqit

if __name__ == '__main__':
    raise AssertionError("run app.py and not this file")

""" ------------- Errors ------------- """


@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template('domain_error.html')


@app.route("/highway", methods=['GET', 'POST'])
def highway():
    return render_template('agent_error.html')


@app.route("/explanation", methods=['GET', 'POST'])
def explanation():
    user_id = session['user_id']
    form = LoadMoreForm()
    if GLOBAL_VARS['videos'][user_id]:
        if form.validate_on_submit():
            flash_messages_and_load_more()
        return render_template('explanation.html', form=form,
                               videos=GLOBAL_VARS['videos'][user_id], home=session['home'],
                               query=session['query'])
    return render_template('explanation.html', home=session['home'], query=session['query'])


""" ---------------- AGENTS ---------------- """
@app.route("/highway/plain", methods=['GET', 'POST'])
def highway_plain():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Plain'
    session['home'] = 'highway_plain'
    return asqit()
