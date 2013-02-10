Autopsy
==============

![Autopsy Logo](https://github.com/davelab6/autopsy/raw/master/logo.png)

Autopsy is a [FontLab Studio](http://www.fontlab.com/font-editor/fontlab-studio/) add-on for analyzing design consistency across multiple fonts.

![Screen shot of the Autopsy interface](https://github.com/davelab6/autopsy/raw/master/showing.png)

It visualizes a selection of letters side by side and puts it into a PDF for visual comparison. If visual comparison isn’t enough for you, it dissects what’s there and what’s not and puts that into simple graphs.

#### Single fonts

Compare the design of glyphs across different fonts or families. Something you can’t do in FontLab without generating each font an loading them into some document.

#### Multiple Master instances

Compare the design of glyphs without generating instances. In FontLab you can use the MM-slider, but with Autopsy you can audit the exact instances you will generate later on.

Read all the details in the [User Guide](fontlab/Autopsy User Guide.pdf).

Licence
------------

Autopsy is libre software, licensed under the terms of the GNU GPLv3

Answers and questions
---------------------

#### Why do I need this?

You don’t get your kicks from punches, stiff serifs and ink cracks?
Move, nothing to see here. Otherwise you need this tool to make sure that the letters you draw are consistent in design across your font family. It doesn’t go into aesthetic details of lettershapes. That’s up to your type design skills. But you can now make sure that the width of your Light, Bold and Black blend well behaved according to b=√(ac), a=b²÷c and c=b²÷c. Read more about interpolation theory at [Luc[as]’s](http://www.lucasfonts.com/) (click on *Information* and then *Interpolation theory*) or on [Typophile](http://www.typophile.com/node/39376).

#### Dude, I superpolate. I know that my fonts are b=√(ac), a=b²÷c and c=b²÷c !

Right. This tool is not for the superpolators. It is for those who draw fonts in single files, one for Regular, one for Bold and one for Black.
It is useful for foundries who are updating ancient font families that have been digitized when Multiple Master or [Superpolator](http://superpolator.com/) was unheard of. Those fonts often have huge design inconsistencies that are difficult to come by if you can’t see them.

#### But I can already compare my fonts now. I generate each of them, fire up InDesign, place each letter of each font on the pages, export the thing as a PDF, open Acrobat and view the thing on the screen.

Right.

Recent changes
---------------

### Version 1.101 (2013-02-10)

In January 2013, Dave Crossland asked Yanone to make Autopsy libre software and he agreed (under the GPLv3) as long as no one asks him to support it.

> ---------- Forwarded message ----------
```
> From: Yanone
> Date: 28 January 2013 06:56
> To: Dave Crossland <d.crossland@gmail.com>
```
> 
> > I was curious if/when Autopsy will be made libre, as it would be good
> > to include in FontForge.
> 
> My only problem is that I don't want to support the software at this point.
> I've written it at a point when I was just making the first steps into object
> oriented programming and the code is a mess. If you promise that you don't ask
> me about the code you can have and use it. You will need to rewrite the small
> GUI part. The object model is based on RGlyph, if I remember correctly, so
> that shouldn't be much of a problem to use. I know that Georg already made a
> Glyphs.app compatible version.
> 
> There's no ongoing interest in Autopsy. Neither have people bought any
> licenses for several years in a row now nor has anybody asked for an updated
> version. So please go ahead if you find it useful. I might still rewrite it in
> the future and again try to sell it, but it won't be a feature-identical
> version. And it won't happen any time soon.
> 
> Make it GPL3, please. Thank you.

### Version 1.1 (2009-03-04)

* Added: PDF Bookmarks
* Added: Option to draw glyphs filled or empty, to check for FontLab’s RemoveOverlap errors
* Added: Option to display font’s full name under each glyph
* Bugfix: Often one glyph appeared twice in the PDF

Ideas for future versions
------------------------------

* Save individual presets of preferences from the GUI
* Use option boxes instead of check boxes in GUI. Hello, FontLab? Hello??
* Generally improve User Interface
* Get glyphs with zero width and missing glyphs right
* Support TrueType outlines
* If you must use TrueType fonts now, convert them PostScript outlines first.
* Tweak colors and fonts of the PDF from the GUI

Anything missing? This is libre software so you're free to contribute it!
