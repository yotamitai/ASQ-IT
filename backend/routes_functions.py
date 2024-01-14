from collections import defaultdict

from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, session
from backend import GLOBAL_VARS
from queries.common import log_msg
from interfaces.globals import FORMS, LTLF
from queries.query_traces import get_query_highlights, load_more_videos


def check_uid():
    if request.args.get('ltlf'):
        session['user_id'] = 'free_hand_ltlf'
        return True
    if request.args.get('uid'):
        session['user_id'] = request.args.get('uid')
        log_msg(f"Session user id set to: {session['user_id']}")
        return True
    else:
        if not session.get('user_id'):
            return False
        else:
            log_msg(f"Session user id is: {session['user_id']}")
            return True


def flash_messages():
    if GLOBAL_VARS['videos'][session['user_id']]:
        if not GLOBAL_VARS["unseen"][session['user_id']]:
            msg = "There are no additional matching videos"
        else:
            msg = f'{GLOBAL_VARS["unseen"][session["user_id"]]} more videos are available.'
        flash(f'Your videos have been generated!\n {msg}', 'success')
    else:
        flash(f'No videos found for this query.', 'error')


def flash_messages_and_load_more():
    if GLOBAL_VARS["unseen"][session["user_id"]]:
        log_msg(f"\n\n---------- Start - Load More -----------  Time: {datetime.now()}")
        load_more_videos(GLOBAL_VARS['args'][session["user_id"]])
        log_msg(f"\n\n---------- End - Load More -----------  Time: {datetime.now()}")
        if not GLOBAL_VARS["unseen"][session['user_id']]:
            msg = "There are no additional matching videos"
        else:
            msg = f'{GLOBAL_VARS["unseen"][session["user_id"]]} more videos are available.'
        flash(f'Your videos have been generated!\n {msg}', 'success')
    else:
        flash(f'No more videos to show', 'error')
        GLOBAL_VARS['videos'][session["user_id"]] = []


def check_free_ltlf():
    if request.args.get('ltlf'):
        formula = request.args.get('ltlf').replace("^", " ").replace("and", '&')
        args = LTLF[session['domain']](formula)
        args.agent = session['agent']
        args.user_id = session['user_id']
        args.seq_min_len = session['seq_min_len']
        log_msg(f"******FREE HAND LTLF PASSED******\n\t{formula}")
        GLOBAL_VARS['args'][session["user_id"]] = args
        if "seq_min_len" in session.keys():
            args.seq_min_len = session["seq_min_len"]
        get_query_highlights(args)
        log_msg("video retrieval completed")
        flash_messages()
        return redirect(url_for('explanation'))


""" EXPERIMENTS"""
""" ---------------- For experiments ---------------- """
LIMIT_MIN = 3  # max number of queries or queries avialable to participants
LIMIT_MAX = 10  # min number of queries or queries avialable to participants
NUM_VIDS_HL = 1
NUM_VIDS_ASQIT = 4


def beautify_query(query_dict):
    str_dict = defaultdict(list)
    for k, v in query_dict.items():
        if not v or k == 'csrf_token':
            continue
        if k.startswith('start'):
            str_dict['Start Frame'] += [v]
        elif k.startswith('end'):
            str_dict['End Frame'] += [v]
        else:
            str_dict['Constraint'] += [v]
    return ', '.join([k+': ' +' '.join(str_dict[k]) for k in str_dict])


def asqit():
    domain = session['domain']
    if request.args.get('minlen'):
        session["seq_min_len"] = int(request.args.get('minlen'))
        log_msg(f"******Min video length changed to {session['seq_min_len']}******")
    freehand_ltlf = check_free_ltlf()
    if freehand_ltlf: return freehand_ltlf
    user_id = session['user_id']
    form = FORMS[domain]()
    GLOBAL_VARS['seen'][user_id], GLOBAL_VARS['videos'][user_id] = [], []
    GLOBAL_VARS['vector_state_counter'] = 0
    if form.validate_on_submit():
        log_msg(f"\n----------Start - Query -----------  Time: {datetime.now()}, \t{user_id}")
        log_msg(f"form validated on submit, \t{user_id}")
        args = LTLF[domain](form.data)
        args.user_id, args.agent, = user_id, session['agent']
        if "seq_min_len" in session.keys():
            args.seq_min_len = session["seq_min_len"]
        args.num_trajectories = NUM_VIDS_ASQIT
        log_msg(f"Interface args obtained, \t{user_id}")
        GLOBAL_VARS['args'][user_id] = args
        get_query_highlights(args)
        log_msg(f"----------END- Query -----------  Time: {datetime.now()}, \t{user_id} \n")
        flash_messages()
        log_msg(f"test Time: {datetime.now()}, \t{user_id} \n")

        relevant_data = dict(list(args.query_data.items())[:9])
        session['query'] = beautify_query(relevant_data) if \
            [v for v in relevant_data.values() if v] else 'No specification'

        return redirect(url_for('explanation'))
    return render_template(f'asqit_{domain}.html', form=form,
                           uses=LIMIT_MAX - GLOBAL_VARS["count_queries"][user_id])
