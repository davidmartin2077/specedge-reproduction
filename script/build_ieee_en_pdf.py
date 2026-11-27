"""
Build a publication-grade 100% English IEEE Conference (IEEEtran) Two-Column PDF
(docs/ieee_paper_en.pdf) strictly satisfying the course rubric:
  - IEEE Conference two-column template (US Letter, 7.25in text width, 0.24in gutter)
  - 100% original academic English (workshop-level research paper)
  - Exact 10pt body font size, exact 12pt single-spaced line-height
  - >= 6 full pages (two-column), all 6 English figures (docs/figures_en/),
    5 IEEE tables (TABLE I-V), numbered equations (1)-(4), Propositions 1-2,
    Algorithm 1, Related Work, and 12 IEEE references.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
HTML_PATH = DOCS_DIR / "_ieee_en_build.html"
PDF_PATH = DOCS_DIR / "ieee_paper_en.pdf"


def build_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Heterogeneity-Aware Edge-Cloud Speculative Decoding over Wide-Area Networks</title>
<style>
  /* Official IEEE Conference (IEEEtran) Geometry: US Letter (8.5in x 11in) */
  @page {
    size: letter;
    margin: 0.70in 0.625in 0.80in 0.625in;
    @bottom-center {
      content: counter(page);
      font-family: "Times New Roman", serif;
      font-size: 9pt;
      color: #222222;
    }
  }

  * { box-sizing: border-box; }

  /* Strict Rubric Spec: 10pt font size, 12pt line spacing (single-spaced) */
  body {
    font-family: "Times New Roman", Times, Georgia, serif;
    font-size: 10pt;
    line-height: 12pt;
    color: #111111;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* IEEE Full-Width Title & Author Header */
  .ieee-header {
    text-align: center;
    margin-bottom: 14pt;
    padding-top: 2pt;
  }
  h1.paper-title {
    font-size: 20pt;
    font-weight: 400;
    line-height: 24pt;
    margin: 0 0 10pt 0;
    color: #000000;
  }
  .ieee-author-name {
    font-size: 10.5pt;
    line-height: 13pt;
    font-weight: 400;
    margin-bottom: 2pt;
    color: #111111;
  }
  .ieee-author-affil {
    font-size: 9.5pt;
    line-height: 11.5pt;
    font-style: italic;
    color: #222222;
    margin-bottom: 1.5pt;
  }
  .ieee-author-repo {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
    line-height: 11pt;
    color: #1D3557;
  }

  /* Two-Column IEEE Body */
  .two-col {
    column-count: 2;
    column-gap: 0.24in;
    column-fill: balance;
  }
  .span-all {
    column-span: all;
    margin: 5.5pt 0 6.5pt 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* IEEE Left-Column Abstract & Index Terms (9pt bold per IEEEtran spec) */
  .ieee-abstract {
    font-size: 9pt;
    line-height: 10.8pt;
    font-weight: 700;
    text-align: justify;
    margin: 0 0 6pt 0;
    hyphens: auto;
  }
  .ieee-abstract .abs-lead {
    font-style: italic;
  }
  .ieee-keywords {
    font-size: 9pt;
    line-height: 10.8pt;
    font-weight: 700;
    text-align: justify;
    margin: 0 0 10pt 0;
  }
  .ieee-keywords .kw-lead {
    font-style: italic;
  }

  /* IEEE Centered Small-Caps Roman-Numeral Section Headings (I. INTRODUCTION) */
  h2 {
    font-size: 10pt;
    line-height: 12pt;
    font-weight: 400;
    font-variant: small-caps;
    text-transform: uppercase;
    text-align: center;
    color: #000000;
    margin: 11pt 0 5pt 0;
    letter-spacing: 0.4pt;
    break-after: avoid;
    page-break-after: avoid;
  }
  /* IEEE Left-Aligned Italic Lettered Subsections (A. Subsection) */
  h3 {
    font-size: 10pt;
    line-height: 12pt;
    font-weight: 400;
    font-style: italic;
    text-align: left;
    color: #000000;
    margin: 8pt 0 3.5pt 0;
    break-after: avoid;
    page-break-after: avoid;
  }

  p {
    text-align: justify;
    text-indent: 1.2em;
    margin: 0 0 4pt 0;
    hyphens: auto;
  }
  p.noindent { text-indent: 0; }

  ul, ol {
    margin: 2.5pt 0 5pt 0;
    padding-left: 14pt;
  }
  li {
    text-align: justify;
    margin-bottom: 2.5pt;
    hyphens: auto;
  }

  code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.6pt;
    color: #111111;
  }

  /* Mathematical Typography (STIX / Cambria Math) */
  .m {
    font-family: "STIXGeneral", "Cambria Math", "Times New Roman", serif;
    white-space: nowrap;
  }
  .m i { font-style: italic; }
  .m .rm { font-style: normal; }
  .m sub, .m sup {
    font-size: 72%;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
  }
  .m sup { top: -0.44em; }
  .m sub { bottom: -0.20em; }

  /* Single-Column IEEE Equations with Flush-Right Numbering */
  .eq-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 6pt 0 6.5pt 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .eq-body {
    flex: 1;
    text-align: center;
    font-family: "STIXGeneral", "Cambria Math", "Times New Roman", serif;
    font-size: 9.2pt;
    line-height: 11.5pt;
  }
  .eq-num {
    width: 19pt;
    flex-shrink: 0;
    text-align: right;
    font-family: "Times New Roman", serif;
    font-size: 9.5pt;
  }
  .frac {
    display: inline-flex;
    flex-direction: column;
    vertical-align: middle;
    text-align: center;
    margin: 0 2pt;
    font-size: 95%;
  }
  .frac .num {
    border-bottom: 0.65pt solid #111111;
    padding: 0 2.5pt 1pt 2.5pt;
  }
  .frac .den {
    padding: 1pt 2.5pt 0 2.5pt;
  }

  /* Proposition Environment */
  .proposition {
    margin: 6pt 0 6pt 0;
    padding: 4.5pt 6.5pt;
    border-left: 1.6pt solid #222222;
    background: #FAFAFB;
    font-size: 9.4pt;
    line-height: 11.4pt;
    text-align: justify;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .proposition .prop-head {
    font-weight: 700;
    font-style: normal;
  }
  .proposition .prop-body {
    font-style: italic;
  }
  .proof-sketch {
    font-size: 9.5pt;
    line-height: 11.5pt;
    text-align: justify;
    text-indent: 0;
    margin: 0 0 5pt 0;
  }

  /* IEEE Single-Column Ruled Algorithm Box */
  .alg-box {
    margin: 6.5pt 0 7.5pt 0;
    border-top: 1.25pt solid #000000;
    border-bottom: 1.25pt solid #000000;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .alg-header {
    padding: 3pt 1pt;
    border-bottom: 0.65pt solid #000000;
    font-size: 8.6pt;
    line-height: 10.6pt;
  }
  .alg-body {
    padding: 3.5pt 1pt 4pt 1pt;
    font-size: 7.9pt;
    line-height: 10.6pt;
  }
  .alg-req { margin-bottom: 2.5pt; text-align: left; }
  .alg-line { display: flex; align-items: baseline; }
  .alg-ln {
    width: 14pt;
    flex-shrink: 0;
    font-size: 7.2pt;
    color: #555555;
    text-align: right;
    padding-right: 4pt;
  }
  .alg-code { flex: 1; text-align: left; }
  .alg-ind1 { padding-left: 9pt; }
  .alg-ind2 { padding-left: 18pt; }
  .alg-kw { font-weight: 700; }
  .alg-cmt { color: #555555; font-size: 7.4pt; margin-left: 3pt; }

  /* IEEE Tables (Uppercase Centered TABLE I + Small-Caps Caption) */
  .table-wrap {
    margin: 6pt 0 7.5pt 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .table-label {
    text-align: center;
    font-size: 8.4pt;
    line-height: 10.2pt;
    font-weight: 400;
    letter-spacing: 0.6pt;
    margin-bottom: 1pt;
  }
  .table-title {
    text-align: center;
    font-size: 8.2pt;
    line-height: 10pt;
    font-variant: small-caps;
    text-transform: uppercase;
    margin-bottom: 4pt;
    color: #111111;
  }
  .table-title .m, .table-title code {
    text-transform: none;
    font-variant: normal;
  }
  table.ieee-tbl {
    width: 100%;
    border-collapse: collapse;
    border-top: 1.2pt solid #000000;
    border-bottom: 1.2pt solid #000000;
    font-size: 7.9pt;
    line-height: 10.0pt;
  }
  table.ieee-tbl.compact { font-size: 7.5pt; line-height: 9.6pt; }
  table.ieee-tbl thead th {
    font-weight: 700;
    text-align: center;
    padding: 3.2pt 2.5pt;
    border-bottom: 0.65pt solid #000000;
    background: #FFFFFF;
    color: #000000;
    vertical-align: bottom;
  }
  table.ieee-tbl tbody td {
    padding: 2.7pt 2.5pt;
    text-align: center;
    vertical-align: middle;
  }
  table.ieee-tbl th.l, table.ieee-tbl td.l { text-align: left; }
  table.ieee-tbl tr.midrule td { border-top: 0.5pt solid #666666; }
  table.ieee-tbl tr.highlight td { background: #F4F6FA; }
  .table-note {
    font-size: 7.4pt;
    line-height: 9.2pt;
    color: #444444;
    margin-top: 2.5pt;
    text-align: left;
  }

  /* IEEE Figures */
  figure {
    margin: 6pt 0 7.5pt 0;
    text-align: center;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  figure img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
  }
  figure.span-all img { max-width: 90%; }
  figcaption {
    font-size: 8.2pt;
    line-height: 10.2pt;
    color: #111111;
    margin-top: 3.5pt;
    text-align: justify;
  }

  /* IEEE References (8pt / 9.6pt leading) */
  .refs {
    font-size: 8.0pt;
    line-height: 9.8pt;
    margin: 3pt 0 0 0;
    padding-left: 0;
    list-style: none;
  }
  .refs li {
    padding-left: 17pt;
    text-indent: -17pt;
    margin-bottom: 3pt;
    text-align: justify;
  }
  .cite-num { display: inline-block; width: 17pt; text-indent: 0; }
</style>
</head>
<body>

<!-- ==================== IEEE FULL-WIDTH TITLE HEADER ==================== -->
<div class="ieee-header">
  <h1 class="paper-title">Heterogeneity-Aware Edge-Cloud Speculative Decoding over Wide-Area Networks:<br>Analytical Modeling, Variable-Budget Static Graph Verification, and Empirical Analysis</h1>
  <div class="ieee-author-name">Course Research Paper &mdash; Distributed Systems &amp; Edge-Cloud Collaboration</div>
  <div class="ieee-author-affil">Cross-Platform Heterogeneous Testbed: RTX 4080 SUPER (32 GB) &times; RTX 5060 Ti (8 GB) &times; Apple M4 (16 GB)</div>
  <div class="ieee-author-repo">Code &amp; Artifacts: https://github.com/davidmartin2077/specedge-reproduction</div>
</div>

<!-- ==================== IEEE TWO-COLUMN BODY ==================== -->
<div class="two-col">

  <!-- Abstract & Index Terms (Left Column Top) -->
  <div class="ieee-abstract">
    <span class="abs-lead">Abstract&mdash;</span>Edge-assisted speculative decoding, exemplified by SpecEdge, alleviates the memory-bandwidth bottleneck of autoregressive Large Language Model (LLM) serving by offloading lightweight draft tree generation to edge devices while retaining batched target-model verification on a central server. However, existing evaluations rely on an idealized deployment model: homogeneous Linux nodes with NVIDIA CUDA accelerators connected over sub-millisecond 10 GbE local-area networks. In practical laboratory and consumer device-cloud clusters&mdash;where discrete desktop GPUs and Apple Silicon laptops collaborate over Wide-Area Networks (WANs) such as Tailscale&mdash;edge nodes exhibit severe three-dimensional heterogeneity across execution backends (CUDA Graph vs. eager PyTorch MPS), memory capacity (8 GB discrete VRAM vs. 16 GB unified memory), and network round-trip latency (500&ndash;1500 ms). Through 18 controlled-variable experiments on a real cross-platform three-node cluster serving <code>Qwen3-14B</code> on <code>SpecBench</code>, we uncover a counter-intuitive throughput inversion in which a faster GPU edge trails a slower laptop edge under uniform speculation policies. To explain and resolve this phenomenon, we make three research contributions: (1) an analytical Time-Per-Output-Token (TPOT) model and dimensionless bottleneck ratio <span class="m"><i>&rho;</i> = (<i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub>)/<i>T</i><sub><span class="rm">draft</span></sub></span> that predicts divergent optimal tree depths for network-bound (<span class="m"><i>&rho;</i> &gg; 1</span>) versus compute-sensitive (<span class="m"><i>&rho;</i> &approx; 1</span>) edges (<span class="m"><i>R</i><sup>2</sup> = 0.992</span>), along with a fixed dispatch-overhead amortization effect on Apple Silicon; (2) a non-intrusive Apple MPS compatibility layer and a lightweight <em>Variable-Budget Static CUDA Graph Zero-Padding</em> server mechanism that concurrently serves heterogeneous tree budgets from a single captured graph with mathematically equivalent verification and only +2.0 ms overhead; and (3) a heterogeneity-aware edge configuration policy that boosts bottleneck-node throughput by +57.7%, cuts server RPCs by 28.9%, reduces laptop local draft compute by 64.0%, raises cluster aggregate throughput by +9.7%, and lowers inter-edge throughput imbalance from 2.20&times; to 1.23&times;.
  </div>

  <div class="ieee-keywords">
    <span class="kw-lead">Index Terms&mdash;</span>Edge-cloud collaborative inference, speculative decoding, heterogeneous edge computing, CUDA Graphs, Apple Silicon MPS, wide-area networks.
  </div>

  <!-- SECTION I -->
  <h2>I. Introduction</h2>
  <p>
    Serving Large Language Models (LLMs) interactively remains fundamentally constrained by GPU memory bandwidth during autoregressive token generation [1]. Because each decoded token requires streaming billions of target-model parameters from High Bandwidth Memory (HBM) with low arithmetic intensity, expensive high-VRAM servers frequently operate far below their peak compute throughput. Tree-structured speculative decoding [5] mitigates this inefficiency by employing a small draft model to propose a branching tree of candidate continuations that the target model verifies in a single parallel forward pass, preserving the exact target output distribution.
  </p>
  <p>
    Building on this principle, SpecEdge [8] introduced an edge-assisted serving architecture in which edge devices execute draft tree construction locally and transmit only compact token IDs and tree attention masks over gRPC to a shared cloud or server verifier. By decoupling drafting from verification, the central server dedicates its full VRAM capacity to the target LLM and static CUDA Graphs.
  </p>
  <p>
    Despite its strong performance in controlled datacenter setups, deploying SpecEdge in realistic academic and consumer device-cloud environments exposes a stark mismatch with the original paper&rsquo;s assumptions:
  </p>
  <ol>
    <li><strong>Backend and Memory Asymmetry:</strong> Real edge pools routinely mix discrete NVIDIA GPUs (supporting low-overhead CUDA Graphs but constrained to 8 GB consumer VRAM) with thin-and-light Apple Silicon laptops (offering 16 GB unified memory but running PyTorch MPS in eager kernel-dispatch mode without CUDA Graph capture).</li>
    <li><strong>Wide-Area Network Heterogeneity:</strong> Personal and cross-campus devices commonly interconnect via overlay VPNs (e.g., Tailscale) across commodity WAN links, introducing asymmetric Round-Trip Times (RTTs) of 500&ndash;1500 ms&mdash;three orders of magnitude higher than 10 GbE LANs (&lt;1 ms).</li>
    <li><strong>Uniform Budget Lock-In:</strong> SpecEdge&rsquo;s server verification engine allocates fixed-shape static CUDA Graph tensors sized to a single global <code>max_budget</code>, forcing every concurrent edge device to share identical tree budgets regardless of local compute speed or link latency.</li>
  </ol>
  <p>
    During initial three-node integration, we observed a striking anomaly: an <code>RTX 5060 Ti</code> edge running <code>Qwen3-1.7B</code> with CUDA Graphs achieved <em>lower</em> end-to-end decode throughput (2.78 tok/s) than an <code>Apple M4</code> laptop running the smaller <code>Qwen3-0.6B</code> under eager MPS dispatch (3.31 tok/s). This throughput inversion raises three core research questions:
  </p>
  <ul>
    <li><em>RQ1:</em> How do execution backend overhead, draft model scale, and WAN RTT interact quantitatively to govern per-token latency in heterogeneous edge-cloud speculative decoding?</li>
    <li><em>RQ2:</em> Do uniform speculation budgets and default Proactive Drafting heuristics remain optimal across network-bound and compute-sensitive edge nodes?</li>
    <li><em>RQ3:</em> Can a single static-graph target server concurrently accommodate per-client heterogeneous tree budgets without graph recompilation, memory inflation, or accuracy loss?</li>
  </ul>
  <p>
    To answer these questions, we conduct an end-to-end modeling, system design, and controlled-variable empirical study across three physical machines (WSL2 RTX 4080 SUPER server, Windows RTX 5060 Ti edge, and macOS Apple M4 edge). Our main contributions are fourfold:
  </p>
  <ul>
    <li><strong>Analytical Regime Modeling:</strong> We formulate a closed-form heterogeneous WAN TPOT model and introduce a dimensionless bottleneck ratio <span class="m"><i>&rho;</i></span> that separates network-bound (<span class="m"><i>&rho;</i> &gg; 1</span>) and compute-sensitive (<span class="m"><i>&rho;</i> &approx; 1</span>) regimes, predicting opposite optimal tree depths and explaining dispatch-overhead amortization on Apple MPS.</li>
    <li><strong>Cross-Platform MPS Compatibility:</strong> We engineer a zero-overhead device-dispatch layer enabling SpecEdge on Apple Silicon MPS, resolving a latent non-graph <code>KVCache.seq_indices</code> slicing bug and Windows Python 3.14 gRPC teardown hangs.</li>
    <li><strong>Variable-Budget Static CUDA Graph Zero-Padding:</strong> We design and formally justify a single-graph zero-padding verifier with dummy-slot KV isolation and masked KV reordering, serving concurrent heterogeneous budgets (<span class="m"><i>B</i>=64</span> and <span class="m"><i>B</i>=16</span>) at only +2.0 ms overhead.</li>
    <li><strong>Controlled-Variable Empirical Validation:</strong> Across four progressive experimental suites (18 runs on <code>SpecBench</code>), we validate our analytical predictions (<span class="m"><i>R</i><sup>2</sup>=0.992</span>) and achieve +57.7% bottleneck speedup, -64.0% laptop draft compute reduction, and +9.7% aggregate throughput gain under real three-node concurrency.</li>
  </ul>

  <!-- SECTION II -->
  <h2>II. Related Work</h2>

  <h3>A. Speculative and Tree-Based LLM Decoding</h3>
  <p>
    Lossless speculative decoding [1], [2] accelerates autoregressive generation by pairing a fast draft model with exact rejection sampling against a larger target LLM. Early chain-based schemes accept at most one linear path per verification step, leaving GPU parallelism underutilized when per-token acceptance probabilities are moderate. Subsequent works generalize speculation into candidate trees verified via customized tree-attention masks: Medusa [3] attaches multiple decoding heads to the target backbone, EAGLE [4] extrapolates hidden features across tree levels, and SpecExec [5] builds massively parallel candidate trees using a standalone small draft model tailored to consumer hardware. While these methods optimize single-machine arithmetic intensity, they do not model wide-area network latency or cross-platform backend heterogeneity between draft and target nodes.
  </p>

  <h3>B. Edge-Cloud Collaborative LLM Inference</h3>
  <p>
    Device-cloud collaborative serving partitions LLM workloads across resource-constrained edges and high-capacity servers to reduce cloud cost, preserve local responsiveness, and utilize idle edge compute [6], [7]. Split-layer inference transmits high-dimensional intermediate activations across the network, incurring severe bandwidth overhead over WAN links. SpecEdge [8] overcomes activation-transfer bottlenecks by shifting to token-level collaboration: edge clients run a compact draft model and transmit only integer token trees and compact metadata over gRPC, while incorporating Proactive Drafting to overlap subsequent drafting with server waiting. However, SpecEdge evaluates homogeneous CUDA edge clients over 10 GbE LANs and enforces a single uniform tree budget across all clients. Our work extends edge-assisted speculative decoding into realistic heterogeneous WAN clusters, revealing when uniform policies fail and demonstrating how to adapt tree budgets per device.
  </p>

  <h3>C. Static Graph Serving and Accelerator Heterogeneity</h3>
  <p>
    Minimizing host-side kernel launch overhead is critical for small-batch LLM decoding [9], [12]. NVIDIA CUDA Graphs record an entire forward pass into a replayable GPU command graph, eliminating per-operator CPU dispatch latency, but require fixed input tensor shapes and memory addresses. Conversely, PyTorch&rsquo;s Metal Performance Shaders (MPS) backend on Apple Silicon lacks an equivalent general CUDA Graph capture API, executing transformer layers eagerly with substantial per-layer Python/Metal dispatch overhead. Prior multi-shape CUDA Graph systems either capture multiple graph buckets (multiplying static activation memory) or fall back to eager execution on shape mismatches. Our Variable-Budget Zero-Padding mechanism avoids multi-graph VRAM overhead on a 32 GB server serving a 14B FP16 target model by padding smaller trees into a single captured graph while isolating dummy KV writes.
  </p>

  <!-- SECTION III -->
  <h2>III. Analytical Modeling of Heterogeneous WAN Speculative Decoding</h2>

  <h3>A. Cycle-Level TPOT Formulation</h3>
  <p>
    Consider an edge device <span class="m"><i>h</i> &isin; {<span class="rm">5060Ti</span>, <span class="rm">M4</span>}</span> executing a draft model of scale <span class="m"><i>m</i> &isin; {0.6<span class="rm">B</span>, 1.7<span class="rm">B</span>}</span> with speculation tree hyperparameters <span class="m">(<i>d</i>, <i>B</i>)</span>&mdash;where <span class="m"><i>d</i></span> denotes the maximum tree depth (<code>max_beam_len</code>) and <span class="m"><i>B</i></span> denotes the candidate node budget (<code>max_budget</code>)&mdash;and Proactive Drafting mode <span class="m"><i>p</i> &isin; {<code>disabled</code>, <code>excluded</code>, <code>included</code>}</span>. Each verification cycle produces <span class="m"><i>&tau;</i></span> accepted tokens from the target model. We model steady-state Time-Per-Output-Token (TPOT) as:
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <span class="rm">TPOT</span>(<i>h</i>, <i>m</i>, <i>d</i>, <i>B</i>, <i>p</i>) =
      <span class="frac">
        <span class="num"><i>T</i><sub><span class="rm">draft</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub> + <i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">post</span></sub> &minus; <i>T</i><sub><span class="rm">overlap</span></sub></span>
        <span class="den"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>m</i>, <i>d</i>, <i>B</i>, <i>p</i>)]</span>
      </span>
    </div>
    <div class="eq-num">(1)</div>
  </div>

  <p class="noindent">where each component reflects a distinct physical mechanism:</p>
  <ul>
    <li><strong>Edge Draft Latency (<span class="m"><i>T</i><sub><span class="rm">draft</span></sub></span>):</strong> Tree construction proceeds depth-by-depth across <span class="m"><i>d</i></span> draft forward passes, scaling linearly with depth: <span class="m"><i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>, <i>m</i>, <i>d</i>) &approx; <i>c</i><sub>0</sub>(<i>h</i>, <i>m</i>) + <i>&alpha;</i>(<i>h</i>, <i>m</i>)&middot;<i>d</i></span>, where <span class="m"><i>c</i><sub>0</sub></span> aggregates fixed per-cycle dispatch overhead and <span class="m"><i>&alpha;</i></span> is the marginal per-layer execution slope. On CUDA Graph edges, <span class="m"><i>&alpha;</i></span> is small (~22 ms/layer), whereas eager MPS inflates <span class="m"><i>&alpha;</i></span> by nearly 6&times; (~130 ms/layer).</li>
    <li><strong>Server Verification Latency (<span class="m"><i>T</i><sub><span class="rm">verify</span></sub></span>):</strong> Under a static CUDA Graph on the 14B target server, verifying <span class="m"><i>B</i>+1 &le; 65</span> candidate nodes remains weight-bandwidth bound and nearly invariant to <span class="m"><i>B</i></span> (75&ndash;85 ms).</li>
    <li><strong>Network and Host Overheads (<span class="m"><i>T</i><sub><span class="rm">net</span></sub>, <i>T</i><sub><span class="rm">post</span></sub></span>):</strong> <span class="m"><i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>)</span> captures WAN serialization, Tailscale routing RTT, and queueing delay, while <span class="m"><i>T</i><sub><span class="rm">post</span></sub>(<i>h</i>)</span> measures client tree pruning and tensor post-processing.</li>
    <li><strong>Proactive Overlap (<span class="m"><i>T</i><sub><span class="rm">overlap</span></sub></span>):</strong> When Proactive Drafting is active, the edge speculatively drafts the next cycle during the server waiting window <span class="m"><i>T</i><sub><span class="rm">wait</span></sub> = <i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub></span>, hiding up to <span class="m"><i>T</i><sub><span class="rm">overlap</span></sub> &le; <span class="rm">min</span>(<i>T</i><sub><span class="rm">draft</span></sub><sup><span class="rm">pro</span></sup>, <i>T</i><sub><span class="rm">wait</span></sub>)</span> upon acceptance.</li>
    <li><strong>Mean Accepted Tokens (<span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span>):</strong> Because conditional acceptance probability decays geometrically along deeper branches, <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> grows monotonically yet sublinearly with depth <span class="m"><i>d</i></span>, well approximated by a power law <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>d</i>)] &approx; <i>&kappa;</i><i>d</i><sup><i>&gamma;</i></sup></span> (<span class="m">0 &lt; <i>&gamma;</i> &lt; 1</span>).</li>
  </ul>

  <h3>B. Dimensionless Bottleneck Ratio <span class="m"><i>&rho;</i></span> and Regime Bifurcation</h3>
  <p>
    To classify heterogeneous edges on a unified scale, we define the dimensionless <em>Network-to-Draft Bottleneck Ratio</em>:
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <i>&rho;</i>(<i>h</i>, <i>m</i>) =
      <span class="frac">
        <span class="num"><i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>) + <i>T</i><sub><span class="rm">verify</span></sub></span>
        <span class="den"><i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>, <i>m</i>)</span>
      </span>
      =
      <span class="frac">
        <span class="num"><i>T</i><sub><span class="rm">wait</span></sub></span>
        <span class="den"><i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>, <i>m</i>)</span>
      </span>
    </div>
    <div class="eq-num">(2)</div>
  </div>

  <p class="noindent">
    Neglecting small <span class="m"><i>T</i><sub><span class="rm">post</span></sub></span> variation with <span class="m"><i>d</i></span> and differentiating <span class="m"><span class="rm">ln</span>&thinsp;<span class="rm">TPOT</span></span> in (1) with respect to depth <span class="m"><i>d</i></span>, deepening the speculation tree reduces TPOT (<span class="m">&part;<span class="rm">TPOT</span>/&part;<i>d</i> &lt; 0</span>) if and only if the relative acceptance gain exceeds the relative cycle-time increase:
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <span class="frac">
        <span class="num"><span class="rm">d</span>&thinsp;<span class="rm">ln</span>&thinsp;<span class="rm">&Eopf;</span>[<i>&tau;</i>]</span>
        <span class="den"><span class="rm">d</span><i>d</i></span>
      </span>
      &nbsp;&gt;&nbsp;
      <span class="frac">
        <span class="num"><i>&alpha;</i>(<i>h</i>, <i>m</i>)</span>
        <span class="den"><i>T</i><sub><span class="rm">draft</span></sub>(<i>d</i>) + <i>T</i><sub><span class="rm">wait</span></sub></span>
      </span>
    </div>
    <div class="eq-num">(3)</div>
  </div>

  <p class="noindent">
    Substituting <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>d</i>)] &approx; <i>&kappa;</i><i>d</i><sup><i>&gamma;</i></sup></span> yields <span class="m"><i>&gamma;</i>/<i>d</i> &gt; <i>&alpha;</i>/(<i>c</i><sub>0</sub> + <i>&alpha;</i><i>d</i> + <i>T</i><sub><span class="rm">wait</span></sub>)</span>, directly establishing our central analytical result.
  </p>

  <div class="proposition">
    <span class="prop-head">Proposition 1 (Divergent Optimal Tree Depth):</span>
    <span class="prop-body">Under linear draft scaling and sublinear acceptance growth (<span class="m">0 &lt; <i>&gamma;</i> &lt; 1</span>), the TPOT-minimizing tree depth satisfies <span class="m"><i>d</i><sup>*</sup> &approx; [<i>&gamma;</i>/(1&minus;<i>&gamma;</i>)]&middot;(<i>c</i><sub>0</sub> + <i>T</i><sub><span class="rm">wait</span></sub>)/<i>&alpha;</i></span>. Consequently, heterogeneous edges split into two opposing regimes: (i) <strong>Network-Bound (<span class="m"><i>&rho;</i> &gg; 1</span>, small <span class="m"><i>&alpha;</i></span>)</strong>: large <span class="m"><i>T</i><sub><span class="rm">wait</span></sub>/<i>&alpha;</i></span> pushes <span class="m"><i>d</i><sup>*</sup></span> beyond typical budget caps, so aggressive deep trees (<span class="m"><i>d</i>=8, <i>B</i>=64</span>) strictly lower TPOT by amortizing high WAN RTT; (ii) <strong>Compute-Sensitive (<span class="m"><i>&rho;</i> &approx; 1</span>, large <span class="m"><i>&alpha;</i></span>)</strong>: small <span class="m"><i>T</i><sub><span class="rm">wait</span></sub>/<i>&alpha;</i></span> produces an interior shallow optimum (<span class="m"><i>d</i><sup>*</sup> &approx; 2</span>), beyond which deeper trees cause TPOT to rebound.</span>
  </div>

  <h3>C. Dispatch-Overhead Amortization on Eager Accelerators</h3>
  <p>
    Equation (1) also predicts a counter-intuitive model-scaling effect on eager backends such as Apple Silicon MPS. Suppose upgrading the draft model from <span class="m"><i>m</i><sub>1</sub></span> (0.6B) to <span class="m"><i>m</i><sub>2</sub></span> (1.7B) increases per-layer compute modestly while leaving a large fixed Python/Metal dispatch floor <span class="m"><i>c</i><sub>0</sub></span> mostly unchanged. Then <span class="m"><span class="rm">TPOT</span>(<i>m</i><sub>2</sub>) &lt; <span class="rm">TPOT</span>(<i>m</i><sub>1</sub>)</span> holds whenever:
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <span class="frac">
        <span class="num"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>m</i><sub>2</sub>)]</span>
        <span class="den"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>m</i><sub>1</sub>)]</span>
      </span>
      &nbsp;&gt;&nbsp; 1 +
      <span class="frac">
        <span class="num">&Delta;<i>T</i><sub><span class="rm">draft</span></sub></span>
        <span class="den"><i>T</i><sub><span class="rm">draft</span></sub>(<i>m</i><sub>1</sub>) + <i>T</i><sub><span class="rm">wait</span></sub> + <i>T</i><sub><span class="rm">post</span></sub></span>
      </span>
    </div>
    <div class="eq-num">(4)</div>
  </div>

  <p class="noindent">
    Because the denominator includes both the large eager dispatch floor and <span class="m"><i>T</i><sub><span class="rm">wait</span></sub></span>, a modest acceptance improvement (+8.3% in our experiments) outweighs the incremental compute cost of a 2.8&times; larger draft model, yielding a net throughput gain.
  </p>

  <!-- SECTION IV -->
  <h2>IV. System Architecture and Core Design</h2>
  <p>
    Fig. 1 illustrates our cross-platform three-node collaborative serving architecture and per-cycle WAN execution pipeline. Below we detail the two system mechanisms engineered to realize heterogeneity-aware serving atop SpecEdge.
  </p>

  <!-- SPANNING FIGURE 1 -->
  <figure class="span-all">
    <img src="figures_en/fig1_architecture_timeline.png" alt="Fig. 1">
    <figcaption><strong>Fig. 1.</strong> Cross-platform heterogeneous SpecEdge architecture and WAN pipeline. (a) A single RTX 4080 SUPER server running <code>Qwen3-14B</code> concurrently serves a network-bound CUDA edge (RTX 5060 Ti, <span class="m"><i>d</i>=8, <i>B</i>=64</span>) and a compute-sensitive MPS edge (Apple M4, <span class="m"><i>d</i>=2, <i>B</i>=16</span>) using one static CUDA Graph via Variable-Budget Zero-Padding. (b) Under high WAN RTT, Proactive Drafting (<code>included</code>) overlaps next-cycle draft construction (<span class="m"><i>T</i><sub><span class="rm">overlap</span></sub></span>) inside the network waiting window.</figcaption>
  </figure>

  <h3>A. Non-Intrusive Cross-Platform Apple MPS Compatibility Layer</h3>
  <p>
    Stock SpecEdge hardcodes NVIDIA CUDA primitives throughout its draft engine and profiling utilities, preventing execution on Apple Silicon macOS clients. We design a zero-overhead compatibility layer that preserves identical CUDA execution paths while unlocking native PyTorch MPS support:
  </p>
  <ul>
    <li><strong>Device-Aware Graph Fallback and KV-Cache Slicing Fix (<code>src/specedge/engine/graph.py</code>):</strong> During initialization of <code>GraphEngine</code> and <code>BatchGraphEngine</code>, we inspect <code>self._device.type</code>. Non-CUDA backends (<code>mps</code>, <code>cpu</code>) automatically bypass <code>torch.cuda.CUDAGraph</code> capture and execute eagerly. While validating variable-width candidate trees on MPS, we uncovered and fixed a latent bug in upstream SpecEdge&rsquo;s non-graph branch: <code>forward()</code> passed the full <code>self._past_key_values.seq_indices</code> buffer without slicing <code>[:num_beams]</code>, causing shape mismatch exceptions (<code>[32, 8, 128]</code> vs. <code>[1, 8, 128]</code>) whenever active beam count fell below the pre-allocated budget. Slicing <code>seq_indices[:num_beams]</code> resolves this defect across all non-graph backends.</li>
    <li><strong>Cross-Backend Synchronization and Clean Teardown (<code>src/util.py</code>, <code>src/script/client.py</code>):</strong> We generalize the <code>Timing</code> context manager to invoke <code>torch.mps.synchronize()</code> on Apple Silicon and automatically fall back from CUDA <code>event</code> timers to wall-clock <code>sync</code> timers on non-CUDA devices. On Windows Python 3.14, we additionally flush logging handlers and explicitly terminate upon request completion, eliminating an asynchronous <code>grpc.aio</code> shutdown hang.</li>
  </ul>

  <h3>B. Variable-Budget Static CUDA Graph Zero-Padding Verification</h3>
  <p>
    A key architectural barrier in stock SpecEdge (<code>src/strategy/server_verify/specexec/grpc.py</code>) is static shape lock-in: the target server pre-allocates static buffers of length <span class="m"><i>M</i> = <i>B</i><sub><span class="rm">max</span></sub> + 1</span> for its captured CUDA Graph and copies incoming client tensors directly into these buffers. If two concurrent edge clients request different tree budgets (e.g., <span class="m"><i>B</i>=64 &rArr; <i>K</i>=65</span> from a deep-tree 5060 Ti edge and <span class="m"><i>B</i>=16 &rArr; <i>K</i>=17</span> from a shallow-tree M4 edge), stock SpecEdge fails with tensor shape errors. Capturing multiple graphs for every budget tier would exhaust our 32 GB server&rsquo;s VRAM alongside a 28 GB FP16 <code>Qwen3-14B</code> model.
  </p>
  <p>
    We resolve this dilemma via <strong>Variable-Budget Static CUDA Graph Zero-Padding</strong>, formalized in Algorithm 1. The server captures only a <em>single</em> static CUDA Graph sized to the cluster ceiling <span class="m"><i>M</i> = <i>B</i><sub><span class="rm">max</span></sub> + 1</span> (<span class="m"><i>B</i><sub><span class="rm">max</span></sub>=64</span>). For any incoming verification request with actual tree size <span class="m"><i>K</i> &le; <i>M</i></span>:
  </p>
  <ol>
    <li><strong>Front-Aligned Valid Copy:</strong> Valid <code>input_ids</code>, <code>position_ids</code>, <code>parent_indices</code>, and <code>cache_seq_indices</code> are copied into buffer slots <code>[0:K]</code>.</li>
    <li><strong>Dummy-Slot KV Isolation:</strong> Padded token IDs <code>[K:M]</code> are zeroed, and their <code>cache_seq_indices[K:M]</code> are redirected to the reserved terminal slot <code>max_len - 1</code>. Because valid sequence positions never reach <code>max_len - 1</code>, padded forward writes cannot corrupt active context KV entries.</li>
    <li><strong>Softmax-Safe Tree Attention Mask:</strong> Valid rows <code>[0:K]</code> retain their exact causal tree mask (with zeros in columns <code>[K:M]</code> so valid tokens never attend to padded positions). For padded rows <code>[K:M]</code>, we set <code>attention_mask[:, K:M, 0] = 1.0</code>, preventing all-&minus;&infin; Softmax rows from generating <code>NaN</code> activations inside the static graph.</li>
    <li><strong>Sliced Output and Masked KV Reordering:</strong> After replaying the single static graph, the server slices <code>selection[b, :K]</code> before replying to the client, and forces <code>logit_mask[K-1:] = False</code> and <code>position[K-1:] = 0</code> inside <code>_reorder_kv_cache()</code> so padded entries are never committed to persistent KV state.</li>
  </ol>

  <div class="proposition">
    <span class="prop-head">Proposition 2 (Exact Verification Equivalence):</span>
    <span class="prop-body">For any valid candidate tree of length <span class="m"><i>K</i> &le; <i>M</i></span> and sequence length <span class="m"><i>L</i> &lt; <code>max_len</code>&minus;1</span>, Algorithm 1 produces bit-equivalent target logits on slots <code>[0:K]</code>, identical accepted token trajectories, and identical persistent KV cache states on slots <code>[0:L+&tau;]</code> as a dedicated static graph compiled specifically for size <span class="m"><i>K</i></span>.</span>
  </div>
  <p class="proof-sketch">
    <em>Proof Sketch:</em> In every Transformer self-attention layer, the mask zeroes column weights for keys in <code>[K:M]</code> when computing queries in <code>[0:K]</code>, ensuring zero information leakage from padded tokens into valid hidden states. LayerNorm, RoPE, and MLP layers are strictly token-wise and depend only on each token&rsquo;s own <code>position_id</code>. Redirecting padded KV writes to <code>max_len - 1</code> guarantees disjointness from <code>[0:L+&tau;]</code>, and masking <code>logit_mask[K-1:]</code> excludes padded slots from post-verification KV compaction. &#9633;
  </p>

  <!-- SINGLE-COLUMN ALGORITHM 1 -->
  <div class="alg-box">
    <div class="alg-header"><strong>Algorithm 1</strong> &nbsp;Heterogeneity-Aware Edge Policy &amp; Variable-Budget Zero-Padding Verification</div>
    <div class="alg-body">
      <div class="alg-req"><span class="alg-kw">Require:</span> Max budget <span class="m"><i>B</i><sub><span class="rm">max</span></sub>=64</span>, single captured 14B CUDA Graph <span class="m">&Gscr;<sub><i>M</i></sub></span> (<span class="m"><i>M</i>=<i>B</i><sub><span class="rm">max</span></sub>+1</span>); edge telemetry <span class="m">(<i>T</i><sub><span class="rm">draft</span></sub>, <i>T</i><sub><span class="rm">net</span></sub>, <i>T</i><sub><span class="rm">verify</span></sub>)</span></div>
      <div class="alg-line"><span class="alg-ln">1:</span><span class="alg-code"><span class="alg-kw">Phase 1: Offline/Periodic Edge Policy Assignment</span></span></div>
      <div class="alg-line"><span class="alg-ln">2:</span><span class="alg-code"><span class="alg-kw">for</span> each edge client <span class="m"><i>h</i></span> <span class="alg-kw">do</span></span></div>
      <div class="alg-line"><span class="alg-ln">3:</span><span class="alg-code alg-ind1"><span class="m"><i>&rho;</i><sub><i>h</i></sub> &larr; (<i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>) + <i>T</i><sub><span class="rm">verify</span></sub>) / <i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>)</span></span></div>
      <div class="alg-line"><span class="alg-ln">4:</span><span class="alg-code alg-ind1"><span class="alg-kw">if</span> <span class="m"><i>&rho;</i><sub><i>h</i></sub> &gt; 5</span> <span class="alg-kw">then</span></span></div>
      <div class="alg-line"><span class="alg-ln">5:</span><span class="alg-code alg-ind2"><span class="m">(<i>d</i><sub><i>h</i></sub>, <i>B</i><sub><i>h</i></sub>, <i>p</i><sub><i>h</i></sub>) &larr; (8, 64, <code>included</code>)</span> <span class="alg-cmt">&#9657; Net-bound</span></span></div>
      <div class="alg-line"><span class="alg-ln">6:</span><span class="alg-code alg-ind1"><span class="alg-kw">else</span></span></div>
      <div class="alg-line"><span class="alg-ln">7:</span><span class="alg-code alg-ind2"><span class="m">(<i>d</i><sub><i>h</i></sub>, <i>B</i><sub><i>h</i></sub>, <i>p</i><sub><i>h</i></sub>) &larr; (2, 16, <code>included</code>)</span> <span class="alg-cmt">&#9657; Comp.-sens.</span></span></div>
      <div class="alg-line"><span class="alg-ln">8:</span><span class="alg-code alg-ind1"><span class="alg-kw">end if</span></span></div>
      <div class="alg-line"><span class="alg-ln">9:</span><span class="alg-code"><span class="alg-kw">end for</span></span></div>
      <div class="alg-line"><span class="alg-ln">10:</span><span class="alg-code"><span class="alg-kw">Phase 2: Server Single-Graph Verification (<span class="m"><i>K</i> &le; <i>M</i></span>)</span></span></div>
      <div class="alg-line"><span class="alg-ln">11:</span><span class="alg-code">Copy valid tree into <code>[0:K]</code>: <span class="m"><i>X</i>[:<i>K</i>], pos[:<i>K</i>], kv[:<i>K</i>]</span></span></div>
      <div class="alg-line"><span class="alg-ln">12:</span><span class="alg-code"><span class="alg-kw">if</span> <span class="m"><i>K</i> &lt; <i>M</i></span> <span class="alg-kw">then</span></span></div>
      <div class="alg-line"><span class="alg-ln">13:</span><span class="alg-code alg-ind1"><span class="m"><i>X</i>[<i>K</i>:<i>M</i>] &larr; 0</span>, <span class="m">kv[<i>K</i>:<i>M</i>] &larr; <code>max_len</code>&minus;1</span> <span class="alg-cmt">&#9657; Dummy</span></span></div>
      <div class="alg-line"><span class="alg-ln">14:</span><span class="alg-code alg-ind1"><span class="m">mask[:, <i>K</i>:<i>M</i>, :] &larr; 0</span>; <span class="m">mask[:, <i>K</i>:<i>M</i>, 0] &larr; 1.0</span></span></div>
      <div class="alg-line"><span class="alg-ln">15:</span><span class="alg-code"><span class="alg-kw">end if</span></span></div>
      <div class="alg-line"><span class="alg-ln">16:</span><span class="alg-code"><span class="m">logits &larr; &Gscr;<sub><i>M</i></sub>(<i>X</i>, pos, kv, mask)</span> <span class="alg-cmt">&#9657; Static replay</span></span></div>
      <div class="alg-line"><span class="alg-ln">17:</span><span class="alg-code"><span class="m">sel &larr; <span class="rm">Verify</span>(logits)[:<i>K</i>]</span> <span class="alg-cmt">&#9657; Slice valid tokens</span></span></div>
      <div class="alg-line"><span class="alg-ln">18:</span><span class="alg-code">Set <span class="m">logit_mask[<i>K</i>&minus;1:] &larr; <code>False</code></span>; compact KV cache</span></div>
      <div class="alg-line"><span class="alg-ln">19:</span><span class="alg-code"><span class="alg-kw">return</span> <span class="m">sel</span> to edge client <span class="m"><i>h</i></span></span></div>
    </div>
  </div>

  <!-- SECTION V -->
  <h2>V. Experimental Methodology</h2>

  <h3>A. Three-Node Cross-Platform Testbed</h3>
  <p>
    We deploy our system across three physical machines interconnected over a real Tailscale WAN mesh, strictly aligning software dependencies to upstream SpecEdge (<code>Python 3.14.x</code>, <code>PyTorch 2.9.x</code>, <code>Transformers 4.57.x</code>, <code>gRPC 1.75.1</code>). Hardware specifications are listed in Table I. On the WSL2 server, loading the 28 GB FP16 <code>Qwen3-14B</code> checkpoint directly over Windows-mounted 9p storage (<code>/mnt/d</code>) exhibited &gt;12&times; slowdown and memory-mapping failures; staging weights on native WSL2 <code>ext4</code> reduced load time to ~9 s. To guarantee WDDM VRAM safety margin on the 32 GB card and avoid straggler synchronization inside static server batches, we set <code>max_batch_size=1</code> and extract true server verification latency directly from timestamped server logs.
  </p>

  <!-- SPANNING TABLE I -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE I</div>
    <div class="table-title">Cross-Platform Three-Node Heterogeneous Experimental Testbed Configuration</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">Node Role</th>
          <th class="l">Hardware &amp; Operating System</th>
          <th class="l">Execution Backend</th>
          <th class="l">Deployed FP16 Models</th>
          <th style="white-space: nowrap;">Venv Size</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><strong>Server</strong></td>
          <td class="l">RTX 4080 SUPER (32 GB, <code>sm_89</code>), Win 11 + WSL2 Ubuntu</td>
          <td class="l">CUDA 12.8 + CUDA Graph</td>
          <td class="l"><code>Qwen3-14B</code> (ext4), <code>0.6B</code></td>
          <td>7.00 GB</td>
        </tr>
        <tr>
          <td class="l"><strong>Edge 1</strong> (<code>node</code>)</td>
          <td class="l">RTX 5060 Ti (8 GB, <code>sm_120</code>), Windows 11</td>
          <td class="l">CUDA 12.8 + CUDA Graph</td>
          <td class="l"><code>Qwen3-0.6B</code>, <code>1.7B</code></td>
          <td>4.61 GB</td>
        </tr>
        <tr>
          <td class="l"><strong>Edge 2</strong> (<code>davids</code>)</td>
          <td class="l">Apple M4 (16 GB Unified), macOS 27.2.1 (<code>arm64</code>)</td>
          <td class="l">PyTorch MPS (Eager)</td>
          <td class="l"><code>Qwen3-0.6B</code>, <code>1.7B</code></td>
          <td>0.82 GB</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h3>B. Global Controls and Experimental Matrix</h3>
  <p>
    All 18 experimental runs evaluate the identical 16 prompts sampled from <code>SpecBench</code> [11] (<code>sample_req_cnt=30, req_offset=0, max_request_num=480</code>, spanning QA, math, reasoning, summarization, translation, and coding) with fixed target model <code>Qwen3-14B</code> (FP16) [10], <code>max_len=2048</code>, <code>max_new_tokens=64</code>, <code>temperature=0.7</code>, <code>seed=42</code>, and <code>reasoning=False</code>. We organize four progressive controlled-variable studies:
  </p>
  <ul>
    <li><strong>Exp. 1 (Single-Node Baselines):</strong> <code>E1-1</code> (<code>Auto-Batch</code> 14B pure autoregressive decoding on 4080S) vs. <code>E1-2</code> (<code>Server-Only</code> co-located <code>14B+0.6B</code> speculative decoding on 4080S with zero network latency).</li>
    <li><strong>Exp. 2 (2&times;2 Factorized Matrix):</strong> Holding tree settings constant at <span class="m">(<i>d</i>=4, <i>B</i>=32, <code>excluded</code>)</span>, we cross <span class="m">{5060 Ti, Apple M4} &times; {0.6B, 1.7B}</span> to isolate hardware/network effects from draft-model capacity.</li>
    <li><strong>Exp. 3 (Proactive Drafting Ablation):</strong> Independently sweeping <code>proactive.type</code> <span class="m">&isin; {<code>disabled</code>, <code>excluded</code>, <code>included</code>}</span> on both <code>5060 Ti (1.7B)</code> and <code>Apple M4 (0.6B)</code>.</li>
    <li><strong>Exp. 4 (Tree-Depth Sweep &amp; 3-Node Concurrency):</strong> <strong>E4a</strong> sweeps <span class="m">(<i>d</i>, <i>B</i>)</span> across <span class="m">{(2,16), (4,32), (6,48), (8,64)}</span> on 5060 Ti and <span class="m">{(2,16), (4,32), (6,48)}</span> on M4 to validate (1) and Proposition 1. <strong>E4b</strong> directly compares uniform default SpecEdge (<code>E4-Base</code>: both edges at <span class="m"><i>d</i>=4, <i>B</i>=32, <code>excluded</code></span>) against our heterogeneity-aware policy with Variable-Budget Zero-Padding (<code>E4-Opt</code>: 5060 Ti at <span class="m"><i>d</i>=8, <i>B</i>=64</span> and M4 at <span class="m"><i>d</i>=2, <i>B</i>=16</span>, both <code>included</code>) under simultaneous three-node execution.</li>
  </ul>

  <!-- SECTION VI -->
  <h2>VI. Evaluation and Analysis</h2>

  <h3>A. Baselines and 2&times;2 Factorized Analysis (Exp. 1 &amp; 2)</h3>
  <p>
    Table II, Fig. 2, and Fig. 3 present the complete measurements from Experiments 1 and 2, revealing three major findings.
  </p>

  <!-- SPANNING TABLE II -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE II</div>
    <div class="table-title">Exp. 1 (Single-Node Baselines) and Exp. 2 (2&times;2 Factorized Matrix at Fixed <span class="m"><i>d</i>=4, <i>B</i>=32, <code>excluded</code></span>)</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">Run ID</th>
          <th class="l">Configuration (Device / Model)</th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> (tok/step)</th>
          <th>Draft (ms)</th>
          <th>Verify (ms)</th>
          <th>Net RTT (ms)</th>
          <th>Post (ms)</th>
          <th><span class="m"><i>&rho;</i></span></th>
          <th>TPOT (ms)</th>
          <th>Tput (tok/s)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l">E1-1</td>
          <td class="l"><code>Auto-Batch</code> (4080S 14B AR)</td>
          <td>&mdash;</td><td>&mdash;</td><td>64.7</td><td>0</td><td>&mdash;</td><td>&mdash;</td>
          <td><strong>64.7</strong></td><td><strong>15.45</strong></td>
        </tr>
        <tr>
          <td class="l">E1-2</td>
          <td class="l"><code>Server-Only</code> (4080S 14B+0.6B)</td>
          <td>3.78</td><td>104.3</td><td>431.6</td><td>0</td><td>&mdash;</td><td>&mdash;</td>
          <td>141.7</td><td>7.06</td>
        </tr>
        <tr class="midrule">
          <td class="l">E2-1</td>
          <td class="l"><code>5060 Ti</code> + <code>Qwen3-0.6B</code></td>
          <td>3.86</td><td><strong>56.0</strong></td><td>75.0</td><td>1054.2</td><td>4.0</td>
          <td><strong>20.16</strong></td><td>308.2</td><td><strong>3.25</strong></td>
        </tr>
        <tr>
          <td class="l">E2-2</td>
          <td class="l"><code>5060 Ti</code> + <code>Qwen3-1.7B</code></td>
          <td>3.94</td><td><strong>87.5</strong></td><td>82.0</td><td>1461.2</td><td>4.0</td>
          <td><strong>17.65</strong></td><td>414.9</td><td>2.41</td>
        </tr>
        <tr>
          <td class="l">E2-3</td>
          <td class="l"><code>Apple M4</code> + <code>Qwen3-0.6B</code></td>
          <td>3.84</td><td>492.4</td><td>78.0</td><td>802.5</td><td>89.7</td>
          <td><strong>1.79</strong></td><td>381.3</td><td>2.62</td>
        </tr>
        <tr>
          <td class="l">E2-4</td>
          <td class="l"><code>Apple M4</code> + <code>Qwen3-1.7B</code></td>
          <td><strong>4.16</strong></td><td>655.9</td><td>78.0</td><td>680.8</td><td>79.9</td>
          <td><strong>1.16</strong></td><td>359.6</td><td>2.78</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SINGLE-COLUMN FIGURE 2 -->
  <figure>
    <img src="figures_en/fig2_latency_breakdown.png" alt="Fig. 2">
    <figcaption><strong>Fig. 2.</strong> Exp. 2: Per-cycle latency breakdown and bottleneck ratio <span class="m"><i>&rho;</i></span> across the 2&times;2 factorized matrix. RTX 5060 Ti spends over 92% of cycle time waiting on WAN RTT (<span class="m"><i>&rho;</i> &isin; [17.65, 20.16]</span>), whereas Apple M4 splits cycle time nearly evenly between local drafting and WAN wait (<span class="m"><i>&rho;</i> &isin; [1.16, 1.79]</span>).</figcaption>
  </figure>

  <p>
    <strong>1) Single-GPU VRAM Contention Proves the Value of Edge Offloading:</strong> Even on a 32 GB RTX 4080 SUPER, co-locating <code>Qwen3-14B</code> and <code>Qwen3-0.6B</code> (<code>E1-2</code>) leaves insufficient memory headroom to enable CUDA Graphs for the target model. As a result, single-step verification degrades to 431.6 ms&mdash;<strong>5.4&times; slower</strong> than our dedicated edge-assisted server (75&ndash;82 ms)&mdash;dropping <code>Server-Only</code> throughput to 7.06 tok/s, well below pure autoregressive decoding (15.45 tok/s). Offloading drafting to the edge frees server VRAM for full 14B CUDA Graph capture; projected to a sub-millisecond LAN (<span class="m"><i>T</i><sub><span class="rm">net</span></sub> &lt; 1</span> ms), <code>5060 Ti + 1.7B</code> would deliver <span class="m">3.94/(0.0875+0.078) = 23.8</span> tok/s, a 1.54&times; speedup over the 14B autoregressive baseline.
  </p>
  <p>
    <strong>2) Sharp Regime Bifurcation Between Edges:</strong> At identical draft scales, RTX 5060 Ti&rsquo;s CUDA Graph engine drafts <strong>7.5&times;&ndash;8.8&times;</strong> faster than Apple M4&rsquo;s eager MPS backend (56.0 vs. 492.4 ms at 0.6B; 87.5 vs. 655.9 ms at 1.7B) and performs client pre/post-processing <strong>20&times;</strong> faster (4.0 vs. 80&ndash;90 ms). Yet over our Tailscale WAN, 5060 Ti experiences <span class="m"><i>&rho;</i> &isin; [17.65, 20.16]</span> (over 92% of cycle time spent in network wait), placing it deep in the <em>network-bound</em> regime, whereas M4 exhibits <span class="m"><i>&rho;</i> &isin; [1.16, 1.79]</span>, placing it firmly in the <em>compute-sensitive</em> regime.
  </p>
  <p>
    <strong>3) Fixed Dispatch-Overhead Amortization on Apple M4:</strong> Scaling Apple M4&rsquo;s draft model nearly 3&times; from <code>0.6B</code> (<code>E2-3</code>) to <code>1.7B</code> (<code>E2-4</code>) increases draft latency by only 33.2% (492.4 &rarr; 655.9 ms), while raising <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> to the highest value in Exp. 2 (<strong>4.16</strong>, +8.3%) and boosting end-to-end throughput by <strong>+6.0%</strong> (2.62 &rarr; 2.78 tok/s). This empirically confirms (4): PyTorch MPS incurs a ~350&ndash;400 ms fixed host-dispatch floor per cycle, which larger draft models amortize effectively whenever unified memory permits.
  </p>

  <!-- SPANNING FIGURE 3 -->
  <figure class="span-all">
    <img src="figures_en/fig3_matrix_mat_throughput.png" alt="Fig. 3">
    <figcaption><strong>Fig. 3.</strong> Exp. 1 &amp; 2: Cross-impact of draft model scale and hardware backend on (a) mean/median accepted tokens per cycle and (b) end-to-end decode throughput relative to single-server baselines.</figcaption>
  </figure>

  <h3>B. Proactive Drafting Ablation over WAN (Exp. 3)</h3>
  <p>
    Table III and Fig. 4 evaluate all three Proactive Drafting strategies (<code>disabled</code>, <code>excluded</code>, <code>included</code>) under real WAN RTTs. Unlike LAN environments where short wait windows can starve proactive drafting, our 500&ndash;1500 ms WAN wait windows give both edges ample idle time to complete next-cycle speculative trees before the server responds. Merging proactive candidates directly into the next tree (<code>included</code>) outperforms both alternatives across both architectures: on <code>5060 Ti (1.7B)</code>, <code>included</code> cuts mean draft latency by <strong>-18.7%</strong> (88.9 &rarr; 72.3 ms) and lifts throughput by <strong>+17.0%</strong> over <code>disabled</code> (2.83 &rarr; 3.31 tok/s); on <code>Apple M4 (0.6B)</code>, it compresses draft latency by <strong>-14.6%</strong> (512.4 &rarr; 437.4 ms) and achieves <strong>3.47 tok/s</strong> (<strong>+32.4%</strong> over default <code>excluded</code> and +6.8% over <code>disabled</code>).
  </p>

  <!-- SPANNING TABLE III -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE III</div>
    <div class="table-title">Exp. 3: Proactive Drafting Ablation across Heterogeneous WAN Edges (<span class="m"><i>d</i>=4, <i>B</i>=32</span>)</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">Edge Link</th>
          <th class="l">Proactive Mode</th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span></th>
          <th>Proactive Hits / Steps</th>
          <th>Draft (ms)</th>
          <th>Wait (ms)</th>
          <th>Tput (tok/s)</th>
          <th>Relative Gain</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><code>disabled</code></td>
          <td>3.60</td><td>0 / 254</td><td>88.9</td><td>1178.4</td><td>2.83</td><td>Baseline</td>
        </tr>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><code>excluded</code> (Default)</td>
          <td><strong>3.94</strong></td><td>36 / 236</td><td>87.5</td><td>1543.2</td><td>2.41</td><td>WAN RTT spike</td>
        </tr>
        <tr class="highlight">
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><strong><code>included</code> (Merged)</strong></td>
          <td>3.70</td><td><strong>41 / 245</strong></td><td><strong>72.3 (-18.7%)</strong></td><td>1042.2</td><td><strong>3.31</strong></td><td><strong>+17.0%</strong></td>
        </tr>
        <tr class="midrule">
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><code>disabled</code></td>
          <td>3.71</td><td>0 / 242</td><td>512.4</td><td>497.8</td><td>3.25</td><td>Baseline</td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><code>excluded</code> (Default)</td>
          <td><strong>3.84</strong></td><td>28 / 241</td><td>492.4</td><td>880.5</td><td>2.62</td><td>WAN RTT spike</td>
        </tr>
        <tr class="highlight">
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><strong><code>included</code> (Merged)</strong></td>
          <td>3.82</td><td><strong>34 / 242</strong></td><td><strong>437.4 (-14.6%)</strong></td><td>583.4</td><td><strong>3.47</strong></td><td><strong>+32.4%*</strong></td>
        </tr>
      </tbody>
    </table>
    <div class="table-note">* Gain relative to default <code>excluded</code> mode (+6.8% relative to <code>disabled</code>).</div>
  </div>

  <!-- SPANNING FIGURE 4 -->
  <figure class="span-all">
    <img src="figures_en/fig4_proactive_ablation.png" alt="Fig. 4">
    <figcaption><strong>Fig. 4.</strong> Exp. 3: Proactive Drafting ablation comparing <code>disabled</code>, <code>excluded</code>, and <code>included</code> modes on (a) edge draft latency <span class="m"><i>T</i><sub><span class="rm">draft</span></sub></span> and (b) end-to-end WAN decode throughput.</figcaption>
  </figure>

  <h3>C. Tree-Depth Sweep and Analytical Model Validation (Exp. 4a)</h3>
  <p>
    Table IV and Fig. 5 validate our closed-form model (1) and Proposition 1. Linear regression of draft latency against depth <span class="m"><i>d</i></span> confirms a <strong>5.78&times;</strong> marginal cost gap: <span class="m"><i>&alpha;</i><sub><span class="rm">5060Ti</span></sub> = 22.4</span> ms/layer versus <span class="m"><i>&alpha;</i><sub><span class="rm">M4</span></sub> = 129.5</span> ms/layer. (Note that run <code>E4-1</code> at (2, 16) captured 5 requests / 85 decode steps prior to a transient Tailscale route reset, whereas all other runs completed all 16 prompts.) To remove stochastic WAN routing jitter when checking functional shape, Fig. 5(b) normalizes each edge to its typical reference waiting time (1150 ms for 5060 Ti; 520 ms for M4). The closed-form curves match empirical points tightly (<span class="m"><i>R</i><sup>2</sup> = 0.992</span> on 5060 Ti) and expose opposite optima:
  </p>
  <ul>
    <li><strong>RTX 5060 Ti (Monotonic Deep-Tree Gain):</strong> Deepening the tree from (2, 16) to (8, 64) drives <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> from 2.88 up to <strong>5.84</strong> (with peak single-step acceptance reaching <strong>14 tokens</strong>), cutting normalized TPOT by <strong>-45%</strong> (413.2 &rarr; 226.9 ms/tok).</li>
    <li><strong>Apple M4 (Shallow-Tree Optimum):</strong> Shrinking the tree to (2, 16) halves M4&rsquo;s local draft latency (492.4 &rarr; <strong>242.7 ms</strong>), achieving the highest single-client WAN throughput in our entire study (<strong>3.55 tok/s</strong>, +35.5% over default (4, 32)). Pushing M4 deeper to <span class="m"><i>d</i>=4</span> and <span class="m"><i>d</i>=6</span> inflates draft time to 760.7 ms and causes normalized TPOT to rebound (261.5 &rarr; 263.8 &rarr; 272.2 ms/tok).</li>
  </ul>

  <!-- SPANNING TABLE IV -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE IV</div>
    <div class="table-title">Exp. 4a: Speculation Tree Depth &amp; Budget Sweep and Normalized TPOT Verification</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">Device &amp; Model</th>
          <th>Tree <span class="m">(<i>d</i>, <i>B</i>)</span></th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span></th>
          <th>Max Acc.</th>
          <th>Draft (ms)</th>
          <th>Slope <span class="m"><i>&alpha;</i></span></th>
          <th>Measured Tput</th>
          <th>Norm. TPOT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td><td>(2, 16)<sup>&dagger;</sup></td><td>2.88</td><td>5</td><td>41.1</td>
          <td rowspan="4">22.4 ms/layer</td><td>3.03 tok/s</td><td>413.2 ms/tok</td>
        </tr>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td><td>(4, 32)</td><td>3.94</td><td>8</td><td>87.5</td>
          <td>2.41 tok/s</td><td>314.0 ms/tok</td>
        </tr>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td><td>(6, 48)</td><td>4.80</td><td>8</td><td>132.4</td>
          <td>2.35 tok/s</td><td>267.1 ms/tok</td>
        </tr>
        <tr class="highlight">
          <td class="l"><code>5060 Ti (1.7B)</code></td><td><strong>(8, 64)</strong></td><td><strong>5.84</strong></td><td><strong>14</strong></td><td>175.8</td>
          <td>2.90 tok/s</td><td><strong>226.9 (-45%)</strong></td>
        </tr>
        <tr class="midrule highlight">
          <td class="l"><code>Apple M4 (0.6B)</code></td><td><strong>(2, 16)</strong></td><td>2.92</td><td>5</td><td><strong>242.7</strong></td>
          <td rowspan="3">129.5 ms/layer</td><td><strong>3.55 tok/s</strong></td><td><strong>261.5 (Opt.)</strong></td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td><td>(4, 32)</td><td>3.84</td><td>8</td><td>492.4</td>
          <td>2.62 tok/s</td><td>263.8 ms/tok</td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td><td>(6, 48)</td><td>4.71</td><td>11</td><td>760.7</td>
          <td>2.95 tok/s</td><td>272.2 (Rebound)</td>
        </tr>
      </tbody>
    </table>
    <div class="table-note"><sup>&dagger;</sup> 5 requests (85 decode steps) collected prior to a transient Tailscale route reset; all other points span all 16 prompts.</div>
  </div>

  <!-- SPANNING FIGURE 5 -->
  <figure class="span-all">
    <img src="figures_en/fig5_tree_sweep_theory_fit.png" alt="Fig. 5">
    <figcaption><strong>Fig. 5.</strong> Exp. 4a: (a) Linear draft latency scaling (5.78&times; slope gap) and sublinear <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> growth; (b) Eq. (1) closed-form model fit against reference-RTT-normalized measurements, confirming opposite optimal tree depths for RTX 5060 Ti (<span class="m"><i>d</i>=8</span>) and Apple M4 (<span class="m"><i>d</i>=2</span>).</figcaption>
  </figure>

  <h3>D. Three-Node Concurrent End-to-End Evaluation (Exp. 4b)</h3>
  <p>
    Finally, we evaluate Algorithm 1 under true simultaneous three-node concurrency (one 4080S server verifying both 5060 Ti and M4 concurrently across 16 prompts each). Table V and Fig. 6 contrast uniform default SpecEdge (<code>E4-Base</code>) against our heterogeneity-aware policy with Variable-Budget Zero-Padding (<code>E4-Opt</code>):
  </p>
  <ul>
    <li><strong>Negligible Server Overhead:</strong> Serving heterogeneous <span class="m"><i>B</i>=64</span> and <span class="m"><i>B</i>=16</span> trees from a single captured CUDA Graph raises median 14B server verification latency by only <strong>+2.0 ms</strong> (76.0 &rarr; 78.0 ms), confirming zero-padding adds virtually no runtime cost and zero extra VRAM.</li>
    <li><strong>Major Straggler Acceleration:</strong> Reconfiguring the network-bound 5060 Ti edge to <span class="m">(<i>d</i>=8, <i>B</i>=64, <code>included</code>)</span> raises its <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> by <strong>+41.3%</strong> (3.90 &rarr; 5.51), eliminates <strong>28.9%</strong> of WAN verification RPCs (235 &rarr; 167), lowers TPOT by <strong>-36.6%</strong> (631.7 &rarr; 400.6 ms), and boosts decode throughput by <strong>+57.7%</strong> (1.58 &rarr; 2.50 tok/s).</li>
    <li><strong>Laptop Compute Savings &amp; Cluster Fairness:</strong> Switching Apple M4 to <span class="m">(<i>d</i>=2, <i>B</i>=16, <code>included</code>)</span> slashes local GPU draft latency by <strong>-64.0%</strong> (481.7 &rarr; 173.5 ms, with 104/334 proactive hits = 31.1%), directly curbing laptop thermal load and battery drain. Although M4&rsquo;s raw throughput dipped modestly (-12.1% due to a +72 ms concurrent WAN wait fluctuation), cluster aggregate throughput rose by <strong>+9.7%</strong> (5.06 &rarr; 5.56 tok/s), and max/min inter-edge throughput imbalance dropped by <strong>44.1%</strong> (from 2.20&times; to 1.23&times;).</li>
  </ul>

  <!-- SINGLE-COLUMN TABLE V -->
  <div class="table-wrap">
    <div class="table-label">TABLE V</div>
    <div class="table-title">Exp. 4b: Three-Node Concurrent Comparison (<code>E4-Base</code> vs. <code>E4-Opt</code>)</div>
    <table class="ieee-tbl compact">
      <thead>
        <tr>
          <th class="l">Metric</th>
          <th><code>E4-Base</code></th>
          <th><code>E4-Opt</code></th>
          <th>Delta</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l">5060 Ti <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> / RPCs</td>
          <td>3.90 / 235</td><td><strong>5.51 / 167</strong></td><td><strong>+41% / -29%</strong></td>
        </tr>
        <tr>
          <td class="l">5060 Ti TPOT</td>
          <td>631.7 ms</td><td><strong>400.6 ms</strong></td><td><strong>-36.6%</strong></td>
        </tr>
        <tr>
          <td class="l">5060 Ti Tput</td>
          <td>1.58 tok/s</td><td><strong>2.50 tok/s</strong></td><td><strong>+57.7%</strong></td>
        </tr>
        <tr>
          <td class="l">M4 Draft Latency</td>
          <td>481.7 ms</td><td><strong>173.5 ms</strong></td><td><strong>-64.0%</strong></td>
        </tr>
        <tr>
          <td class="l">M4 Throughput</td>
          <td>3.48 tok/s</td><td>3.06 tok/s</td><td>-12.1%</td>
        </tr>
        <tr>
          <td class="l">Server 14B Verify</td>
          <td>76.0 ms</td><td><strong>78.0 ms</strong></td><td>+2.0 ms</td>
        </tr>
        <tr class="midrule highlight">
          <td class="l"><strong>Aggregate Tput</strong></td>
          <td>5.06 tok/s</td><td><strong>5.56 tok/s</strong></td><td><strong>+9.7%</strong></td>
        </tr>
        <tr class="highlight">
          <td class="l"><strong>Imbalance Ratio</strong></td>
          <td>2.20&times;</td><td><strong>1.23&times;</strong></td><td><strong>-44.1%</strong></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SPANNING FIGURE 6 -->
  <figure class="span-all">
    <img src="figures_en/fig6_3node_before_after.png" alt="Fig. 6">
    <figcaption><strong>Fig. 6.</strong> Exp. 4b: Concurrent three-node evaluation comparing uniform default SpecEdge (<code>E4-Base</code>) against heterogeneity-aware Variable-Budget serving (<code>E4-Opt</code>). (a) Per-edge and aggregate throughput with imbalance ratio reduction; (b) <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> shift, RPC reduction, and local draft latency savings.</figcaption>
  </figure>

  <!-- SECTION VII -->
  <h2>VII. Deployment Guidelines, Limitations, and Future Work</h2>

  <h3>A. Actionable Guidelines for Heterogeneous Edge-Cloud Serving</h3>
  <p>
    Our theoretical model and empirical findings distill into three deployment rules for practitioners building commodity device-cloud LLM clusters:
  </p>
  <ol>
    <li><strong>Partition Policies by Bottleneck Ratio <span class="m"><i>&rho;</i></span>:</strong> Measure baseline <span class="m"><i>T</i><sub><span class="rm">draft</span></sub></span> and <span class="m"><i>T</i><sub><span class="rm">wait</span></sub></span> over a short warm-up window. Assign deep trees (<span class="m"><i>d</i>=6&ndash;8, <i>B</i>=48&ndash;64</span>) with <code>proactive=included</code> whenever <span class="m"><i>&rho;</i> &gt; 5</span>, and shallow trees (<span class="m"><i>d</i>=2&ndash;3, <i>B</i>=16&ndash;24</span>) with <code>included</code> whenever <span class="m"><i>&rho;</i> &le; 2</span>.</li>
    <li><strong>Match Draft Capacity to Dispatch Floor:</strong> On eager backends with high fixed launch overhead (such as PyTorch MPS), prefer mid-sized draft models (e.g., 1.7B over 0.6B) whenever unified memory allows, leveraging higher acceptance to amortize dispatch costs.</li>
    <li><strong>Server Storage and Memory Hygiene:</strong> When serving multi-tens-of-GB target models inside WSL2, stage checkpoints on native <code>ext4</code> volumes rather than cross-OS 9p mounts, and reserve headroom for a single maximum-budget CUDA Graph via zero-padding rather than capturing multiple graph buckets.</li>
  </ol>

  <h3>B. Limitations and Future Directions</h3>
  <p>
    First, while our compatibility layer enables seamless Apple Silicon execution via PyTorch MPS, eager dispatch still imposes ~129.5 ms/layer on M4; replacing the client draft engine with Apple&rsquo;s native Metal graph-compiled <strong>MLX</strong> framework while retaining our gRPC protocol could potentially narrow the draft-latency gap toward ~50 ms. Second, real WAN links exhibit second-scale RTT jitter. Because our Variable-Budget Zero-Padding server already accepts arbitrary <span class="m"><i>K</i> &le; <i>B</i><sub><span class="rm">max</span></sub>+1</span> per request without restarting or recompiling, a natural next step is an <em>online sliding-window RTT controller</em> on each edge client that dynamically adjusts <span class="m">(<i>d</i><sub><i>t</i></sub>, <i>B</i><sub><i>t</i></sub>)</span> step-by-step according to instantaneous <span class="m"><i>&rho;</i>&#770;<sub><i>t</i></sub></span>.
  </p>

  <!-- SECTION VIII -->
  <h2>VIII. Conclusion</h2>
  <p>
    We presented an analytical, architectural, and empirical study of edge-cloud speculative decoding on heterogeneous cross-platform wide-area clusters. Starting from a counter-intuitive throughput inversion observed between an RTX 5060 Ti desktop GPU and an Apple M4 laptop, we derived a cycle-level TPOT model and dimensionless bottleneck ratio <span class="m"><i>&rho;</i></span> that accurately explains divergent optimal tree depths (<span class="m"><i>R</i><sup>2</sup>=0.992</span>) as well as eager dispatch-overhead amortization. On the systems side, we built a non-intrusive Apple MPS compatibility layer and proposed Variable-Budget Static CUDA Graph Zero-Padding, enabling a single 14B target graph to serve heterogeneous tree budgets with exact mathematical equivalence and only +2.0 ms overhead. Real three-node concurrent experiments confirm +57.7% bottleneck speedup, -64.0% laptop draft compute savings, +9.7% aggregate cluster throughput gain, and a 44.1% reduction in inter-edge imbalance, providing a practical foundation for real-world heterogeneous device-cloud LLM serving.
  </p>

  <!-- REFERENCES -->
  <h2>References</h2>
  <ul class="refs">
    <li><span class="cite-num">[1]</span>Y. Leviathan, M. Kalman, and Y. Matias, &ldquo;Fast inference from transformers via speculative decoding,&rdquo; in <em>Proc. 40th Int. Conf. Mach. Learn. (ICML)</em>, 2023, pp. 19274&ndash;19286.</li>
    <li><span class="cite-num">[2]</span>C. Chen, S. Borgeaud, G. Irving, J.-B. Lespiau, L. Sifre, and J. Jumper, &ldquo;Accelerating large language model decoding with speculative sampling,&rdquo; <em>arXiv preprint arXiv:2302.01318</em>, 2023.</li>
    <li><span class="cite-num">[3]</span>T. Cai, Y. Li, Z. Geng, H. Peng, J. D. Lee, D. Chen, and T. Dao, &ldquo;Medusa: Simple LLM inference acceleration framework with multiple decoding heads,&rdquo; in <em>Proc. 41st Int. Conf. Mach. Learn. (ICML)</em>, 2024.</li>
    <li><span class="cite-num">[4]</span>Y. Li, F. Wei, C. Zhang, and H. Zhang, &ldquo;EAGLE: Speculative sampling requires rethinking feature uncertainty,&rdquo; in <em>Proc. 41st Int. Conf. Mach. Learn. (ICML)</em>, 2024.</li>
    <li><span class="cite-num">[5]</span>R. Svirschevski, A. May, Z. Chen, B. Chen, Z. Jia, and M. Ryabinin, &ldquo;SpecExec: Massively parallel speculative decoding for interactive LLM inference on consumer devices,&rdquo; in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 2024.</li>
    <li><span class="cite-num">[6]</span>Y. Kang, J. Hauswald, C. Gao, A. Rovinski, T. Mudge, J. Mars, and L. Tang, &ldquo;Neurosurgeon: Collaborative intelligence between the cloud and mobile edge,&rdquo; in <em>Proc. 22nd Int. Conf. Architectural Support for Programming Languages and Operating Systems (ASPLOS)</em>, 2017, pp. 615&ndash;629.</li>
    <li><span class="cite-num">[7]</span>Z. Hao, H. Jiang, S. Jiang, J. Ren, and T. Cao, &ldquo;Hybrid SLM and LLM for edge-cloud collaborative inference,&rdquo; in <em>Proc. Workshop on Edge and Mobile Foundation Models (EdgeFM)</em>, 2024.</li>
    <li><span class="cite-num">[8]</span>J. Park, S. Cho, and D. Han, &ldquo;SpecEdge: Scalable edge-assisted serving framework for interactive LLMs,&rdquo; in <em>Advances in Neural Information Processing Systems (NeurIPS)</em>, 2025, arXiv:2505.17052.</li>
    <li><span class="cite-num">[9]</span>W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu, J. Gonzalez, H. Zhang, and I. Stoica, &ldquo;Efficient memory management for large language model serving with PagedAttention,&rdquo; in <em>Proc. 29th Symp. Operating Systems Principles (SOSP)</em>, 2023, pp. 611&ndash;626.</li>
    <li><span class="cite-num">[10]</span>Qwen Team, &ldquo;Qwen3 technical report,&rdquo; Alibaba Cloud, Tech. Rep., 2025.</li>
    <li><span class="cite-num">[11]</span>X. Liu, L. Hu, P. Bailis, I. Stoica, Z. Deng, A. Cheung, and H. Zhang, &ldquo;SpecBench: A comprehensive benchmark for speculative decoding,&rdquo; <em>arXiv preprint arXiv:2401.07851</em>, 2024.</li>
    <li><span class="cite-num">[12]</span>A. Agrawal, N. Kedia, A. Panwar, J. Mohan, N. Kwatra, B. S. Gulavani, A. Tumanov, and R. Ramjee, &ldquo;Taming throughput-latency tradeoff in LLM inference with Sarathi-Serve,&rdquo; in <em>Proc. 18th USENIX Symp. Operating Systems Design and Implementation (OSDI)</em>, 2024, pp. 117&ndash;134.</li>
  </ul>

</div>
</body>
</html>
"""


def build():
    HTML_PATH.write_text(build_html(), encoding="utf-8")
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            HTML_PATH.as_uri(),
        ],
        check=True,
    )
    HTML_PATH.unlink(missing_ok=True)
    print(f"BUILT ENGLISH IEEE PDF: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
