import customtkinter as ctk
from gcal import getService, getEvents, pushEvents
from datetime import timedelta

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# color constants
BG_SIDEBAR     = "#1a1a2e"
BG_MAIN        = "#16213e"
BG_CARD        = "#1f2b47"
BG_TOPBAR      = "#1a1a2e"
ACCENT         = "#4f8ef7"
ACCENT_DIM     = "#2a4a8a"
TEXT_PRIMARY   = "#e8eaf6"
TEXT_SECONDARY = "#8892a4"
TEXT_MUTED     = "#4a5568"
HARD_BG        = "#3d1515"
HARD_TEXT      = "#f87171"
SOFT_BG        = "#1a2744"
SOFT_TEXT      = "#93c5fd"
DIVIDER        = "#2a3550"
DANGER         = "#f87171"

FONT_TITLE   = ("Helvetica Neue", 22, "bold")
FONT_HEADING = ("Helvetica Neue", 14, "bold")
FONT_BODY    = ("Helvetica Neue", 13)
FONT_SMALL   = ("Helvetica Neue", 11)
FONT_MONO    = ("Courier New", 12)


class App(ctk.CTk):
    def __init__(self, fg_color=None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.calService = getService()
        self.calEvents  = getEvents(self.calService)

        self.tasks       = []
        self.timeline    = []
        self.unscheduled = []
        self.activeView  = "schedule"

        self.urgencyWeight    = ctk.DoubleVar(value=0.5)
        self.importanceWeight = ctk.DoubleVar(value=0.5)
        self.dayStart         = ctk.StringVar(value="08:00")
        self.dayEnd           = ctk.StringVar(value="22:00")
        self.slotSize         = ctk.IntVar(value=30)
        self.numDays          = ctk.IntVar(value=7)

        self.title("Timestop")
        self.geometry("1360x768")
        self.minsize(900, 600)
        self.configure(fg_color=BG_MAIN)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._buildSidebar()
        self._buildMainArea()
        self.switchView("schedule")

    # ─── SIDEBAR ────────────────────────────────────────────────
    def _buildSidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=BG_SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # logo
        logoFrame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logoFrame.pack(fill="x", padx=20, pady=(28, 24))
        ctk.CTkLabel(logoFrame, text="⏱", font=("Helvetica Neue", 28)).pack(side="left")
        ctk.CTkLabel(logoFrame, text="  Timestop", font=FONT_TITLE,
                     text_color=TEXT_PRIMARY).pack(side="left")

        # divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=DIVIDER).pack(fill="x", padx=16, pady=(0, 16))

        # nav label
        ctk.CTkLabel(self.sidebar, text="NAVIGATION", font=("Helvetica Neue", 10),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(0, 8))

        # nav buttons
        self.navBtns = {}
        for key, label in [("schedule", "  Schedule"), ("tasks", "  Tasks"), ("settings", "  Settings")]:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                font=FONT_BODY, height=40,
                fg_color="transparent", hover_color=ACCENT_DIM,
                text_color=TEXT_SECONDARY, corner_radius=8,
                command=lambda k=key: self.switchView(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.navBtns[key] = btn

        # bottom label
        ctk.CTkFrame(self.sidebar, height=1, fg_color=DIVIDER).pack(fill="x", padx=16, pady=16, side="bottom")
        ctk.CTkLabel(self.sidebar, text="BeachHacks 9.0", font=FONT_SMALL,
                     text_color=TEXT_MUTED).pack(side="bottom", pady=(0, 12))

    def _setActiveNav(self, key):
        for k, btn in self.navBtns.items():
            if k == key:
                btn.configure(fg_color=ACCENT_DIM, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

    # ─── MAIN AREA ───────────────────────────────────────────────
    def _buildMainArea(self):
        self.mainArea = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.mainArea.grid(row=0, column=1, sticky="nsew")
        self.mainArea.grid_rowconfigure(2, weight=1)
        self.mainArea.grid_columnconfigure(0, weight=1)

        # topbar
        self.topbar = ctk.CTkFrame(self.mainArea, height=64, fg_color=BG_TOPBAR, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_propagate(False)
        self.topbar.grid_columnconfigure(1, weight=1)

        self.titleLabel = ctk.CTkLabel(self.topbar, text="Schedule",
                                        font=FONT_TITLE, text_color=TEXT_PRIMARY)
        self.titleLabel.grid(row=0, column=0, padx=24, pady=16, sticky="w")

        btnFrame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        btnFrame.grid(row=0, column=2, padx=16, pady=12, sticky="e")

        self.pushBtn = ctk.CTkButton(
            btnFrame, text="Push to Calendar", width=160, height=36,
            font=FONT_SMALL, corner_radius=8,
            fg_color=ACCENT_DIM, hover_color=ACCENT,
            text_color=TEXT_PRIMARY, state="disabled",
            command=self.pushToCalendar
        )
        self.pushBtn.pack(side="right", padx=(8, 0))

        self.genButton = ctk.CTkButton(
            btnFrame, text="Generate Schedule", width=160, height=36,
            font=FONT_SMALL, corner_radius=8,
            fg_color=ACCENT, hover_color="#3a7de8",
            text_color="white", command=self.generateSchedule
        )
        self.genButton.pack(side="right", padx=(8, 0))

        self.addTaskBtn = ctk.CTkButton(
            btnFrame, text="+ Add Task", width=110, height=36,
            font=FONT_SMALL, corner_radius=8,
            fg_color="transparent", border_width=1,
            border_color=ACCENT, hover_color=ACCENT_DIM,
            text_color=ACCENT, command=self.openAddTask
        )
        self.addTaskBtn.pack(side="right", padx=(8, 0))

        # divider
        ctk.CTkFrame(self.mainArea, height=1, fg_color=DIVIDER).grid(row=1, column=0, sticky="ew")

        # scrollable content
        self.contentFrame = ctk.CTkScrollableFrame(
            self.mainArea, fg_color=BG_MAIN, corner_radius=0,
            scrollbar_button_color=DIVIDER
        )
        self.contentFrame.grid(row=2, column=0, sticky="nsew")

    # ─── VIEW SWITCHING ──────────────────────────────────────────
    def switchView(self, view):
        self.activeView = view
        self._setActiveNav(view)
        for widget in self.contentFrame.winfo_children():
            widget.destroy()

        titles = {"schedule": "Schedule", "tasks": "Tasks", "settings": "Settings"}
        self.titleLabel.configure(text=titles[view])

        if view == "schedule":
            self.displaySchedule()
        elif view == "tasks":
            self.displayTasks()
        elif view == "settings":
            self.displaySettings()

    # ─── SCHEDULE VIEW ───────────────────────────────────────────
    def displaySchedule(self):
        if not self.timeline and not self.calEvents:
            self._emptyState("No schedule yet",
                             "Add tasks and click 'Generate Schedule' to get started.")
            return

        if self.calEvents:
            self._sectionLabel("Blocked from Google Calendar")
            for event in self.calEvents:
                timeStr = event["start"].strftime("%I:%M %p") + "  →  " + event["end"].strftime("%I:%M %p")
                row = ctk.CTkFrame(self.contentFrame, fg_color="#0d1f3c", corner_radius=10)
                row.pack(fill="x", padx=20, pady=3)
                ctk.CTkLabel(row, text=timeStr, font=FONT_MONO,
                             text_color=SOFT_TEXT, width=200).pack(side="left", padx=16, pady=10)
                ctk.CTkFrame(row, width=1, fg_color=DIVIDER).pack(side="left", fill="y", pady=8)
                ctk.CTkLabel(row, text=event["title"], font=FONT_BODY,
                             text_color=TEXT_SECONDARY).pack(side="left", padx=16)

        if self.timeline:
            self._sectionLabel("Scheduled Tasks")

            # group slots by day
            from datetime import date as dateType

            occupied = [s for s in self.timeline if s[2] is not None and self.isFirstSlot(s)]

            days = {}
            for slot in occupied:
                d = slot[0].date()
                if d not in days:
                    days[d] = []
                days[d].append(slot)

            today = dateType.today()

            for day, slots in days.items():
                # day header
                if day == today:
                    dayLabel = "Today"
                elif day == today + timedelta(days=1):
                    dayLabel = "Tomorrow"
                else:
                    dayLabel = day.strftime("%A, %b %d")

                # day header row
                headerRow = ctk.CTkFrame(self.contentFrame, fg_color=ACCENT_DIM, corner_radius=8)
                headerRow.pack(fill="x", padx=20, pady=(12, 4))
                ctk.CTkLabel(headerRow, text=dayLabel, font=FONT_HEADING,
                            text_color=TEXT_PRIMARY).pack(side="left", padx=14, pady=6)
                ctk.CTkLabel(headerRow, text=day.strftime("%B %d, %Y"), font=FONT_SMALL,
                            text_color=TEXT_SECONDARY).pack(side="right", padx=14)

                # slots for this day
                for slot in slots:
                    # only count slots on this specific day
                    taskSlotsToday = [
                        s for s in self.timeline
                        if s[2] == slot[2] and s[0].date() == day
                    ]

                    if taskSlotsToday:
                        lastSlotToday = taskSlotsToday[-1]
                        endTime = lastSlotToday[0] + timedelta(minutes=self.slotSize.get())
                    else:
                        endTime = slot[0] + timedelta(minutes=self.slotSize.get())

                    # check if task continues tomorrow
                    allTaskSlots = [s for s in self.timeline if s[2] == slot[2]]
                    continuesNextDay = any(s[0].date() > day for s in allTaskSlots)

                    timeStr = slot[0].strftime("%I:%M %p") + "  →  " + endTime.strftime("%I:%M %p")
                    if continuesNextDay:
                        timeStr += "  (continues)"

                    self._scheduleRow(timeStr, slot[2])
        if self.unscheduled:
            self._sectionLabel("Could Not Schedule")
            for task in self.unscheduled:
                row = ctk.CTkFrame(self.contentFrame, fg_color=HARD_BG, corner_radius=10)
                row.pack(fill="x", padx=20, pady=3)
                ctk.CTkLabel(row, text=task.n, font=FONT_BODY,
                             text_color=HARD_TEXT).pack(side="left", padx=16, pady=10)
                ctk.CTkLabel(row, text="No available slot found", font=FONT_SMALL,
                             text_color=TEXT_MUTED).pack(side="right", padx=16)

    def _scheduleRow(self, timeStr, task):
        row = ctk.CTkFrame(self.contentFrame, fg_color=BG_CARD, corner_radius=10)
        row.pack(fill="x", padx=20, pady=3)
        ctk.CTkLabel(row, text=timeStr, font=FONT_MONO,
                     text_color=TEXT_SECONDARY, width=200).pack(side="left", padx=16, pady=12)
        ctk.CTkFrame(row, width=1, fg_color=DIVIDER).pack(side="left", fill="y", pady=8)
        ctk.CTkLabel(row, text=task.n, font=FONT_BODY,
                     text_color=TEXT_PRIMARY).pack(side="left", padx=16)
        badgeBg   = HARD_BG   if task.type == "hard" else SOFT_BG
        badgeText = HARD_TEXT if task.type == "hard" else SOFT_TEXT
        ctk.CTkLabel(row, text=task.type, fg_color=badgeBg, text_color=badgeText,
                     corner_radius=6, font=FONT_SMALL, width=50).pack(side="right", padx=16)

    # ─── TASKS VIEW ──────────────────────────────────────────────
    def displayTasks(self):
        if not self.tasks:
            self._emptyState("No tasks yet",
                             "Click '+ Add Task' in the top bar to add your first task.")
            return
        for task in self.tasks:
            self.addTaskCard(task.n, task.duration, task.importance, task.type, task.deadline)

    def addTaskCard(self, name, duration, importance, deadType, deadline):
        wrapper = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        wrapper.pack(fill="x", padx=20, pady=4)

        card = ctk.CTkFrame(wrapper, fg_color=BG_CARD, corner_radius=12)
        card.pack(fill="x")

        accentColor = HARD_TEXT if deadType == "hard" else ACCENT
        ctk.CTkFrame(card, width=4, fg_color=accentColor,
                     corner_radius=2).pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        topRow = ctk.CTkFrame(inner, fg_color="transparent")
        topRow.pack(fill="x")

        nameLabel = ctk.CTkLabel(topRow, text=name, font=FONT_HEADING, text_color=TEXT_PRIMARY)
        nameLabel.pack(side="left")

        badgeBg   = HARD_BG   if deadType == "hard" else SOFT_BG
        badgeText = HARD_TEXT if deadType == "hard" else SOFT_TEXT
        badge = ctk.CTkLabel(topRow, text=deadType.upper(), fg_color=badgeBg,
                              text_color=badgeText, corner_radius=6,
                              font=("Helvetica Neue", 10, "bold"), width=55)
        badge.pack(side="right", padx=4)

        metaLabel = ctk.CTkLabel(inner, text=f"{duration} min  ·  importance {importance}/10",
                                  font=FONT_SMALL, text_color=TEXT_MUTED)
        metaLabel.pack(anchor="w", pady=(2, 0))

        # expandable details
        detailsFrame = ctk.CTkFrame(wrapper, fg_color="#1a2235", corner_radius=12)
        expanded = [False]

        deadlineStr = deadline.strftime("%b %d, %Y  %I:%M %p") if deadline else "No deadline"
        for label, value in [("Deadline", deadlineStr), ("Duration", f"{duration} minutes"),
                              ("Importance", f"{importance} / 10"), ("Type", deadType)]:
            row = ctk.CTkFrame(detailsFrame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL,
                         text_color=TEXT_MUTED, width=80).pack(side="left")
            ctk.CTkLabel(row, text=value, font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(side="left", padx=8)

        def toggleDetails(event=None):
            if expanded[0]:
                detailsFrame.pack_forget()
                expanded[0] = False
            else:
                detailsFrame.pack(fill="x", pady=(2, 0))
                expanded[0] = True

        for widget in [card, inner, topRow, nameLabel, metaLabel, badge]:
            widget.bind("<Button-1>", toggleDetails)

    # ─── SETTINGS VIEW ───────────────────────────────────────────
    def displaySettings(self):
        self._sectionLabel("Schedule Weights")
        self._settingSlider("Urgency weight",
                            "Prioritizes tasks with sooner deadlines",
                            self.urgencyWeight, 0, 1)
        self._settingSlider("Importance weight",
                            "Prioritizes tasks with higher user-set importance",
                            self.importanceWeight, 0, 1)
        self._sectionLabel("Time Preferences")
        self._settingEntry("Day start time (HH:MM)", self.dayStart)
        self._settingEntry("Day end time  (HH:MM)", self.dayEnd)
        self._sectionLabel("Scheduling Options")
        self._settingDropdown("Slot size (minutes)", self.slotSize, ["15", "30", "60"])
        self._settingSlider("Days to schedule ahead",
                            "How many days forward the scheduler plans",
                            self.numDays, 1, 14, steps=13, isInt=True)

    def _settingSlider(self, title, subtitle, variable, fromVal, toVal, steps=100, isInt=False):
        frame = ctk.CTkFrame(self.contentFrame, fg_color=BG_CARD, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=6)
        headerRow = ctk.CTkFrame(frame, fg_color="transparent")
        headerRow.pack(fill="x", padx=16, pady=(14, 0))
        ctk.CTkLabel(headerRow, text=title, font=FONT_BODY,
                     text_color=TEXT_PRIMARY).pack(side="left")
        valLabel = ctk.CTkLabel(headerRow, text="", font=FONT_BODY,
                                text_color=ACCENT, width=40)
        valLabel.pack(side="right")

        def updateLabel(val):
            valLabel.configure(text=str(int(float(val))) if isInt else f"{float(val):.2f}")

        updateLabel(variable.get())
        ctk.CTkLabel(frame, text=subtitle, font=FONT_SMALL,
                     text_color=TEXT_MUTED).pack(anchor="w", padx=16)
        ctk.CTkSlider(frame, from_=fromVal, to=toVal, number_of_steps=steps,
                      variable=variable, command=updateLabel,
                      button_color=ACCENT, progress_color=ACCENT_DIM
                      ).pack(fill="x", padx=16, pady=(6, 14))

    def _settingEntry(self, title, variable):
        frame = ctk.CTkFrame(self.contentFrame, fg_color=BG_CARD, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(frame, text=title, font=FONT_BODY,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkEntry(frame, textvariable=variable, font=FONT_BODY,
                     fg_color=BG_MAIN, border_color=DIVIDER,
                     text_color=TEXT_PRIMARY).pack(fill="x", padx=16, pady=(0, 14))

    def _settingDropdown(self, title, variable, options):
        frame = ctk.CTkFrame(self.contentFrame, fg_color=BG_CARD, corner_radius=12)
        frame.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(frame, text=title, font=FONT_BODY,
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkOptionMenu(frame, variable=variable, values=options,
                          fg_color=BG_MAIN, button_color=ACCENT_DIM,
                          text_color=TEXT_PRIMARY).pack(fill="x", padx=16, pady=(0, 14))

    # ─── ADD TASK POPUP ──────────────────────────────────────────
    def openAddTask(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Task")
        popup.geometry("420x520")
        popup.configure(fg_color=BG_SIDEBAR)
        popup.after(100, popup.lift)

        ctk.CTkLabel(popup, text="New Task", font=FONT_TITLE,
                     text_color=TEXT_PRIMARY).pack(pady=(24, 4), padx=24, anchor="w")
        ctk.CTkFrame(popup, height=1, fg_color=DIVIDER).pack(fill="x", padx=24, pady=(0, 16))

        def field(label, placeholder):
            ctk.CTkLabel(popup, text=label, font=FONT_SMALL,
                         text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(8, 2))
            e = ctk.CTkEntry(popup, placeholder_text=placeholder, font=FONT_BODY,
                             fg_color=BG_CARD, border_color=DIVIDER,
                             text_color=TEXT_PRIMARY, height=36)
            e.pack(fill="x", padx=24)
            return e

        nameEntry       = field("Task name", "e.g. Finish assignment")
        durationEntry   = field("Duration (minutes)", "e.g. 60")
        importanceEntry = field("Importance (1–10)", "e.g. 5")

        ctk.CTkLabel(popup, text="Deadline type", font=FONT_SMALL,
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=(8, 2))
        deadTypeMenu = ctk.CTkOptionMenu(popup, values=["soft", "hard", "none"],
                                          fg_color=BG_CARD, button_color=ACCENT_DIM,
                                          text_color=TEXT_PRIMARY)
        deadTypeMenu.pack(fill="x", padx=24)

        deadlineEntry = field("Deadline (days from now)", "e.g. 3  — leave blank for none")

        errorLabel = ctk.CTkLabel(popup, text="", font=FONT_SMALL, text_color=DANGER)
        errorLabel.pack(pady=(8, 0))

        def confirm():
            from datetime import datetime, timedelta
            from task import Task

            name     = nameEntry.get().strip()
            duration = durationEntry.get().strip()
            imp      = importanceEntry.get().strip()
            deadType = deadTypeMenu.get()
            daysAway = deadlineEntry.get().strip()

            if not name:
                errorLabel.configure(text="Task name cannot be empty.")
                return
            if not duration.isdigit() or int(duration) <= 0:
                errorLabel.configure(text="Duration must be a positive number.")
                return
            if not imp.isdigit() or not 1 <= int(imp) <= 10:
                errorLabel.configure(text="Importance must be between 1 and 10.")
                return
            if deadType != "none" and daysAway and not daysAway.isdigit():
                errorLabel.configure(text="Deadline must be a number of days.")
                return

            deadline = datetime.now() + timedelta(days=int(daysAway)) if daysAway else None
            newTask  = Task(name, int(duration), int(imp), deadType, deadline=deadline)
            self.tasks.append(newTask)
            self.addTaskCard(name, int(duration), int(imp), deadType, deadline)
            popup.destroy()

        ctk.CTkButton(popup, text="Add Task", command=confirm, height=40,
                      fg_color=ACCENT, hover_color="#3a7de8",
                      font=FONT_BODY, corner_radius=10).pack(fill="x", padx=24, pady=16)

    # ─── SCHEDULE GENERATION ─────────────────────────────────────
    def generateSchedule(self):
        from schedule import Schedule
        from datetime import time

        if not self.tasks:
            return

        startParts = self.dayStart.get().split(":")
        endParts   = self.dayEnd.get().split(":")

        s = Schedule(
            tasks=self.tasks,
            dayStart=time(int(startParts[0]), int(startParts[1])),
            dayEnd=time(int(endParts[0]),     int(endParts[1])),
            slotSize=self.slotSize.get(),
            urgencyWeight=self.urgencyWeight.get(),
            impWeight=self.importanceWeight.get()
        )

        self.timeline, self.unscheduled = s.genSchedule(self.calEvents)
        self.switchView("schedule")
        self.pushBtn.configure(state="normal")

    def pushToCalendar(self):
        if not self.timeline:
            return
        pushEvents(self.calService, self.timeline)

    # ─── HELPERS ─────────────────────────────────────────────────
    def isFirstSlot(self, slot):
        idx = self.timeline.index(slot)
        if idx == 0:
            return True
        return self.timeline[idx - 1][2] != slot[2]

    def _sectionLabel(self, text):
        ctk.CTkLabel(self.contentFrame, text=text.upper(),
                     font=("Helvetica Neue", 10), text_color=TEXT_MUTED
                     ).pack(anchor="w", padx=24, pady=(20, 6))

    def _emptyState(self, title, subtitle):
        frame = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        frame.pack(expand=True, pady=60)
        ctk.CTkLabel(frame, text=title, font=FONT_TITLE,
                     text_color=TEXT_SECONDARY).pack()
        ctk.CTkLabel(frame, text=subtitle, font=FONT_BODY,
                     text_color=TEXT_MUTED).pack(pady=8)

