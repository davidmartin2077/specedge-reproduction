"""
Generate 6 publication-grade 100% English IEEE Conference figures
from docs/exp_summary.json -> docs/figures_en/ (.png, .svg, .pdf).
"""

import json
from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

# Clean IEEE camera-ready typography: crisp sans-serif labels + STIX LaTeX math
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#2B2D42"
plt.rcParams["axes.linewidth"] = 0.85
plt.rcParams["xtick.color"] = "#1F2937"
plt.rcParams["ytick.color"] = "#1F2937"

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_PATH = REPO_ROOT / "docs" / "exp_summary.json"
FIG_DIR = REPO_ROOT / "docs" / "figures_en"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Colorblind-safe, print-friendly IEEE publication palette
C_NAVY = "#1D3557"
C_BLUE = "#457B9D"
C_TEAL = "#2A9D8F"
C_TEAL_DARK = "#1B6B63"
C_CORAL = "#D95F43"
C_AMBER = "#E9B44C"
C_PURPLE = "#6C5B7B"
C_SLATE = "#7A8288"
C_BG_BLUE = "#F0F5FA"
C_BG_TEAL = "#EEF8F6"
C_BG_PURPLE = "#F5F2F8"
C_BG_WARM = "#FDF6EE"


def save_fig(fig, name: str):
    fig.savefig(FIG_DIR / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG_DIR / f"{name}.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Generated figures_en/{name}.png / .svg / .pdf")


def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4, color="#999999")
    ax.set_axisbelow(True)


def plot_fig1_architecture():
    fig, ax = plt.subplots(figsize=(10.6, 5.85))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.22)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc, ec, title_bg):
        p = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12",
            facecolor=fc, edgecolor=ec, linewidth=1.35,
        )
        ax.add_patch(p)
        hdr = mpatches.FancyBboxPatch(
            (x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.05,rounding_size=0.10",
            facecolor=title_bg, edgecolor=ec, linewidth=1.05,
        )
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - 0.21, title, ha="center", va="center",
                fontsize=9.0, fontweight="bold", color="white")
        ax.text(x + w / 2, y + (h - 0.42) / 2, body, ha="center", va="center",
                fontsize=8.0, color="#1F2937", linespacing=1.44)

    ax.text(0.2, 5.98, "(a) Heterogeneous Cross-Platform Three-Node Deployment & Variable-Budget Zero-Padding Server",
            fontsize=9.9, fontweight="bold", color=C_NAVY)

    box(
        0.2, 4.00, 3.30, 1.72,
        "Edge 1: RTX 5060 Ti (8 GB, CUDA)",
        "Qwen3-1.7B | CUDA Graph (22.4 ms/layer)\nFast compute + High WAN RTT $\\Rightarrow\\ \\rho \\gg 1$\nPolicy: Deep tree ($d{=}8, B{=}64$) + included",
        C_BG_BLUE, C_NAVY, C_NAVY,
    )
    box(
        0.2, 2.06, 3.30, 1.72,
        "Edge 2: Apple M4 (16 GB Unified)",
        "Qwen3-0.6B/1.7B | MPS Eager (129.5 ms/layer)\nLarge RAM + Lower RTT $\\Rightarrow\\ \\rho \\approx 1$\nPolicy: Shallow tree ($d{=}2, B{=}16$) + included",
        C_BG_TEAL, C_TEAL_DARK, C_TEAL,
    )

    cloud = mpatches.FancyBboxPatch(
        (3.96, 2.74), 2.14, 2.34, boxstyle="round,pad=0.06,rounding_size=0.18",
        facecolor=C_BG_WARM, edgecolor=C_CORAL, linewidth=1.35, linestyle="--",
    )
    ax.add_patch(cloud)
    ax.text(5.03, 4.66, "Tailscale WAN\ngRPC (:8000)", ha="center", va="center",
            fontsize=9.0, fontweight="bold", color=C_CORAL)
    ax.text(5.03, 3.62,
            "Transfers compact\ncandidate token tree\n& tree attention mask\n\nEdge 1 RTT: ~1.0–1.5 s\nEdge 2 RTT: ~0.5–0.8 s",
            ha="center", va="center", fontsize=7.8, color="#333333", linespacing=1.34)

    box(
        6.60, 2.28, 4.20, 3.24,
        "Server: RTX 4080 SUPER (32 GB, WSL2)",
        "Target Model: Qwen3-14B (FP16, ext4 load ~9 s)\nMedian Tree Verification: $T_{\\mathrm{verify}} \\approx$ 76–78 ms\n\nVariable-Budget Static CUDA Graph Zero-Padding:\n• Single captured CUDA Graph ($B_{\\max}{=}64, M{=}65$)\n• Pad small tree ($K{=}17$) to $65$; redirect KV to dummy slot\n• Safe attention mask & sliced output; only +2.0 ms overhead",
        C_BG_PURPLE, C_PURPLE, C_PURPLE,
    )

    ax.annotate("", xy=(3.91, 4.44), xytext=(3.56, 4.74),
                arrowprops=dict(arrowstyle="<->", color=C_NAVY, lw=1.6))
    ax.annotate("", xy=(3.91, 3.34), xytext=(3.56, 2.94),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL_DARK, lw=1.6))
    ax.annotate("", xy=(6.54, 3.90), xytext=(6.16, 3.90),
                arrowprops=dict(arrowstyle="<->", color=C_PURPLE, lw=1.8))

    ax.text(0.2, 1.70, "(b) Per-Cycle WAN Verification Timeline & Proactive Drafting Latency Hiding ($T_{\\mathrm{overlap}}$)",
            fontsize=9.9, fontweight="bold", color=C_NAVY)

    y1, bh = 1.20, 0.34
    ax.text(0.2, y1 + bh / 2, "Proactive Off\n(Serial Wait)", va="center", ha="left",
            fontsize=8.0, fontweight="bold", color="#444444")
    segs1 = [
        (1.75, 1.35, C_NAVY, "$T_{\\mathrm{draft}}$"),
        (3.10, 3.30, C_CORAL, "$T_{\\mathrm{net}}$ (Uplink + Downlink WAN RTT)"),
        (6.40, 0.85, C_PURPLE, "$T_{\\mathrm{verify}}$"),
        (7.25, 1.35, C_NAVY, "Next $T_{\\mathrm{draft}}$"),
        (8.60, 2.20, C_CORAL, "Next $T_{\\mathrm{net}}$ ..."),
    ]
    for sx, sw, sc, sl in segs1:
        ax.add_patch(mpatches.Rectangle((sx, y1), sw, bh, facecolor=sc, edgecolor="white", lw=0.8, alpha=0.92))
        ax.text(sx + sw / 2, y1 + bh / 2, sl, ha="center", va="center", color="white", fontsize=7.6, fontweight="bold")

    ax.annotate("", xy=(7.80, 1.05), xytext=(8.60, 1.05),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL_DARK, lw=1.4))
    ax.text(8.20, 0.98, "Saved $-T_{\\mathrm{overlap}}$", ha="center", va="top",
            fontsize=7.5, fontweight="bold", color=C_TEAL_DARK)

    y2 = 0.42
    ax.text(0.2, y2 + bh / 2, "Proactive\n(included)", va="center", ha="left",
            fontsize=8.0, fontweight="bold", color=C_TEAL_DARK)
    segs2 = [
        (1.75, 1.35, C_NAVY, "$T_{\\mathrm{draft}}$"),
        (3.10, 3.30, C_CORAL, "$T_{\\mathrm{net}}$ (Wait Window)"),
        (6.40, 0.85, C_PURPLE, "$T_{\\mathrm{verify}}$"),
        (7.25, 0.55, C_AMBER, "Finish"),
        (7.80, 3.00, C_CORAL, "Next $T_{\\mathrm{net}}$ launched early ..."),
    ]
    for sx, sw, sc, sl in segs2:
        ax.add_patch(mpatches.Rectangle((sx, y2), sw, bh, facecolor=sc, edgecolor="white", lw=0.8, alpha=0.92))
        ax.text(sx + sw / 2, y2 + bh / 2, sl, ha="center", va="center",
                color="#1F2937" if sc == C_AMBER else "white", fontsize=7.5, fontweight="bold")

    ov = mpatches.FancyBboxPatch((2.92, 0.08), 3.68, 0.24, boxstyle="round,pad=0.02,rounding_size=0.06",
                                 facecolor=C_TEAL, edgecolor=C_TEAL_DARK, lw=0.9, alpha=0.95)
    ax.add_patch(ov)
    ax.text(2.92 + 3.68 / 2, 0.20, "Edge runs Proactive Draft in parallel (hides $T_{\\mathrm{overlap}}$)",
            ha="center", va="center", color="white", fontsize=7.2, fontweight="bold")

    save_fig(fig, "fig1_architecture_timeline")


def plot_fig2_latency_breakdown(s: dict):
    keys = [
        ("e2_1_node_0.6b", "RTX 5060 Ti\nQwen3-0.6B"),
        ("e2_2_node_1.7b", "RTX 5060 Ti\nQwen3-1.7B"),
        ("e2_3_mac_0.6b", "Apple M4\nQwen3-0.6B"),
        ("e2_4_mac_1.7b", "Apple M4\nQwen3-1.7B"),
    ]
    labels = [lbl for _, lbl in keys]
    drafts = [s[k]["mean_draft_ms"] for k, _ in keys]
    verifies = [s[k]["server_verify_ms"] for k, _ in keys]
    nets = [s[k]["net_rtt_ms"] for k, _ in keys]
    posts = [s[k]["mean_post_ms"] for k, _ in keys]
    rhos = [s[k]["rho"] for k, _ in keys]

    x = np.arange(len(labels))
    w = 0.50
    fig, ax = plt.subplots(figsize=(7.4, 4.45))

    ax.bar(x, drafts, w, label="Edge Draft ($T_{\\mathrm{draft}}$)", color=C_NAVY, edgecolor="white", lw=0.6)
    ax.bar(x, verifies, w, bottom=drafts, label="Server 14B Verify ($T_{\\mathrm{verify}}$)",
           color=C_PURPLE, edgecolor="white", lw=0.6, hatch="///")
    b3 = [d + v for d, v in zip(drafts, verifies)]
    ax.bar(x, nets, w, bottom=b3, label="WAN RTT & Queue ($T_{\\mathrm{net}}$)", color=C_CORAL, edgecolor="white", lw=0.6)
    b4 = [b + n for b, n in zip(b3, nets)]
    ax.bar(x, posts, w, bottom=b4, label="Edge Pre/Post ($T_{\\mathrm{post}}$)", color=C_AMBER, edgecolor="white", lw=0.6)

    totals = [b + p for b, p in zip(b4, posts)]
    for i, (tot, rho, dr, nt, b3_i) in enumerate(zip(totals, rhos, drafts, nets, b3)):
        regime = "Net-Bound" if rho > 5 else "Compute-Sens."
        ax.text(
            i, tot + 35,
            f"{tot:.0f} ms\n$\\rho = {rho:.1f}$ ({regime})",
            ha="center", va="bottom", fontsize=8.3, fontweight="bold",
            color=C_CORAL if rho > 5 else C_TEAL_DARK,
        )
        if dr > 180:
            ax.text(i, dr / 2, f"{dr:.0f} ms", ha="center", va="center",
                    color="white", fontsize=8.2, fontweight="bold")
        if nt > 400:
            ax.text(i, b3_i + nt / 2, f"{nt:.0f} ms", ha="center", va="center",
                    color="white", fontsize=8.2, fontweight="bold")

    ax.set_ylabel("Mean Verification Cycle Latency (ms)", fontsize=9.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.0)
    ax.set_ylim(0, max(totals) * 1.44)
    style_ax(ax)
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC",
              loc="upper center", ncol=2, fontsize=8.3)
    plt.tight_layout()
    save_fig(fig, "fig2_latency_breakdown")


def plot_fig3_matrix_mat_throughput(s: dict):
    keys = [
        ("e2_1_node_0.6b", "5060 Ti\n0.6B", C_NAVY),
        ("e2_2_node_1.7b", "5060 Ti\n1.7B", C_BLUE),
        ("e2_3_mac_0.6b", "M4\n0.6B", C_TEAL),
        ("e2_4_mac_1.7b", "M4\n1.7B", C_TEAL_DARK),
        ("e1_2_server_only", "Server-Only\n14B+0.6B", C_PURPLE),
    ]
    labels = [lbl for _, lbl, _ in keys]
    mats = [s[k]["mean_acc"] for k, _, _ in keys]
    meds = [s[k]["median_acc"] for k, _, _ in keys]
    tputs = [s[k]["throughput_tok_s"] for k, _, _ in keys]
    colors = [c for _, _, c in keys]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    x = np.arange(len(labels))

    bars1 = ax1.bar(x, mats, width=0.52, color=colors, edgecolor="#222222", lw=0.6, label="Mean $\\mathbb{E}[\\tau]$")
    ax1.scatter(x, meds, color=C_AMBER, edgecolor="#222222", marker="D", s=46, zorder=5, label="Median")
    for b, val, med in zip(bars1, mats, meds):
        ax1.text(b.get_x() + b.get_width() / 2, max(val, med) + 0.14, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=8.7, fontweight="bold", color="#1F2937")
    ax1.set_title("(a) Mean Accepted Tokens per Cycle ($d{=}4, B{=}32$)", fontsize=9.8, fontweight="bold", pad=8)
    ax1.set_ylabel("Accepted Tokens / Step", fontsize=9.4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.5)
    ax1.set_ylim(0, 6.25)
    style_ax(ax1)
    ax1.legend(loc="upper center", ncol=2, fontsize=8.2, frameon=True, facecolor="white")

    bars2 = ax2.bar(x, tputs, width=0.52, color=colors, edgecolor="#222222", lw=0.6)
    for b, val in zip(bars2, tputs):
        ax2.text(b.get_x() + b.get_width() / 2, val + 0.30, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=8.7, fontweight="bold", color="#1F2937")

    ab_tput = s["e1_1_auto_batch"]["throughput_tok_s"]
    ax2.axhline(ab_tput, color=C_CORAL, linestyle="--", lw=1.6,
                label=f"Auto-Batch 14B AR Baseline ({ab_tput:.2f} tok/s)")

    ax2.annotate("M4 Dispatch Amortization\n0.6B → 1.7B (+6.0%)", xy=(3, tputs[3] + 1.35), xytext=(1.85, 8.4),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.25),
                 fontsize=7.7, fontweight="bold", color=C_TEAL_DARK, ha="center",
                 bbox=dict(boxstyle="round,pad=0.26", fc=C_BG_TEAL, ec=C_TEAL, lw=0.8))
    ax2.annotate("No Target CUDA Graph\n5.4× Slower Verify", xy=(4, tputs[4] + 1.35), xytext=(3.35, 12.2),
                 arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=1.25),
                 fontsize=7.7, fontweight="bold", color=C_PURPLE, ha="center",
                 bbox=dict(boxstyle="round,pad=0.26", fc=C_BG_PURPLE, ec=C_PURPLE, lw=0.8))

    ax2.set_title("(b) End-to-End Decode Throughput vs. Baselines", fontsize=9.8, fontweight="bold", pad=8)
    ax2.set_ylabel("Decode Throughput (tokens/s)", fontsize=9.4)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.5)
    ax2.set_ylim(0, ab_tput * 1.20)
    style_ax(ax2)
    ax2.legend(loc="upper left", fontsize=8.1, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig3_matrix_mat_throughput")


def plot_fig4_proactive_ablation(s: dict):
    modes = ["disabled\n(Off)", "excluded\n(Default)", "included\n(Merged)"]
    node_keys = ["e3_1_node_1.7b_pro_disabled", "e2_2_node_1.7b", "e3_3_node_1.7b_pro_included"]
    mac_keys = ["e3_4_mac_0.6b_pro_disabled", "e2_3_mac_0.6b", "e3_6_mac_0.6b_pro_included"]

    n_draft = [s[k]["mean_draft_ms"] for k in node_keys]
    m_draft = [s[k]["mean_draft_ms"] for k in mac_keys]
    n_tput = [s[k]["throughput_tok_s"] for k in node_keys]
    m_tput = [s[k]["throughput_tok_s"] for k in mac_keys]

    x = np.arange(len(modes))
    w = 0.34
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.0))

    b1 = ax1.bar(x - w / 2, n_draft, w, label="RTX 5060 Ti (1.7B)", color=C_NAVY, edgecolor="white", lw=0.6)
    b2 = ax1.bar(x + w / 2, m_draft, w, label="Apple M4 (0.6B)", color=C_TEAL, edgecolor="white", lw=0.6)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 10, f"{h:.1f}",
                 ha="center", va="bottom", fontsize=8.4, fontweight="bold")
    ax1.annotate("-18.7%", xy=(2 - w / 2, n_draft[2] + 45), xytext=(2 - w / 2, n_draft[2] + 125),
                 ha="center", fontsize=8.2, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.15))
    ax1.annotate("-14.6%", xy=(2 + w / 2, m_draft[2] + 45), xytext=(2 + w / 2, m_draft[2] + 120),
                 ha="center", fontsize=8.2, fontweight="bold", color=C_TEAL_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.15))

    ax1.set_title("(a) Edge Draft Latency ($T_{\\mathrm{draft}}$) Reduction", fontsize=9.8, fontweight="bold", pad=8)
    ax1.set_ylabel("Mean Draft Latency $T_{\\mathrm{draft}}$ (ms)", fontsize=9.4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes, fontsize=9.0)
    ax1.set_ylim(0, 695)
    style_ax(ax1)
    ax1.legend(loc="upper center", ncol=2, fontsize=8.2, frameon=True, facecolor="white")

    b3 = ax2.bar(x - w / 2, n_tput, w, label="RTX 5060 Ti (1.7B)", color=C_NAVY, edgecolor="white", lw=0.6)
    b4 = ax2.bar(x + w / 2, m_tput, w, label="Apple M4 (0.6B)", color=C_TEAL, edgecolor="white", lw=0.6)
    for b in list(b3) + list(b4):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 0.08, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=8.4, fontweight="bold")
    ax2.text(2 - w / 2, n_tput[2] + 0.38, "+17.0%", ha="center", fontsize=8.1, fontweight="bold", color=C_CORAL)
    ax2.text(2 + w / 2, m_tput[2] + 0.38, "+32.4%*", ha="center", fontsize=8.1, fontweight="bold", color=C_TEAL_DARK)
    ax2.text(0.02, 0.84, "*Gain over default excluded mode", transform=ax2.transAxes,
             fontsize=7.6, color="#555555", va="top")

    ax2.set_title("(b) End-to-End WAN Decode Throughput Gain", fontsize=9.8, fontweight="bold", pad=8)
    ax2.set_ylabel("Decode Throughput (tokens/s)", fontsize=9.4)
    ax2.set_xticks(x)
    ax2.set_xticklabels(modes, fontsize=9.0)
    ax2.set_ylim(0, 4.95)
    style_ax(ax2)
    ax2.legend(loc="upper center", ncol=2, fontsize=8.2, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig4_proactive_ablation")


def plot_fig5_tree_sweep_theory_fit(s: dict):
    node_sweep = [
        (2, 16, "e4_1_node_1.7b_d2_b16"),
        (4, 32, "e2_2_node_1.7b"),
        (6, 48, "e4_2_node_1.7b_d6_b48"),
        (8, 64, "e4_3_node_1.7b_d8_b64"),
    ]
    mac_sweep = [
        (2, 16, "e4_4_mac_0.6b_d2_b16"),
        (4, 32, "e2_3_mac_0.6b"),
        (6, 48, "e4_5_mac_0.6b_d6_b48"),
    ]

    nd = np.array([d for d, _, _ in node_sweep], dtype=float)
    n_dr = np.array([s[k]["mean_draft_ms"] for _, _, k in node_sweep])
    n_mat = np.array([s[k]["mean_acc"] for _, _, k in node_sweep])

    md = np.array([d for d, _, _ in mac_sweep], dtype=float)
    m_dr = np.array([s[k]["mean_draft_ms"] for _, _, k in mac_sweep])
    m_mat = np.array([s[k]["mean_acc"] for _, _, k in mac_sweep])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.2))

    ax1_r = ax1.twinx()
    l1 = ax1.plot(nd, n_dr, "o-", color=C_NAVY, lw=2.0, ms=6.5, label="5060 Ti $T_{\\mathrm{draft}}$ (22.4 ms/layer)")
    l2 = ax1.plot(md, m_dr, "s-", color=C_TEAL, lw=2.0, ms=6.5, label="Apple M4 $T_{\\mathrm{draft}}$ (129.5 ms/layer)")
    l3 = ax1_r.plot(nd, n_mat, "^--", color=C_CORAL, lw=1.7, ms=6.5, label="5060 Ti (1.7B) $\\mathbb{E}[\\tau]$")
    l4 = ax1_r.plot(md, m_mat, "D:", color=C_PURPLE, lw=1.7, ms=5.8, label="Apple M4 (0.6B) $\\mathbb{E}[\\tau]$")

    for dv, rv in zip(nd, n_dr):
        ax1.text(dv, rv + 24, f"{rv:.0f}", ha="center", fontsize=8.0, color=C_NAVY, fontweight="bold")
    for dv, rv in zip(md, m_dr):
        ax1.text(dv, rv + 26, f"{rv:.0f}", ha="center", fontsize=8.0, color=C_TEAL_DARK, fontweight="bold")

    ax1.set_xlabel("Max Speculation Tree Depth $d$ (max_beam_len)", fontsize=9.3)
    ax1.set_ylabel("Edge Draft Latency $T_{\\mathrm{draft}}$ (ms)", fontsize=9.3)
    ax1_r.set_ylabel("Mean Accepted Length $\\mathbb{E}[\\tau]$ (tok/step)", fontsize=9.3, color=C_CORAL)
    ax1.set_xticks([2, 4, 6, 8])
    ax1.set_ylim(0, 910)
    ax1_r.set_ylim(1.5, 6.7)
    ax1.spines["top"].set_visible(False)
    ax1_r.spines["top"].set_visible(False)
    ax1.grid(axis="y", linestyle="--", lw=0.6, alpha=0.35)
    ax1.set_title("(a) Linear Draft Scaling & Sublinear MAT Growth", fontsize=9.8, fontweight="bold", pad=8)
    lines = l1 + l2 + l3 + l4
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left", fontsize=7.6, frameon=True, facecolor="white")

    na, nc = np.polyfit(nd, n_dr, 1)
    ma, mc = np.polyfit(md, m_dr, 1)
    n_mc = np.polyfit(np.log(nd), np.log(n_mat), 1)
    m_mc = np.polyfit(np.log(md), np.log(m_mat), 1)

    d_grid = np.linspace(1.8, 8.2, 120)
    T_wait_node_ref, T_wait_mac_ref = 1150.0, 520.0
    n_meas = (n_dr + T_wait_node_ref) / n_mat
    m_meas = (m_dr + T_wait_mac_ref) / m_mat

    def pred_node(d):
        return (na * d + nc + T_wait_node_ref) / (np.exp(n_mc[1]) * d ** n_mc[0])

    def pred_mac(d):
        return (ma * d + mc + T_wait_mac_ref) / (np.exp(m_mc[1]) * d ** m_mc[0])

    n_pred_at = pred_node(nd)
    r2_node = 1.0 - np.sum((n_meas - n_pred_at) ** 2) / np.sum((n_meas - np.mean(n_meas)) ** 2)

    ax2.plot(d_grid, pred_node(d_grid), "--", color=C_NAVY, lw=1.9, label=f"5060 Ti Eq. (1) Fit ($R^2={r2_node:.3f}$)")
    ax2.scatter(nd, n_meas, color=C_NAVY, s=58, zorder=5, label="5060 Ti Measured (Norm.)")
    ax2.plot(d_grid, pred_mac(d_grid), "--", color=C_TEAL, lw=1.9, label="Apple M4 Eq. (1) Fit")
    ax2.scatter(md, m_meas, color=C_TEAL, marker="s", s=58, zorder=5, label="Apple M4 Measured (Norm.)")

    ax2.annotate("5060 Ti Optimum\n$d{=}8$: TPOT $-45\\%$", xy=(8, n_meas[-1]), xytext=(5.35, 175),
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.3),
                 fontsize=8.1, fontweight="bold", color=C_NAVY,
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_BLUE, ec=C_NAVY, lw=0.7))
    ax2.annotate("M4 Shallow Optimum\n$d{=}2$ (rebounds at $d \\geq 4$)", xy=(2, m_meas[0]), xytext=(2.10, 185),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.3),
                 fontsize=8.0, fontweight="bold", color=C_TEAL_DARK,
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_TEAL, ec=C_TEAL, lw=0.7))

    ax2.set_xlabel("Max Speculation Tree Depth $d$ (max_beam_len)", fontsize=9.3)
    ax2.set_ylabel("Normalized TPOT (ms/token)", fontsize=9.3)
    ax2.set_xticks([2, 4, 6, 8])
    ax2.set_ylim(145, 455)
    style_ax(ax2)
    ax2.set_title("(b) Eq. (1) Analytical Fit & Divergent Optima", fontsize=9.8, fontweight="bold", pad=8)
    ax2.legend(loc="upper right", fontsize=7.6, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig5_tree_sweep_theory_fit")


def plot_fig6_3node_before_after(s: dict):
    base = s["e4_base_3node"]
    opt = s["e4_opt_3node"]

    cats = ["Edge 1\n(5060 Ti / 1.7B)", "Edge 2\n(Apple M4 / 0.6B)", "Cluster Aggregate\n(3-Node Total)"]
    base_tp = [base["node"]["throughput_tok_s"], base["mac"]["throughput_tok_s"], base["aggregate_throughput_tok_s"]]
    opt_tp = [opt["node"]["throughput_tok_s"], opt["mac"]["throughput_tok_s"], opt["aggregate_throughput_tok_s"]]

    base_mat = [base["node"]["mean_acc"], base["mac"]["mean_acc"]]
    opt_mat = [opt["node"]["mean_acc"], opt["mac"]["mean_acc"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    x = np.arange(len(cats))
    w = 0.34

    ax1.bar(x - w / 2, base_tp, w, label="E4-Base: Uniform ($d{=}4, B{=}32$, excluded)", color=C_SLATE, edgecolor="white", lw=0.6)
    ax1.bar(x + w / 2, opt_tp, w, label="E4-Opt: Hetero (5060 Ti 8/64 | M4 2/16, included)", color=C_CORAL, edgecolor="white", lw=0.6)

    for i, (v0, v1) in enumerate(zip(base_tp, opt_tp)):
        gain = (v1 - v0) / v0 * 100.0
        ax1.text(i - w / 2, v0 + 0.12, f"{v0:.2f}", ha="center", va="bottom", fontsize=8.5, color="#333333")
        ax1.text(i + w / 2, v1 + 0.12, f"{v1:.2f}\n({gain:+.1f}%)", ha="center", va="bottom",
                 fontsize=8.4, fontweight="bold", color=C_CORAL if gain >= 0 else C_NAVY)

    ax1.text(0.02, 0.72, "Imbalance Ratio:\n2.20× → 1.23× (-44%)", transform=ax1.transAxes,
             fontsize=7.8, fontweight="bold", color=C_NAVY,
             bbox=dict(boxstyle="round,pad=0.28", fc=C_BG_BLUE, ec=C_NAVY, lw=0.8))

    ax1.set_title("(a) Concurrent 3-Node Throughput (Before vs. After)", fontsize=9.8, fontweight="bold", pad=8)
    ax1.set_ylabel("Decode Throughput (tokens/s)", fontsize=9.4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=8.6)
    ax1.set_ylim(0, max(max(base_tp), max(opt_tp)) * 1.40)
    style_ax(ax1)
    ax1.legend(loc="upper left", fontsize=7.5, frameon=True, facecolor="white")

    x2 = np.arange(2)
    c2 = ["Edge 1 (5060 Ti)\n$d{=}4 \\to d{=}8$", "Edge 2 (Apple M4)\n$d{=}4 \\to d{=}2$"]
    ax2.bar(x2 - w / 2, base_mat, w, label="E4-Base $\\mathbb{E}[\\tau]$", color=C_SLATE, edgecolor="white", lw=0.6)
    ax2.bar(x2 + w / 2, opt_mat, w, label="E4-Opt $\\mathbb{E}[\\tau]$", color=C_TEAL, edgecolor="white", lw=0.6)
    for i, (v0, v1) in enumerate(zip(base_mat, opt_mat)):
        ax2.text(i - w / 2, v0 + 0.12, f"{v0:.2f}", ha="center", va="bottom", fontsize=8.8)
        ax2.text(i + w / 2, v1 + 0.12, f"{v1:.2f}", ha="center", va="bottom",
                 fontsize=8.8, fontweight="bold", color=C_TEAL_DARK)

    ax2.annotate("Server RPCs -28.9%\n(235 → 167 calls)", xy=(0 + w / 2, opt_mat[0] + 0.50), xytext=(0 + w / 2, 6.45),
                 ha="center", fontsize=7.8, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.15),
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_BLUE, ec=C_NAVY, lw=0.75))
    ax2.annotate("Local Draft -64.0%\n(482 → 174 ms)", xy=(1 + w / 2, opt_mat[1] + 0.55), xytext=(1 + w / 2, 4.65),
                 ha="center", fontsize=7.8, fontweight="bold", color=C_TEAL_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.15),
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_TEAL, ec=C_TEAL, lw=0.75))

    ax2.set_title("(b) MAT & Overhead under Variable-Budget Serving", fontsize=9.8, fontweight="bold", pad=8)
    ax2.set_ylabel("Mean Accepted Length $\\mathbb{E}[\\tau]$ (tok/step)", fontsize=9.4)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(c2, fontsize=9.0)
    ax2.set_ylim(0, 8.15)
    style_ax(ax2)
    ax2.legend(loc="upper center", ncol=2, fontsize=8.1, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig6_3node_before_after")


if __name__ == "__main__":
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    plot_fig1_architecture()
    plot_fig2_latency_breakdown(summary)
    plot_fig3_matrix_mat_throughput(summary)
    plot_fig4_proactive_ablation(summary)
    plot_fig5_tree_sweep_theory_fit(summary)
    plot_fig6_3node_before_after(summary)
    print("ALL ENGLISH IEEE FIGURES GENERATED.")
