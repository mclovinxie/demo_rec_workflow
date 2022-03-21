#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@File       demo.py.py
@Author     McLovin Xie
@Date       3/4/2022 2:41 PM
@Contact    mclovin.xxh@gmail.com
"""

import numpy as np
import streamlit as st

from const import (
    APP_NAME, SIDE_BAR_TITLE, MODELS, WINDOW_SIZES, YES_OR_NO, SERVICE_TOKEN_SEPARATOR, CHANGE_TEXT
)
from models import models, precursor, successor


# @st.cache(allow_output_mutation=True)
# def load_model(m, w):
#     return models[f'{m.lower()}_{int(w)}']


st.set_page_config(
    layout='wide', page_title=APP_NAME
)
st.title(APP_NAME)
st.sidebar.text(SIDE_BAR_TITLE)

top_k = st.sidebar.slider('How many services do you need?', 1, 20, 5)
# layout = st.sidebar.radio('Specify the layout', LAYOUTS)
layout = 'text'
successor_enabled = st.sidebar.radio('Enable successor probability', YES_OR_NO)
model_name = st.sidebar.selectbox(label='Select a generation strategy to apply', options=MODELS, index=0)
window_size = st.sidebar.selectbox(
    label='Specify the context size',
    options=[e // 2 for e in WINDOW_SIZES],
    index=0, key='window_size'
)
arch_svg = st.sidebar.radio('Display the high-level architecture', YES_OR_NO)

# the_model = load_model(model_name, window_size * 2 + 1)
the_model = models[f'{model_name.lower()}_{int(window_size) * 2 + 1}']


def render_svg():
    """Renders the given svg string."""
    import base64
    svg = """
            <svg xmlns="./resources/imgs/architecture.png" width="100" height="100">
                <circle cx="50" cy="50" r="40" stroke="green" stroke-width="4" fill="yellow" />
            </svg>
        """
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


def render_png():
    from PIL import Image
    image = Image.open('./resources/imgs/architecture.png')
    st.image(image, caption='Blueprint of our solution')


if arch_svg == 'Yes':
    render_png()

input_column, result_column = st.columns(2)


def coefficient(tl, t):
    if SERVICE_TOKEN_SEPARATOR not in t:
        n_pre = precursor.get(tl, {}).get(t, 0)
        n_suc = successor.get(tl, {}).get(t, 0)
    else:
        n_pre, n_suc = 0, 0
        for e in t.split(SERVICE_TOKEN_SEPARATOR):
            for tle in tl.split(SERVICE_TOKEN_SEPARATOR):
                n_pre += precursor.get(tle, {}).get(e, 0)
                n_suc += successor.get(tle, {}).get(e, 0)
    # n_pre, n_suc = n_pre / 10, n_suc / 10
    return np.exp(n_suc) / (np.exp(n_pre) + np.exp(n_suc))


def rec(context):
    context = context[-window_size:]
    context.reverse()
    try:
        the_model.wv.most_similar(positive=context, topn=top_k * 50)
    except Exception as ex:
        new_context = []
        for e in context:
            for ee in e.split(SERVICE_TOKEN_SEPARATOR):
                new_context.append(ee)
        context = new_context
    try:
        similarities = {e[0]: e[1] for e in the_model.wv.most_similar(positive=context, topn=top_k * 30)}
        if successor_enabled == 'Yes':
            for k in similarities:
                similarities[k] *= coefficient(context[-1], k)
            similarities = sorted(similarities.items(), key=lambda e: e[1], reverse=True)
            candidates = [e[0] for e in similarities][:top_k]
        else:
            candidates = [e[0] for e in the_model.wv.most_similar(positive=context, topn=top_k)]
        candidates = [f'{SERVICE_TOKEN_SEPARATOR}'.join(e.split(SERVICE_TOKEN_SEPARATOR)) if SERVICE_TOKEN_SEPARATOR in e else e for e in candidates]
    except Exception as e:
        st.warning('Oops... Some errors happened. Please check your inputs.')
        st.sidebar.text_area('Console logs', str(e), height=200, disabled=True)
        candidates = []
    return candidates


def update_inputs():
    if model_name.lower() == 'bfs':
        values = []
        # idx = 0
        for i, e in enumerate(st.session_state.get('last_result') or []):
            if st.session_state.get(f'checkbox_{i}') or []:
                values.append(f' {SERVICE_TOKEN_SEPARATOR} '.join(st.session_state[f'checkbox_{i}']))
        #     for ee in e.split(SERVICE_TOKEN_SEPARATOR):
        #         if st.session_state.get(f'checkbox_{idx}'):
        #             values.append(ee)
        #             idx += 1
    else:
        values = [
            e for i, e in enumerate(st.session_state.get('last_result') or []) if st.session_state.get(f'checkbox_{i}')
        ]
    input_tokens = st.session_state.get('input')
    new_tokens = input_tokens or ''
    for value in values:
        if value in input_tokens:
            new_tokens = new_tokens.replace(f'{value}\n', '')
        else:
            if len(new_tokens) > 1:
                new_tokens = f'{new_tokens}\n{value}'
            else:
                new_tokens = value
    st.session_state.update({'input': new_tokens})


def clear_input():
    st.session_state.update({'input': ''})


update_inputs()


input_column.subheader('Workflow on the fly')
input_text = input_column.text_area(
    "Create your own workflow here in form of service tokens. Each line is a service token. If a service token is comprised of multiple services, you can concatenate them with '+'.",
    height=300, key='input'
)
input_column.button('Clear', on_click=clear_input)
tokens = [line.replace(' ', '') for line in input_text.split('\n')]
if not tokens or len(tokens) < 1 or (len(tokens) == 1 and tokens[0] == ''):
    tokens = [the_model.wv.index_to_key[np.random.randint(1, 1000)], ]
result = rec(tokens)
st.session_state['last_result'] = result
result_column.subheader('Recommended service(s)')
result_column.write('Select a service or services from the list to continue your journey of workflow composition:')

select_form = result_column.form('select_form', clear_on_submit=True)
with select_form:
    if model_name.lower() == 'bfs':
        # idx = 0
        # for i, e in enumerate(result):
        #     with st.expander('Expand to choose more'):
        #         for j, ee in enumerate(e.split(SERVICE_TOKEN_SEPARATOR)):
        #             st.checkbox(ee, key=f'checkbox_{idx}')
        #             idx += 1
        st.markdown(CHANGE_TEXT, unsafe_allow_html=True)
        selected = []
        for i, e in enumerate(result):
            ee = e.split(SERVICE_TOKEN_SEPARATOR)
            selected.append(st.multiselect('', options=sorted(set(ee), key=ee.index), key=f'checkbox_{i}'))
    else:
        selected = [st.checkbox(e, key=f'checkbox_{i}') for i, e in enumerate(result)]
select_form.form_submit_button('Go')
