import streamlit as st
from filters import *
import numpy as np
from io import BytesIO
import json


def img_to_bytes(img):
    buf = BytesIO()
    img.save(buf, format="png")
    return buf.getvalue()


def spectrum_log(_ft): # логарифмічна шкала для кращого відображення:
    return 20 * np.log(np.abs(_ft)) 


def apply_transform(_image, _shift):
    _ft = np.fft.fft2(_image)
    if _shift:
        st.session_state["original_ft"] = np.fft.fftshift(_ft)
    else:
        st.session_state["original_ft"] = _ft
    st.session_state["new"] = False
    return


def img_changed():
    st.session_state["new"] = True
    st.session_state["original_ft"] = None
    st.session_state["filtered_ft"] = None


def d_values(_ft):
    M, N = _ft.shape
    m, n = M//2, N//2
    _max = np.sqrt((m ** 2) + (n ** 2))
    _average = _max*0.5
    _min = 0.0
    return (_min, _max, _average)


def apply_filter(_filter, _d0, _w, _order):
    st.session_state["filtered_ft"] = frequency_filter(_filter,st.session_state["original_ft"], _d0, _w, _order)


def show_examples():
    st.session_state["examples_shown"] = True
    

def hide_examples():
    st.session_state["examples_shown"] = False
    

with open("examples/examples.json", "r", encoding="UTF-8") as read_file:
    examples_dicts = json.load(read_file)


