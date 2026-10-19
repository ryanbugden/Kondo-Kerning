# menuTitle: Kondo Kerning


from importlib import reload
import ezui
import tools

reload(tools)


class KondoKerning(ezui.WindowController):
    def build(self):
        content = """
        * TwoColumnForm         @form

        > : Span:
        > (X) Current Font      @spanRadios
        > ( ) All Fonts

        > ---

        > : Clear:
        > [X] Empty Groups             @clearEmptyGroupsCheckbox
        > [X] One-Member Groups        @clearSingleMemberGroupsCheckbox
        > [ ] All Groups               @clearAllGroupsCheckbox
        > ---
        > [X] Missing Group Members    @clearMissingMembersCheckbox
        > ---
        > [ ] Zero-Value Pairs         @clearZeroValueKernsCheckbox
        > [ ] All Pairs                @clearAllKerningCheckbox
        > ---
        > [X] Missing Pairs            @clearMissingKerningCheckbox
        > [X] Try To Salvage           @tryToSalvageCheckbox

        > ---

        > : Clean Up:
        > [X] Normalize Group Order    @normalizeGroupOrder
        > * HorizontalStack
        >> [ ] Round Values By         @roundKerningCheckbox
        >> [_5_]                       @roundValueTextField

        ---

        (Apply)                 @applyButton
        """

        descriptionData = dict(
            form=dict(titleColumnWidth=70, itemColumnWidth=180),
            roundValueTextField=dict(
                width=50,
                valueType="integer",
            ),
            applyButton=dict(width="fill"),
        )
        self.w = ezui.EZPanel(
            title="Kondo Kerning",
            content=content,
            descriptionData=descriptionData,
            controller=self,
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.setDefaultButton(self.w.getItem("applyButton"))
        # All group checkboxes except for All
        self.group_checkboxes = [
            self.w.getItem(item)
            for item in self.w.getItems().keys()
            if "group" in item.lower()
            and "checkbox" in item.lower()
            and "all" not in item.lower()
        ]
        # All kern checkboxes except for All
        self.kern_checkboxes = [
            self.w.getItem(item)
            for item in self.w.getItems().keys()
            if "kern" in item.lower()
            and "checkbox" in item.lower()
            and "all" not in item.lower()
        ]
        self.roundKerningCheckboxCallback(self.w.getItem("roundKerningCheckbox"))

    def started(self):
        self.w.open()

    # # Automatically uncheck other boxes
    # def clearAllGroupsCheckboxCallback(self, sender):
    #     if sender.get():
    #         for checkbox in self.group_checkboxes:
    #             checkbox.set(False)
    # def clearAllKerningCheckboxCallback(self, sender):
    #     if sender.get():
    #         for checkbox in self.kern_checkboxes:
    #             checkbox.set(False)

    def roundKerningCheckboxCallback(self, sender):
        self.w.getItem("roundValueTextField").enable(sender.get())

    def applyButtonCallback(self, sender):
        fonts = [[CurrentFont()], AllFonts()][self.w.getItem("spanRadios").get()]
        clear_empty_groups = self.w.getItem("clearEmptyGroupsCheckbox").get()
        clear_all_groups = self.w.getItem("clearAllGroupsCheckbox").get()
        clear_zero_kerning = self.w.getItem("clearZeroValueKernsCheckbox").get()
        clear_missing_members = self.w.getItem("clearMissingMembersCheckbox").get()
        clear_single_member_groups = self.w.getItem(
            "clearSingleMemberGroupsCheckbox"
        ).get()
        clear_missing_kerning = self.w.getItem("clearMissingKerningCheckbox").get()
        clear_all_kerning = self.w.getItem("clearAllKerningCheckbox").get()
        salvage = self.w.getItem("tryToSalvageCheckbox").get()
        normalize_group_order = self.w.getItem("normalizeGroupOrder").get()
        round_value = [None, int(self.w.getItem("roundValueTextField").get())][
            self.w.getItem("roundKerningCheckbox").get()
        ]

        for font in fonts:
            tools.kondo_kerning(
                font,
                clear_empty_groups=clear_empty_groups,
                clear_all_groups=clear_all_groups,
                clear_zero_kerning=clear_zero_kerning,
                clear_missing_members=clear_missing_members,
                clear_single_member_groups=clear_single_member_groups,
                clear_missing_kerning=clear_missing_kerning,
                clear_all_kerning=clear_all_kerning,
                salvage=salvage,
                normalize_group_order=normalize_group_order,
                round_value=round_value,
                report=True,
            )


KondoKerning()
