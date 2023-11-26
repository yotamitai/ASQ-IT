from flask import render_template, session
from backend import app, GLOBAL_VARS
from backend.forms.common import LoadMoreForm
from backend.routes_functions import flash_messages_and_load_more, run_domain, check_uid, \
    check_uid_highlights, experiment_asqit, experiment_highlights, asqit, highlights

if __name__ == '__main__':
    raise AssertionError("run app.py and not this file")

""" ------------- Errors ------------- """


@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template('domain_error.html')


@app.route("/frogger", methods=['GET', 'POST'])
def frogger():
    return render_template('agent_error.html')


@app.route("/highway", methods=['GET', 'POST'])
def highway():
    return render_template('agent_error.html')


@app.route("/explanation", methods=['GET', 'POST'])
def explanation():
    user_id = session['user_id']
    # log_msg(f"TEST - 1  Time: {datetime.now()}, \t{user_id}")
    form = LoadMoreForm()
    if GLOBAL_VARS['videos'][user_id]:
        if form.validate_on_submit():
            # log_msg(f"TEST - 2  Time: {datetime.now()}, \t{user_id}")
            flash_messages_and_load_more()
        # log_msg(f"TEST - 3  Time: {datetime.now()}, \t{user_id}")
        return render_template('explanation.html', form=form,
                               videos=GLOBAL_VARS['videos'][user_id], home=session['home'],
                               query=session['query'])
    # log_msg(f"TEST - 4  Time: {datetime.now()}, \t{user_id}")
    return render_template('explanation.html', home=session['home'], query=session['query'])


""" ---------------- AGENTS ---------------- """


@app.route("/frogger/expert", methods=['GET', 'POST'])
def frogger_expert():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'frogger'
    session['agent'] = 'Expert'
    session['home'] = 'frogger_expert'
    return run_domain()


@app.route("/highway/plain", methods=['GET', 'POST'])
def highway_plain():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Plain'
    session['home'] = 'highway_plain'
    return asqit()
    # return run_domain()


@app.route("/highway/conditional1", methods=['GET', 'POST'])
def highway_conditional1():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional1'
    session['home'] = 'highway_conditional1'
    return run_domain()


@app.route("/highway/conditional2", methods=['GET', 'POST'])
def highway_conditional2():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional2'
    session['home'] = 'highway_conditional2'
    return run_domain()


""" ---------------- For experiments ---------------- """
LIMIT_MIN = 3  # max number of queries or queries avialable to participants
LIMIT_MAX = 10  # min number of queries or queries avialable to participants
NUM_VIDS = 2


@app.route("/ehlplain", methods=['GET', 'POST'])
def highlights_plain():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Plain'
    session['home'] = 'highlights_plain'
    session['num_vids'] = len(GLOBAL_VARS['static_videos'][session['agent']])
    return highlights()

@app.route("/easqc1", methods=['GET', 'POST'])
def asqit_conditional1():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional1'
    session['home'] = 'asqit_conditional1'
    return experiment_asqit()


@app.route("/ehlc1", methods=['GET', 'POST'])
def highlights_conditional1():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional1'
    session['home'] = 'highlights_conditional1'
    return experiment_highlights()


@app.route("/ehlc2", methods=['GET', 'POST'])
def highlights_conditional2():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional2'
    session['home'] = 'highlights_conditional2'
    return experiment_highlights()


"""Conditional agent 3  - SecondLane-BumperCar"""


@app.route("/easqc3", methods=['GET', 'POST'])
def asqit_conditional3():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional3'
    session['home'] = 'asqit_conditional3'
    return asqit()


@app.route("/ehlc3", methods=['GET', 'POST'])
def highlights_conditional3():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional3'
    session['home'] = 'highlights_conditional3'
    session['num_vids'] = len(GLOBAL_VARS['static_videos'][session['agent']])
    # return experiment_highlights()
    return highlights()


@app.route("/ehlc4", methods=['GET', 'POST'])
def highlights_conditional4():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional4'
    session['home'] = 'highlights_conditional4'
    session['num_vids'] = len(GLOBAL_VARS['static_videos'][session['agent']])
    # return experiment_highlights()
    return highlights()


"""Conditional agent 4  - Plain-FirstLane"""


@app.route("/easqc4", methods=['GET', 'POST'])
def asqit_conditional4():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'highway'
    session['agent'] = 'Conditional4'
    session['home'] = 'asqit_conditional4'
    return asqit()


"""Frogger NoLeft"""


@app.route("/ehlnl", methods=['GET', 'POST'])
def highlights_noleft():
    if not check_uid_highlights(): return render_template('uid_error.html')
    session['domain'] = 'frogger'
    session['agent'] = 'NoLeft'
    session['home'] = 'highlights_noleft'
    return experiment_highlights()


@app.route("/easqnl", methods=['GET', 'POST'])
def asqit_noleft():
    if not check_uid(): return render_template('uid_error.html')
    session['domain'] = 'frogger'
    session['agent'] = 'NoLeft'
    session['home'] = 'asqit_noleft'
    return experiment_asqit()
