import os.path
from collections import defaultdict
from os.path import join

from copy import copy

from datetime import datetime

from random import randrange
from flask import render_template, flash, redirect, url_for, request, session
from backend import GLOBAL_VARS
from backend.forms.common import check_ID, LoadMoreForm, BackButtonForm
from queries.common import log_msg
from interfaces.globals import FORMS, LTLF
from queries.query_traces import get_query_highlights, load_more_videos


def run_domain():
    domain = session['domain']
    freehand_ltlf = check_free_ltlf()
    if freehand_ltlf: return freehand_ltlf
    user_id = session['user_id']
    form = FORMS[domain]()
    check = check_ID()
    if check.submit.data:
        finished = "yes" if GLOBAL_VARS["count_queries"][user_id] >= 3 else "no"
        return render_template(f'{domain}_query.html', form=form, done=check, finished=finished)
    GLOBAL_VARS['seen'][user_id], GLOBAL_VARS['videos'][user_id] = [], []
    GLOBAL_VARS['vector_state_counter'] = 0
    if form.validate_on_submit():
        log_msg(f"\n----------Start - Query -----------  Time: {datetime.now()}, \t{user_id}")
        log_msg(f"form validated on submit, \t{user_id}")
        args = LTLF[domain](form.data)
        args.user_id, args.agent = user_id, session['agent']
        log_msg(f"Interface args obtained, \t{user_id}")
        GLOBAL_VARS['args'][user_id] = args
        get_query_highlights(args)
        log_msg(f"----------END- Query -----------  Time: {datetime.now()}, \t{user_id} \n")
        flash_messages()
        log_msg(f"test Time: {datetime.now()}, \t{user_id} \n")
        return redirect(url_for('explanation'))
    return render_template(f'{domain}_query.html', form=form, done=check)


def get_videos(num_videos=1, previous=False):
    videos = []
    # videos_list = GLOBAL_VARS['static_videos'][agent][indx:]
    # for i in range(min(num_videos, len(videos_list))):
    #     videos.append(videos_list.pop(0))
    #     session['video_index'] += 1
    if previous:
        session['video_index'] -= 1
    else:
        if session['video_index'] < session['num_vids'] - 1:
            session['video_index'] += 1
    return [join("videos", session['agent'], f"HL_{session['video_index']}.mp4")]


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


def check_uid_highlights():
    if request.args.get('uid'):
        if session.get("user_id") != request.args.get('uid'):
            session['user_id'] = request.args.get('uid')
            log_msg(f"Session user id set to: {session['user_id']}")
            session['video_index'] = 0
            session['count_queries'] = 0
            session['videos'] = []
            return True
        else:
            log_msg(f"Session user id is: {session['user_id']}")
            return True

    elif session.get("user_id"):
        log_msg(f"Session user id is: {session['user_id']}")
        return True
    else:
        return False


def experiment_asqit():
    if GLOBAL_VARS['done'][session['user_id']]: return render_template('done.html')
    domain = session['domain']
    freehand_ltlf = check_free_ltlf()
    if freehand_ltlf: return freehand_ltlf
    user_id = session['user_id']
    form = FORMS[domain]()
    check = check_ID()
    if check.submit.data:
        if GLOBAL_VARS["count_queries"][user_id] >= LIMIT_MIN:
            GLOBAL_VARS['done'][session['user_id']] = True
            return render_template(f'done.html')
        else:
            return render_template(f'asqit_{domain}_query.html', form=form, done=check,
                                   finished="no",
                                   uses=LIMIT_MAX - GLOBAL_VARS["count_queries"][user_id])

    GLOBAL_VARS['seen'][user_id], GLOBAL_VARS['videos'][user_id] = [], []
    GLOBAL_VARS['vector_state_counter'] = 0
    if form.validate_on_submit():
        # if GLOBAL_VARS["count_queries"][user_id] == LIMIT_MAX:
        #     return render_template(f'done.html')
        log_msg(f"\n----------Start - Query -----------  Time: {datetime.now()}, \t{user_id}")
        log_msg(f"form validated on submit, \t{user_id}")
        args = LTLF[domain](form.data)
        args.user_id, args.agent = user_id, session['agent']
        args.num_trajectories = NUM_VIDS_ASQIT
        log_msg(f"Interface args obtained, \t{user_id}")
        GLOBAL_VARS['args'][user_id] = args
        get_query_highlights(args)
        log_msg(f"----------END- Query -----------  Time: {datetime.now()}, \t{user_id} \n")
        flash_messages()
        log_msg(f"test Time: {datetime.now()}, \t{user_id} \n")
        return redirect(url_for('explanation'))
    return render_template(f'asqit_{domain}_query.html', form=form, done=check,
                           uses=LIMIT_MAX - GLOBAL_VARS["count_queries"][user_id])


def experiment_highlights():
    if not check_uid_highlights(): return render_template('uid_error.html')
    if GLOBAL_VARS['done'][session['user_id']]: return render_template('done.html')
    form = LoadMoreForm()
    check = check_ID()
    if check.submit.data:
        if session['count_queries'] >= LIMIT_MIN:
            GLOBAL_VARS['done'][session['user_id']] = True
            return render_template(f'done.html')
        else:
            return render_template(f'highlights_limit.html', form=form, done=check, finished="no",
                                   videos=session['videos'],
                                   uses=LIMIT_MAX - session['count_queries'])
    if form.validate_on_submit():
        # if session['count_queries'] == LIMIT_MAX: return render_template(f'done.html')
        session['videos'] = get_videos(NUM_VIDS_HL, session['agent'], session['video_index'])
        if not os.path.exists(join('backend/static/', session['videos'][0])):
            return render_template(f'done.html')
        session['count_queries'] += 1
        return render_template('highlights_limit.html', form=form, done=check,
                               videos=session['videos'],
                               uses=LIMIT_MAX - session['count_queries'])
    return render_template('highlights_limit.html', form=form, done=check,
                           videos=session['videos'],
                           uses=LIMIT_MAX - session['count_queries'])


def highlights():
    form = LoadMoreForm()
    back = BackButtonForm()
    if 'previous' in request.form and back.validate_on_submit():
        session['videos'] = get_videos(previous=True)
        log_msg('Button Pressed: previous')
        back = back if session['video_index'] else None
        return render_template('highlights.html', form=form, back=back, videos=session['videos'])

    if 'next' in request.form and form.validate_on_submit():
        session['videos'] = get_videos()
        log_msg('Button Pressed: next')
        form = form if session['video_index'] != session['num_vids'] - 1 else None
        return render_template('highlights.html', form=form, back=back, videos=session['videos'])

    session['videos'] = [join("videos", session['agent'], f"HL_0.mp4")]
    return render_template('highlights.html', form=form, back=None, videos=session['videos'])


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
