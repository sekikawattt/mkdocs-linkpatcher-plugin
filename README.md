# MkDocs LinkPatcher Plugin


## Installation
dependencies: Python 2.7, 3.3+
```bash
git clone https://github.com/sekikawattt/mkdocs-linkpatcher-plugin.git
cd mkdocs-linkpatcher-plugin
pip install -e .

```
mkdocs.yml
```yml
plugins:
  - linkpatcher-plugin:
```

## features
### `:` is converted into header
```md
:: tuna

:::::: tuna
```
↓`mkdocs build`
```html
<p>
<h2 class="linkpatcher" id="linkpatcher_tuna">tuna</h2>
</p>
<p>
<h6 class="linkpatcher" id="linkpatcher_tuna">tuna</h6>
</p>
```

### linked automatically
```md
:: tuna
tuna
```
↓`mkdocs build`
```html
<p>
<h2 class="linkpatcher" id="linkpatcher_tuna">tuna</h2>
<a class="linkpatcher_link" href="./index.html#linkpatcher_tuna">tuna</a></p>
```
### alias
```md
:: tuna, maguro
maguro, tuna
```
↓`mkdocs build`
```html
<p>
<h2 class="linkpatcher" id="linkpatcher_tuna">tuna</h2>
<a class="linkpatcher_link" href="./index.html#linkpatcher_tuna">maguro</a>, <a class="linkpatcher_link" href="./index.html#linkpatcher_tuna">tuna</a></p>
```
### avoid to be extracted
```md
:: !description, tuna_description
description, tuna_description
```
↓`mkdocs build`
```html
<p>
<h2 class="linkpatcher" id="linkpatcher_description">description</h2>
description, <a class="linkpatcher_link" href="./index.html#linkpatcher_description">tuna_description</a></p>
```

### link beyond pages
mkdocs.yml
```yaml
plugins:
  - linkpatcher-plugin
pages:
  - index.md
  - tuna:
      - tuna.md
```
index.md
```md
:: !ingredient, ingredient_of_soy_source
salt, soy, and...
```
tuna.md
```md
## soy_source
Soysource.
Best source for me.
Its flavor is far from soy.
See, ingredient_of_soy_source
```
↓`mkdocs build`

/index.html
```html
<p>
<h2 class="linkpatcher" id="linkpatcher_ingredient">ingredient</h2>
salt, soy, and...</p>
```
/tuna/index.html
```html
<p>Soysource.
Best source for me.
Its flavor is far from <a class="linkpatcher_link" href="../index.html#linkpatcher_ingredient">soy</a>.
See <a class="linkpatcher_link" href="../index.html#linkpatcher_ingredient">ingredient_of_soy_source</a>.</p>
```
