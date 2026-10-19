from pprint import pprint
from mojo.roboFont import RFont


def _kondo_round(x, base=5):
    return base * round(x / base)


def _salvage_pair(font, pair):
    l, r = pair
    if l not in font.keys() and l not in font.groups.keys():
        l = ".".join(l.split(".")[2:])
        if l not in font.keys():
            return None
    if r not in font.keys() and r not in font.groups.keys():
        r = ".".join(r.split(".")[2:])
        if r not in font.keys():
            return None
    return (l, r) if (l, r) != pair else None


def _flatten_kerning(font, group_name):
    """
    Takes a group that's about to be deleted,
    looks at all its kerning in the font,
    returns its flattened kerning.
    """
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


def _process_kerning(
    font,
    clear_zero_kerning=False,
    clear_missing_kerning=True,
    clear_all_kerning=False,
    salvage=True,
    round_value=None,
    report=True,
):
    def log(*args):
        if report:
            print(*args)

    if clear_all_kerning:
        font.kerning.clear()
        log("\t🔥 Kerning")
        return

    # Rounding Kerning
    if round_value is not None:
        for pair, value in font.kerning.items():
            font.kerning[pair] = _kondo_round(value, round_value)
        log(f"\t🔵 Kerning: Rounded by {round_value}.")

    # Clear zero values
    if clear_zero_kerning:
        log(f"\t👀 Kerning: Looking for zero-value pairs")
        for pair, value in font.kerning.items():
            if value == 0:
                log(f"\t🫧 Kerning: Removing {pair}   Value: {value}.")
                font.kerning.pop(pair)

    # Delete empty pairs
    if clear_missing_kerning:
        log(f"\t👀 Kerning: Looking for pairs involving glyphs not present in font")
        for pair, value in font.kerning.items():
            invalid_names = set()
            pair_has_valid_glyphs = False

            # Check if both glyph/group names are valid
            for side in pair:
                # Invalid group name
                if "public" in side:
                    if side not in font.groups.keys():
                        invalid_names.add(side)
                        break
                # Invalid glyph name
                else:
                    if side not in font.keys():
                        invalid_names.add(side)
                        break

            if not invalid_names:
                pair_has_valid_glyphs = True
                for side in pair:
                    # Each side must resolve to an existing glyph.
                    if side in font.groups:
                        side_is_valid = any(
                            member in font for member in font.groups[side]
                        )
                    else:
                        side_is_valid = side in font
                    if not side_is_valid:
                        invalid_names.add(side)
                        pair_has_valid_glyphs = False

            if pair_has_valid_glyphs is False:
                reassigned_pair = _salvage_pair(font, pair)
                if salvage and reassigned_pair:
                    log(
                        f"\t🔀 Kerning: Reassigning pair: {pair} ---> {reassigned_pair}   One or more groups was not present."
                    )
                    font.kerning[reassigned_pair] = font.kerning[pair]
                    font.kerning.pop(pair)
                else:
                    log(
                        f"\t🫧 Kerning: Deleting pair: {pair}   One or more glyphs (or groups) not present.",
                        f"Invalid names: {invalid_names}. Couldn’t reassign.",
                    )
                    font.kerning.pop(pair)


def _process_groups(
    font,
    clear_empty_groups=True,
    clear_all_groups=False,
    clear_missing_members=True,
    clear_single_member_groups=True,
    report=True,
):
    def log(*args):
        if report:
            print(*args)

    if clear_all_groups:
        font.groups.clear()
        log("\t🔥 Groups")
        return

    if clear_empty_groups:
        # Delete empty groups
        log(f"\t👀 Groups: Looking for empty groups")
        for group, members in font.groups.items():
            group_has_valid_members = False
            for member in members:
                if member in font.keys():
                    group_has_valid_members = True
                    break
            if group_has_valid_members is False:
                log(f"\t🫧 Groups: Deleting group {group}.  It was empty.")
                font.groups.pop(group)

    if clear_missing_members:
        # Delete members from groups if the member is not in the font
        log(f"\t👀 Groups: Looking for group members that are missing in the font.")
        for group, members in font.groups.items():
            new_members = []
            for member in members:
                if member in font.keys():
                    new_members.append(member)
                else:
                    log(
                        f"\t🫧 Groups: Removing group member {member} from group {group}."
                    )
            font.groups[group] = new_members

    if clear_single_member_groups:
        # Delete groups that only have one member
        log(f"\t👀 Groups: Looking for single-member groups.")
        for group, members in font.groups.items():
            if len(members) == 1:
                flattened_kerning = _flatten_kerning(font, group)
                log(
                    f"\t🫧 Groups: Deleting group {group}.  It had one member. Flattening its kerning:"
                )
                if report:
                    pprint(flattened_kerning)
                font.groups.pop(group)
                font.kerning.update(flattened_kerning)


def kondo_kerning(
    font,
    clear_empty_groups=True,
    clear_all_groups=False,
    clear_zero_kerning=False,
    clear_missing_members=True,
    clear_single_member_groups=True,
    clear_missing_kerning=True,
    clear_all_kerning=False,
    salvage=True,
    round_value=None,
    report=True,
):
    """Run the existing cleanup algorithm on one font in place.

    Defaults match the UI. Set report=False to suppress console output.
    round_value=None disables rounding. The font is returned without saving.
    This structural refactor retains the existing cleanup order and logic.

    Examples:
        kondo_kerning(font, clear_zero_kerning=False)
        font.kondoKerning(round_value=5, report=False)
    """

    def log(*args):
        if report:
            print(*args)

    log("\n*********************\nKondo Kerning Report:\n*********************")
    log(font.info.familyName, font.info.styleName)

    # Kerning
    if any(
        (
            clear_zero_kerning,
            clear_missing_kerning,
            clear_all_kerning,
            round_value is not None,
        )
    ):
        _process_kerning(
            font,
            clear_zero_kerning=clear_zero_kerning,
            clear_missing_kerning=clear_missing_kerning,
            clear_all_kerning=clear_all_kerning,
            salvage=salvage,
            round_value=round_value,
            report=report,
        )
    else:
        log("\t🆗 Skipping Kerning.")

    # Groups
    if any(
        (
            clear_empty_groups,
            clear_all_groups,
            clear_missing_members,
            clear_single_member_groups,
        )
    ):
        _process_groups(
            font,
            clear_empty_groups=clear_empty_groups,
            clear_all_groups=clear_all_groups,
            clear_missing_members=clear_missing_members,
            clear_single_member_groups=clear_single_member_groups,
            report=report,
        )
    else:
        log("\t🆗 Skipping Groups.")

    log("Kondo Kerning done.\n*********************")
    font.changed()

    return font


# Expose the same function as a method without duplicating its options.
RFont.kondoKerning = kondo_kerning
