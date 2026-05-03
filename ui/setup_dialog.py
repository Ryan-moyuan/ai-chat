"""首次设置向导 - 输入 API Key 或使用 Ollama"""
import customtkinter as ctk
import tkinter as tk
from config_loader import load_config, save_config
from i18n import t


class SetupDialog:
    """首次设置对话框"""

    def __init__(self, parent, on_complete):
        self.parent = parent
        self.on_complete = on_complete
        self._build()

    def _build(self):
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(t("app_title"))
        self.dialog.geometry("550x550")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 居中
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 550) // 2
        y = (self.dialog.winfo_screenheight() - 550) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # 标题
        ctk.CTkLabel(self.dialog, text="Setup", font=("Arial", 22, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self.dialog, text=t("setup_welcome"), text_color="gray",
                      wraplength=450).pack(pady=5)

        # 模式选择
        mode_frame = ctk.CTkFrame(self.dialog)
        mode_frame.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(mode_frame, text="选择模式 / Mode:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        self.mode_var = tk.StringVar(value="api")

        api_radio = ctk.CTkRadioButton(
            mode_frame, text="API (Anthropic / 阿里云)", variable=self.mode_var, value="api",
            command=self._toggle_mode
        )
        api_radio.pack(anchor="w", padx=30, pady=5)

        ollama_radio = ctk.CTkRadioButton(
            mode_frame, text="Ollama 本地模型 (免费，无需 API)", variable=self.mode_var, value="ollama",
            command=self._toggle_mode
        )
        ollama_radio.pack(anchor="w", padx=30, pady=5)

        # API 配置
        self.api_frame = ctk.CTkFrame(self.dialog)
        self.api_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(self.api_frame, text=t("anthropic_key"), font=("Arial", 13)).pack(anchor="w", padx=10, pady=(10, 0))
        self.key_var = tk.StringVar()
        entry = ctk.CTkEntry(self.api_frame, textvariable=self.key_var, width=450, height=35)
        entry.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(self.api_frame, text=t("base_url"), font=("Arial", 13)).pack(anchor="w", padx=10, pady=(10, 0))
        self.url_var = tk.StringVar()
        url_entry = ctk.CTkEntry(self.api_frame, textvariable=self.url_var, width=450, height=35)
        url_entry.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.api_frame, text=t("setup_url_hint"), text_color="gray", font=("Arial", 10),
                      wraplength=400).pack(anchor="w", padx=10, pady=(0, 10))

        # Ollama 配置
        self.ollama_frame = ctk.CTkFrame(self.dialog)

        ctk.CTkLabel(self.ollama_frame, text="Ollama 地址:", font=("Arial", 13)).pack(anchor="w", padx=10, pady=(10, 0))
        self.ollama_url_var = tk.StringVar(value="http://localhost:11434")
        ollama_url_entry = ctk.CTkEntry(self.ollama_frame, textvariable=self.ollama_url_var, width=450, height=35)
        ollama_url_entry.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(self.ollama_frame, text="模型名称:", font=("Arial", 13)).pack(anchor="w", padx=10, pady=(10, 0))
        self.ollama_model_var = tk.StringVar(value="qwen2.5:7b")
        ollama_model_entry = ctk.CTkEntry(self.ollama_frame, textvariable=self.ollama_model_var, width=450, height=35)
        ollama_model_entry.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            self.ollama_frame,
            text="先安装 Ollama: brew install ollama\n然后运行：ollama pull qwen2.5:7b",
            text_color="gray", font=("Arial", 10), justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 10))

        self._toggle_mode()

        # 说明
        info = ctk.CTkLabel(self.dialog, text=t("setup_info"), text_color="gray",
                             wraplength=450, justify="left", font=("Arial", 11))
        info.pack(pady=10, padx=30)

        # 按钮
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text=t("setup_start"), width=150, height=40,
                       font=("Arial", 14, "bold"), command=self._save).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text=t("setup_skip"), width=150, height=40,
                       command=self._skip).pack(side="left", padx=10)

    def _toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "api":
            self.api_frame.pack(fill="x", padx=30, pady=10)
            self.ollama_frame.pack_forget()
        else:
            self.api_frame.pack_forget()
            self.ollama_frame.pack(fill="x", padx=30, pady=10)

    def _save(self):
        config = load_config()
        if self.mode_var.get() == "ollama":
            config["use_ollama"] = True
            config["ollama_url"] = self.ollama_url_var.get().strip()
            config["ollama_model"] = self.ollama_model_var.get().strip()
            config["anthropic_api_key"] = ""
            config["anthropic_base_url"] = ""
        else:
            config["use_ollama"] = False
            config["anthropic_api_key"] = self.key_var.get().strip()
            config["anthropic_base_url"] = self.url_var.get().strip()
        config["setup_done"] = True
        save_config(config)
        self.dialog.destroy()
        self.on_complete()

    def _skip(self):
        config = load_config()
        config["setup_done"] = True
        save_config(config)
        self.dialog.destroy()
        self.on_complete()
