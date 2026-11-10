# menuTitle: Kondo Kerning


from importlib import reload
import ezui
from mojo.extensions import setExtensionDefault, getExtensionDefault
import tools

reload(tools)


EXT_KEY = "com.ryanbugden.kondoKerning"


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
        > [ ] Clear Redundant Exceptions     @clearRedundantExceptionsCheckbox
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

        # Restore UI values
        try:
            self.w.setItemValues(
                getExtensionDefault(EXT_KEY, fallback=self.w.getItemValues())
            )
        except KeyError:
            pass

        self.roundKerningCheckboxCallback(self.w.getItem("roundKerningCheckbox"))

    def started(self):
        self.w.open()

    def destroy(self):
        setExtensionDefault(EXT_KEY, self.w.getItemValues())

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
        clear_redundant_exceptions = self.w.getItem(
            "clearRedundantExceptionsCheckbox"
        ).get()
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
                clear_redundant_exceptions=clear_redundant_exceptions,
                clear_all_kerning=clear_all_kerning,
                round_value=round_value,
                salvage=salvage,
                report=True,
            )


KondoKerning()
