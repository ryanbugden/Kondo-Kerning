# menuTitle: Kondo Kerning


import ezui
from pprint import pprint


def my_round(x, base=5):
    return base * round(x/base)
    
    
def salvage_pair(font, pair):
    l, r = pair
    if l not in font.keys() and l not in font.groups.keys():
        l = ".".join(l.split(".")[2:])
        if l not in font.keys():
            return None
    if r not in font.keys() and r not in font.groups.keys():
        r = ".".join(r.split(".")[2:])
        if r not in font.keys():
            return None
    return (l, r)
    
    
def flatten_kerning(font, group_name):
    '''
    Takes a group that's about to be deleted,
    looks at all its kerning in the font,
    returns its flattened kerning.
    '''
    members = font.groups[group_name]
    new_kerning = {}
    for pair, value in font.kerning.items():
        if pair[0] == group_name and pair[1] in group_name:
            for member in members:
                for other_member in members:
                    new_kerning[(member, other_member)] = value
        elif pair[0] == group_name:
            for member in members:
                new_kerning[(member, pair[1])] = value
        elif pair[1] == group_name:
            for member in members:
                new_kerning[(pair[0], member)] = value
    return new_kerning
        

class KondoKerning(ezui.WindowController):

    def build(self):
        content = """
        * TwoColumnForm         @form

        > : Span:
        > (X) Current Font      @spanRadios
        > ( ) All Fonts
        
        > : Clear:
        > [X] Empty Groups             @clearEmptyGroupsCheckbox 
        > [X] One-Member Groups        @clearSingleMemberGroupsCheckbox
        > [ ] All Groups               @clearAllGroupsCheckbox
        > ---
        > [X] Missing Group Members    @clearMissingMembersCheckbox
        > ---
        > [X] Zero-Value Pairs         @clearZeroValueKernsCheckbox
        > [ ] All Pairs                @clearAllKerningCheckbox
        > ---
        > [X] Missing Pairs            @clearMissingKerningCheckbox
        > [X] Try To Salvage           @tryToSalvageCheckbox
        > ---
        
        > : Round:
        > * HorizontalStack
        >> [ ] by               @roundKerningCheckbox
        >> [_5_]                @roundValueTextField
        
        ---
        
        (Apply)                 @applyButton
        """

        descriptionData = dict(
            form=dict(
                titleColumnWidth=60,
                itemColumnWidth=180
            ),
            roundValueTextField=dict(
                width=50,
                valueType="integer",
            ),
            applyButton=dict(
                width='fill'
            ),
        )
        self.w = ezui.EZPanel(
            title="Kondo Kerning",
            content=content,
            descriptionData=descriptionData,
            controller=self
        )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.setDefaultButton(self.w.getItem("applyButton"))
        # All group checkboxes except for All
        self.group_checkboxes = [self.w.getItem(item) for item in self.w.getItems().keys() if "group" in item.lower() and "checkbox" in item.lower() and "all" not in item.lower()]
        # All kern checkboxes except for All
        self.kern_checkboxes = [self.w.getItem(item) for item in self.w.getItems().keys() if "kern" in item.lower() and "checkbox" in item.lower() and "all" not in item.lower()]
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
        clear_single_member_groups = self.w.getItem("clearSingleMemberGroupsCheckbox").get()
        clear_missing_kerning = self.w.getItem("clearMissingKerningCheckbox").get()
        clear_all_kerning = self.w.getItem("clearAllKerningCheckbox").get()
        salvage = self.w.getItem("tryToSalvageCheckbox").get()
        round_setting   = [None, int(self.w.getItem("roundValueTextField").get())][self.w.getItem("roundKerningCheckbox").get()]

        
        print("\n*********************\nKondo Kerning Report:\n*********************")
        for f in fonts:    
            print(f.info.familyName, f.info.styleName)
            
            # Kerning Management
            if clear_all_kerning:
                f.kerning.clear()
                print("\t🔥 Kerning")
                
            else:
                # Rounding Kerning
                if round_setting is not None:
                    for pair, value in f.kerning.items():
                        f.kerning[pair] = my_round(value, round_setting)
                    print(f"\t🔵 Kerning: Rounded by {round_setting}.")
                    
                # Clear zero values
                if clear_zero_kerning:
                    print(f"\t👀 Kerning: Looking for zero-value pairs")
                    for pair, value in f.kerning.items():
                        if value == 0:
                            print(f"\t🫧 Kerning: Removing {pair}   Value: {value}.")
                            f.kerning.pop(pair)
                        
                # Delete empty pairs
                if clear_missing_kerning:
                    print(f"\t👀 Kerning: Looking for pairs involving glyphs not present in font")
                    for pair, value in f.kerning.items():
                        invalid_names = set()
                        pair_has_valid_glyphs = False
                        # Check if both glyph/group names are valid
                        for side in pair:
                            if "public" in side:
                                if side not in f.groups.keys():
                                    invalid_names.add(side)
                                    break
                            else:
                                if side not in f.keys():
                                    invalid_names.add(side)
                                    break
                        if not invalid_names:
                            for side in pair:
                                # Check groups
                                if side in f.groups.keys():
                                    for member in f.groups[side]:
                                        if member in f.keys():
                                            pair_has_valid_glyphs = True
                                            break
                                # Check unique pair members
                                else:
                                    if side in f.keys():
                                        pair_has_valid_glyphs = True
                                        break
                                if pair_has_valid_glyphs == True: break
                        if pair_has_valid_glyphs == False:
                            reassigned_pair = salvage_pair(f, pair)
                            if salvage and reassigned_pair:
                                print(f"\t🔀 Kerning: Reassigning pair: {pair} ---> {reassigned_pair}   One or more groups was not present.")
                                f.kerning[reassigned_pair] = f.kerning[pair]
                                f.kerning.pop(pair)
                            else: 
                                print(f"\t🫧 Kerning: Deleting pair: {pair}   One or more glyphs (or groups) not present. Invalid names: {invalid_names}. Couldn’t reassign.")
                                f.kerning.pop(pair)
                else:
                    print("\t🆗 Skipping Kerning.")
                

            # Groups management
            if clear_all_groups:
                f.groups.clear()
                print("\t🔥 Groups")
            else:
                if clear_empty_groups:
                    # Delete empty groups
                    print(f"\t👀 Groups: Looking for empty groups")
                    for group, members in f.groups.items():
                        group_has_valid_members = False
                        for member in members:
                            if member in f.keys():
                                group_has_valid_members = True
                                break
                        if group_has_valid_members == False:
                            print(f"\t🫧 Groups: Deleting group {group}.  It was empty.")
                            f.groups.pop(group)
                if clear_missing_members:
                    # Delete members from groups if the member is not in the font
                    print(f"\t👀 Groups: Looking for group members that are missing in the font.")
                    for group, members in f.groups.items():
                        new_members = []
                        for member in members:
                            if member in f.keys():
                                new_members.append(member)
                            else:
                                print(f"\t🫧 Groups: Removing group member {member} from group {group}.")
                        f.groups[group] = new_members
                if clear_single_member_groups:
                    # Delete groups that only have one member
                    print(f"\t👀 Groups: Looking for single-member groups.")
                    for group, members in f.groups.items():
                        if len(members) == 1:
                            flattened_kerning = flatten_kerning(f, group)
                            print(f"\t🫧 Groups: Deleting group {group}.  It had one member. Flattening its kerning:")
                            pprint(flattened_kerning)
                            f.groups.pop(group)
                            f.kerning.update(flattened_kerning)
                else:
                    print("\t🆗 Skipping Groups.")
                

                
            print("Kondo Kerning done.\n*********************")
            
            f.changed()


KondoKerning()
