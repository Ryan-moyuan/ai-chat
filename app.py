"""主窗口 - CustomTkinter Tab 布局"""
import customtkinter as ctk
from config_loader import load_config
from i18n import set_language, init as i18n_init


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        config = load_config()
        theme = config.get("theme", "dark")
        ctk.set_appearance_mode(theme)

        # 初始化 i18n
        i18n_init()
        lang = config.get("language", "en")
        set_language(lang)

        from i18n import t
        self.title(t("app_title"))
        self.geometry("1000x700")
        self.minsize(800, 600)

        # Store tab IDs for rebuilding
        self._tab_ids = ["tab_chat", "tab_image", "tab_knowledge", "tab_settings"]
        self._panels = {}

        self._build_ui()

        # 检查是否首次使用（没有 API Key）
        if not config.get("setup_done", False) or not config.get("anthropic_api_key", ""):
            from ui.setup_dialog import SetupDialog
            SetupDialog(self, self._on_setup_complete)

    def _on_setup_complete(self):
        """设置完成回调"""
        pass

    def _build_ui(self):
        from i18n import t

        # 使用 Tab 视图
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建标签页
        for tab_id in self._tab_ids:
            self.tab_view.add(t(tab_id))

        # 聊天面板
        from ui.chat_panel import ChatPanel
        self._panels["chat"] = ChatPanel(self.tab_view.tab(t(self._tab_ids[0])), self)
        self._panels["chat"].pack(fill="both", expand=True, padx=5, pady=5)

        # 图像生成面板
        from ui.image_panel import ImagePanel
        self._panels["image"] = ImagePanel(self.tab_view.tab(t(self._tab_ids[1])), self)
        self._panels["image"].pack(fill="both", expand=True, padx=5, pady=5)

        # 知识库面板
        from ui.knowledge_panel import KnowledgePanel
        self._panels["knowledge"] = KnowledgePanel(self.tab_view.tab(t(self._tab_ids[2])), self)
        self._panels["knowledge"].pack(fill="both", expand=True, padx=5, pady=5)

        # 设置面板
        from ui.settings_panel import SettingsPanel
        self._panels["settings"] = SettingsPanel(self.tab_view.tab(t(self._tab_ids[3])), self)
        self._panels["settings"].pack(fill="both", expand=True, padx=5, pady=5)

        # 切换到聊天标签页
        self.tab_view.set(t(self._tab_ids[0]))

    def rebuild(self):
        """语言切换后重建整个窗口"""
        # 清除
        for panel in self._panels.values():
            if panel.winfo_exists():
                panel.destroy()
        self._panels.clear()

        if self.tab_view.winfo_exists():
            self.tab_view.destroy()

        self._build_ui()
