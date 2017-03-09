signal-wont-let-me-attach
=========================

Store arbitrary files inside PNGs to overcome nonsensical file type
restrictions.

![Demo](http://i.imgur.com/4S9wEoo.png)

Examples
--------

Pack `foo.pdf` into `foo.png`:

```console
signal-wont-let-me-attach foo.pdf
```

Pack `foo.pdf` into `bar.png`:

```console
signal-wont-let-me-attach foo.pdf bar.png
```

Unpack and delete `file.png` restoring the original file:

```console
signal-wont-let-me-attach file.png
```

Setup
-----

Install dependencies:

```console
pip install -r requirements.txt
```
