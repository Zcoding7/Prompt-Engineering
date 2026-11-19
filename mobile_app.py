import flet as ft
from openai import OpenAI
from huggingface_hub import InferenceClient
from datetime import datetime

GROQ_URL = "https://groq.com"
GROQ_MODELS = ["openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
HF_MODELS = ["meta-llama/Llama-3.1-8B-Instruct", "Qwen/Qwen2.5-7B-Instruct"]

def main(page: ft.Page):
    page.title = "Prompt Engineering Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    provider_dropdown = ft.Dropdown(
        label="AI Provider",
        value="Groq",
        options=[ft.dropdown.Option("Groq"), ft.dropdown.Option("Hugging Face")],
        expand=True
    )

    api_key_input = ft.TextField(
        label="API Key",
        password=True,
        can_reveal_password=True,
        expand=True
    )

    temp_slider = ft.Slider(min=0.0, max=1.0, divisions=10, value=0.3, label="{value}")
    temp_label = ft.Text("Temperature: 0.3", size=14)

    def on_temp_change(e):
        temp_label.value = f"Temperature: {round(temp_slider.value, 1)}"
        page.update()

    temp_slider.on_change = on_temp_change

    def call_ai(prompt: str) -> str:
        key = api_key_input.value.strip()
        provider = provider_dropdown.value
        temp = round(temp_slider.value, 1)

        if not prompt.strip():
            return "Please enter a prompt first."
        if not key:
            return f"Missing {provider} API key. Enter it at the top."

        models = GROQ_MODELS if provider == "Groq" else HF_MODELS
        last_error = None

        for model in models:
            try:
                if provider == "Groq":
                    client = OpenAI(api_key=key, base_url=GROQ_URL)
                    res = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temp,
                        max_tokens=512
                    )
                    return res.choices[0].message.content or "Empty response."
                else:
                    client = InferenceClient(model=model, token=key)
                    res = client.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temp,
                        max_tokens=512
                    )
                    return res.choices[0].message.content or "Empty response."
            except Exception as e:
                last_error = e

        return f"Error ({type(last_error).__name__}): {last_error}"

    vague_input = ft.TextField(label="1. Vague Prompt", multiline=True, min_lines=2)
    vague_output = ft.Text("Output will appear here...", selectable=True, color=ft.Colors.BLUE_200)

    spec_input = ft.TextField(label="2. Specific Prompt", multiline=True, min_lines=2)
    spec_output = ft.Text("Output will appear here...", selectable=True, color=ft.Colors.GREEN_200)

    ctx_input = ft.TextField(label="3. Contextual Prompt", multiline=True, min_lines=3)
    ctx_output = ft.Text("Output will appear here...", selectable=True, color=ft.Colors.AMBER_200)

    def run_step(input_field, output_text, btn):
        btn.disabled = True
        output_text.value = "Generating response..."
        page.update()
        output_text.value = call_ai(input_field.value)
        btn.disabled = False
        page.update()

    btn_vague = ft.ElevatedButton("Run Vague Prompt", on_click=lambda e: run_step(vague_input, vague_output, btn_vague))
    btn_spec = ft.ElevatedButton("Run Specific Prompt", on_click=lambda e: run_step(spec_input, spec_output, btn_spec))
    btn_ctx = ft.ElevatedButton("Run Contextual Prompt", on_click=lambda e: run_step(ctx_input, ctx_output, btn_ctx))

    q1 = ft.TextField(label="1. How did specificity change the response?", multiline=True)
    q2 = ft.TextField(label="2. How did context improve the response?", multiline=True)
    q3 = ft.TextField(label="3. Which prompt was best and why?", multiline=True)

    def copy_report(e):
        report = (
            f"PROMPT ENGINEERING LAB REPORT ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
            f"1. VAGUE:\nPrompt: {vague_input.value}\nResponse: {vague_output.value}\n\n"
            f"2. SPECIFIC:\nPrompt: {spec_input.value}\nResponse: {spec_output.value}\n\n"
            f"3. CONTEXTUAL:\nPrompt: {ctx_input.value}\nResponse: {ctx_output.value}\n\n"
            f"REFLECTIONS:\nQ1: {q1.value}\nQ2: {q2.value}\nQ3: {q3.value}"
        )
        page.set_clipboard(report)
        page.snack_bar = ft.SnackBar(ft.Text("Full Lab Report copied to clipboard!"))
        page.snack_bar.open = True
        page.update()

    btn_copy = ft.FilledButton("Copy Full Lab Report", icon=ft.Icons.COPY, on_click=copy_report)

    sample_output = ft.Column(spacing=12)

    def run_samples(e):
        btn_samples.disabled = True
        sample_output.controls.clear()
        sample_output.controls.append(ft.Text("Running all 3 sample prompts..."))
        page.update()

        samples = [
            ("VAGUE PROMPT", "Explain technology."),
            ("SPECIFIC PROMPT", "Explain three benefits of educational technology in five bullet points for university students."),
            ("CONTEXTUAL PROMPT", "Explain three benefits of educational technology for university students who have limited internet access. Use simple English, provide practical classroom examples, and suggest affordable solutions. Keep it under 200 words.")
        ]

        sample_output.controls.clear()
        for label, prompt in samples:
            res = call_ai(prompt)
            sample_output.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(label, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
                        ft.Text(f"Prompt: {prompt}", italic=True, size=12),
                        ft.Text(res, selectable=True)
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=8
                )
            )
            page.update()

        btn_samples.disabled = False
        page.update()

    btn_samples = ft.FilledButton("Run All 3 Sample Prompts", on_click=run_samples)

    lab_view = ft.Column([
        vague_input,
        btn_vague,
        ft.Container(vague_output, padding=10, bgcolor=ft.Colors.SURFACE_VARIANT, border_radius=8),
        ft.Divider(),
        spec_input,
        btn_spec,
        ft.Container(spec_output, padding=10, bgcolor=ft.Colors.SURFACE_VARIANT, border_radius=8),
        ft.Divider(),
        ctx_input,
        btn_ctx,
        ft.Container(ctx_output, padding=10, bgcolor=ft.Colors.SURFACE_VARIANT, border_radius=8),
        ft.Divider(),
        ft.Text("Reflection Questions", size=18, weight=ft.FontWeight.BOLD),
        q1, q2, q3,
        btn_copy
    ], spacing=10)

    samples_view = ft.Column([
        ft.Text("Automated Benchmark", size=18, weight=ft.FontWeight.BOLD),
        btn_samples,
        sample_output
    ], spacing=12)

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        tabs=[
            ft.Tab(text="Interactive Lab", content=ft.Container(lab_view, padding=ft.padding.only(top=15))),
            ft.Tab(text="Sample Benchmark", content=ft.Container(samples_view, padding=ft.padding.only(top=15))),
        ],
        expand=True
    )

    page.add(
        ft.Text("🧪 Prompt Engineering Studio", size=22, weight=ft.FontWeight.BOLD),
        ft.Row([provider_dropdown, api_key_input]),
        temp_label,
        temp_slider,
        ft.Divider(),
        tabs
    )

ft.app(target=main)
