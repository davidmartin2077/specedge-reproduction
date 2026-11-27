"""
Build an authentic IEEE Conference (IEEEtran) Two-Column Paper PDF
(docs/course_report.pdf) matching docs/paper.tex:
- US Letter (8.5in x 11in), IEEEtran conference margins (0.75in top, 1.0in bottom, 0.625in L/R)
- Full-width centered title & author block (no NeurIPS thick bars)
- Two-column body (column-gap: 0.25in), left-column Abstract & Index Terms
- Centered Roman-numeral section headings (I., II., ...) & italic lettered subsections (A., B., ...)
- Single-column & spanning (column-span: all) IEEE figures, TABLE I-V, equations (1)-(3),
  Algorithm 1 ruled box, and IEEE-style numbered references.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
HTML_PATH = DOCS_DIR / "_ieee_build.html"
PDF_PATH = DOCS_DIR / "course_report.pdf"


def build_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>面向异构跨平台广域网边缘集群的端边协同投机解码</title>
<style>
  /* Official IEEE Conference (IEEEtran) Page Geometry: US Letter, 7.25in text width */
  @page {
    size: letter;
    margin: 0.72in 0.625in 0.85in 0.625in;
    @bottom-center {
      content: counter(page);
      font-family: "Times New Roman", serif;
      font-size: 8.5pt;
      color: #333333;
    }
  }

  * { box-sizing: border-box; }

  body {
    font-family: "Times New Roman", "Noto Serif SC", "SimSun", serif;
    font-size: 9.0pt;
    line-height: 1.38;
    color: #111111;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* IEEE Full-Width Title & Author Header (No horizontal rules) */
  .ieee-header {
    text-align: center;
    margin-bottom: 13pt;
    padding-top: 2pt;
  }
  h1.paper-title {
    font-size: 18.5pt;
    font-weight: 700;
    line-height: 1.26;
    margin: 0 0 9pt 0;
    color: #000000;
  }
  .ieee-author-name {
    font-size: 10.2pt;
    font-weight: 700;
    margin-bottom: 2pt;
    color: #111111;
  }
  .ieee-author-affil {
    font-size: 8.8pt;
    font-style: italic;
    color: #222222;
    margin-bottom: 1.5pt;
  }
  .ieee-author-repo {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.2pt;
    color: #1D3557;
  }

  /* IEEE Two-Column Flow */
  .two-col {
    column-count: 2;
    column-gap: 0.24in;
    column-fill: balance;
  }
  .span-all {
    column-span: all;
    margin: 8pt 0 9pt 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  /* IEEE Left-Column Abstract & Index Terms */
  .ieee-abstract {
    font-size: 8.4pt;
    line-height: 1.38;
    text-align: justify;
    margin: 0 0 6pt 0;
  }
  .ieee-abstract .abs-lead {
    font-weight: 700;
    font-style: italic;
  }
  .ieee-keywords {
    font-size: 8.3pt;
    line-height: 1.36;
    text-align: justify;
    margin: 0 0 9pt 0;
  }
  .ieee-keywords .kw-lead {
    font-weight: 700;
    font-style: italic;
  }

  /* IEEE Centered Roman-Numeral Section Headings (I., II., ...) */
  h2 {
    font-size: 9.8pt;
    font-weight: 700;
    text-align: center;
    color: #000000;
    margin: 10pt 0 4.5pt 0;
    letter-spacing: 0.3pt;
    line-height: 1.25;
    break-after: avoid;
    page-break-after: avoid;
  }
  /* IEEE Left-Aligned Italic Lettered Subsections (A., B., ...) */
  h3 {
    font-size: 9.2pt;
    font-weight: 700;
    font-style: italic;
    text-align: left;
    color: #000000;
    margin: 7.5pt 0 3pt 0;
    line-height: 1.25;
    break-after: avoid;
    page-break-after: avoid;
  }

  p {
    text-align: justify;
    text-indent: 1.6em;
    margin: 0 0 4.5pt 0;
  }
  p.noindent {
    text-indent: 0;
  }

  ul, ol {
    margin: 2pt 0 5pt 0;
    padding-left: 14pt;
  }
  li {
    text-align: justify;
    margin-bottom: 2.5pt;
  }

  /* Clean IEEE Monospace (\texttt) */
  code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.0pt;
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

  /* IEEE Single-Column Display Equations with Flush-Right Number (1), (2), (3) */
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
    font-size: 8.7pt;
    line-height: 1.25;
  }
  .eq-num {
    width: 18pt;
    flex-shrink: 0;
    text-align: right;
    font-family: "Times New Roman", serif;
    font-size: 8.8pt;
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

  /* IEEE Proposition Block */
  .proposition {
    margin: 5.5pt 0 6pt 0;
    padding: 4.5pt 6.5pt;
    border-left: 1.8pt solid #222222;
    background: #FAFAFB;
    font-size: 8.6pt;
    line-height: 1.36;
    text-align: justify;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .proposition .prop-head { font-weight: 700; }

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
    font-size: 8.4pt;
    line-height: 1.3;
  }
  .alg-body {
    padding: 3.5pt 1pt 4pt 1pt;
    font-size: 7.7pt;
    line-height: 1.42;
  }
  .alg-req {
    margin-bottom: 2.5pt;
    text-align: left;
  }
  .alg-line {
    display: flex;
    align-items: baseline;
  }
  .alg-ln {
    width: 14pt;
    flex-shrink: 0;
    font-size: 7.0pt;
    color: #555555;
    text-align: right;
    padding-right: 4pt;
  }
  .alg-code { flex: 1; text-align: left; }
  .alg-ind1 { padding-left: 9pt; }
  .alg-ind2 { padding-left: 18pt; }
  .alg-kw { font-weight: 700; }
  .alg-cmt { color: #555555; font-size: 7.3pt; margin-left: 4pt; }

  /* IEEE Tables (Centered Uppercase TABLE I / II Caption + Booktabs Rules) */
  .table-wrap {
    margin: 6pt 0 7.5pt 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .table-label {
    text-align: center;
    font-size: 8.2pt;
    font-weight: 700;
    letter-spacing: 0.6pt;
    margin-bottom: 1pt;
  }
  .table-title {
    text-align: center;
    font-size: 8.2pt;
    margin-bottom: 4pt;
    color: #111111;
  }
  table.ieee-tbl {
    width: 100%;
    border-collapse: collapse;
    border-top: 1.2pt solid #000000;
    border-bottom: 1.2pt solid #000000;
    font-size: 7.8pt;
    line-height: 1.28;
  }
  table.ieee-tbl.compact {
    font-size: 7.4pt;
  }
  table.ieee-tbl thead th {
    font-weight: 700;
    text-align: center;
    padding: 3.5pt 2.5pt;
    border-bottom: 0.65pt solid #000000;
    background: #FFFFFF;
    color: #000000;
    vertical-align: bottom;
  }
  table.ieee-tbl tbody td {
    padding: 2.8pt 2.5pt;
    text-align: center;
    vertical-align: middle;
  }
  table.ieee-tbl th.l, table.ieee-tbl td.l { text-align: left; }
  table.ieee-tbl tr.midrule td {
    border-top: 0.5pt solid #666666;
  }
  table.ieee-tbl tr.highlight td {
    background: #F4F6FA;
  }
  .table-note {
    font-size: 7.4pt;
    color: #444444;
    margin-top: 2.5pt;
    text-align: left;
  }

  /* IEEE Figures (Single-Column & Two-Column Spanning) */
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
  figure.span-all img {
    max-width: 96%;
  }
  figcaption {
    font-size: 8.0pt;
    line-height: 1.34;
    color: #111111;
    margin-top: 3.5pt;
    text-align: justify;
  }

  /* IEEE References */
  .refs {
    font-size: 7.9pt;
    line-height: 1.34;
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
  .cite-num {
    display: inline-block;
    width: 17pt;
    text-indent: 0;
  }
</style>
</head>
<body>

<!-- ==================== IEEE FULL-WIDTH TITLE BLOCK ==================== -->
<div class="ieee-header">
  <h1 class="paper-title">面向异构跨平台广域网边缘集群的端边协同投机解码：<br>建模、系统改造与差异化优化</h1>
  <div class="ieee-author-name">课程研究报告（基于 SpecEdge, NeurIPS 2025）</div>
  <div class="ieee-author-affil">跨平台三机异构实验平台：RTX 4080 SUPER (32 GB) &times; RTX 5060 Ti (8 GB) &times; Apple M4 (16 GB)</div>
  <div class="ieee-author-repo">https://github.com/davidmartin2077/specedge-reproduction</div>
</div>

<!-- ==================== IEEE TWO-COLUMN BODY ==================== -->
<div class="two-col">

  <!-- Abstract & Index Terms in Left Column -->
  <div class="ieee-abstract">
    <span class="abs-lead">摘要 (Abstract)—</span>以 SpecEdge [1] 为代表的端边协同投机解码通过将轻量级草稿模型卸载至边缘设备、将大模型验证保留在服务端，有效缓解了大语言模型自回归推理的访存瓶颈。然而，原论文评测建立在“同构 Linux + NVIDIA CUDA + 10 GbE 局域网（RTT &lt; 1 ms）”的理想前提之上。在真实的消费级跨平台边缘集群（NVIDIA 独显主机与 Apple Silicon 笔记本经 Tailscale 广域网组网）中，节点在计算后端（CUDA Graph vs. PyTorch MPS Eager）、显存容量（8 GB vs. 16 GB 统一内存）和网络往返延迟（WAN RTT）上高度异构。本文在真实三机集群（Server：RTX 4080 SUPER 32 GB 运行 <code>Qwen3-14B</code>；Edge 1：RTX 5060 Ti 8 GB；Edge 2：Apple M4 16 GB）上开展四组控制变量实验（18 个实测配置点，统一 <code>SpecBench</code>），主要贡献包括：(1) 实现面向 Apple Silicon MPS 的无侵入式兼容层及服务端 <strong>Variable-Budget 静态 CUDA Graph 零填充机制</strong>，以仅 <strong>+2.0 ms</strong> 开销并发支持异构树预算；(2) 提出广域网 TPOT 解析模型与无量纲瓶颈比判据 <span class="m"><i>&rho;</i> = (<i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub>)/<i>T</i><sub><span class="rm">draft</span></sub></span>，揭示网络受限端（<span class="m"><i>&rho;</i> &gg; 1</span>）与算力敏感端（<span class="m"><i>&rho;</i> &approx; 1</span>）相反的最优树深拐点，并发现 M4 的“固定调度底噪摊销效应”；(3) 在三机并发实测中将瓶颈节点（5060 Ti）吞吐提升 <strong>+57.7%</strong>（<span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> 由 3.90 升至 5.51，RPC 减少 28.9%）、将 M4 本地草稿耗时压缩 <strong>-64.0%</strong>，集群总吞吐提升 <strong>+9.7%</strong>，双端不均衡比由 2.20&times; 收敛至 1.23&times;。
  </div>

  <div class="ieee-keywords">
    <span class="kw-lead">关键词 (Index Terms)—</span>端边协同推理，投机解码，异构边缘集群，CUDA Graph，Apple Silicon MPS，控制变量实验。
  </div>

  <!-- SECTION I -->
  <h2>I. 引言与研究动机</h2>
  <p>
    大语言模型（LLM）的自回归解码具有显著的访存受限特征：每生成一个新 Token 均需完整读取一次主模型权重，导致高显存服务端算力利用率偏低。投机解码 [3] 及树状并行扩展 SpecExec [2] 通过轻量草稿模型批量生成候选树，交由主模型一次前向并行验收，在严格保持输出分布无损的前提下显著提升吞吐。SpecEdge（NeurIPS 2025）[1] 将其拓展至端边协同架构：草稿模型卸载至边缘端，仅经 gRPC 发送轻量 Token ID 树与树掩码至服务端，将主端显存与算力全部释放给大模型批量验证。
  </p>
  <p>
    但在真实高校实验室与个人多端算力整合场景中，边缘环境与原论文理想条件存在显著鸿沟：
  </p>
  <ul>
    <li><strong>硬件与软件栈异构</strong>：桌面 NVIDIA GPU 支持 CUDA Graph（算子发射极快），但显存受限（8 GB）；Apple Silicon 轻薄本（M4）拥有 16 GB 统一内存，但 PyTorch MPS 缺乏 CUDA Graph，处于逐算子 Eager 调度模式。</li>
    <li><strong>网络拓扑异构</strong>：跨校/家用设备经 Tailscale 广域网互联，不同节点 RTT 差异达 2&ndash;3&times;（数百至上千毫秒），远超 10 GbE 局域网亚毫秒延迟。</li>
    <li><strong>反直觉预实验现象</strong>：初期三机联调中，算力更强、模型更大的 <code>RTX 5060 Ti (1.7B)</code> 吞吐（2.78 tok/s）反而低于算力更弱、模型更小的 <code>Apple M4 (0.6B)</code>（3.31 tok/s）。</li>
  </ul>
  <p>
    本文围绕该现象系统研究：<em>在算力、显存与 WAN RTT 高度异构的边缘集群中，决定吞吐的本质瓶颈是什么？原论文的统一树预算与 Proactive Drafting 是否仍然最优？如何以最小系统代价实现按端定制的异构协同加速？</em>
  </p>

  <!-- SECTION II -->
  <h2>II. 异构端边协同理论建模</h2>

  <h3>A. 广域网单 Token 延迟（TPOT）解析模型</h3>
  <p>
    针对边缘设备 <span class="m"><i>h</i> &isin; {<span class="rm">5060Ti</span>, <span class="rm">M4</span>}</span>、草稿模型规模 <span class="m"><i>m</i> &isin; {0.6<span class="rm">B</span>, 1.7<span class="rm">B</span>}</span>、投机树超参 <span class="m">(<i>d</i>, <i>B</i>)</span> 及主动草稿模式 <span class="m"><i>p</i></span>，我们将单轮平均生成 1 个有效 Token 的延迟（TPOT）建模为：
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <span class="rm">TPOT</span> =
      <span class="frac">
        <span class="num"><i>T</i><sub><span class="rm">draft</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub> + <i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">post</span></sub> &minus; <i>T</i><sub><span class="rm">overlap</span></sub></span>
        <span class="den"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>m</i>, <i>d</i>, <i>B</i>, <i>p</i>)]</span>
      </span>
    </div>
    <div class="eq-num">(1)</div>
  </div>

  <p class="noindent">
    其中：<span class="m"><i>T</i><sub><span class="rm">draft</span></sub>(<i>d</i>) &approx; <i>c</i><sub>0</sub>(<i>h</i>, <i>m</i>) + <i>&alpha;</i>(<i>h</i>, <i>m</i>)&middot;<i>d</i></span> 为端侧树展开耗时，<span class="m"><i>&alpha;</i></span> 为单层边际时间代价；<span class="m"><i>T</i><sub><span class="rm">verify</span></sub>(<i>B</i>)</span> 为主端 14B 树验证耗时（4080S CUDA Graph 下恒定于 75&ndash;85 ms）；<span class="m"><i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>)</span> 与 <span class="m"><i>T</i><sub><span class="rm">post</span></sub>(<i>h</i>)</span> 分别为广域网往返和端侧前后处理耗时；<span class="m"><i>T</i><sub><span class="rm">overlap</span></sub> &le; <span class="rm">min</span>(<i>T</i><sub><span class="rm">draft</span></sub><sup><span class="rm">pro</span></sup>, <i>T</i><sub><span class="rm">net</span></sub> + <i>T</i><sub><span class="rm">verify</span></sub>)</span> 为 Proactive Drafting 隐藏掉的草稿时间；<span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>(<i>d</i>)] &approx; <i>&kappa;</i><i>d</i><sup><i>&gamma;</i></sup></span>（<span class="m">0 &lt; <i>&gamma;</i> &lt; 1</span>）为平均接受长度（MAT）。
  </p>

  <h3>B. 无量纲瓶颈比判据 <span class="m"><i>&rho;</i></span> 与分化推论</h3>
  <p>
    为统一度量边缘节点所处的物理机制区，定义无量纲<strong>网络-草稿瓶颈比</strong>：
  </p>

  <div class="eq-row">
    <div class="eq-body m">
      <i>&rho;</i>(<i>h</i>, <i>m</i>) &nbsp;=&nbsp;
      <span class="frac">
        <span class="num"><i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>) + <i>T</i><sub><span class="rm">verify</span></sub></span>
        <span class="den"><i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>, <i>m</i>)</span>
      </span>
    </div>
    <div class="eq-num">(2)</div>
  </div>

  <p class="noindent">
    记等待窗口 <span class="m"><i>T</i><sub><span class="rm">wait</span></sub> = <i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>) + <i>T</i><sub><span class="rm">verify</span></sub></span>，对式 (1) 关于树深 <span class="m"><i>d</i></span> 求导，可得 <span class="m">&part;<span class="rm">TPOT</span>/&part;<i>d</i> &lt; 0</span> 的充要条件：
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

  <div class="proposition">
    <span class="prop-head">推论 1（异构边缘的最优树深分化）：</span>由式 (3) 导出两类相反优化区间：<strong>(i) 网络受限区（<span class="m"><i>&rho;</i> &gg; 1</span> 且 <span class="m"><i>&alpha;</i></span> 极小，如 5060 Ti）</strong>：右侧趋近 0，激进加深投机树（增大 <span class="m"><i>d</i>, <i>B</i></span>）并启用 <code>included</code> 可大幅抬高 <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span>、摊薄高 WAN RTT；<strong>(ii) 算力敏感区（<span class="m"><i>&rho;</i> &approx; 1</span> 且 <span class="m"><i>&alpha;</i></span> 较大，如 M4）</strong>：深树使分子增速反超分母亚线性增益，存在<strong>浅树最优拐点（小 <span class="m"><i>d</i></span>、小 <span class="m"><i>B</i></span>）</strong>。
  </div>

  <!-- SECTION III -->
  <h2>III. 系统架构与核心工程改造</h2>
  <p>
    Fig. 1 展示了本文搭建的跨平台三机异构协同架构与 Proactive Drafting 延迟隐藏时序。
  </p>

  <!-- SPANNING FIGURE 1 -->
  <figure class="span-all">
    <img src="figures/fig1_architecture_timeline.png" alt="Fig. 1">
    <figcaption><strong>Fig. 1.</strong> 跨平台异构 SpecEdge 三机协同部署架构与 Variable-Budget 零填充验证流水线示意图。(a) Server 以单一静态 CUDA Graph 并发服务网络受限端（RTX 5060 Ti）与算力敏感端（Apple M4）；(b) 高 WAN RTT 下 <code>included</code> 主动草稿将下一轮草稿计算 <span class="m"><i>T</i><sub><span class="rm">overlap</span></sub></span> 隐藏在等待窗口内。</figcaption>
  </figure>

  <h3>A. Apple Silicon MPS 无侵入式跨平台兼容层</h3>
  <p>
    原版 SpecEdge 在 <code>GraphEngine</code> 与 <code>Timing</code> 中硬编码了 CUDA 接口。在保证 CUDA 路径零额外开销的前提下，我们完成了两处核心适配：(1) 在 <code>src/specedge/engine/graph.py</code> 中按 <code>device.type</code> 跳过 <code>mps</code> 端的 <code>CUDAGraph</code> 捕获，并定位修复了原版非图分支遗漏 <code>seq_indices[:num_beams]</code> 切片导致的 KV Cache 维度失配缺陷；(2) 在 <code>src/util.py</code> 与 <code>src/script/client.py</code> 中支持 <code>torch.mps.synchronize()</code>、平滑回退非 CUDA 端 <code>event</code> 计时，并消除 Windows Python 3.14 下 <code>grpc.aio</code> 退出挂起问题。
  </p>

  <h3>B. Variable-Budget 静态 CUDA Graph 零填充机制</h3>
  <p>
    原版服务端验证器（<code>src/strategy/server_verify/specexec/grpc.py</code>）按全局固定长度 <span class="m"><i>M</i> = <i>B</i><sub><span class="rm">max</span></sub> + 1</span> 分配静态图缓冲区，强迫所有并发 Edge 共用同一 <code>max_budget</code>。为此，我们提出轻量级 <strong>Variable-Budget 静态 CUDA Graph 零填充机制</strong>（Algorithm 1）：服务端仅按集群最大预算 <span class="m"><i>B</i><sub><span class="rm">max</span></sub> = 64</span> 捕获单一静态图；当客户端发来实际树长 <span class="m"><i>K</i> &le; <i>M</i></span> 的请求时，将有效数据写入前 <span class="m"><i>K</i></span> 槽，将填充槽 <code>[K:]</code> 的 KV 写入重定向至末尾哑槽 <code>max_len - 1</code> 并置安全注意力掩码防 <code>NaN</code>；图复放后按 <code>[:K]</code> 切片回传，并在 KV 重排阶段屏蔽填充位，确保数学等价。实测额外验证开销仅 <strong>+2.0 ms</strong>。
  </p>

  <!-- SINGLE-COLUMN ALGORITHM 1 -->
  <div class="alg-box">
    <div class="alg-header"><strong>Algorithm 1</strong> &nbsp;异构感知配置与 Variable-Budget 零填充验证</div>
    <div class="alg-body">
      <div class="alg-req"><span class="alg-kw">Require:</span> 最大预算 <span class="m"><i>B</i><sub><span class="rm">max</span></sub>=64</span>，单一 14B 静态图 <span class="m">&Gscr;<sub><i>M</i></sub></span>（<span class="m"><i>M</i>=<i>B</i><sub><span class="rm">max</span></sub>+1</span>）；边缘端探测指标 <span class="m">(<i>T</i><sub><span class="rm">draft</span></sub>, <i>T</i><sub><span class="rm">net</span></sub>, <i>T</i><sub><span class="rm">verify</span></sub>)</span></div>
      <div class="alg-line"><span class="alg-ln">1:</span><span class="alg-code"><span class="alg-kw">Phase 1: 按瓶颈比 <span class="m"><i>&rho;</i></span> 分配异构端侧策略</span></span></div>
      <div class="alg-line"><span class="alg-ln">2:</span><span class="alg-code"><span class="alg-kw">for</span> 每个边缘节点 <span class="m"><i>h</i></span> <span class="alg-kw">do</span></span></div>
      <div class="alg-line"><span class="alg-ln">3:</span><span class="alg-code alg-ind1"><span class="m"><i>&rho;</i><sub><i>h</i></sub> &larr; (<i>T</i><sub><span class="rm">net</span></sub>(<i>h</i>) + <i>T</i><sub><span class="rm">verify</span></sub>) / <i>T</i><sub><span class="rm">draft</span></sub>(<i>h</i>)</span></span></div>
      <div class="alg-line"><span class="alg-ln">4:</span><span class="alg-code alg-ind1"><span class="alg-kw">if</span> <span class="m"><i>&rho;</i><sub><i>h</i></sub> &gt; 5</span> <span class="alg-kw">then</span></span></div>
      <div class="alg-line"><span class="alg-ln">5:</span><span class="alg-code alg-ind2"><span class="m">(<i>d</i><sub><i>h</i></sub>, <i>B</i><sub><i>h</i></sub>, <i>p</i><sub><i>h</i></sub>) &larr; (8, 64, <code>included</code>)</span> <span class="alg-cmt">&#9657; 5060 Ti</span></span></div>
      <div class="alg-line"><span class="alg-ln">6:</span><span class="alg-code alg-ind1"><span class="alg-kw">else</span></span></div>
      <div class="alg-line"><span class="alg-ln">7:</span><span class="alg-code alg-ind2"><span class="m">(<i>d</i><sub><i>h</i></sub>, <i>B</i><sub><i>h</i></sub>, <i>p</i><sub><i>h</i></sub>) &larr; (2, 16, <code>included</code>)</span> <span class="alg-cmt">&#9657; Apple M4</span></span></div>
      <div class="alg-line"><span class="alg-ln">8:</span><span class="alg-code alg-ind1"><span class="alg-kw">end if</span></span></div>
      <div class="alg-line"><span class="alg-ln">9:</span><span class="alg-code"><span class="alg-kw">end for</span></span></div>
      <div class="alg-line"><span class="alg-ln">10:</span><span class="alg-code"><span class="alg-kw">Phase 2: 服务端单图零填充验证（任意 <span class="m"><i>K</i> &le; <i>M</i></span>）</span></span></div>
      <div class="alg-line"><span class="alg-ln">11:</span><span class="alg-code"><span class="m"><i>X</i>[0:<i>K</i>] &larr; req.ids</span>, <span class="m">pos[0:<i>K</i>] &larr; req.pos</span>, <span class="m">kv[0:<i>K</i>] &larr; req.kv</span></span></div>
      <div class="alg-line"><span class="alg-ln">12:</span><span class="alg-code"><span class="alg-kw">if</span> <span class="m"><i>K</i> &lt; <i>M</i></span> <span class="alg-kw">then</span></span></div>
      <div class="alg-line"><span class="alg-ln">13:</span><span class="alg-code alg-ind1"><span class="m"><i>X</i>[<i>K</i>:<i>M</i>] &larr; 0</span>, <span class="m">kv[<i>K</i>:<i>M</i>] &larr; <code>max_len</code>&minus;1</span></span></div>
      <div class="alg-line"><span class="alg-ln">14:</span><span class="alg-code alg-ind1"><span class="m">mask[:, <i>K</i>:<i>M</i>, 0] &larr; 1.0</span> <span class="alg-cmt">&#9657; 防 Softmax NaN</span></span></div>
      <div class="alg-line"><span class="alg-ln">15:</span><span class="alg-code"><span class="alg-kw">end if</span></span></div>
      <div class="alg-line"><span class="alg-ln">16:</span><span class="alg-code"><span class="m">logits &larr; &Gscr;<sub><i>M</i></sub>(<i>X</i>, pos, kv, mask)</span></span></div>
      <div class="alg-line"><span class="alg-ln">17:</span><span class="alg-code"><span class="m">sel &larr; <span class="rm">Verify</span>(logits)[0:<i>K</i>]</span></span></div>
      <div class="alg-line"><span class="alg-ln">18:</span><span class="alg-code"><span class="m">logit_mask[<i>K</i>&minus;1:] &larr; <code>False</code></span>，执行无损 KV 重排</span></div>
      <div class="alg-line"><span class="alg-ln">19:</span><span class="alg-code"><span class="alg-kw">return</span> <span class="m">sel</span> 至边缘节点 <span class="m"><i>h</i></span></span></div>
    </div>
  </div>

  <!-- SECTION IV -->
  <h2>IV. 控制变量实验设计</h2>
  <p>
    三台设备软件依赖严格对齐原论文 <code>pyproject.toml</code>（Python 3.14.x、PyTorch 2.9.x、Transformers 4.57.x、gRPC 1.75.1），软硬件配置见 Table I。全部 18 组实测均固定使用 <code>SpecBench</code> [5] 同一批 16 条请求（<code>sample_req_cnt=30, max_request_num=480</code>）、<code>Qwen3-14B</code>（FP16）[4]、<code>max_len=2048</code>、<code>max_new_tokens=64</code>、<code>temperature=0.7</code>、<code>seed=42</code>。
  </p>
  <p>
    实验分四组递进展开：<strong>实验 1</strong> 对比单机基线 <code>Auto-Batch</code>（14B 纯自回归）与 <code>Server-Only</code>（同卡 <code>14B+0.6B</code>）；<strong>实验 2</strong> 固定 <span class="m">(<i>d</i>=4, <i>B</i>=32, <code>excluded</code>)</span> 交叉测试 <span class="m">{5060 Ti, M4} &times; {0.6B, 1.7B}</span>；<strong>实验 3</strong> 消融 <code>proactive.type</code> <span class="m">&isin; {<code>disabled</code>, <code>excluded</code>, <code>included</code>}</span>；<strong>实验 4</strong> 包含树深扫描拟合（4a）与三机并发终极对照（4b：<code>E4-Base</code> vs. <code>E4-Opt</code>）。
  </p>

  <!-- SPANNING TABLE I -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE I</div>
    <div class="table-title">三机跨平台异构实验平台软硬件与环境配置</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">节点角色</th>
          <th class="l">硬件与操作系统</th>
          <th class="l">推理后端</th>
          <th class="l">本地部署模型</th>
          <th style="white-space: nowrap;">环境体积</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><strong>Server</strong></td>
          <td class="l">RTX 4080 SUPER (32 GB, <code>sm_89</code>), WSL2 Ubuntu</td>
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
          <td class="l">Apple M4 (16 GB 统一内存), macOS 27.2.1</td>
          <td class="l">PyTorch MPS (Eager)</td>
          <td class="l"><code>Qwen3-0.6B</code>, <code>1.7B</code></td>
          <td>0.82 GB</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION V -->
  <h2>V. 实验结果与深度分析</h2>

  <h3>A. 实验 1 &amp; 2：基线对照与 2&times;2 交叉矩阵</h3>
  <p>
    Table II 与 Fig. 2、Fig. 3 汇总了实验 1 与实验 2 的实测数据，揭示三条核心规律：
  </p>

  <!-- SPANNING TABLE II -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE II</div>
    <div class="table-title">实验 1（单机基线）与实验 2（2&times;2 交叉控制变量矩阵，统一 <span class="m"><i>d</i>=4, <i>B</i>=32, <code>excluded</code></span>）实测汇总</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">编号</th>
          <th class="l">配置（设备 / 模型）</th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> (tok/步)</th>
          <th>Draft (ms)</th>
          <th>Verify (ms)</th>
          <th>Net RTT (ms)</th>
          <th>Post (ms)</th>
          <th><span class="m"><i>&rho;</i></span></th>
          <th>TPOT (ms)</th>
          <th>吞吐 (tok/s)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l">E1-1</td>
          <td class="l"><code>Auto-Batch</code> (4080S 独跑 14B)</td>
          <td>&mdash;</td><td>&mdash;</td><td>64.7</td><td>0</td><td>&mdash;</td><td>&mdash;</td>
          <td><strong>64.7</strong></td><td><strong>15.45</strong></td>
        </tr>
        <tr>
          <td class="l">E1-2</td>
          <td class="l"><code>Server-Only</code> (同卡 14B+0.6B)</td>
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
    <img src="figures/fig2_latency_breakdown.png" alt="Fig. 2">
    <figcaption><strong>Fig. 2.</strong> 实验 2：2&times;2 控制变量矩阵的单轮延迟拆解与瓶颈比 <span class="m"><i>&rho;</i></span> 对比。5060 Ti 超过 92% 时间耗于网络等待（<span class="m"><i>&rho;</i> &isin; [17.6, 20.2]</span>），M4 本地草稿与网络等待相当（<span class="m"><i>&rho;</i> &isin; [1.16, 1.79]</span>）。</figcaption>
  </figure>

  <ol>
    <li><strong>单卡显存拥挤验证端边卸载的必要性（E1-1 vs. E1-2）</strong>：32 GB 4080S 同卡部署 <code>14B+0.6B</code> 因剩余显存不足无法开启主模型 CUDA Graph，单次验证恶化至 431.6 ms（慢于专用 Server 的 75&ndash;82 ms 达 <strong>5.4&times;</strong>），吞吐跌至 7.06 tok/s。草稿卸载至边缘后，在局域网（RTT &lt; 1 ms）下 <code>5060 Ti + 1.7B</code> 等效吞吐可达 23.8 tok/s（较 14B 纯自回归加速 1.54&times;）。</li>
    <li><strong>两类 Edge 落入相反性能机制区（Fig. 2）</strong>：同模型下 5060 Ti 草稿速度领先 M4 达 <strong>7.5&times;&ndash;8.8&times;</strong>、前后处理快 <strong>20&times;</strong>，但瓶颈比 <span class="m"><i>&rho;</i> &isin; [17.6, 20.2]</span>（重度网络受限）；M4 处于 <span class="m"><i>&rho;</i> &isin; [1.16, 1.79]</span>（算力敏感）。</li>
    <li><strong>M4 的“固定调度底噪摊销效应”（E2-3 vs. E2-4）</strong>：M4 模型由 <code>0.6B</code> 放大近 3&times; 至 <code>1.7B</code>，Draft 仅增 33%（492.4 &rarr; 655.9 ms），<span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> 跃升至全场最高 <strong>4.16</strong>（+8.3%），吞吐反升 <strong>+6.0%</strong>（2.62 &rarr; 2.78 tok/s），表明 MPS Eager 约 350&ndash;400 ms 的固定调度底噪可被较大草稿模型有效摊薄。</li>
  </ol>

  <!-- SPANNING FIGURE 3 -->
  <figure class="span-all">
    <img src="figures/fig3_matrix_mat_throughput.png" alt="Fig. 3">
    <figcaption><strong>Fig. 3.</strong> 实验 1 &amp; 2：模型规模与异构硬件对 (a) 每轮接受长度 <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> 与 (b) 端到端解码吞吐的交叉影响。</figcaption>
  </figure>

  <h3>B. 实验 3：Proactive Drafting 广域网消融</h3>
  <p>
    Table III 与 Fig. 4 表明，在高 RTT 广域网下 <code>included</code> 模式在两类异构设备上全面胜出：在 <code>5060 Ti (1.7B)</code> 上将 Draft 压缩 <strong>-18.7%</strong>（88.9 &rarr; 72.3 ms）、吞吐较关闭时提升 <strong>+17.0%</strong>（2.83 &rarr; 3.31 tok/s）；在 <code>Apple M4 (0.6B)</code> 上将 Draft 压缩 <strong>-14.6%</strong>（512.4 &rarr; 437.4 ms）、吞吐达 3.47 tok/s（较默认 <code>excluded</code> 提升 <strong>+32.4%</strong>）。充裕的广域网等待窗口使主动草稿几乎总能在回包前完成，采用 <code>included</code> 将其直接并入下一轮候选树可最大化隐藏 <span class="m"><i>T</i><sub><span class="rm">overlap</span></sub></span>。
  </p>

  <!-- SPANNING TABLE III -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE III</div>
    <div class="table-title">实验 3：Proactive Drafting 广域网消融实验实测结果（<span class="m"><i>d</i>=4, <i>B</i>=32</span>）</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">边缘链路</th>
          <th class="l">Proactive 模式</th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span></th>
          <th>命中步数</th>
          <th>Draft (ms)</th>
          <th>Wait (ms)</th>
          <th>吞吐 (tok/s)</th>
          <th>相对变化</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><code>disabled</code></td>
          <td>3.60</td><td>0</td><td>88.9</td><td>1178.4</td><td>2.83</td><td>基准</td>
        </tr>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><code>excluded</code> (默认)</td>
          <td><strong>3.94</strong></td><td>36 / 236</td><td>87.5</td><td>1543.2</td><td>2.41</td><td>RTT 波动</td>
        </tr>
        <tr class="highlight">
          <td class="l"><code>5060 Ti (1.7B)</code></td>
          <td class="l"><strong><code>included</code> (融合)</strong></td>
          <td>3.70</td><td><strong>41 / 245</strong></td><td><strong>72.3 (-18.7%)</strong></td><td>1042.2</td><td><strong>3.31</strong></td><td><strong>+17.0%</strong></td>
        </tr>
        <tr class="midrule">
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><code>disabled</code></td>
          <td>3.71</td><td>0</td><td>512.4</td><td>497.8</td><td>3.25</td><td>基准</td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><code>excluded</code> (默认)</td>
          <td><strong>3.84</strong></td><td>28 / 241</td><td>492.4</td><td>880.5</td><td>2.62</td><td>RTT 波动</td>
        </tr>
        <tr class="highlight">
          <td class="l"><code>Apple M4 (0.6B)</code></td>
          <td class="l"><strong><code>included</code> (融合)</strong></td>
          <td>3.82</td><td><strong>49 / 246</strong></td><td><strong>437.4 (-14.6%)</strong></td><td>583.4</td><td><strong>3.47</strong></td><td><strong>+32.4%*</strong></td>
        </tr>
      </tbody>
    </table>
    <div class="table-note">* 相对默认 <code>excluded</code> 模式提升（相对 <code>disabled</code> 提升 +6.8%）。</div>
  </div>

  <!-- SPANNING FIGURE 4 -->
  <figure class="span-all">
    <img src="figures/fig4_proactive_ablation.png" alt="Fig. 4">
    <figcaption><strong>Fig. 4.</strong> 实验 3：Proactive Drafting 消融实验（<code>disabled</code> vs. <code>excluded</code> vs. <code>included</code>）。(a) 草稿耗时 <span class="m"><i>T</i><sub><span class="rm">draft</span></sub></span> 压缩效果；(b) 广域网端到端解码吞吐提升。</figcaption>
  </figure>

  <h3>C. 实验 4a：投机树深度扫描与解析公式拟合验证</h3>
  <p>
    Table IV 与 Fig. 5 验证了推论 1：5060 Ti 与 M4 单层草稿增量斜率分别为 22.4 ms/层 与 129.5 ms/层（相差 <strong>5.78&times;</strong>）。归一化链路参考等待时间（5060 Ti: 1150 ms；M4: 520 ms）后，式 (1) 预测曲线与实测点高度吻合（5060 Ti 拟合优度 <span class="m"><i>R</i><sup>2</sup> = 0.992</span>）：<code>5060 Ti</code> 随树深单调加速，在 <span class="m">(<i>d</i>=8, <i>B</i>=64)</span> 处 <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> 飙升至 <strong>5.84</strong>（单步最高接受 <strong>14 tokens</strong>），归一化 TPOT 下降 <strong>45%</strong>；而 <code>Apple M4</code> 在浅树 <span class="m">(<i>d</i>=2, <i>B</i>=16)</span> 处取得极小值（Draft 腰斩至 242.7 ms，单端吞吐达全场最高的 <strong>3.55 tok/s</strong>），继续加深至 <span class="m"><i>d</i>=4, 6</span> 后 TPOT 抬头反弹。
  </p>

  <!-- SPANNING TABLE IV -->
  <div class="table-wrap span-all">
    <div class="table-label">TABLE IV</div>
    <div class="table-title">实验 4a：投机树深度与预算 <span class="m">(<i>d</i>, <i>B</i>)</span> 扫描实测数据及归一化 TPOT 对比</div>
    <table class="ieee-tbl">
      <thead>
        <tr>
          <th class="l">设备与模型</th>
          <th>树参 <span class="m">(<i>d</i>, <i>B</i>)</span></th>
          <th><span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span></th>
          <th>Max 接受</th>
          <th>Draft (ms)</th>
          <th>单层斜率</th>
          <th>实测吞吐</th>
          <th>归一化 TPOT</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l"><code>5060 Ti (1.7B)</code></td><td>(2, 16)</td><td>2.88</td><td>5</td><td>41.1</td>
          <td rowspan="4">22.4 ms/层</td><td>3.03 tok/s</td><td>413.2 ms/tok</td>
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
          <td rowspan="3">129.5 ms/层</td><td><strong>3.55 tok/s</strong></td><td><strong>261.5 (最优)</strong></td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td><td>(4, 32)</td><td>3.84</td><td>8</td><td>492.4</td>
          <td>2.62 tok/s</td><td>263.8 ms/tok</td>
        </tr>
        <tr>
          <td class="l"><code>Apple M4 (0.6B)</code></td><td>(6, 48)</td><td>4.71</td><td>11</td><td>760.7</td>
          <td>2.95 tok/s</td><td>272.2 (反弹)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SPANNING FIGURE 5 -->
  <figure class="span-all">
    <img src="figures/fig5_tree_sweep_theory_fit.png" alt="Fig. 5">
    <figcaption><strong>Fig. 5.</strong> 实验 4a：(a) 端侧草稿耗时线性标度律与接受长度亚线性增长；(b) 式 (1) 解析模型拟合与 5060 Ti（深树最优）vs. Apple M4（浅树拐点）的相反趋势验证。</figcaption>
  </figure>

  <h3>D. 实验 4b：Variable-Budget 三机并发终极对照</h3>
  <p>
    Table V 与 Fig. 6 展示了三机真实并发场景下默认统一配置（<code>E4-Base</code>）与本文异构感知优化 + Variable-Budget 服务端（<code>E4-Opt</code>）的直接对比。凭借单一静态 CUDA Graph 零填充机制，服务端以仅 <strong>+2.0 ms</strong> 的验证开销（76.0 &rarr; 78.0 ms）并发支撑 <span class="m"><i>B</i>=64</span> 与 <span class="m"><i>B</i>=16</span> 两类候选树，使长尾节点（5060 Ti）吞吐暴涨 <strong>+57.7%</strong>、RPC 往返减少 <strong>-28.9%</strong>，笔记本端（M4）本地 GPU 草稿耗时削减 <strong>-64.0%</strong>，集群总吞吐提升 <strong>+9.7%</strong>，双端不均衡比由 2.20&times; 收敛至 1.23&times;（-44.1%）。
  </p>

  <!-- SINGLE-COLUMN TABLE V -->
  <div class="table-wrap">
    <div class="table-label">TABLE V</div>
    <div class="table-title">实验 4b：三机并发终极对照（<code>E4-Base</code> vs. <code>E4-Opt</code>）</div>
    <table class="ieee-tbl compact">
      <thead>
        <tr>
          <th class="l">评估指标</th>
          <th><code>E4-Base</code></th>
          <th><code>E4-Opt</code></th>
          <th>相对变化</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="l">5060 Ti <span class="m"><span class="rm">&Eopf;</span>[<i>&tau;</i>]</span> / RPC</td>
          <td>3.90 / 235</td><td><strong>5.51 / 167</strong></td><td><strong>+41% / -29%</strong></td>
        </tr>
        <tr>
          <td class="l">5060 Ti TPOT</td>
          <td>631.7 ms</td><td><strong>400.6 ms</strong></td><td><strong>-36.6%</strong></td>
        </tr>
        <tr>
          <td class="l">5060 Ti 吞吐</td>
          <td>1.58 tok/s</td><td><strong>2.50 tok/s</strong></td><td><strong>+57.7%</strong></td>
        </tr>
        <tr>
          <td class="l">M4 Draft 耗时</td>
          <td>481.7 ms</td><td><strong>173.5 ms</strong></td><td><strong>-64.0%</strong></td>
        </tr>
        <tr>
          <td class="l">M4 吞吐</td>
          <td>3.48 tok/s</td><td>3.06 tok/s</td><td>-12.1%</td>
        </tr>
        <tr>
          <td class="l">Server 验证耗时</td>
          <td>76.0 ms</td><td><strong>78.0 ms</strong></td><td>+2.0 ms</td>
        </tr>
        <tr class="midrule highlight">
          <td class="l"><strong>集群总吞吐</strong></td>
          <td>5.06 tok/s</td><td><strong>5.56 tok/s</strong></td><td><strong>+9.7%</strong></td>
        </tr>
        <tr class="highlight">
          <td class="l"><strong>不均衡比</strong></td>
          <td>2.20&times;</td><td><strong>1.23&times;</strong></td><td><strong>-44.1%</strong></td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SPANNING FIGURE 6 -->
  <figure class="span-all">
    <img src="figures/fig6_3node_before_after.png" alt="Fig. 6">
    <figcaption><strong>Fig. 6.</strong> 实验 4b：Variable-Budget 异构并发服务终极对照（<code>E4-Base</code> vs. <code>E4-Opt</code>）。(a) 三机并发吞吐与双端均衡度改善；(b) 异构树预算下的接受长度跃升与本地草稿开销削减。</figcaption>
  </figure>

  <!-- SECTION VI -->
  <h2>VI. 工程部署建议与局限性</h2>
  <p>
    <strong>异构部署决策准则：</strong>(1) 依据瓶颈比 <span class="m"><i>&rho;</i></span> 分区配置：<span class="m"><i>&rho;</i> &gt; 5</span> 采用深树（<span class="m"><i>d</i>=6&ndash;8, <i>B</i>=48&ndash;64</span>）+ <code>included</code>，<span class="m"><i>&rho;</i> &le; 2</span> 采用浅树（<span class="m"><i>d</i>=2&ndash;3, <i>B</i>=16&ndash;24</span>）+ <code>included</code>；(2) 在具备固定调度底噪的 Eager 端（M4 MPS），显存充足时可选用中等草稿模型（<code>1.7B</code>）摊薄底噪；(3) 在 WSL2 部署大模型权重务必置于原生 ext4 分区（28 GB 模型加载仅 ~9 s，较 9p 挂盘快 12&times; 以上），并限制 <code>max_batch_size=1</code> 以保障 WDDM 显存安全余量。
  </p>
  <p>
    <strong>局限性与未来工作：</strong>受限于 PyTorch MPS 的 Eager 调度，M4 单层草稿仍需 ~129 ms，未来可替换为原生 Metal 图编译框架（如 MLX）并保持 gRPC 协议兼容；同时依托 Variable-Budget 零填充服务端，可在客户端引入滑动窗口 RTT 估计器，实现推理期免重启的在线自适应调树 <span class="m">(<i>d</i><sub><i>t</i></sub>, <i>B</i><sub><i>t</i></sub>)</span>。
  </p>

  <!-- SECTION VII -->
  <h2>VII. 结论</h2>
  <p>
    本文基于 NeurIPS 2025 的 SpecEdge 框架，在真实跨平台三机异构广域网集群上完成了系统的解析建模、跨后端与 Variable-Budget 静态图零填充改造及 18 组控制变量实验。研究定量揭示了网络受限端与算力敏感端的相反最优树深规律，以仅 +2.0 ms 服务端验证开销实现了长尾边缘节点 +57.7% 加速、笔记本端本地草稿 -64.0% 算力缩减及集群总吞吐 +9.7% 提升，为真实消费级异构端边大模型推理提供了兼具理论解释力与工程可行性的完整方案。
  </p>

  <!-- REFERENCES -->
  <h2>参考文献 (REFERENCES)</h2>
  <ul class="refs">
    <li><span class="cite-num">[1]</span>J. Park, S. Cho, and D. Han, &ldquo;SpecEdge: Scalable edge-assisted serving framework for interactive LLMs,&rdquo; in <em>Proc. NeurIPS</em>, 2025, arXiv:2505.17052.</li>
    <li><span class="cite-num">[2]</span>R. Svirschevski <em>et al.</em>, &ldquo;SpecExec: Massively parallel speculative decoding for interactive LLM inference on consumer devices,&rdquo; in <em>Proc. NeurIPS</em>, 2024.</li>
    <li><span class="cite-num">[3]</span>Y. Leviathan, M. Kalman, and Y. Matias, &ldquo;Fast inference from transformers via speculative decoding,&rdquo; in <em>Proc. ICML</em>, 2023.</li>
    <li><span class="cite-num">[4]</span>Qwen Team, &ldquo;Qwen3 technical report,&rdquo; Alibaba Cloud, 2025.</li>
    <li><span class="cite-num">[5]</span>X. Liu <em>et al.</em>, &ldquo;SpecBench: A comprehensive benchmark for speculative decoding,&rdquo; 2024.</li>
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
    print(f"BUILT IEEE CONFERENCE PDF: {PDF_PATH} ({PDF_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    build()
