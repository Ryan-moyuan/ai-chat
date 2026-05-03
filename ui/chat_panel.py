"""聊天面板"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image as PILImage, ImageTk
import threading
from i18n import t
import core.chat_engine as chat_engine
import core.memory_manager as memory
import core.rag_engine as rag
import core.feedback as feedback
from core.image_generator import generate as gen_image, save_image
from config_loader import load_config


class MessageBubble(ctk.CTkFrame):
    """单条消息气泡"""

    def __init__(self, parent, role, content, message_id=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=("gray85", "gray25"))
        self.role = role
        self.message_id = message_id
        self._feedback_added = False

        # 角色标签
        label = t("role_ai") if role == "assistant" else t("role_you")
        self.role_label = ctk.CTkLabel(self, text=label, font=("Arial", 12, "bold"))
        self.role_label.pack(anchor="w", padx=10, pady=(8, 2))

        # 内容
        self.content_label = ctk.CTkLabel(
            self, text=content, wraplength=700, justify="left", anchor="w"
        )
        self.content_label.pack(anchor="w", padx=10, pady=(0, 4))

        # 图像占位
        self.image_ref = None
        self.feedback_row = None

    def add_image(self, pil_image):
        """在气泡中添加图像"""
        img = ImageTk.PhotoImage(pil_image.resize((300, 300)))
        self.image_ref = img  # keep reference
        self.image_label = ctk.CTkLabel(self, text="", image=img)
        self.image_label.image = img
        self.image_label.pack(anchor="w", padx=10, pady=(0, 4))

    def add_feedback_buttons(self, on_feedback=None):
        """添加反馈按钮"""
        if self._feedback_added:
            return
        self._feedback_added = True
        self.feedback_row = ctk.CTkFrame(self, fg_color="transparent")
        self.feedback_row.pack(anchor="w", padx=10, pady=(0, 8))

        btn_up = ctk.CTkButton(
            self.feedback_row, text="up", width=40, height=20, font=("Arial", 10),
            command=lambda: self._do_feedback(True, on_feedback),
        )
        btn_up.pack(side="left", padx=(0, 5))
        btn_up.configure(fg_color=("green", "dark green"))

        btn_down = ctk.CTkButton(
            self.feedback_row, text="down", width=40, height=20, font=("Arial", 10),
            command=lambda: self._do_feedback(False, on_feedback),
        )
        btn_down.pack(side="left")
        btn_down.configure(fg_color=("red", "dark red"))

    def _do_feedback(self, is_good, callback):
        if self.message_id:
            feedback.give_feedback(self.message_id, is_good)
        if callback:
            callback()


class ChatPanel(ctk.CTkFrame):
    """聊天面板"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.conv_id = None
        self._message_count = 0
        self._current_bubbles = []
        self._default_title = t("new_chat_default")

        self._build_ui()
        # 创建默认会话
        self.conv_id = memory.create_conversation(self._default_title)
        self._update_conversation_list()

    def _build_ui(self):
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(toolbar, text=t("conversation_list"), font=("Arial", 13, "bold")).pack(side="left", padx=5)
        self.conv_var = tk.StringVar()
        self.conv_menu = ctk.CTkOptionMenu(toolbar, values=[], variable=self.conv_var, width=200,
                                           command=self._switch_conversation)
        self.conv_menu.pack(side="left", padx=5)

        new_btn = ctk.CTkButton(toolbar, text=t("new_conversation"), width=100, command=self._new_conversation)
        new_btn.pack(side="left", padx=5)

        del_btn = ctk.CTkButton(toolbar, text=t("delete"), width=60, fg_color="red", command=self._delete_conversation)
        del_btn.pack(side="left", padx=5)

        # 消息显示区
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text=t("dialog_title"))
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.messages_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.messages_container.pack(fill="both", expand=True)

        # 状态提示
        self.status_label = ctk.CTkLabel(self, text=t("status_empty"), text_color="gray")
        self.status_label.pack(anchor="w", padx=5, pady=(0, 5))

        # 底部输入区
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.image_mode_var = tk.BooleanVar(value=False)
        img_toggle = ctk.CTkCheckBox(input_frame, text=t("generate_image"), variable=self.image_mode_var)
        img_toggle.pack(side="left", padx=5)

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text=t("placeholder_message"), height=40)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.input_entry.bind("<Return>", lambda e: self._send())

        send_btn = ctk.CTkButton(input_frame, text=t("send"), width=80, command=self._send)
        send_btn.pack(side="right", padx=5)

    def _update_conversation_list(self):
        convs = memory.get_conversations()
        values = [f"{c['title']} ({c['id']})" for c in convs]
        self.conv_menu.configure(values=values)
        if values and not self.conv_var.get():
            self.conv_var.set(values[0])

    def _new_conversation(self):
        self.conv_id = memory.create_conversation(self._default_title)
        self._update_conversation_list()
        self._clear_messages()

    def _delete_conversation(self):
        val = self.conv_var.get()
        if not val:
            return
        cid = val.split("(")[-1].rstrip(")")
        memory.delete_conversation(cid)
        self._update_conversation_list()
        self._clear_messages()
        self.conv_id = memory.create_conversation(self._default_title)

    def _switch_conversation(self, val):
        cid = val.split("(")[-1].rstrip(")")
        self.conv_id = cid
        self._clear_messages()
        self._load_messages()

    def _clear_messages(self):
        for w in self.messages_container.winfo_children():
            w.destroy()
        self._message_count = 0
        self._current_bubbles.clear()

    def _load_messages(self):
        if not self.conv_id:
            return
        messages = memory.get_conversation_messages(self.conv_id)
        for msg in messages:
            bubble = MessageBubble(self.messages_container, msg["role"], msg["content"])
            bubble.pack(fill="x", pady=5, padx=10)

    def _add_message(self, role, content, message_id=None):
        bubble = MessageBubble(self.messages_container, role, content, message_id)
        bubble.pack(fill="x", pady=5, padx=10)
        self._current_bubbles.append(bubble)

        self.messages_container.update_idletasks()
        self.scroll_frame._parent_canvas.yview_moveto(1.0)
        return bubble

    def _send(self):
        text = self.input_entry.get().strip()
        if not text:
            return

        self.input_entry.delete(0, "end")
        self._message_count += 1

        # 保存用户消息
        user_msg_id = memory.save_message(self.conv_id, "user", text)
        self._add_message("user", text, user_msg_id)

        # 更新会话标题（第一条消息时）
        if self._message_count == 1:
            memory.update_conversation_title(self.conv_id, text[:30])
            self._update_conversation_list()

        if self.image_mode_var.get():
            self._generate_image(text)
        else:
            self._chat(text)

    def _get_rag_context(self, query):
        """获取 RAG 检索结果"""
        try:
            return rag.retrieve(query)
        except Exception:
            return ""

    def _chat(self, user_text):
        """发送聊天请求（流式）"""
        config = load_config()
        max_turns = config.get("max_history_turns", 20)

        history = memory.get_conversation_messages(self.conv_id)
        context_messages = history[:-1] if len(history) > 1 else []
        context_messages = context_messages[-(max_turns * 2):] if context_messages else []

        system_ctx = self._get_rag_context(user_text)
        if system_ctx:
            system_ctx = f"以下是参考文档内容：\n{system_ctx}\n\n请基于以上文档内容回答用户的问题。"

        bubble = self._add_message("assistant", "...")
        bubble.content_label.configure(text=t("thinking"))
        self.status_label.configure(text=t("generating"))

        def stream_worker():
            try:
                response_messages = context_messages.copy()
                response_messages.append({"role": "user", "content": user_text})

                stream = chat_engine.chat(response_messages, system_context=system_ctx)

                full_text = ""
                for chunk in stream:
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        text_delta = chunk.delta.text
                        full_text += text_delta
                        self.after(0, lambda t=full_text: bubble.content_label.configure(text=t))
                        self.after(0, lambda: self.scroll_frame._parent_canvas.yview_moveto(1.0))

                ai_msg_id = memory.save_message(self.conv_id, "assistant", full_text)
                self.after(0, lambda: bubble.add_feedback_buttons())

            except Exception as e:
                error_msg = t("error_format", error=str(e))
                self.after(0, lambda: bubble.content_label.configure(text=error_msg))
            finally:
                self.after(0, lambda: self.status_label.configure(text=t("status_empty")))

        threading.Thread(target=stream_worker, daemon=True).start()

    def _generate_image(self, prompt):
        """生成图像"""
        bubble = self._add_message("assistant", t("image_generating_prompt", prompt=prompt[:50]))
        self.status_label.configure(text=t("generating_image"))

        def gen_worker():
            try:
                config = load_config()
                mode = config.get("image_provider", "local")

                img = gen_image(prompt, mode=mode, negative_prompt="", num_steps=30)
                path = save_image(img)

                self.after(0, lambda: bubble.content_label.configure(text=t("image_generated", prompt=prompt)))
                self.after(0, lambda: bubble.add_image(img))
                memory.save_message(self.conv_id, "assistant", f"{t('image_tag')} {prompt}")

            except Exception as e:
                error_msg = t("image_error", error=str(e))
                self.after(0, lambda: bubble.content_label.configure(text=error_msg))
            finally:
                self.after(0, lambda: self.status_label.configure(text=t("status_empty")))

        threading.Thread(target=gen_worker, daemon=True).start()
