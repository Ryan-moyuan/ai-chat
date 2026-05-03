"""设置面板"""
import customtkinter as ctk
import tkinter as tk
from i18n import t, set_language, init as i18n_init
from config_loader import load_config, save_config


class SettingsPanel(ctk.CTkFrame):
    """设置面板"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        ctk.CTkLabel(self, text=t("settings_title"), font=("Arial", 18, "bold")).pack(pady=10)

        # API Keys
        api_frame = ctk.CTkFrame(self)
        api_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(api_frame, text=t("api_keys_title"), font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        # Anthropic Key
        frame1 = ctk.CTkFrame(api_frame, fg_color="transparent")
        frame1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame1, text=t("anthropic_key"), width=120).pack(side="left", padx=5)
        self.anthropic_key_var = tk.StringVar()
        entry1 = ctk.CTkEntry(frame1, textvariable=self.anthropic_key_var, show="*", width=300)
        entry1.pack(side="left", padx=5, fill="x", expand=True)

        # Base URL
        frame1b = ctk.CTkFrame(api_frame, fg_color="transparent")
        frame1b.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame1b, text=t("base_url"), width=120).pack(side="left", padx=5)
        self.anthropic_base_url_var = tk.StringVar()
        entry1b = ctk.CTkEntry(frame1b, textvariable=self.anthropic_base_url_var, width=300)
        entry1b.pack(side="left", padx=5, fill="x", expand=True)

        # Stability Key
        frame2 = ctk.CTkFrame(api_frame, fg_color="transparent")
        frame2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame2, text=t("stability_key"), width=120).pack(side="left", padx=5)
        self.stability_key_var = tk.StringVar()
        entry2 = ctk.CTkEntry(frame2, textvariable=self.stability_key_var, show="*", width=300)
        entry2.pack(side="left", padx=5, fill="x", expand=True)

        # OpenAI Key
        frame3 = ctk.CTkFrame(api_frame, fg_color="transparent")
        frame3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame3, text=t("openai_key"), width=120).pack(side="left", padx=5)
        self.openai_key_var = tk.StringVar()
        entry3 = ctk.CTkEntry(frame3, textvariable=self.openai_key_var, show="*", width=300)
        entry3.pack(side="left", padx=5, fill="x", expand=True)

        # 模型设置
        model_frame = ctk.CTkFrame(self)
        model_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(model_frame, text=t("model_settings"), font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        # 模型选择
        frame4 = ctk.CTkFrame(model_frame, fg_color="transparent")
        frame4.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame4, text=t("claude_model"), width=120).pack(side="left", padx=5)
        self.claude_model_var = tk.StringVar()
        ctk.CTkOptionMenu(frame4, values=["qwen3.5-plus", "claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-sonnet-20241022"],
                          variable=self.claude_model_var, width=250).pack(side="left", padx=5)

        # SD 模型
        frame5 = ctk.CTkFrame(model_frame, fg_color="transparent")
        frame5.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame5, text=t("sd_model"), width=120).pack(side="left", padx=5)
        self.sd_model_var = tk.StringVar()
        ctk.CTkOptionMenu(frame5, values=["runwayml/stable-diffusion-v1-5", "stabilityai/stable-diffusion-2-1",
                                           "prompthero/sd-mixline"],
                          variable=self.sd_model_var, width=250).pack(side="left", padx=5)

        # 图像生成模式
        frame6 = ctk.CTkFrame(model_frame, fg_color="transparent")
        frame6.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame6, text=t("image_mode"), width=120).pack(side="left", padx=5)
        self.image_provider_var = tk.StringVar()
        ctk.CTkOptionMenu(frame6, values=["local", "dalle", "stability"],
                          variable=self.image_provider_var, width=250).pack(side="left", padx=5)

        # 语言设置
        lang_frame = ctk.CTkFrame(self)
        lang_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(lang_frame, text="Language", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        frame_lang = ctk.CTkFrame(lang_frame, fg_color="transparent")
        frame_lang.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame_lang, text="Language:", width=120).pack(side="left", padx=5)
        self.lang_var = tk.StringVar()
        ctk.CTkOptionMenu(frame_lang, values=["en - English", "zh - 中文", "ja - 日本語"],
                          variable=self.lang_var, width=250, command=self._change_language).pack(side="left", padx=5)

        # 高级设置
        adv_frame = ctk.CTkFrame(self)
        adv_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(adv_frame, text=t("advanced_settings"), font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        # 最大历史轮数
        frame7 = ctk.CTkFrame(adv_frame, fg_color="transparent")
        frame7.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame7, text=t("memory_turns"), width=120).pack(side="left", padx=5)
        self.max_turns_var = tk.IntVar(value=20)
        ctk.CTkSlider(frame7, from_=5, to=50, variable=self.max_turns_var, width=200,
                       command=lambda v: self.turns_label.configure(text=str(int(v)))).pack(side="left", padx=5)
        self.turns_label = ctk.CTkLabel(frame7, text="20", width=30)
        self.turns_label.pack(side="left", padx=5)

        # RAG top K
        frame8 = ctk.CTkFrame(adv_frame, fg_color="transparent")
        frame8.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame8, text=t("rag_topk"), width=120).pack(side="left", padx=5)
        self.rag_topk_var = tk.IntVar(value=3)
        ctk.CTkSlider(frame8, from_=1, to=10, variable=self.rag_topk_var, width=200,
                       command=lambda v: self.rag_label.configure(text=str(int(v)))).pack(side="left", padx=5)
        self.rag_label = ctk.CTkLabel(frame8, text="3", width=30)
        self.rag_label.pack(side="left", padx=5)

        # 主题
        frame9 = ctk.CTkFrame(adv_frame, fg_color="transparent")
        frame9.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(frame9, text=t("theme_label"), width=120).pack(side="left", padx=5)
        self.theme_var = tk.StringVar()
        ctk.CTkOptionMenu(frame9, values=["dark", "light", "system"],
                          variable=self.theme_var, width=250).pack(side="left", padx=5)

        # 保存按钮
        save_btn = ctk.CTkButton(self, text=t("save_settings"), width=200, height=40,
                                  font=("Arial", 14, "bold"), command=self._save_settings)
        save_btn.pack(pady=20)

        self.save_status = ctk.CTkLabel(self, text=t("status_empty"), text_color="gray")
        self.save_status.pack()

    def _change_language(self, val):
        """切换语言"""
        if "zh" in val:
            lang_code = "zh"
        elif "en" in val:
            lang_code = "en"
        elif "ja" in val:
            lang_code = "ja"
        else:
            return

        # 先保存到配置
        config = load_config()
        config["language"] = lang_code
        save_config(config)

        # 切换语言
        set_language(lang_code)
        i18n_init()

        # 重建窗口
        self.app.rebuild()

    def _load_settings(self):
        config = load_config()
        self.anthropic_key_var.set(config.get("anthropic_api_key", ""))
        self.anthropic_base_url_var.set(config.get("anthropic_base_url", ""))
        self.stability_key_var.set(config.get("stability_api_key", ""))
        self.openai_key_var.set(config.get("openai_api_key", ""))
        self.claude_model_var.set(config.get("claude_model", "claude-sonnet-4-20250514"))
        self.sd_model_var.set(config.get("sd_model", "runwayml/stable-diffusion-v1-5"))
        self.image_provider_var.set(config.get("image_provider", "dalle"))
        self.max_turns_var.set(config.get("max_history_turns", 20))
        self.rag_topk_var.set(config.get("rag_top_k", 3))
        self.theme_var.set(config.get("theme", "dark"))
        self.turns_label.configure(text=str(self.max_turns_var.get()))
        self.rag_label.configure(text=str(self.rag_topk_var.get()))

        # 语言
        lang = config.get("language", "en")
        lang_map = {"zh": "zh - 中文", "en": "en - English", "ja": "ja - 日本語"}
        self.lang_var.set(lang_map.get(lang, "en - English"))

    def _save_settings(self):
        config = load_config()
        config["anthropic_api_key"] = self.anthropic_key_var.get()
        config["anthropic_base_url"] = self.anthropic_base_url_var.get()
        config["stability_api_key"] = self.stability_key_var.get()
        config["openai_api_key"] = self.openai_key_var.get()
        config["claude_model"] = self.claude_model_var.get()
        config["sd_model"] = self.sd_model_var.get()
        config["image_provider"] = self.image_provider_var.get()
        config["max_history_turns"] = self.max_turns_var.get()
        config["rag_top_k"] = self.rag_topk_var.get()
        config["theme"] = self.theme_var.get()

        # 保存语言
        lang_val = self.lang_var.get()
        if "zh" in lang_val:
            config["language"] = "zh"
        elif "en" in lang_val:
            config["language"] = "en"
        elif "ja" in lang_val:
            config["language"] = "ja"

        save_config(config)

        # 应用主题
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)

        self.save_status.configure(text=t("settings_saved"), text_color="green")
