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

        > : Groups:
        > [X] Clear Empty Groups             @clearEmptyGroupsCheckbox
        > [X] Clear One-Member Groups        @clearSingleMemberGroupsCheckbox
        > [X] Clear Missing Group Members    @clearMissingMembersCheckbox
        > [ ] Clear All Groups               @clearAllGroupsCheckbox
        > [X] Normalize Group Order          @normalizeGroupOrder

        > ---

        > : Kerning:

        > [ ] Clear Zero-Value Pairs         @clearZeroValueKernsCheckbox
        > [X] Clear Missing Pairs            @clearMissingKerningCheckbox
        > [ ] Clear All Pairs                @clearAllKerningCheckbox
        > * HorizontalStack
        >> [ ] Round Values By               @roundKerningCheckbox
        >> [_5_]                             @roundValueTextField

        > ---

        > [ ] Try To Salvage           @tryToSalvageCheckbox

        ---

        (Apply)                 @applyButton
        """

        descriptionData = dict(
            form=dict(titleColumnWidth=70, itemColumnWidth=210),
            roundValueTextField=dict(
                width="fill",
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
        # Require a font first
        all_fonts = AllFonts()
        if not all_fonts:
            print("[Kondo Kerning] Open a font first.")
            return

        if self.w.getItem("spanRadios").get() == 0:
            fonts = [all_fonts[0]]
        else:
            fonts = all_fonts
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
        round_value = None
        if self.w.getItem("roundKerningCheckbox").get():
            round_value = int(self.w.getItem("roundValueTextField").get())

        for font in fonts:
            tools.kondo_kerning(
                font,
                clear_empty_groups=clear_empty_groups,
                clear_single_member_groups=clear_single_member_groups,
                clear_missing_members=clear_missing_members,
                clear_all_groups=clear_all_groups,
                normalize_group_order=normalize_group_order,
                clear_zero_kerning=clear_zero_kerning,
                clear_missing_kerning=clear_missing_kerning,
                clear_all_kerning=clear_all_kerning,
                round_value=round_value,
                salvage=salvage,
                report=True,
            )


KondoKerning()
