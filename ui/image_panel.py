"""图像生成面板"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image as PILImage, ImageTk
import threading
from i18n import t
from core.image_generator import generate as gen_image, save_image
from config_loader import load_config


class ImagePanel(ctk.CTkFrame):
    """图像生成面板"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_image = None
        self._build_ui()

    def _build_ui(self):
        # 模式选择
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(mode_frame, text="", font=("Arial", 13, "bold")).pack(side="left", padx=5)

        self.mode_var = tk.StringVar(value="dalle")
        ctk.CTkRadioButton(mode_frame, text=t("image_provider_local"), variable=self.mode_var, value="local").pack(side="left", padx=5)
        ctk.CTkRadioButton(mode_frame, text=t("image_provider_dalle"), variable=self.mode_var, value="dalle").pack(side="left", padx=5)
        ctk.CTkRadioButton(mode_frame, text=t("image_provider_stability"), variable=self.mode_var, value="stability").pack(side="left", padx=5)

        # Prompt 输入
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(prompt_frame, text=t("prompt_label"), font=("Arial", 13)).pack(anchor="w", padx=5, pady=(5, 0))
        self.prompt_text = ctk.CTkTextbox(prompt_frame, height=80, wrap="word")
        self.prompt_text.pack(fill="x", padx=5, pady=(0, 5))

        # Negative Prompt
        neg_frame = ctk.CTkFrame(self)
        neg_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(neg_frame, text=t("neg_prompt_label"), font=("Arial", 13)).pack(anchor="w", padx=5, pady=(5, 0))
        self.neg_prompt_text = ctk.CTkTextbox(neg_frame, height=50, wrap="word")
        self.neg_prompt_text.insert("0.0", t("neg_prompt_default"))
        self.neg_prompt_text.pack(fill="x", padx=5, pady=(0, 5))

        # 参数控制
        param_frame = ctk.CTkFrame(self)
        param_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(param_frame, text=t("params_label")).pack(anchor="w", padx=5, pady=(5, 0))

        steps_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
        steps_frame.pack(fill="x", padx=20, pady=(0, 5))
        ctk.CTkLabel(steps_frame, text=t("steps_label")).pack(side="left", padx=5)
        self.steps_var = tk.IntVar(value=30)
        steps_slider = ctk.CTkSlider(steps_frame, from_=10, to=50, variable=self.steps_var, width=200)
        steps_slider.pack(side="left", padx=5)
        self.steps_label = ctk.CTkLabel(steps_frame, text="30", width=20)
        self.steps_label.pack(side="left", padx=5)
        steps_slider.configure(command=lambda v: self.steps_label.configure(text=str(int(v))))

        size_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=(0, 5))
        ctk.CTkLabel(size_frame, text=t("size_label")).pack(side="left", padx=5)
        self.size_var = tk.StringVar(value="512x512")
        for size in ["256x256", "512x512", "768x768", "1024x1024"]:
            ctk.CTkRadioButton(size_frame, text=size, variable=self.size_var, value=size).pack(side="left", padx=5)

        # 生成按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=10)

        self.generate_btn = ctk.CTkButton(btn_frame, text=t("btn_generate"), height=40, font=("Arial", 15, "bold"), command=self._generate)
        self.generate_btn.pack(side="left", padx=5)

        self.save_btn = ctk.CTkButton(btn_frame, text=t("btn_save"), height=40, command=self._save)
        self.save_btn.pack(side="left", padx=5)

        # 状态
        self.status_label = ctk.CTkLabel(self, text=t("status_empty"), text_color="gray")
        self.status_label.pack(anchor="center", padx=5, pady=5)

        # 图像展示区
        img_frame = ctk.CTkFrame(self)
        img_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.image_label = ctk.CTkLabel(img_frame, text=t("image_placeholder"), font=("Arial", 14))
        self.image_label.pack(expand=True, fill="both")

    def _get_size(self):
        w, h = self.size_var.get().split("x")
        return int(w), int(h)

    def _generate(self):
        prompt = self.prompt_text.get("0.0", "end").strip()
        if not prompt:
            self.status_label.configure(text=t("status_no_prompt"), text_color="orange")
            return

        neg_prompt = self.neg_prompt_text.get("0.0", "end").strip()
        steps = self.steps_var.get()
        width, height = self._get_size()
        mode = self.mode_var.get()

        self.status_label.configure(text=t("generating_image"), text_color="blue")
        self.generate_btn.configure(state="disabled")

        def gen_worker():
            try:
                img = gen_image(
                    prompt, mode=mode,
                    negative_prompt=neg_prompt,
                    num_steps=steps,
                    width=width, height=height,
                )
                self.current_image = img

                # 缩放显示
                display_img = img.copy()
                display_img.thumbnail((600, 600))
                tk_img = ImageTk.PhotoImage(display_img)

                self.after(0, lambda: self.image_label.configure(image=tk_img, text=""))
                self.after(0, lambda: setattr(self.image_label, "image", tk_img))
                self.after(0, lambda: self.status_label.configure(text=t("status_done"), text_color="green"))

            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=t("error_format", error=str(e)), text_color="red"))
            finally:
                self.after(0, lambda: self.generate_btn.configure(state="normal"))

        threading.Thread(target=gen_worker, daemon=True).start()

    def _save(self):
        if not self.current_image:
            self.status_label.configure(text=t("status_no_image"), text_color="orange")
            return

        path = save_image(self.current_image)
        self.status_label.configure(text=t("status_save", path=path), text_color="green")
