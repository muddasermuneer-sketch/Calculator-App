import streamlit as st
import math
import operator
import pandas as pd
from typing import Optional

st.set_page_config(page_title="Calculator", page_icon="🧮", layout="centered")

# --- Helpers ---
OPS_BASIC = {
    "Add (a + b)": operator.add,
    "Subtract (a - b)": operator.sub,
    "Multiply (a × b)": operator.mul,
    "Divide (a ÷ b)": operator.truediv,
    "Floor Divide (a // b)": operator.floordiv,
    "Modulus (a % b)": operator.mod,
    "Power (a ** b)": operator.pow,
}

OPS_SCI = {
    "sin(a)": lambda a, b=None: math.sin(a),
    "cos(a)": lambda a, b=None: math.cos(a),
    "tan(a)": lambda a, b=None: math.tan(a),
    "log(a)": lambda a, b=None: math.log(a),
    "log10(a)": lambda a, b=None: math.log10(a),
    "sqrt(a)": lambda a, b=None: math.sqrt(a),
    "exp(a)": lambda a, b=None: math.exp(a),
    "a^b": lambda a, b: math.pow(a, b),
}

def compute(op_func, a: float, b: Optional[float] = None):
    try:
        if b is None:
            return op_func(a)
        else:
            return op_func(a, b)
    except ZeroDivisionError:
        st.error("Division by zero is undefined.")
        return None
    except ValueError as e:
        st.error(f"Math domain error: {e}")
        return None
    except OverflowError as e:
        st.error(f"Number too large: {e}")
        return None

# --- UI ---
st.title("🧮 Streamlit Calculator")
st.caption("Basic and scientific operations with a clean, minimal UI.")

mode = st.segmented_control("Mode", options=["Basic", "Scientific"], default="Basic")

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts

with st.container(border=True):
    if mode == "Basic":
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("a", value=0.0, step=1.0, format="%.10g")
        with col2:
            b = st.number_input("b", value=0.0, step=1.0, format="%.10g")

        op_label = st.selectbox("Operation", list(OPS_BASIC.keys()), index=0)
        op_func = OPS_BASIC[op_label]

        if st.button("Compute", type="primary", use_container_width=True):
            result = compute(op_func, a, b)
            if result is not None:
                st.success(f"Result: {result}")
                st.session_state.history.append(
                    {"Mode": mode, "Operation": op_label, "a": a, "b": b, "Result": result}
                )

    else:
        col1, col2 = st.columns(2)
        with col1:
            a = st.number_input("a", value=0.0, step=1.0, format="%.10g")
        with col2:
            # b may be optional for unary ops
            b_enabled = st.checkbox("Use second input (b)", value=False)
            b = st.number_input("b", value=0.0, step=1.0, format="%.10g", disabled=not b_enabled)

        op_label = st.selectbox("Operation", list(OPS_SCI.keys()), index=0)
        op_func = OPS_SCI[op_label]

        if st.button("Compute", type="primary", use_container_width=True):
            result = compute(op_func, a, b if b_enabled else None)
            if result is not None:
                st.success(f"Result: {result}")
                st.session_state.history.append(
                    {
                        "Mode": mode,
                        "Operation": op_label,
                        "a": a,
                        "b": (b if b_enabled else None),
                        "Result": result,
                    }
                )

with st.expander("📝 History", expanded=False):
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True, hide_index=True)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "Download history (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="calc_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            if st.button("Clear history", use_container_width=True):
                st.session_state.history = []
                st.toast("History cleared.", icon="🧹")
    else:
        st.info("No calculations yet. Results will appear here.")

st.caption("Tip: You can enter scientific notation like 1e-6. Trig uses radians.")
