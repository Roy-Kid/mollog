---
title: mollog
description: Structured logging for Python with a stdlib-compatible API.
hide:
  - navigation
  - toc
hero:
  title: mollog
  description: A structured logger you can drop in where <code>import logging</code> was. Keep the stdlib format strings and the third-party ecosystem that emits through <code>logging</code>, and gain structured fields, context propagation, JSON / Rich formatters, and an optional Logfire backend.
  install:
    label: Install
    command: pip install molcrafts-mollog
  badges:
    - img: https://img.shields.io/pypi/v/molcrafts-mollog
      href: https://pypi.org/project/molcrafts-mollog/
      alt: PyPI version
    - img: https://img.shields.io/badge/python-3.12%2B-blue.svg
      href: https://pypi.org/project/molcrafts-mollog/
      alt: Python 3.12+
    - img: https://img.shields.io/badge/license-BSD--3--Clause-blue.svg
      href: https://github.com/MolCrafts/mollog/blob/master/LICENSE
      alt: License BSD-3-Clause
  actions:
    - label: Get started
      href: getting-started/
      style: primary
    - label: Configuration
      href: configuration/
    - label: API reference
      href: api/
---

<h1 class="molcrafts-sr-only">mollog</h1>

<div class="molcrafts-manual-home" markdown>

<!-- ────────────────────────────────────────────────────────────
     AT A GLANCE — compact frame: static label + one code block
     ──────────────────────────────────────────────────────────── -->

<section class="molcrafts-manual-section molcrafts-manual-section--compact" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">At a glance</span>

## Configure once, log structured fields

`configure()` takes the same `format=` string you already know. Pass keyword
arguments and they ride along as structured `extra` fields; libraries that
still use stdlib `logging` are captured and routed through mollog.

</div>

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")

mollog.info("service booted", port=8080)
```

</section>

<!-- ────────────────────────────────────────────────────────────
     CAPABILITIES — stack frame + 2-column grid of linked cards
     ──────────────────────────────────────────────────────────── -->

<section class="molcrafts-manual-section molcrafts-manual-section--stack" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">What mollog gives you</span>

## A drop-in that does more once you're in

</div>

<div class="molcrafts-manual-grid molcrafts-manual-grid--cols-2">
  <a href="getting-started/">
    <strong>Stdlib-compatible</strong>
    <p>Drop-in for <code>logging.basicConfig</code>: stdlib <code>%(asctime)s</code>-style format strings via <code>StdlibStyleFormatter</code>, so existing config keeps working.</p>
  </a>
  <a href="configuration/">
    <strong>Stdlib bridge</strong>
    <p>Records from libraries that still use <code>logging</code> (httpx, urllib3, openai, …) are captured and routed through mollog — one place to configure everything.</p>
  </a>
  <a href="getting-started/">
    <strong>Structured fields</strong>
    <p>Attach <code>extra</code> fields per call and reuse them with <code>Logger.bind()</code>. Named loggers carry a hierarchy with propagation.</p>
  </a>
  <a href="context/">
    <strong>Context propagation</strong>
    <p>Context-local fields via the <code>Context</code> namespace; <code>Context.scope(...)</code> doubles as a Logfire span once <code>configure_logfire(...)</code> has run.</p>
  </a>
  <a href="rich/">
    <strong>Formatters &amp; handlers</strong>
    <p>Text, JSON, Rich, and stdlib-style formatters over stream, file, rotating, timed-rotating, queue, and null handlers.</p>
  </a>
  <a href="logfire/">
    <strong>Optional Logfire backend</strong>
    <p>Ship records to Pydantic Logfire via <code>LogfireHandler</code> and <code>configure_logfire(...)</code> — opt-in, never a runtime dependency.</p>
  </a>
</div>

</section>

<!-- ────────────────────────────────────────────────────────────
     MANUAL INDEX — stack frame, full-width numbered chapter list
     ──────────────────────────────────────────────────────────── -->

<section class="molcrafts-manual-section molcrafts-manual-section--stack" markdown>

<div class="molcrafts-manual-section__header" markdown>

<span class="molcrafts-manual-eyebrow">Find your page</span>

## The manual in seven chapters

</div>

<nav class="molcrafts-manual-index" aria-label="Manual chapters">
  <a href="getting-started/">
    <span>01</span>
    <strong>Getting Started</strong>
    <em>Install mollog, configure the root logger, and reach for the common patterns.</em>
  </a>
  <a href="configuration/">
    <span>02</span>
    <strong>Configuration</strong>
    <em>Root logger setup, the stdlib bridge, and clean teardown.</em>
  </a>
  <a href="context/">
    <span>03</span>
    <strong>Context Propagation</strong>
    <em>Request- and task-scoped metadata that follows every record.</em>
  </a>
  <a href="behavior/">
    <span>04</span>
    <strong>Behavior</strong>
    <em>Concurrency, reserved fields, and shutdown semantics.</em>
  </a>
  <a href="rich/">
    <span>05</span>
    <strong>Rich Console</strong>
    <em>Colored terminal output for local development.</em>
  </a>
  <a href="logfire/">
    <span>06</span>
    <strong>Logfire</strong>
    <em>The optional Pydantic Logfire backend and span integration.</em>
  </a>
  <a href="api/">
    <span>07</span>
    <strong>API Reference</strong>
    <em>The complete exported surface.</em>
  </a>
</nav>

</section>

</div>
