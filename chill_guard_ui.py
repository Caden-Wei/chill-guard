"""Image-led macOS workspace; detection, persisted settings and OS actions stay in the controller."""
import json
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageOps

from chill_guard_i18n import Language

WHITE, RAIL, INK = '#FFFFFF', '#EFF3F8', '#17202D'
MUTED, LINE, BLUE, PREVIEW = '#58677B', '#DFE5EE', '#005FCC', '#F1F5FA'
ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)) / 'assets/ui'
MODEL_CODES = ('yolo26s.pt', 'yolo11s.pt', 'yolo11n.pt')
MODEL_LABELS = ('YOLO26s (recommended)', 'YOLO11s (legacy)', 'YOLO11n (lightweight)')
ENGINE_CODES = ('coreml', 'auto', 'pytorch')
ENGINE_LABELS = ('Apple Core ML (recommended)', 'Automatic', 'PyTorch compatibility')


def setup_theme(app):
    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')
    app.root.configure(background=WHITE)


class Workspace:
    def __init__(self, app, version):
        self.app, self.version = app, version
        self.language = Language(app.runtime.get_settings().language)
        self.bindings, self.dynamic_bindings = [], []
        self.images, self.scroll_pages = {}, {}
        self.synchronizing = False
        self.last_signature = self.app_signature = self.editor_signature = None
        self.origins = json.loads((ASSETS / 'origins.json').read_text())
        self.app_icons = {v['application']: k for k, v in self.origins.items() if 'application' in v}
        self.build()

    def t(self, key):
        return self.language.text(key)

    def image(self, name, size=20):
        key = (name, size)
        if key not in self.images:
            source = Image.open(ASSETS / name).convert('RGBA')
            self.images[key] = ctk.CTkImage(source, source, size=(size, size))
        return self.images[key]

    def font(self, size=13, bold=False):
        return ctk.CTkFont(family='SF Pro Text', size=size, weight='bold' if bold else 'normal')

    def frame(self, parent, color=WHITE, bordered=False, **kwargs):
        return ctk.CTkFrame(parent, fg_color=color, corner_radius=12 if bordered else 0,
                            border_width=1 if bordered else 0, border_color=LINE, **kwargs)

    def label(self, parent, key=None, size=13, bold=False, color=INK, **kwargs):
        widget = ctk.CTkLabel(parent, text=kwargs.pop('text', self.t(key) if key else ''), font=self.font(size, bold),
                              text_color=color, anchor='w', **kwargs)
        if key:
            self.bindings.append((widget, key))
        return widget

    def button(self, parent, key, command, primary=False, **kwargs):
        widget = ctk.CTkButton(parent, text=self.t(key) if key else '', command=command,
                              font=self.font(13, primary), height=34, corner_radius=9,
                              fg_color=BLUE if primary else '#F2F5F9',
                              hover_color='#0562D9' if primary else '#E4EBF4',
                              text_color=WHITE if primary else INK, **kwargs)
        if key:
            self.bindings.append((widget, key))
        # CTk's drawn controls need explicit keyboard focus and activation on macOS.
        widget._canvas.configure(takefocus=1)
        widget.bind('<Return>', lambda _: (widget.invoke(), 'break')[1])
        widget.bind('<space>', lambda _: (widget.invoke(), 'break')[1])
        widget.bind('<FocusIn>', lambda _: widget.configure(border_width=2, border_color=BLUE))
        widget.bind('<FocusOut>', lambda _: widget.configure(border_width=0))
        return widget

    def check(self, parent, key, variable, command=None):
        widget = ctk.CTkSwitch(parent, text=self.t(key), variable=variable,
                               command=command or self.refresh, font=self.font(),
                               progress_color=BLUE, button_color=WHITE, button_hover_color='#DCE6F5',
                               fg_color='#D0D7E2', text_color=INK, switch_width=36, switch_height=20, width=330)
        self.bindings.append((widget, key))
        widget._canvas.configure(takefocus=1)
        widget.bind('<space>', lambda _: (widget.toggle(), 'break')[1])
        return widget

    def dynamic(self, parent, source, **kwargs):
        display = tk.StringVar()
        def render(*_):
            value = self.language.system(source.get())
            if display.get() != value:
                display.set(value)
        source.trace_add('write', render)
        self.dynamic_bindings.append(render)
        render()
        return ctk.CTkLabel(parent, textvariable=display, font=self.font(11), text_color=MUTED,
                            anchor='w', **kwargs)

    def build(self):
        a = self.app
        a.root.geometry('1120x760')
        a.root.minsize(1000, 690)
        a.root.title('Chill Guard')
        outer = self.frame(a.root)
        outer.pack(fill='both', expand=True)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)
        rail = self.frame(outer, RAIL, width=204)
        rail.grid(row=0, column=0, sticky='nsew')
        rail.grid_propagate(False)
        rail.columnconfigure(0, weight=1)
        rail.rowconfigure(6, weight=1)
        brand = self.frame(rail, RAIL)
        brand.grid(row=0, column=0, sticky='ew', padx=16, pady=(27, 8))
        icon_source = Image.open(ASSETS.parent / 'app_icon_1024.png').convert('RGBA')
        self.brand_icon = ctk.CTkImage(icon_source, icon_source, size=(40, 40))
        self.label(brand, image=self.brand_icon, width=40, height=40).pack(side='left', padx=(0, 9))
        self.label(brand, size=18, bold=True, text='Chill Guard').pack(side='left')
        self.label(rail, 'Local privacy protection', size=11, color=MUTED).grid(row=1, column=0, sticky='w', padx=18, pady=(0, 25))
        a.panel_buttons, a.panel_frames = {}, {}
        self.nav_icons = {}
        for row, (key, title, icon) in enumerate((('overview', 'Overview', 'home'), ('startup', 'Protected apps', 'apps'), ('parameters', 'Detection', 'settings'), ('hotkeys', 'Shortcuts', 'keyboard')), 2):
            button = self.button(rail, title, lambda k=key: a.switch_settings_panel(k),
                                 width=172, anchor='w', image=self.image(f'{icon}-gray.png'), compound='left')
            button.configure(height=42, border_spacing=12, fg_color=RAIL)
            button.grid(row=row, column=0, sticky='ew', padx=12, pady=3)
            a.panel_buttons[key] = button
            self.nav_icons[key] = icon
        self.label(rail, 'Local processing · No image upload', size=10, color=MUTED, wraplength=170).grid(row=7, column=0, sticky='w', padx=18, pady=(0, 9))
        self.label(rail, size=11, color=MUTED, text=f'v{self.version}').grid(row=8, column=0, sticky='w', padx=18, pady=(0, 19))
        content = self.frame(outer)
        content.grid(row=0, column=1, sticky='nsew')
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        toolbar = self.frame(content, height=44)
        toolbar.grid(row=0, column=0, sticky='ew')
        toolbar.grid_propagate(False)
        language_group = self.frame(toolbar, '#F1F3F7', width=118, height=28)
        language_group.configure(corner_radius=8)
        language_group.pack(side='right', padx=22, pady=8)
        language_group.pack_propagate(False)
        self.language_var = tk.StringVar(value='中文' if self.language.code == 'zh' else 'English')
        self.language_buttons = {}
        for code, text in (('zh', '中文'), ('en', 'EN')):
            button = self.button(language_group, None, lambda c=code: self.set_language(c), width=55)
            button.configure(text=text, height=24, corner_radius=6)
            button.pack(side='left', padx=2, pady=2)
            self.language_buttons[code] = button
        pages = self.frame(content)
        pages.grid(row=1, column=0, sticky='nsew')
        pages.rowconfigure(0, weight=1)
        pages.columnconfigure(0, weight=1)
        for key in a.panel_buttons:
            page = self.frame(pages)
            page.grid(row=0, column=0, sticky='nsew', padx=22, pady=(10, 0))
            a.panel_frames[key] = page
        a.entries = {}
        a.model_var = tk.StringVar(value=a.default_settings.model_name)
        a.backend_var = tk.StringVar(value=a.default_settings.inference_backend)
        a.preview_var = tk.BooleanVar(value=a.runtime.get_settings().preview_enabled)
        a.alert_sound_var = tk.BooleanVar(value=a.runtime.get_settings().alert_sound_enabled)
        a.far_target_boost_var = tk.BooleanVar(value=False)
        a.start_stop_hotkey_var, a.mute_hold_hotkey_var = tk.StringVar(), tk.StringVar()
        self.model_choice, self.backend_choice = tk.StringVar(), tk.StringVar()
        # A controller-compatible text model; the user edits actual application rows.
        a.blacklist_text = tk.Text(a.root)
        a.blacklist_text.bind('<<Modified>>', a.on_blacklist_text_modified)
        self.build_overview(a.panel_frames['overview'])
        self.build_apps(a.panel_frames['startup'])
        self.build_detection(a.panel_frames['parameters'])
        self.build_hotkeys(a.panel_frames['hotkeys'])
        self.footer = self.frame(content)
        self.footer.grid(row=2, column=0, sticky='ew', padx=22, pady=(12, 18))
        self.footer.columnconfigure(0, weight=1)
        self.save_state = tk.StringVar()
        ctk.CTkLabel(self.footer, textvariable=self.save_state, text_color=MUTED, font=self.font(11)).grid(row=0, column=0, sticky='w')
        self.button(self.footer, 'Save changes', a.apply_settings, primary=True, width=128).grid(row=0, column=1)
        self.render_menu()
        for number, key in enumerate(('overview', 'startup', 'parameters', 'hotkeys'), 1):
            a.root.bind(f'<Command-Key-{number}>', lambda _, k=key: (a.switch_settings_panel(k), 'break')[1])
        a.root.bind('<Command-Key-s>', lambda _: (a.apply_settings(), 'break')[1])
        a.root.bind('<Command-Shift-Key-L>', lambda _: (self.toggle_language(), 'break')[1])
        for var in (a.model_var, a.backend_var, a.alert_sound_var, a.far_target_boost_var, a.start_stop_hotkey_var, a.mute_hold_hotkey_var):
            var.trace_add('write', lambda *_: self.refresh())
        a.switch_settings_panel('overview')
        self.select_page('overview')
        a.root.after(50, self.native_appearance)

    def native_appearance(self):
        if sys.platform == 'darwin':
            from AppKit import NSApplication, NSAppearance, NSAppearanceNameAqua
            for window in NSApplication.sharedApplication().windows():
                if str(window.title()) == 'Chill Guard':
                    window.setAppearance_(NSAppearance.appearanceNamed_(NSAppearanceNameAqua))
                    window.setTitlebarAppearsTransparent_(True)

    def heading(self, page, title, subtitle):
        frame = self.frame(page)
        frame.pack(fill='x', pady=(3, 18))
        self.label(frame, title, size=25, bold=True).pack(anchor='w')
        self.label(frame, subtitle, size=12, color=MUTED, wraplength=690).pack(anchor='w', pady=(2, 0))
        return frame

    def build_overview(self, page):
        a = self.app
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        header = self.frame(page)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 18))
        header.columnconfigure(0, weight=1)
        self.label(header, 'Overview', size=25, bold=True).grid(row=0, column=0, sticky='w')
        self.label(header, 'Hide selected apps when your protection rules trigger.', size=12, color=MUTED).grid(row=1, column=0, sticky='w')
        badge = self.frame(header, '#F6F8FB', bordered=True)
        badge.grid(row=0, column=1, rowspan=2, sticky='e', padx=(12, 0))
        self.state_title = tk.StringVar()
        a.status_pill_label = ctk.CTkLabel(badge, textvariable=self.state_title, font=self.font(12, True), text_color=MUTED)
        a.status_pill_label.pack(padx=16, pady=(5, 0))
        self.state_note = tk.StringVar()
        ctk.CTkLabel(badge, textvariable=self.state_note, font=self.font(10), text_color=MUTED, height=18).pack(padx=16, pady=(0, 5))
        body = self.frame(page)
        body.grid(row=1, column=0, sticky='nsew')
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)
        self.preview_card = self.frame(body, PREVIEW, bordered=True)
        self.preview_card.grid(row=0, column=0, sticky='nsew', padx=(0, 14))
        self.preview_card.rowconfigure(0, weight=1)
        self.preview_card.columnconfigure(0, weight=1)
        a.preview_label = ctk.CTkLabel(self.preview_card, text='', fg_color=PREVIEW)
        a.preview_label.grid(row=0, column=0, sticky='nsew', padx=9, pady=9)
        self.empty_preview = self.frame(self.preview_card, PREVIEW)
        self.empty_preview.place(relx=.5, rely=.47, anchor='center')
        self.label(self.empty_preview, image=self.image('camera-gray.png', 57)).pack(pady=(0, 14))
        self.preview_title = tk.StringVar()
        ctk.CTkLabel(self.empty_preview, textvariable=self.preview_title, font=self.font(17, True), text_color=INK).pack()
        self.preview_help = tk.StringVar()
        self.preview_help_label = ctk.CTkLabel(self.empty_preview, textvariable=self.preview_help, font=self.font(12), text_color=MUTED, wraplength=350, justify='center')
        self.preview_help_label.pack(pady=(5, 19))
        self.primary_button = self.button(self.empty_preview, None, self.preview_action, primary=True,
                                          width=156, image=self.image('play-white.png', 13))
        self.primary_button.configure(height=38)
        self.primary_button.pack()
        self.preview_toolbar = self.frame(self.preview_card, PREVIEW, width=0, height=0)
        # The toolbar is placed only while controls exist; an empty frame can occlude the CTA.
        self.preview_toggle = self.button(self.preview_toolbar, 'Hide preview', self.toggle_preview, width=112)
        self.stop_button = self.button(self.preview_toolbar, 'Stop protection', a.toggle_monitoring_from_hotkey, width=122)
        inspector = self.frame(body, width=292)
        inspector.grid(row=0, column=1, sticky='ns')
        inspector.grid_propagate(False)
        inspector.columnconfigure(0, weight=1)
        inspector.rowconfigure(1, weight=1)
        config = self.frame(inspector, bordered=True)
        config.grid(row=0, column=0, sticky='ew', pady=(0, 13))
        config.columnconfigure(1, weight=1)
        self.label(config, 'Detection configuration', size=14, bold=True).grid(row=0, column=0, columnspan=2, sticky='w', padx=16, pady=(10, 6))
        edit = self.button(config, None, lambda: a.switch_settings_panel('parameters'), width=26, image=self.image('settings-gray.png', 16))
        edit.grid(row=0, column=1, sticky='e', padx=12)
        self.model_value, self.engine_value, self.engine_title, self.rule_value = (tk.StringVar() for _ in range(4))
        for row, (title, value) in enumerate((('Detection model', self.model_value), (None, self.engine_value), ('Protection rules', self.rule_value)), 1):
            if title:
                self.label(config, title, size=11, color=MUTED, height=22).grid(row=row, column=0, sticky='w', padx=16, pady=3)
            else:
                ctk.CTkLabel(config, textvariable=self.engine_title, text_color=MUTED, font=self.font(11), anchor='w', height=22).grid(row=row, column=0, sticky='w', padx=16, pady=3)
            ctk.CTkLabel(config, textvariable=value, text_color=INK, font=self.font(11), anchor='e', wraplength=155, justify='right', height=22).grid(row=row, column=1, sticky='e', padx=(8, 16), pady=3)
        self.frame(config, height=8, width=1).grid(row=4, column=0)
        self.overview_apps = self.frame(inspector, bordered=True)
        self.overview_apps.grid(row=1, column=0, sticky='nsew')
        apps_header = self.frame(self.overview_apps)
        apps_header.pack(fill='x', padx=16, pady=(12, 5))
        self.apps_count = tk.StringVar()
        ctk.CTkLabel(apps_header, textvariable=self.apps_count, text_color=INK, font=self.font(14, True), anchor='w').pack(side='left')
        self.button(apps_header, None, lambda: a.switch_settings_panel('startup'), width=25, image=self.image('plus-gray.png', 16)).pack(side='right')
        self.overview_app_rows = self.frame(self.overview_apps)
        self.overview_app_rows.pack(fill='both', expand=True, padx=16, pady=(2, 9))
        self.feedback_label = self.dynamic(page, a.status_var, wraplength=800)
        self.feedback_label.grid(row=2, column=0, sticky='ew', pady=(6, 2))
        shortcut = self.frame(page, bordered=True)
        shortcut.grid(row=3, column=0, sticky='ew', pady=(8, 18))
        shortcut.columnconfigure(1, weight=1)
        self.label(shortcut, image=self.image('keyboard-gray.png', 24)).grid(row=0, column=0, rowspan=2, padx=(17, 12), pady=15)
        self.label(shortcut, 'Quick controls', size=13, bold=True).grid(row=0, column=1, sticky='w', pady=(12, 0))
        self.label(shortcut, 'Toggle protection with your global shortcut.', size=11, color=MUTED).grid(row=1, column=1, sticky='w', pady=(0, 12))
        self.shortcut_value = tk.StringVar()
        ctk.CTkLabel(shortcut, textvariable=self.shortcut_value, font=self.font(16), text_color=INK, fg_color='#F0F3F7', corner_radius=7).grid(row=0, column=2, rowspan=2, padx=14, ipadx=8)
        self.button(shortcut, 'Change shortcut…', lambda: a.switch_settings_panel('hotkeys'), width=126).grid(row=0, column=3, rowspan=2, padx=(0, 16))

    def section(self, parent, title):
        group = self.frame(parent, bordered=True)
        group.pack(fill='x', pady=(0, 13))
        self.label(group, title, size=14, bold=True).pack(anchor='w', padx=18, pady=(13, 8))
        body = self.frame(group)
        body.pack(fill='x', padx=18, pady=(0, 13))
        return body

    def field(self, parent, key, title):
        row = self.frame(parent)
        row.pack(fill='x', pady=5)
        row.columnconfigure(0, weight=1)
        self.label(row, title, wraplength=470).grid(row=0, column=0, sticky='w', padx=(0, 14))
        entry = ctk.CTkEntry(row, width=148, height=32, corner_radius=7, border_color=LINE,
                             fg_color=WHITE, text_color=INK, font=self.font(), justify='right')
        entry.grid(row=0, column=1, sticky='e')
        entry.bind('<KeyRelease>', lambda _: self.refresh())
        entry.bind('<FocusIn>', lambda _: self.reveal_field(entry))
        self.app.entries[key] = entry
        return entry

    def scrollable(self, page, key):
        body = ctk.CTkScrollableFrame(page, fg_color=WHITE, corner_radius=0,
                                     scrollbar_button_color='#D5DDE8', scrollbar_button_hover_color='#AEBBCB')
        body.pack(fill='both', expand=True)
        self.scroll_pages[key] = body._parent_canvas
        return body

    def reveal_field(self, entry):
        canvas = self.scroll_pages.get('advanced' if self.app.monitor_mode_var.get() == 'advanced' else 'basic')
        if not canvas:
            return
        bounds = canvas.bbox('all')
        if not bounds:
            return
        top = entry.winfo_rooty() - canvas.winfo_rooty()
        if top < 0 or top + entry.winfo_height() > canvas.winfo_height():
            body = canvas.nametowidget(canvas.itemcget(canvas.find_all()[0], 'window'))
            canvas.yview_moveto(max(0, (entry.winfo_rooty() - body.winfo_rooty() - 16) / bounds[3]))

    def build_apps(self, page):
        self.heading(page, 'Protected apps', 'Apps on this list are hidden when your protection rules trigger.')
        tools = self.frame(page)
        tools.pack(fill='x', pady=(0, 12))
        self.label(tools, 'Application names', size=14, bold=True).pack(side='left')
        self.button(tools, 'Add application…', self.add_application, image=self.image('plus-gray.png', 13), width=160).pack(side='right')
        self.editor_rows = self.scrollable(page, 'startup')
        manual = self.frame(page)
        manual.pack(fill='x', pady=(10, 0))
        self.manual_name = ctk.CTkEntry(manual, height=34, width=280, corner_radius=7, border_color=LINE, text_color=INK, placeholder_text_color=MUTED, fg_color=WHITE, font=self.font())
        self.manual_name.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.manual_name.bind('<Return>', lambda _: self.add_process())
        self.button(manual, 'Add process name', self.add_process, width=152).pack(side='right')
        self.label(page, 'Use the exact process name. Changes take effect after Save changes.', size=11, color=MUTED).pack(anchor='w', pady=(9, 0))

    def set_apps(self, names):
        self.app.blacklist_text.delete('1.0', 'end')
        self.app.blacklist_text.insert('1.0', '\n'.join(names))
        self.refresh()

    def add_process(self):
        name = self.manual_name.get().strip()
        names = self.app.get_blacklist_items()
        if name and name not in names:
            self.set_apps(names + [name])
        self.manual_name.delete(0, 'end')

    def remove_process(self, name):
        self.set_apps([value for value in self.app.get_blacklist_items() if value != name])

    def application_rows(self, parent, names, editable=False):
        for child in parent.winfo_children():
            child.destroy()
        if not names:
            self.label(parent, 'No applications listed', color=MUTED).pack(anchor='w', pady=14)
        for name in names:
            row = self.frame(parent, '#F8FAFC' if editable else WHITE)
            row.configure(corner_radius=8)
            row.pack(fill='x', pady=3 if editable else 1)
            row.columnconfigure(1, weight=1)
            self.label(row, image=self.image(self.app_icons.get(name, 'apps-gray.png'), 27 if editable else 23), height=28 if editable else 24).grid(row=0, column=0, padx=(12 if editable else 0, 10), pady=8 if editable else 2)
            self.label(row, text=name, size=13 if editable else 12, height=28 if editable else 24).grid(row=0, column=1, sticky='w')
            button = self.button(row, None, (lambda n=name: self.remove_process(n)) if editable else (lambda: self.app.switch_settings_panel('startup')),
                                 width=28, image=self.image('minus-gray.png' if editable else 'chevron-gray.png', 12))
            button.configure(fg_color='#F8FAFC' if editable else WHITE, height=28 if editable else 25)
            button.grid(row=0, column=2, padx=(7, 9 if editable else 0))

    def build_detection(self, page):
        a = self.app
        header = self.heading(page, 'Detection', 'Tune detection for your workspace.')
        a.parameters_toggle_button = self.button(header, 'Advanced', a.show_monitor_advanced_view, width=136)
        a.parameters_toggle_button.place(relx=1, rely=0, anchor='ne')
        stack = self.frame(page)
        stack.pack(fill='both', expand=True)
        stack.rowconfigure(0, weight=1)
        stack.columnconfigure(0, weight=1)
        basic, advanced = self.frame(stack), self.frame(stack)
        for frame in (basic, advanced):
            frame.grid(row=0, column=0, sticky='nsew')
        a.monitor_basic_frame, a.monitor_advanced_frame = basic, advanced
        body = self.scrollable(basic, 'basic')
        models = self.section(body, 'Model and engine')
        for title, variable, codes, labels, destination in (
            ('Detection model', self.model_choice, MODEL_CODES, MODEL_LABELS, a.model_var),
            ('Inference engine', self.backend_choice, ENGINE_CODES, ENGINE_LABELS, a.backend_var)):
            row = self.frame(models)
            row.pack(fill='x', pady=5)
            self.label(row, title).pack(side='left')
            picker = ctk.CTkOptionMenu(row, variable=variable, values=[self.t(x) for x in labels],
                                       command=lambda value, c=codes, l=labels, d=destination: d.set(c[[self.t(x) for x in l].index(value)]),
                                       width=247, height=32, corner_radius=7, font=self.font(12),
                                       fg_color='#F2F5F9', button_color='#E8EDF5', button_hover_color='#DCE5F2',
                                       text_color=INK, dropdown_fg_color=WHITE, dropdown_text_color=INK,
                                       dropdown_hover_color='#E4EEFF', dropdown_font=self.font(12))
            picker.pack(side='right')
            picker._canvas.configure(takefocus=1)
            picker.bind('<space>', lambda _, p=picker: p._open_dropdown_menu())
            if title == 'Detection model':
                self.model_picker = picker
            else:
                self.backend_picker = picker
        self.label(models, 'Native exports are bundled at 1280. Other sizes use the compatibility engine.', size=11, color=MUTED, wraplength=640).pack(anchor='w', pady=(9, 0))
        rules = self.section(body, 'Protection rules')
        for key, title in (('max_allowed_people', 'Allowed people (including you)'), ('trigger_frame_threshold', 'Consecutive trigger frames'), ('cooldown_seconds', 'Alert cooldown (seconds)'), ('confidence_threshold', 'Confidence threshold')):
            self.field(rules, key, title)
        camera = self.section(body, 'Camera')
        for key, title in (('camera_index', 'Camera index'), ('frame_scale', 'Frame scale'), ('detect_imgsz', 'Detection size')):
            self.field(camera, key, title)
        feedback = self.section(body, 'Feedback')
        self.check(feedback, 'Play alert sound', a.alert_sound_var).pack(side='left')
        self.button(feedback, 'Test sound', a.test_alert_sound, width=110).pack(side='right')
        self.button(body, 'Restore detection defaults', self.restore_defaults, width=213).pack(anchor='w', pady=(2, 10))
        advanced_body = self.scrollable(advanced, 'advanced')
        self.label(advanced_body, 'Main-user tracking uses geometry, not facial identity. Review these rules in your actual camera scene.', size=11, color=MUTED, wraplength=680).pack(anchor='w', pady=(0, 14))
        geometry = self.section(advanced_body, 'Ignore-zone geometry')
        for key, title in (('self_box_expand_x', 'Horizontal expansion'), ('self_box_expand_y_top', 'Top expansion'), ('self_box_expand_y_bottom', 'Bottom expansion')):
            self.field(geometry, key, title)
        tracking = self.section(advanced_body, 'Main-user tracking')
        for key, title in (('self_track_min_confidence', 'Tracking confidence'), ('self_track_max_misses', 'Missed-frame tolerance'), ('min_risk_box_area_ratio', 'Minimum risk-box area ratio')):
            self.field(tracking, key, title)
        boost = self.section(advanced_body, 'Long-range boost')
        self.check(boost, 'Enable long-range boost', a.far_target_boost_var).pack(anchor='w', pady=5)
        self.field(boost, 'far_target_confidence', 'Boost confidence')
        self.button(advanced_body, 'Restore detection defaults', self.restore_defaults, width=213).pack(anchor='w', pady=(2, 10))

    def build_hotkeys(self, page):
        a = self.app
        self.heading(page, 'Shortcuts & startup', 'Keep protection within reach.')
        body = self.scrollable(page, 'hotkeys')
        group = self.section(body, 'Global shortcuts')
        self.dynamic(group, a.hotkey_status_var, wraplength=640).pack(anchor='w', pady=(0, 12))
        for key, variable, target in (('Start / stop', a.start_stop_hotkey_var, 'start_stop'), ('Hold to mute', a.mute_hold_hotkey_var, 'mute_hold')):
            row = self.frame(group)
            row.pack(fill='x', pady=6)
            row.columnconfigure(1, weight=1)
            self.label(row, key, width=130).grid(row=0, column=0, sticky='w')
            entry = ctk.CTkEntry(row, textvariable=variable, state='readonly', width=200, height=34,
                                 corner_radius=7, border_color=LINE, text_color=INK, fg_color='#F7F9FC', font=self.font())
            entry.grid(row=0, column=1, sticky='ew', padx=(8, 12))
            self.button(row, 'Capture', lambda t=target: a.begin_hotkey_capture(t), width=90).grid(row=0, column=2)
            if target == 'start_stop':
                a.start_stop_hotkey_entry = entry
            else:
                a.mute_hold_hotkey_entry = entry
        self.label(group, 'Press Capture, then your key combination. Hold the mute shortcut to suppress alerts until release.', size=11, color=MUTED, wraplength=640).pack(anchor='w', pady=(13, 6))
        self.dynamic(group, a.hotkey_hint_var, wraplength=640).pack(anchor='w', pady=(0, 10))
        actions = self.frame(group)
        actions.pack(fill='x')
        self.button(actions, 'Retry listener', a.retry_hotkey_listener, width=126).pack(side='left', padx=(0, 10))
        self.button(actions, 'Accessibility settings', a.open_accessibility_settings, width=180).pack(side='left')
        startup = self.section(body, 'Startup')
        self.check(startup, 'Launch at login', a.launch_at_login_var, a.on_launch_at_login_toggled).pack(anchor='w', pady=(0, 8))
        self.label(startup, 'Changes to startup take effect immediately.', size=11, color=MUTED).pack(anchor='w')

    def select_page(self, name):
        for key, button in self.app.panel_buttons.items():
            active = key == name
            button.configure(fg_color='#DDEBFF' if active else RAIL, text_color=BLUE if active else INK,
                             image=self.image(f'{self.nav_icons[key]}-{"blue" if active else "gray"}.png'))
        if name == 'overview':
            self.footer.grid_remove()
        else:
            self.footer.grid()

    def preview_action(self):
        if self.app.runtime.running:
            if not self.app.preview_var.get():
                self.toggle_preview()
        else:
            self.app.toggle_monitoring_from_hotkey()

    def toggle_preview(self):
        self.app.preview_var.set(not self.app.preview_var.get())
        self.app.on_preview_toggled()
        self.refresh()

    def update_preview(self, frame):
        a = self.app
        if frame is None:
            a.preview_label.configure(image=None)
            # CTkLabel 5.2 leaves its underlying Tk image drawn when image=None.
            # Unmap the image surface so hidden/stopped previews cannot show it.
            a.preview_label.grid_remove()
            self.live_image = None
            self.empty_preview.place(relx=.5, rely=.47, anchor='center')
            return
        import cv2
        size = (max(1, self.preview_card.winfo_width() - 20), max(1, self.preview_card.winfo_height() - 20))
        # Preserve the complete camera frame, including people entering at an edge.
        source = ImageOps.pad(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), size,
                              method=Image.Resampling.LANCZOS, color=PREVIEW)
        self.live_image = ctk.CTkImage(source, source, size=size)
        a.preview_label.configure(image=self.live_image)
        a.preview_label.grid()
        self.empty_preview.place_forget()

    def set_language(self, code):
        self.language_var.set('English' if code == 'en' else '中文')
        self.change_language()

    def change_language(self, _event=None):
        self.language.code = 'en' if self.language_var.get() == 'English' else 'zh'
        settings = self.app.runtime.get_settings()
        settings.language = self.language.code
        self.app.runtime.update_settings(settings)
        self.app.persist_settings(settings)
        for widget, key in self.bindings:
            if widget.winfo_exists():
                widget.configure(text=self.t(key))
        for render in self.dynamic_bindings:
            render()
        self.render_menu()
        self.last_signature = None
        self.refresh()
        self.app.update_status_bar_controls()

    def refresh(self):
        if self.synchronizing:
            return
        self.synchronizing = True
        try:
            a, lang = self.app, self.language.code
            configured = a.runtime.get_settings()
            names = a.get_blacklist_items()
            try:
                dirty = a.serialized_settings(a.parse_settings()) != a.serialized_settings(configured)
            except (ValueError, KeyError):
                dirty = True
            state = a.status_pill_var.get()
            active = getattr(a.runtime, 'active_backend', None) if a.runtime.running else None
            signature = (lang, state, active, a.runtime.running, a.preview_var.get(), a.model_var.get(), a.backend_var.get(),
                         configured.model_name, configured.inference_backend, configured.max_allowed_people,
                         configured.trigger_frame_threshold, tuple(configured.blacklist_apps), tuple(names),
                         a.start_stop_hotkey_var.get(), a.monitor_mode_var.get(), dirty)
            if signature == self.last_signature:
                return
            self.last_signature = signature
            self.model_picker.configure(values=[self.t(x) for x in MODEL_LABELS])
            self.backend_picker.configure(values=[self.t(x) for x in ENGINE_LABELS])
            self.model_choice.set(self.t(MODEL_LABELS[MODEL_CODES.index(a.model_var.get())]) if a.model_var.get() in MODEL_CODES else a.model_var.get())
            self.backend_choice.set(self.t(ENGINE_LABELS[ENGINE_CODES.index(a.backend_var.get())]))
            for code, button in self.language_buttons.items():
                button.configure(fg_color=WHITE if code == lang else '#F1F3F7', text_color=BLUE if code == lang else MUTED)
            self.model_value.set(Path(configured.model_name).stem.replace('yolo', 'YOLO'))
            self.engine_title.set(self.t('Inference engine' if active else 'Configured engine'))
            self.engine_value.set(self.language.system(active) if active else {'coreml': 'Apple Core ML', 'auto': self.t('Automatic'), 'pytorch': 'PyTorch'}[configured.inference_backend])
            self.rule_value.set(f'人数 > {configured.max_allowed_people} · {configured.trigger_frame_threshold} 帧' if lang == 'zh' else f'> {configured.max_allowed_people} people · {configured.trigger_frame_threshold} frame' + ('s' if configured.trigger_frame_threshold != 1 else ''))
            self.state_title.set('●  ' + self.t(state))
            note = {'Running': 'Protection is active', 'Starting': 'Preparing camera', 'Muted': 'Alerts paused', 'Error': 'Check status below', 'Alert': 'Hiding apps'}.get(state, 'Protection has not started')
            self.state_note.set(self.t(note))
            a.status_pill_label.configure(text_color={'Running': '#21835A', 'Starting': BLUE, 'Muted': '#886016', 'Error': '#BC3D42', 'Alert': '#BC3D42'}.get(state, MUTED))
            running = a.runtime.running
            title = 'Camera is off' if not running else ('Preview is hidden' if not a.preview_var.get() else 'Preparing the camera…')
            help_text = 'Analyze the camera view locally after starting.' if not running else ('Detection continues while the preview is hidden.' if not a.preview_var.get() else 'Waiting for the first frame.')
            self.preview_title.set(self.t(title))
            self.preview_help.set(self.t(help_text))
            self.primary_button.configure(text=self.t('Show preview' if running else 'Start protection'), state='disabled' if running and a.preview_var.get() else 'normal')
            self.preview_toolbar.place(relx=1, rely=1, anchor='se', x=-10, y=-10) if running else self.preview_toolbar.place_forget()
            self.stop_button.pack(side='right', padx=(7, 0)) if running else self.stop_button.pack_forget()
            self.preview_toggle.pack(side='right') if running and a.preview_var.get() else self.preview_toggle.pack_forget()
            self.apps_count.set(f'{self.t("Protected apps")}  ({len(configured.blacklist_apps)})')
            app_signature = (lang, tuple(configured.blacklist_apps))
            if app_signature != self.app_signature:
                self.application_rows(self.overview_app_rows, configured.blacklist_apps[:6])
                if len(configured.blacklist_apps) > 6:
                    self.button(self.overview_app_rows, 'Manage all applications', lambda: a.switch_settings_panel('startup'), width=235).pack(fill='x', pady=5)
                self.app_signature = app_signature
            editor_signature = (lang, tuple(names))
            if editor_signature != self.editor_signature:
                self.application_rows(self.editor_rows, names, editable=True)
                self.editor_signature = editor_signature
            self.manual_name.configure(placeholder_text=self.t('Exact process name'))
            self.shortcut_value.set(a.start_stop_hotkey_var.get().replace('Cmd', '⌘').replace('Ctrl', '⌃').replace('Option', '⌥').replace('Alt', '⌥').replace('+', '  '))
            a.parameters_toggle_button.configure(text=self.t('Back to Basics' if a.monitor_mode_var.get() == 'advanced' else 'Advanced'))
            self.save_state.set(self.t('Unsaved changes' if dirty else 'Saved'))
        finally:
            self.synchronizing = False

    def add_application(self):
        filename = filedialog.askopenfilename(title=self.t("Choose an application"), initialdir="/Applications", filetypes=((self.t("Applications"), "*.app"),))
        if not filename:
            return
        name = Path(filename).stem
        # Prefer the declared executable (e.g. Steam -> steam_osx) over display name.
        try:
            import plistlib
            info = plistlib.loads((Path(filename) / "Contents/Info.plist").read_bytes())
            name = info.get("CFBundleExecutable") or name
        except (OSError, ValueError):
            pass
        if name not in self.app.get_blacklist_items():
            current = self.app.blacklist_text.get("1.0", "end").rstrip()
            self.app.blacklist_text.delete("1.0", "end")
            self.app.blacklist_text.insert("1.0", current + ("\n" if current else "") + name)
            self.refresh()


    def restore_defaults(self):
        if messagebox.askyesno(self.t("Restore detection settings?"), self.t("This resets detection parameters. Your application list, shortcuts, language and startup choice are kept."), parent=self.app.root):
            self.app.reset_defaults()


    def render_menu(self):
        a = self.app
        old = getattr(self, "menu", None)
        self.menu = tk.Menu(a.root, tearoff=0)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label=self.t("Show Main Window"), command=a.show_main_window)
        file_menu.add_command(label=self.t("Save changes"), accelerator="Command+S", command=a.apply_settings)
        file_menu.add_separator()
        file_menu.add_command(label=self.t("Quit"), command=a.quit_application)
        self.menu.add_cascade(label=self.t("File"), menu=file_menu)
        edit_menu = tk.Menu(self.menu, tearoff=0)
        for title, action in (("Cut", "Cut"), ("Copy", "Copy"), ("Paste", "Paste"), ("Select all", "SelectAll")):
            edit_menu.add_command(label=self.t(title), command=lambda event=action: a.root.focus_get().event_generate(f"<<{event}>>") if a.root.focus_get() else None)
        self.menu.add_cascade(label=self.t("Edit"), menu=edit_menu)
        window_menu = tk.Menu(self.menu, tearoff=0)
        for number, (key, title) in enumerate((("overview", "Overview"), ("startup", "Protected apps"), ("parameters", "Detection"), ("hotkeys", "Shortcuts & startup")), 1):
            window_menu.add_command(label=self.t(title), accelerator=f"Command+{number}", command=lambda k=key: a.switch_settings_panel(k))
        window_menu.add_separator()
        window_menu.add_command(label=self.t("Switch language"), accelerator="Command+Shift+L", command=self.toggle_language)
        self.menu.add_cascade(label=self.t("Window"), menu=window_menu)
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label=self.t("About Chill Guard"), command=lambda: messagebox.showinfo(self.t("About Chill Guard"), f"Chill Guard {self.version}\n\n" + self.t("Local processing · No image upload"), parent=a.root))
        self.menu.add_cascade(label=self.t("Help"), menu=help_menu)
        a.root.configure(menu=self.menu)
        if old is not None:
            old.destroy()


    def toggle_language(self):
        self.language_var.set("English" if self.language.code == "zh" else "中文")
        self.change_language()



def build_form(app, version):
    app.ui = Workspace(app, version)
