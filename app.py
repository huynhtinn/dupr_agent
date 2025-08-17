import os, time
import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from rag_core import build_rag_chain

load_dotenv()

rag_chain = None

# ---------- THEME & CSS ----------
THEME = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="emerald",
    neutral_hue="slate",
).set(
    body_background_fill="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    body_text_color="*neutral_900",
    button_primary_background_fill="linear-gradient(45deg, #4f46e5 0%, #06b6d4 100%)",
    button_primary_background_fill_hover="linear-gradient(45deg, #4338ca 0%, #0891b2 100%)",
)

CSS = """
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global Styles */
* {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Container & Layout */
.gradio-container { 
  max-width: 1200px !important; 
  margin: 0 auto !important; 
  padding: 20px !important;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
  min-height: 100vh !important;
}

.prose p, .prose li { 
  font-size: 15px; 
  line-height: 1.7; 
  color: #374151;
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(79, 70, 229, 0.3);
  }
  50% {
    box-shadow: 0 0 30px rgba(79, 70, 229, 0.5);
  }
}

/* Header */
.header-card {
  display: flex; 
  align-items: center; 
  gap: 20px; 
  padding: 24px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 24px; 
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
  color: white;
  animation: fadeInUp 0.8s ease-out;
  position: relative;
  overflow: hidden;
}

.header-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.header-card:hover::before {
  left: 100%;
}

.header-icon {
  width: 48px; 
  height: 48px; 
  background: rgba(255,255,255,0.2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  backdrop-filter: blur(10px);
}

.header-title { 
  font-weight: 800; 
  font-size: 28px; 
  margin: 0; 
  background: linear-gradient(45deg, #ffffff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-sub { 
  color: rgba(255,255,255,0.8); 
  font-size: 16px; 
  margin: 4px 0 0 0; 
  font-weight: 400;
}

/* Chatbot Container */
.chat-container {
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  overflow: hidden;
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

.gr-chatbot { 
  border: none !important;
  background: transparent !important;
  border-radius: 0 !important;
}

/* Chat Messages */
.gr-chat-message.user .message-row {
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 20px 20px 4px 20px !important;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.3) !important;
  animation: slideIn 0.3s ease-out;
}

.gr-chat-message.assistant .message-row {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 20px 20px 20px 4px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05) !important;
  animation: slideIn 0.3s ease-out;
}

/* Input Area */
.input-row {
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-top: 1px solid #e2e8f0;
}

/* Buttons */
.gr-button {
  border-radius: 12px !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
  border: none !important;
}

.gr-button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.gr-button.primary {
  background: linear-gradient(45deg, #4f46e5 0%, #06b6d4 100%) !important;
  color: white !important;
}

.gr-button.primary:hover {
  background: linear-gradient(45deg, #4338ca 0%, #0891b2 100%) !important;
}

/* Side Panel */
.side-panel {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  animation: slideIn 0.6s ease-out 0.6s both;
  overflow: hidden;
}

.tab-nav {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

/* Source Chips */
.source-chip {
  display: inline-flex; 
  align-items: center; 
  gap: 8px; 
  padding: 8px 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0ea5e9;
  border-radius: 50px; 
  margin: 6px 8px 6px 0;
  font-size: 13px; 
  color: #0c4a6e;
  transition: all 0.3s ease;
  cursor: pointer;
}

.source-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3);
}

.source-chip span { 
  font-weight: 700;
  background: linear-gradient(45deg, #0ea5e9, #0284c7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Cards */
.card {
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.1);
}

/* Footer */
.footer { 
  text-align: center; 
  color: #64748b; 
  font-size: 14px; 
  padding: 24px 0 8px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
}

/* Sliders & Inputs */
.gr-slider input[type="range"] {
  background: linear-gradient(45deg, #4f46e5, #06b6d4) !important;
}

.gr-textbox {
  border-radius: 16px !important;
  border: 2px solid #e2e8f0 !important;
  transition: all 0.3s ease !important;
}

.gr-textbox:focus {
  border-color: #4f46e5 !important;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
}

/* Loading Animation */
.loading {
  animation: glow 2s ease-in-out infinite;
}

/* Dark Mode */
html.dark {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
}

html.dark .gradio-container { 
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; 
  color: #e2e8f0 !important; 
}

html.dark .header-card { 
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

html.dark .side-panel,
html.dark .chat-container {
  background: rgba(30, 41, 59, 0.95);
  border-color: #334155;
}

html.dark .card { 
  background: rgba(30, 41, 59, 0.8); 
  border-color: #334155; 
}

html.dark .gr-chat-message.user .message-row { 
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
}

html.dark .gr-chat-message.assistant .message-row { 
  background: rgba(51, 65, 85, 0.8) !important; 
  border-color: #475569 !important; 
  color: #e2e8f0 !important;
}

html.dark .source-chip { 
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-color: #0ea5e9; 
  color: #e0f2fe; 
}

/* Responsive Design */
@media (max-width: 768px) {
  .gradio-container {
    padding: 10px !important;
  }
  
  .header-card {
    padding: 16px 20px;
    flex-direction: column;
    text-align: center;
  }
  
  .header-title {
    font-size: 24px;
  }
  
  .gr-chat-message.user .message-row,
  .gr-chat-message.assistant .message-row {
    border-radius: 16px !important;
  }
}
"""

# ---------- HELPERS ----------
def startup():
    global rag_chain
    if rag_chain is None:
        rag_chain = build_rag_chain()

def lc_history_from_messages(history_msgs):
    lc_hist = []
    for m in history_msgs or []:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            lc_hist.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_hist.append(AIMessage(content=content))
    return lc_hist

def format_sources(ctx_docs):
    """
    ctx_docs: list[Document] (rag_chain trả về trong key 'context')
    Render markdown + chip đẹp với emoji và styling cải thiện.
    """
    if not ctx_docs:
        return "📭 **Không có nguồn tham khảo nào được tìm thấy.**"
    
    seen = set()
    chips = []
    bullets = []
    
    for i, d in enumerate(ctx_docs, 1):
        src = d.metadata.get("source", "doc")
        title = d.metadata.get("title") or d.metadata.get("player_name") or f"Tài liệu {i}"
        uid = f"{src}:{title}"
        
        if uid in seen:
            continue
        seen.add(uid)
        
        # Xác định emoji theo loại nguồn
        emoji = "📄"
        if "player" in src.lower():
            emoji = "🏓"
        elif "blog" in src.lower():
            emoji = "📝"
        elif "rule" in src.lower():
            emoji = "📋"
        elif "tournament" in src.lower():
            emoji = "🏆"
        
        chips.append(f'<div class="source-chip">{emoji} <span>{src}</span> {title}</div>')
        
        # Metadata formatting
        meta_bits = []
        if d.metadata.get("player_id"): 
            meta_bits.append(f"🆔 {d.metadata['player_id']}")
        if d.metadata.get("url"):       
            meta_bits.append(f"🔗 [Xem chi tiết]({d.metadata['url']})")
        
        meta_line = (" • " + " • ".join(meta_bits)) if meta_bits else ""
        
        # Preview content
        preview = (d.page_content or "").strip()
        if preview:
            # Lấy 2 dòng đầu hoặc 150 ký tự đầu
            lines = preview.splitlines()
            if len(lines) > 1:
                preview = lines[0] + "\\n" + lines[1]
            preview = preview[:150] + "..." if len(preview) > 150 else preview
        else:
            preview = "Không có nội dung preview."
            
        bullets.append(f"### {emoji} **{title}**\n**Nguồn:** `{src}`{meta_line}\n\n> _{preview}_\n")
    
    chips_html = f'<div style="margin-bottom: 16px;">{" ".join(chips)}</div>'
    sources_content = "\n".join(bullets)
    
    summary = f"**📊 Tổng cộng:** {len(bullets)} nguồn tham khảo được tìm thấy"
    
    return f"{chips_html}\n\n{summary}\n\n---\n\n{sources_content}"

# ---------- CALLBACKS ----------
def respond(user_msg, history_msgs, top_k, dark_on):
    startup()

    # Toggle dark class (client-side JS call below handles it; this is a no-op server-side)
    _ = dark_on

    lc_hist = lc_history_from_messages(history_msgs)
    
    # Tinh chỉnh k (retriever top_k) runtime
    start = time.time()
    
    try:
        resp = rag_chain.invoke(
            {"input": user_msg, "chat_history": lc_hist},
            config={"configurable": {"retriever_kwargs": {"k": int(top_k)}}}
        )
        answer = resp["answer"]
        ctx_docs = resp.get("context", [])
        
        # Thêm emoji và format đẹp hơn cho câu trả lời
        if answer and not answer.startswith(("🏓", "📚", "💡", "⚡")):
            answer = f"🏓 {answer}"
            
    except Exception as e:
        answer = f"❌ **Lỗi:** Không thể xử lý câu hỏi của bạn. Chi tiết: {str(e)}"
        ctx_docs = []

    history_msgs = (history_msgs or []) + [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": answer},
    ]

    sources_md = format_sources(ctx_docs)
    latency = f"{(time.time() - start):.2f}s"
    
    # Meta information with emoji and better formatting
    meta_info = f"""
### ⚡ **Thông tin phản hồi**

📊 **Thời gian xử lý:** {latency}  
🔍 **Số nguồn tìm kiếm:** {int(top_k)}  
📚 **Số nguồn tìm thấy:** {len(ctx_docs)}  
🎯 **Độ chính xác:** {"Cao" if len(ctx_docs) >= 3 else "Trung bình" if len(ctx_docs) >= 1 else "Thấp"}

---

### 💡 **Mẹo sử dụng**
- Hỏi cụ thể hơn để có kết quả chính xác
- Tăng Top-K nếu cần nhiều thông tin hơn
- Sử dụng từ khóa liên quan đến Pickleball, DUPR
"""

    return history_msgs, sources_md, meta_info

def clear_chat():
    return [], "📭 **Không có nguồn tham khảo nào.**", "🔄 **Đã xóa lịch sử chat.** Sẵn sàng cho cuộc trò chuyện mới!"

# ---------- UI ----------
with gr.Blocks(theme=THEME, css=CSS) as demo:
    # Auto-dark according to system preference + enhanced JavaScript
    gr.HTML("""
    <script>
      (function() {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) document.documentElement.classList.add('dark');
        window.toggleDark = function(on){ 
          document.documentElement.classList.toggle('dark', !!on);
          localStorage.setItem('dupr-theme', on ? 'dark' : 'light');
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('dupr-theme');
        if (savedTheme) {
          document.documentElement.classList.toggle('dark', savedTheme === 'dark');
        }
      })();
    </script>
    <script src="/file=static/script.js"></script>
    <link rel="stylesheet" href="/file=static/styles.css">
    """)

    # Header
    with gr.Row():
        with gr.Column():
            gr.HTML("""
              <div class="header-card">
                <div class="header-icon">🏓</div>
                <div>
                  <p class="header-title">DUPR RAG Assistant</p>
                  <p class="header-sub">Trợ lý thông minh cho Pickleball • Tìm kiếm thông tin từ cơ sở dữ liệu chuyên nghiệp</p>
                </div>
              </div>
            """)
    
    # Hidden controls (default values)
    dark_toggle = gr.Checkbox(value=False, visible=False)
    top_k = gr.Slider(1, 10, value=5, step=1, visible=False)

    # Main Chat Interface
    with gr.Row():
        # Chat panel
        with gr.Column(scale=7):
            with gr.Group(elem_classes="chat-container"):
                chatbot = gr.Chatbot(
                    type="messages",
                    height=580,
                    avatar_images=[  # user, assistant
                        "https://cdn-icons-png.flaticon.com/512/9131/9131529.png",
                        "https://cdn-icons-png.flaticon.com/512/4712/4712109.png"
                    ],
                    show_copy_button=True,
                    placeholder="👋 Xin chào! Tôi là trợ lý DUPR. Hãy hỏi tôi về Pickleball, người chơi, hoặc bất kỳ thông tin gì bạn muốn biết...",
                )
                with gr.Row(elem_classes="input-row"):
                    msg = gr.Textbox(
                        placeholder="💬 Hỏi về DUPR, người chơi, bài blog, quy tắc Pickleball...", 
                        scale=7,
                        container=False,
                        show_label=False
                    )
                    send = gr.Button("🚀 Gửi", variant="primary", scale=1)
                    clear = gr.Button("🗑️ Xóa", scale=1)

        # Sources & meta panel
        with gr.Column(scale=5):
            with gr.Group(elem_classes="side-panel"):
                with gr.Tab("📚 Nguồn tham khảo"):
                    sources = gr.Markdown("Chưa có nguồn tham khảo nào.", elem_classes="card")
                with gr.Tab("⚡ Thông tin"):
                    meta = gr.Markdown("", elem_classes="card")

    # Footer
    gr.HTML('''
        <div class="footer">
            ⚡ Được xây dựng với LangChain • Chroma • Groq (Llama 3) • Gradio
            <br>
            🏓 Phiên bản 2.0 - Trợ lý DUPR chuyên nghiệp
        </div>
    ''')

    # Bindings
    send.click(respond, [msg, chatbot, top_k, dark_toggle], [chatbot, sources, meta]).then(lambda: "", None, msg)
    msg.submit(respond, [msg, chatbot, top_k, dark_toggle], [chatbot, sources, meta]).then(lambda: "", None, msg)
    clear.click(clear_chat, None, [chatbot, sources, meta])

    # Dark toggle JS
    def _noop(_): return None
    dark_toggle.change(_noop, dark_toggle, None, js="toggleDark")

if __name__ == "__main__":
    assert os.getenv("GROQ_API_KEY"), "Thiếu GROQ_API_KEY env"
    demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
