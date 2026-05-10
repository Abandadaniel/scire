import streamlit as st
from research_agent import FastResearchAgent
from datetime import datetime
import time

st.set_page_config(
    page_title="Scire",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
    .stChatMessage { animation: fadeIn 0.2s ease-in; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .profanity-badge {
        background-color: #0D98BA;
        font-size: 0.7rem;
        padding: 0.1rem 0.4rem;
        border-radius: 24px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

if 'agent' not in st.session_state:
    st.session_state.agent = FastResearchAgent()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'response_times' not in st.session_state:
    st.session_state.response_times = []

col1, col2, col3 = st.columns(3)
with col1:
    avg_time = sum(st.session_state.response_times[-10:]) / len(st.session_state.response_times[-10:]) if st.session_state.response_times else 0
    st.metric("Avg Response", f"{avg_time:.1f}s")
with col2:
    st.metric("Messages", len(st.session_state.messages))
with col3:
    filtered = sum(1 for m in st.session_state.messages if m.get('profanity_filtered', False))
    st.metric("Filtered", filtered)

st.title("Scire")
st.caption("Quick multilingual research with automatic profanity filtering")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("response_time"):
            st.caption(f"{message['response_time']:.1f}s")
        if message.get("profanity_filtered"):
            st.markdown("<span class='profanity-badge'>Filtered</span>", unsafe_allow_html=True)

user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            start = time.time()
            result = st.session_state.agent.research_fast(user_input)
            response_time = time.time() - start
            
            if result['success']:
                st.markdown(result['response'])
                st.caption(f"{response_time:.1f}s")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['response'],
                    "response_time": response_time,
                    "profanity_filtered": result.get('profanity_filtered', False)
                })
                st.session_state.response_times.append(response_time)
            else:
                st.error(result['response'])
    

with st.sidebar:
    st.title("Settings")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.agent.clear_memory()
        st.session_state.messages = []
        st.session_state.response_times = []
        st.rerun()
    
    st.markdown("---")