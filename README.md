# shogi-gif

Convert a kifu file into an animated gif, for easy sharing

# Usage

Because of the early stage of this project, you can only convert kifu files
with extention `.kifu` into an animated gif. In addition, as long as
python-shogi do not fix its KIF parser (PR waiting), you cannot import
kifu from 81dojo, because it inserts multiple space between move number and
move coordinate. But if you remove these spaces to keep only one, it will
work.

```
python kg-converter.py kifu_name gif_name
```
