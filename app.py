import streamlit as st
from openai import OpenAI
from huggingface_hub import InferenceClient
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from datetime import datetime
import io

st.set_page_config(
    page_title="Prompt Engineering Studio",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Prompt Engineering Studio")
st.markdown("Master **Clarity**, **Specificity**, and **Contextual Information** through interactive AI testing.")

st.sidebar.header("⚙️ Model Configuration")
provider = st.sidebar.selectbox("AI Provider", ["Groq", "Hugging Face"])

default_key = ""
try:
    if provider == "Groq":
        default_key = st.secrets.get("GROQ_API_KEY", "")
    else:
        default_key = st.secrets.get("HF_API_KEY", "")
except Exception:
    default_key = ""

api_key = st.sidebar.text_input(
    f"{provider} API Key",
    value=default_key,
    type="password",
    help="Enter your API key or configure it in Streamlit Secrets."
)

if provider == "Groq":
    model_choice = st.sidebar.selectbox(
        "Select Groq Model",
        ["openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    )
else:
    model_choice = st.sidebar.selectbox(
        "Select Hugging Face Model",
        ["meta-llama/Llama-3.1-8B-Instruct", "Qwen/Qwen2.5-7B-Instruct"]
    )

temperature = st.sidebar.slider("Temperature (Creativity)", 0.0, 1.0, 0.3, 0.1)
max_tokens = st.sidebar.slider("Max Response Length (Tokens)", 128, 2048, 512, 64)

if st.sidebar.button("🗑️ Reset All Lab Data"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

GROQ_URL = "https://groq.com"

def transcribe_voice(audio_bytes) -> str:
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language="en-US")
    except sr.UnknownValueError:
        st.sidebar.warning("Could not understand audio. Please try speaking again.")
        return ""
    except Exception as e:
        st.sidebar.error(f"Audio error: {e}")
        return ""

def generate_response(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "⚠️ Please enter a prompt before running."
    if not api_key:
        return f"⚠️ {provider} API key is missing. Please add it in the left sidebar."

    try:
        if provider == "Groq":
            client = OpenAI(api_key=api_key, base_url=GROQ_URL)
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or "No response returned."
        else:
            client = InferenceClient(model=model_choice, token=api_key)
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or "No response returned."
    except Exception as e:
        return f"❌ {provider} API Error ({type(e).__name__}): {str(e)}"

tab1, tab2, tab3 = st.tabs(["✍️ Interactive Lab", "📊 Side-by-Side Comparison", "📚 Sample Benchmark"])

with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1️⃣ Vague Prompt")
        st.caption("Start with a broad, general request.")
        vague_audio = audio_recorder(text="Speak Vague Prompt", key="vague_mic")
        if vague_audio:
            spoken = transcribe_voice(vague_audio)
            if spoken:
                st.session_state["vague_text"] = spoken

        vague_prompt = st.text_area(
            "Vague Prompt Input",
            value=st.session_state.get("vague_text", ""),
            placeholder="e.g., Explain agriculture.",
            height=130,
            label_visibility="collapsed"
        )
        if st.button("Run Step 1", use_container_width=True):
            with st.spinner("Generating..."):
                st.session_state["vague_res"] = generate_response(vague_prompt)
                st.session_state["saved_vague_p"] = vague_prompt

        if "vague_res" in st.session_state:
            st.info(st.session_state["vague_res"])

    with col2:
        st.subheader("2️⃣ Specific Prompt")
        st.caption("Add a clear task, format, and target audience.")
        spec_audio = audio_recorder(text="Speak Specific Prompt", key="spec_mic")
        if spec_audio:
            spoken = transcribe_voice(spec_audio)
            if spoken:
                st.session_state["spec_text"] = spoken

        specific_prompt = st.text_area(
            "Specific Prompt Input",
            value=st.session_state.get("spec_text", ""),
            placeholder="e.g., List 4 benefits of modern irrigation in bullet points for secondary school students.",
            height=130,
            label_visibility="collapsed"
        )
        if st.button("Run Step 2", use_container_width=True):
            with st.spinner("Generating..."):
                st.session_state["specific_res"] = generate_response(specific_prompt)
                st.session_state["saved_spec_p"] = specific_prompt

        if "specific_res" in st.session_state:
            st.info(st.session_state["specific_res"])

    with col3:
        st.subheader("3️⃣ Contextual Prompt")
        st.caption("Add real-world context, purpose, and strict constraints.")
        ctx_audio = audio_recorder(text="Speak Contextual Prompt", key="ctx_mic")
        if ctx_audio:
            spoken = transcribe_voice(ctx_audio)
            if spoken:
                st.session_state["ctx_text"] = spoken

        contextual_prompt = st.text_area(
            "Contextual Prompt Input",
            value=st.session_state.get("ctx_text", ""),
            placeholder="e.g., Explain 4 affordable drip-irrigation methods for smallholder farmers in Nigeria facing dry-season water shortages. Use simple English, give practical examples, and keep it under 150 words.",
            height=130,
            label_visibility="collapsed"
        )
        if st.button("Run Step 3", use_container_width=True):
            with st.spinner("Generating..."):
                st.session_state["contextual_res"] = generate_response(contextual_prompt)
                st.session_state["saved_ctx_p"] = contextual_prompt

        if "contextual_res" in st.session_state:
            st.info(st.session_state["contextual_res"])

    st.divider()
    st.subheader("📝 Lab Reflection & Report Export")

    q1 = st.text_area("1. How did the AI's response change when the prompt became more specific?", height=80)
    q2 = st.text_area("2. How did adding contextual information improve the response?", height=80)
    q3 = st.text_area("3. Which prompt produced the most relevant and tailored response? Why?", height=80)
    q4 = st.text_area("4. What did you learn about clarity, specificity, and context in prompt engineering?", height=80)

    report_content = f"""PROMPT ENGINEERING STUDIO - LAB REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Provider: {provider} | Model: {model_choice} | Temperature: {temperature}
====================================================================

[STEP 1: VAGUE PROMPT]
Prompt: {st.session_state.get('saved_vague_p', vague_prompt)}
Response:
{st.session_state.get('vague_res', 'Not run yet.')}

--------------------------------------------------------------------
[STEP 2: SPECIFIC PROMPT]
Prompt: {st.session_state.get('saved_spec_p', specific_prompt)}
Response:
{st.session_state.get('specific_res', 'Not run yet.')}

--------------------------------------------------------------------
[STEP 3: CONTEXTUAL PROMPT]
Prompt: {st.session_state.get('saved_ctx_p', contextual_prompt)}
Response:
{st.session_state.get('contextual_res', 'Not run yet.')}

====================================================================
REFLECTION ANSWERS
1. Specificity impact: {q1}
2. Context impact: {q2}
3. Best prompt & why: {q3}
4. Key takeaways: {q4}
"""

    st.download_button(
        label="💾 Download Complete Lab Report (.txt)",
        data=report_content,
        file_name=f"prompt_lab_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with tab2:
    st.subheader("📊 Side-by-Side Output Analysis")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 1. Vague Output")
        st.write(st.session_state.get("vague_res", "_Run Step 1 in the Interactive Lab tab first._"))
    with c2:
        st.markdown("### 2. Specific Output")
        st.write(st.session_state.get("specific_res", "_Run Step 2 in the Interactive Lab tab first._"))
    with c3:
        st.markdown("### 3. Contextual Output")
        st.write(st.session_state.get("contextual_res", "_Run Step 3 in the Interactive Lab tab first._"))

with tab3:
    st.subheader("📚 Automated Sample Benchmark")
    st.markdown("Run all three built-in sample prompts at once to observe how prompt quality transforms AI output.")

    sample_prompts = [
        ("VAGUE PROMPT", "Explain technology."),
        ("SPECIFIC PROMPT", "Explain three benefits of educational technology in five bullet points for university students."),
        ("CONTEXTUAL PROMPT", "Explain three benefits of educational technology for university students who have limited internet access. Use simple English, provide practical classroom examples, and suggest affordable solutions. Organize the answer into five bullet points and keep it under 200 words.")
    ]

    if st.button("▶️ Run All 3 Benchmark Samples", type="primary"):
        b_col1, b_col2, b_col3 = st.columns(3)
