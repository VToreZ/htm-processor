"""
GUI приложение для обработки HTM файлов и записи в .01
С поддержкой Drag & Drop
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Пробуем импортировать tkinterdnd2 для drag & drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    HAS_DND = True
except ImportError:
    HAS_DND = False

from processor import process


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка отчётов HTM -> .01")
        self.root.geometry("500x450")
        self.root.resizable(True, True)

        # Пути к файлам
        self.htm_path = tk.StringVar()
        self.file_01_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(
            main_frame, text="Обработка отчётов HTM -> .01", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Зона Drag & Drop
        self.create_drop_zone(main_frame)

        # Секция выбранных файлов
        files_frame = ttk.LabelFrame(main_frame, text="Выбранные файлы", padding="10")
        files_frame.pack(fill=tk.X, pady=10)

        # HTM файл
        htm_frame = ttk.Frame(files_frame)
        htm_frame.pack(fill=tk.X, pady=2)

        ttk.Label(htm_frame, text="HTM:", width=6).pack(side=tk.LEFT)
        self.htm_label = ttk.Label(
            htm_frame, textvariable=self.htm_path, foreground="gray"
        )
        self.htm_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.htm_status = ttk.Label(htm_frame, text="", width=3)
        self.htm_status.pack(side=tk.RIGHT)

        # .01 файл
        file_01_frame = ttk.Frame(files_frame)
        file_01_frame.pack(fill=tk.X, pady=2)

        ttk.Label(file_01_frame, text=".01:", width=6).pack(side=tk.LEFT)
        self.file_01_label = ttk.Label(
            file_01_frame, textvariable=self.file_01_path, foreground="gray"
        )
        self.file_01_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.file_01_status = ttk.Label(file_01_frame, text="", width=3)
        self.file_01_status.pack(side=tk.RIGHT)

        # Кнопки выбора файлов
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="Выбрать HTM", command=self.select_htm).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(buttons_frame, text="Выбрать .01", command=self.select_01).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(buttons_frame, text="Очистить", command=self.clear_files).pack(
            side=tk.RIGHT, padx=5
        )

        # Кнопка обработки
        self.process_btn = ttk.Button(
            main_frame,
            text="Обработать",
            command=self.run_processing,
            state=tk.DISABLED,
        )
        self.process_btn.pack(pady=10, ipadx=20, ipady=5)

        # Область результатов
        result_frame = ttk.LabelFrame(main_frame, text="Результат", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=8, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Скроллбар для результатов
        scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

    def create_drop_zone(self, parent):
        """Создаёт зону для Drag & Drop"""
        drop_frame = ttk.Frame(parent, relief="groove", borderwidth=2)
        drop_frame.pack(fill=tk.X, pady=10)

        # Внутренний контейнер для центрирования
        inner_frame = ttk.Frame(drop_frame)
        inner_frame.pack(expand=True, pady=20)

        if HAS_DND:
            drop_text = "Перетащите сюда файлы .HTM и .01"
        else:
            drop_text = "Используйте кнопки ниже для выбора файлов"

        self.drop_label = ttk.Label(
            inner_frame, text=drop_text, font=("Arial", 11), foreground="gray"
        )
        self.drop_label.pack()

        sub_label = ttk.Label(
            inner_frame,
            text="или нажмите кнопки выбора ниже",
            font=("Arial", 9),
            foreground="lightgray",
        )
        sub_label.pack()

        # Настраиваем Drag & Drop если доступно
        if HAS_DND:
            drop_frame.drop_target_register(DND_FILES)
            drop_frame.dnd_bind("<<Drop>>", self.on_drop)
            drop_frame.dnd_bind("<<DragEnter>>", self.on_drag_enter)
            drop_frame.dnd_bind("<<DragLeave>>", self.on_drag_leave)

    def on_drop(self, event):
        """Обработчик события Drop"""
        files = self.parse_drop_data(event.data)

        for file_path in files:
            self.add_file(file_path)

        self.update_status()

    def on_drag_enter(self, event):
        """Обработчик входа в зону"""
        self.drop_label.config(foreground="blue")

    def on_drag_leave(self, event):
        """Обработчик выхода из зоны"""
        self.drop_label.config(foreground="gray")

    def parse_drop_data(self, data):
        """Парсит данные из события Drop"""
        files = []

        # Обработка разных форматов
        if "{" in data:
            # Формат с фигурными скобками (пути с пробелами)
            import re

            files = re.findall(r"\{([^}]+)\}", data)
            # Добавляем пути без скобок
            remaining = re.sub(r"\{[^}]+\}", "", data).strip()
            if remaining:
                files.extend(remaining.split())
        else:
            files = data.split()

        return [f.strip() for f in files if f.strip()]

    def add_file(self, file_path):
        """Добавляет файл в соответствующее поле"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".htm", ".html"]:
            self.htm_path.set(file_path)
            self.htm_status.config(text="OK", foreground="green")
        elif ext == ".01":
            self.file_01_path.set(file_path)
            self.file_01_status.config(text="OK", foreground="green")

    def select_htm(self):
        """Диалог выбора HTM файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите HTM файл",
            filetypes=[("HTM files", "*.htm *.html"), ("All files", "*.*")],
        )
        if file_path:
            self.add_file(file_path)
            self.update_status()

    def select_01(self):
        """Диалог выбора .01 файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл .01",
            filetypes=[("01 files", "*.01"), ("All files", "*.*")],
        )
        if file_path:
            self.add_file(file_path)
            self.update_status()

    def clear_files(self):
        """Очищает выбранные файлы"""
        self.htm_path.set("")
        self.file_01_path.set("")
        self.htm_status.config(text="")
        self.file_01_status.config(text="")
        self.update_status()
        self.clear_result()

    def update_status(self):
        """Обновляет состояние кнопки обработки"""
        if self.htm_path.get() and self.file_01_path.get():
            self.process_btn.config(state=tk.NORMAL)
        else:
            self.process_btn.config(state=tk.DISABLED)

    def clear_result(self):
        """Очищает область результатов"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

    def log(self, message):
        """Добавляет сообщение в область результатов"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def run_processing(self):
        """Запускает обработку файлов"""
        htm_path = self.htm_path.get()
        file_01_path = self.file_01_path.get()

        if not htm_path or not file_01_path:
            messagebox.showerror("Ошибка", "Выберите оба файла!")
            return

        # Проверяем существование файлов
        if not os.path.exists(htm_path):
            messagebox.showerror("Ошибка", f"HTM файл не найден:\n{htm_path}")
            return

        if not os.path.exists(file_01_path):
            messagebox.showerror("Ошибка", f"Файл .01 не найден:\n{file_01_path}")
            return

        self.clear_result()
        self.log("Начинаю обработку...")
        self.root.update()

        try:
            result = process(htm_path, file_01_path)

            self.log("")
            self.log(f"Найдено записей в HTM: {result['parsed_count']}")
            self.log(f"Применено значений: {result['applied_count']}")
            self.log(f"Пропущено: {result['skipped_count']}")
            self.log("")
            self.log(f"Результат сохранён: {result['output_path']}")

            if result["errors"]:
                self.log("")
                self.log("Ошибки:")
                for err in result["errors"][:10]:
                    self.log(f"  - {err}")
                if len(result["errors"]) > 10:
                    self.log(f"  ... и ещё {len(result['errors']) - 10}")

            messagebox.showinfo(
                "Готово",
                f"Обработка завершена!\n\nПрименено: {result['applied_count']} значений\nРезультат: {os.path.basename(result['output_path'])}",
            )

        except Exception as e:
            self.log(f"ОШИБКА: {e}")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")


def main():
    # Создаём окно с поддержкой DnD если доступно
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
