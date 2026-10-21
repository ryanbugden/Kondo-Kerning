<img src="source/resources/mechanic_icon.png"  width="80">

# Kondo Kerning
A RoboFont extension for cleaning up kerning and group data in your UFOs.

## A tour of the interface

<img src="source/resources/ui-main.png"  width="300">

### Span
Choose whether you’d like to affect just the current, frontmost UFO or all open UFOs.

### Groups

#### Clear Empty Groups

Remove groups that have no glyphs in them, or only contain glyphs that aren’t in the font (pairs involving these groups are removed, or salvaged when **Try To Salvage** is enabled). 

#### Clear One-Member Groups

Remove groups that only have one member, flattening their grouped kerning to glyph pairs while preserving resolved kerning values.

#### Clear Missing Group Members

Remove glyph names from groups if the glyphs are not in the font.

#### Clear All Groups

Flatten group kerning into individual glyph pairs and remove all groups. To be safe, empty groups are handled first, regardless of whether or not **Clear Empty Groups** is checked.

> [!WARNING]
> Destructive.

#### Normalize Group Order

Sort group members by the font’s glyph order. Members absent from the glyph order follow alphabetically. This matches MetricsMachine’s (v1.3) logic. 

### Kerning

#### Clear Zero-Value Pairs

Remove zero-value pairs while retaining explicit exceptions.

#### Clear Missing Pairs

Remove pairs involving missing glyphs, missing groups, or groups with no glyphs present in the font. Enable **Try To Salvage** to attempt recovery instead.

#### Clear All Pairs

> [!WARNING]
> Destructive.

Remove all kerning pairs.

#### Round Values By

Round kerning values to multiples of the number provided.

### Try To Salvage

Attempt to recover pairs involving invalid group names by replacing them with glyph names. Happens during missing-pair cleanup and empty-group removal. This is “Hail Mary” logic: `public.kern1.a.alt` becomes `a.alt` if that glyph exists.

### Apply

Click this to go, and see a detailed report in the [Output Window](https://robofont.com/documentation/reference/workspace/output-window/) afterward.



## API

Once Kondo Kerning is installed, a `kondoKerning()` method is added to `RFont` objects.

```python
RFont.kondoKerning(
    # Groups
    clear_empty_groups=True,
    clear_single_member_groups=True,
    clear_missing_members=True,
    clear_all_groups=False,
    normalize_group_order=True,
    # Kerning
    clear_zero_kerning=False,
    clear_missing_kerning=True,
    clear_all_kerning=False,
    round_value=None,
    # General
    salvage=False,
    report=True,
)
```

Clean up kerning and groups in a font. Changes are applied directly to the font provided. The method returns the same font object, modified in place, without saving it.

### Arguments

`clear_empty_groups`

**Boolean**. Remove groups that have no glyphs in them, or only contain glyphs that aren’t in the font. Pairs involving these groups are removed, or salvaged when `salvage=True`.

`clear_single_member_groups`

**Boolean**. Remove groups that only have one member, flattening their grouped kerning to glyph pairs while preserving resolved kerning values.

`clear_missing_members`

**Boolean**. Remove glyph names from groups if the glyphs are not in the font.

`clear_all_groups`

**Boolean**. Flatten group kerning into individual glyph pairs and remove all groups. To be safe, empty groups are handled first, regardless of whether or not `clear_empty_groups=True`.

`normalize_group_order`

**Boolean**. Sort group members by the font’s glyph order. Members absent from the glyph order follow alphabetically. This matches MetricsMachine’s (v1.3) logic.

`clear_zero_kerning`

**Boolean**. Remove zero-value pairs while retaining explicit exceptions.

`clear_missing_kerning`

**Boolean**. Remove pairs involving missing glyphs, missing groups, or groups with no glyphs present in the font. Set `salvage=True` to attempt recovery instead.

`clear_all_kerning`

**Boolean**. Remove all kerning pairs.

`round_value`

**Positive integer or None**. Round kerning values to multiples of the number provided. Use a positive integer, such as 5. `None` disables rounding.

`salvage`

**Boolean**. Attempt to recover pairs involving invalid group names by replacing them with glyph names. Happens during missing-pair cleanup and empty-group removal. This is “Hail Mary” logic: `public.kern1.a.alt` becomes `a.alt` if that glyph exists.

`report`

**Boolean**. Print a detailed report in the Output Window.

### Example Scripts

#### Clean up your font with default settings

```python
f = CurrentFont()
f.kondoKerning()
```

#### Clean up and attempt to salvage invalid pairs

```python
f = CurrentFont()
f.kondoKerning(salvage=True)
```

#### Clean and round kerning in all open fonts

```python
for f in AllFonts():
    f.kondoKerning(round_value=5)
```

#### Flatten all groups in a copy of your font

```python
f = CurrentFont()
new_font = f.copy()
new_font.kondoKerning(
    clear_all_groups=True,
)
new_font.openInterface()
```

#### Save a cleaned version of a UFO without opening it

```python
ufo_path = "/path/to/font.ufo"

font = OpenFont(ufo_path, showInterface=False)
font_copy = font.copy()
font_copy.kondoKerning(report=False)
font_copy.save(ufo_path.removesuffix(".ufo") + "-Cleaned.ufo")
```

## Acknowledgements

Built with RoboFont & EZUI. Thanks to Frederik Berlaen & Tal Leming.
