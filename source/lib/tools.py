from pprint import pprint
from mojo.roboFont import RFont


def my_round(x, base=5):
    return base * round(x / base)


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
    return (l, r) if (l, r) == pair else None


def flatten_kerning(font, group_name):
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


def kondo_kerning(
    font,
    clear_empty_groups=True,
    clear_all_groups=False,
    clear_zero_kerning=True,
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

    f = font
    log("\n*********************\nKondo Kerning Report:\n*********************")
    log(f.info.familyName, f.info.styleName)

    # Kerning Management
    if clear_all_kerning:
        f.kerning.clear()
        log("\t🔥 Kerning")

    else:
        # Rounding Kerning
        if round_value is not None:
            for pair, value in f.kerning.items():
                f.kerning[pair] = my_round(value, round_value)
            log(f"\t🔵 Kerning: Rounded by {round_value}.")

        # Clear zero values
        if clear_zero_kerning:
            log(f"\t👀 Kerning: Looking for zero-value pairs")
            for pair, value in f.kerning.items():
                if value == 0:
                    log(f"\t🫧 Kerning: Removing {pair}   Value: {value}.")
                    f.kerning.pop(pair)

        # Delete empty pairs
        if clear_missing_kerning:
            log(f"\t👀 Kerning: Looking for pairs involving glyphs not present in font")
            for pair, value in f.kerning.items():
                invalid_names = set()
                pair_has_valid_glyphs = False

                # Check if both glyph/group names are valid
                for side in pair:
                    # Invalid group name
                    if "public" in side:
                        if side not in f.groups.keys():
                            invalid_names.add(side)
                            break
                    # Invalid glyph name
                    else:
                        if side not in f.keys():
                            invalid_names.add(side)
                            break

                if not invalid_names:
                    pair_has_valid_glyphs = True
                    for side in pair:
                        # Each side must resolve to an existing glyph.
                        if side in f.groups:
                            side_is_valid = any(
                                member in f for member in f.groups[side]
                            )
                        else:
                            side_is_valid = side in f
                        if not side_is_valid:
                            invalid_names.add(side)
                            pair_has_valid_glyphs = False

                if pair_has_valid_glyphs is False:
                    reassigned_pair = salvage_pair(f, pair)
                    if salvage and reassigned_pair:
                        log(
                            f"\t🔀 Kerning: Reassigning pair: {pair} ---> {reassigned_pair}   One or more groups was not present."
                        )
                        f.kerning[reassigned_pair] = f.kerning[pair]
                        f.kerning.pop(pair)
                    else:
                        log(
                            f"\t🫧 Kerning: Deleting pair: {pair}   One or more glyphs (or groups) not present.",
                            f"Invalid names: {invalid_names}. Couldn’t reassign."
                        )
                        f.kerning.pop(pair)
        else:
            log("\t🆗 Skipping Kerning.")

    # Groups management
    if clear_all_groups:
        f.groups.clear()
        log("\t🔥 Groups")
    else:
        if clear_empty_groups:
            # Delete empty groups
            log(f"\t👀 Groups: Looking for empty groups")
            for group, members in f.groups.items():
                group_has_valid_members = False
                for member in members:
                    if member in f.keys():
                        group_has_valid_members = True
                        break
                if group_has_valid_members is False:
                    log(f"\t🫧 Groups: Deleting group {group}.  It was empty.")
                    f.groups.pop(group)
        if clear_missing_members:
            # Delete members from groups if the member is not in the font
            log(f"\t👀 Groups: Looking for group members that are missing in the font.")
            for group, members in f.groups.items():
                new_members = []
                for member in members:
                    if member in f.keys():
                        new_members.append(member)
                    else:
                        log(
                            f"\t🫧 Groups: Removing group member {member} from group {group}."
                        )
                f.groups[group] = new_members
        if clear_single_member_groups:
            # Delete groups that only have one member
            log(f"\t👀 Groups: Looking for single-member groups.")
            for group, members in f.groups.items():
                if len(members) == 1:
                    flattened_kerning = flatten_kerning(f, group)
                    log(
                        f"\t🫧 Groups: Deleting group {group}.  It had one member. Flattening its kerning:"
                    )
                    if report:
                        pprint(flattened_kerning)
                    f.groups.pop(group)
                    f.kerning.update(flattened_kerning)
        else:
            log("\t🆗 Skipping Groups.")

    log("Kondo Kerning done.\n*********************")

    f.changed()

    return font


# Expose the same function as a method without duplicating its options.
RFont.kondoKerning = kondo_kerning
