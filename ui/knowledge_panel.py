"""知识库面板"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import os
from i18n import t
from core.rag_engine import load_document, delete_document, list_documents


class KnowledgePanel(ctk.CTkFrame):
    """知识库管理面板"""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()
        self._refresh_doc_list()

    def _build_ui(self):
        ctk.CTkLabel(self, text=t("knowledge_title"), font=("Arial", 18, "bold")).pack(pady=10)

        # 说明
        desc = ctk.CTkLabel(
            self,
            text=t("knowledge_desc"),
            text_color="gray",
        )
        desc.pack(pady=5)

        # 上传区域
        upload_frame = ctk.CTkFrame(self)
        upload_frame.pack(fill="x", padx=20, pady=10)

        self.upload_btn = ctk.CTkButton(upload_frame, text=t("upload_file"), command=self._upload_file)
        self.upload_btn.pack(side="left", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(upload_frame, text=t("status_empty"), text_color="gray")
        self.status_label.pack(side="left", padx=10, pady=10)

        # 进度条
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.pack(padx=20, pady=5)
        self.progress.set(0)

        # 文档列表
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(list_frame, text=t("loaded_docs"), font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 滚动文档列表
        scroll = ctk.CTkScrollableFrame(list_frame, label_text="")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.docs_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.docs_container.pack(fill="both", expand=True)

        # 统计
        self.stats_label = ctk.CTkLabel(self, text=t("status_empty"), text_color="gray")
        self.stats_label.pack(pady=5)

    def _refresh_doc_list(self):
        """刷新文档列表显示"""
        try:
            docs = list_documents()
        except Exception:
            # 如果 chromadb 未初始化（打包版首次运行），显示空列表
            docs = {}
        total_chunks = 0

        for w in self.docs_container.winfo_children():
            w.destroy()

        if not docs:
            empty_label = ctk.CTkLabel(self.docs_container, text=t("no_docs"), text_color="gray")
            empty_label.pack(pady=20)
        else:
            for i, (filename, chunk_count) in enumerate(docs.items()):
                row = ctk.CTkFrame(self.docs_container, fg_color=("gray85", "gray25"))
                row.pack(fill="x", padx=5, pady=2)

                ctk.CTkLabel(row, text=t("chunk_format", filename=filename, count=chunk_count), width=300).pack(side="left", padx=10, pady=5)

                del_btn = ctk.CTkButton(
                    row, text=t("delete"), width=60, height=24, fg_color="red",
                    command=lambda f=filename: self._delete_doc(f),
                )
                del_btn.pack(side="right", padx=10)

                total_chunks += chunk_count

        doc_count = len(docs)
        self.stats_label.configure(text=t("stats_format", count=doc_count, chunks=total_chunks))

    def _upload_file(self):
        filepath = filedialog.askopenfilename(
            title="选择文档文件",
            filetypes=[
                ("文档文件 / Documents", "*.txt *.pdf *.docx"),
                ("文本文件 / Text", "*.txt"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("所有文件 / All", "*.*"),
            ],
        )
        if not filepath:
            return

        filename = os.path.basename(filepath)
        self.status_label.configure(text=t("status_loading", filename=filename), text_color="blue")
        self.progress.set(0)

        def load_worker():
            try:
                self.after(0, lambda: self.progress.set(0.5))
                chunks = load_document(filepath)
                self.after(0, lambda: self.progress.set(1.0))
                self.after(0, lambda: self.status_label.configure(
                    text=t("status_loaded", filename=filename, chunks=chunks), text_color="green"
                ))
                self.after(0, self._refresh_doc_list)
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=t("status_load_error", error=str(e)), text_color="red"
                ))
            finally:
                self.after(0, lambda: self.progress.set(0))

        threading.Thread(target=load_worker, daemon=True).start()

    def _delete_doc(self, filename):
        delete_document(filename)
        self._refresh_doc_list()
        self.status_label.configure(text=t("status_delete", filename=filename), text_color="green")
