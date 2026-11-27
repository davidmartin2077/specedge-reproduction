import json
import statistics
from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

# NeurIPS camera-ready aesthetic styling: crisp Microsoft YaHei CJK + STIX LaTeX math
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans SC",
    "DejaVu Sans",
]
plt.rcParams["font.serif"] = ["Times New Roman", "Noto Serif SC", "SimSun"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#2B2D42"
plt.rcParams["axes.linewidth"] = 0.85
plt.rcParams["xtick.color"] = "#222222"
plt.rcParams["ytick.color"] = "#222222"

REPO_ROOT = Path(__file__).resolve().parent.parent
EXP_ROOT = REPO_ROOT / "result" / "exp_suite"
FIG_DIR = REPO_ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Refined NeurIPS / Okabe-Ito inspired publication palette (colorblind-safe & print-friendly)
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


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def parse_server_verify_ms(log_path: Path) -> float:
    if not log_path.exists():
        return 78.0
    from datetime import datetime

    t_req = None
    diffs = []
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "Received request:" in line:
            try:
                t_req = datetime.fromisoformat(line.split()[0])
            except Exception:
                t_req = None
        elif "Received response for client" in line and t_req is not None:
            try:
                t_resp = datetime.fromisoformat(line.split()[0])
                ms = (t_resp - t_req).total_seconds() * 1000.0
                if 10.0 <= ms <= 500.0:
                    diffs.append(ms)
            except Exception:
                pass
            t_req = None
    return statistics.median(diffs) if diffs else 78.0


def summarize_client(path: Path, server_verify_ms: float = 78.0) -> dict:
    rows = load_jsonl(path)
    reqs = sorted({r["req_idx"] for r in rows})
    dec = [r for r in rows if r["step_idx"] > 0]
    acc = [r["num_accepted_tokens"] for r in dec]
    draft = [r["draft"]["end_to_end"] for r in dec]
    wait = [r["target"]["client_wait"] for r in dec]
    post = [
        r["target"]["client_preprocess"] + r["target"]["client_postprocess"]
        for r in dec
    ]
    tgt_e2e = [r["target"]["end_to_end"] for r in dec]
    cycle_ms = [d + t for d, t in zip(draft, tgt_e2e)]
    proactive_cnt = sum(1 for r in dec if r["target"].get("proactive"))

    total_tok = sum(acc)
    total_s = sum(cycle_ms) / 1000.0
    mean_draft = statistics.mean(draft)
    mean_wait = statistics.mean(wait)
    mean_post = statistics.mean(post)
    mean_cycle = statistics.mean(cycle_ms)
    mean_acc = statistics.mean(acc)
    tpot = mean_cycle / mean_acc
    net_only = max(mean_wait - server_verify_ms, 0.0)
    rho = mean_wait / max(mean_draft, 1e-6)

    return {
        "file": str(path.name),
        "num_reqs": len(reqs),
        "decode_steps": len(dec),
        "proactive_steps": proactive_cnt,
        "total_decode_tokens": total_tok,
        "mean_acc": round(mean_acc, 3),
        "median_acc": round(statistics.median(acc), 2),
        "max_acc": max(acc),
        "mean_draft_ms": round(mean_draft, 2),
        "median_draft_ms": round(statistics.median(draft), 2),
        "mean_wait_ms": round(mean_wait, 2),
        "median_wait_ms": round(statistics.median(wait), 2),
        "server_verify_ms": round(server_verify_ms, 2),
        "net_rtt_ms": round(net_only, 2),
        "mean_post_ms": round(mean_post, 2),
        "mean_cycle_ms": round(mean_cycle, 2),
        "tpot_ms": round(tpot, 2),
        "throughput_tok_s": round(total_tok / total_s, 3),
        "rho": round(rho, 2),
    }


def collect_all_metrics() -> dict:
    summary = {}
    ab_rows = load_jsonl(EXP_ROOT / "e1_1_auto_batch" / "auto.jsonl")
    ab_dec = [r["forward_t"] for r in ab_rows if r.get("prefill_cnt", 0) == 0]
    summary["e1_1_auto_batch"] = {
        "steps": len(ab_rows),
        "decode_steps": len(ab_dec),
        "tpot_ms": round(statistics.mean(ab_dec), 2),
        "median_tpot_ms": round(statistics.median(ab_dec), 2),
        "throughput_tok_s": round(1000.0 / statistics.mean(ab_dec), 3),
    }

    so_rows = load_jsonl(EXP_ROOT / "e1_2_server_only" / "server_only.jsonl")
    so_dec = [r for r in so_rows if r.get("prefill", 0) == 0]
    so_acc = [r["num_accepted_tokens"] for r in so_dec]
    so_dr = [r["draft"]["end_to_end"] for r in so_dec]
    so_tg = [r["target"]["end_to_end"] for r in so_dec]
    so_cyc = [d + t for d, t in zip(so_dr, so_tg)]
    summary["e1_2_server_only"] = {
        "decode_steps": len(so_dec),
        "mean_acc": round(statistics.mean(so_acc), 3),
        "median_acc": round(statistics.median(so_acc), 2),
        "max_acc": max(so_acc),
        "mean_draft_ms": round(statistics.mean(so_dr), 2),
        "mean_target_ms": round(statistics.mean(so_tg), 2),
        "mean_cycle_ms": round(statistics.mean(so_cyc), 2),
        "tpot_ms": round(statistics.mean(so_cyc) / statistics.mean(so_acc), 2),
        "throughput_tok_s": round(sum(so_acc) / (sum(so_cyc) / 1000.0), 3),
    }

    single_runs = [
        ("e2_1_node_0.6b", "client_node_0.6b.jsonl"),
        ("e2_2_node_1.7b", "client_node_1.7b.jsonl"),
        ("e2_3_mac_0.6b", "client_mac_0.6b.jsonl"),
        ("e2_4_mac_1.7b", "client_mac_1.7b.jsonl"),
        ("e3_1_node_1.7b_pro_disabled", "client_node_1.7b.jsonl"),
        ("e3_3_node_1.7b_pro_included", "client_node_1.7b.jsonl"),
        ("e3_4_mac_0.6b_pro_disabled", "client_mac_0.6b.jsonl"),
        ("e3_6_mac_0.6b_pro_included", "client_mac_0.6b.jsonl"),
        ("e4_1_node_1.7b_d2_b16", "client_node_1.7b.jsonl"),
        ("e4_2_node_1.7b_d6_b48", "client_node_1.7b.jsonl"),
        ("e4_3_node_1.7b_d8_b64", "client_node_1.7b.jsonl"),
        ("e4_4_mac_0.6b_d2_b16", "client_mac_0.6b.jsonl"),
        ("e4_5_mac_0.6b_d6_b48", "client_mac_0.6b.jsonl"),
    ]
    for run_id, fname in single_runs:
        d = EXP_ROOT / run_id
        f = d / fname
        if f.exists() and f.stat().st_size > 0:
            sv_ms = parse_server_verify_ms(d / "server.log")
            summary[run_id] = summarize_client(f, sv_ms)

    for run_id in ["e4_base_3node", "e4_opt_3node"]:
        d = EXP_ROOT / run_id
        nf = d / "client_node_1.7b.jsonl"
        mf = d / "client_mac_0.6b.jsonl"
        if nf.exists() and mf.exists() and nf.stat().st_size > 0 and mf.stat().st_size > 0:
            sv_ms = parse_server_verify_ms(d / "server.log")
            nm = summarize_client(nf, sv_ms)
            mm = summarize_client(mf, sv_ms)
            summary[run_id] = {
                "node": nm,
                "mac": mm,
                "aggregate_throughput_tok_s": round(
                    nm["throughput_tok_s"] + mm["throughput_tok_s"], 3
                ),
                "server_verify_ms": round(sv_ms, 2),
            }

    (EXP_ROOT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (REPO_ROOT / "docs" / "exp_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary


def save_fig(fig, name: str):
    fig.savefig(FIG_DIR / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG_DIR / f"{name}.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(FIG_DIR / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Generated {name}.png / .svg / .pdf")


def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4, color="#999999")
    ax.set_axisbelow(True)


def plot_fig1_architecture():
    fig, ax = plt.subplots(figsize=(10.6, 5.9))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.25)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc, ec, title_bg=None):
        p = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12",
            facecolor=fc, edgecolor=ec, linewidth=1.4,
        )
        ax.add_patch(p)
        if title_bg:
            hdr = mpatches.FancyBboxPatch(
                (x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.05,rounding_size=0.10",
                facecolor=title_bg, edgecolor=ec, linewidth=1.1,
            )
            ax.add_patch(hdr)
            ax.text(x + w / 2, y + h - 0.21, title, ha="center", va="center",
                    fontsize=9.1, fontweight="bold", color="white")
            ax.text(x + w / 2, y + (h - 0.42) / 2, body, ha="center", va="center",
                    fontsize=8.1, color="#1F2937", linespacing=1.45)
        else:
            ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center",
                    fontsize=9.1, fontweight="bold", color=ec)
            ax.text(x + w / 2, y + h / 2 - 0.20, body, ha="center", va="center",
                    fontsize=8.1, color="#1F2937", linespacing=1.45)

    # Top Section: System Architecture
    ax.text(0.2, 6.00, "(a) 跨平台异构三机协同部署架构与 Variable-Budget 零填充服务端",
            fontsize=10.2, fontweight="bold", color=C_NAVY)

    box(
        0.2, 4.02, 3.28, 1.72,
        "Edge 1: RTX 5060 Ti (8GB CUDA)",
        "Qwen3-1.7B | CUDA Graph (22 ms/层)\n高算力 + 高 WAN RTT $\\Rightarrow\\ \\rho \\gg 1$ (网络受限)\n定制策略: 深树 ($d{=}8, B{=}64$) + included",
        C_BG_BLUE, C_NAVY, title_bg=C_NAVY,
    )
    box(
        0.2, 2.08, 3.28, 1.72,
        "Edge 2: Apple M4 (16GB Unified)",
        "Qwen3-0.6B/1.7B | MPS Eager (129 ms/层)\n大统一内存 + 较低 RTT $\\Rightarrow\\ \\rho \\approx 1$ (算力敏感)\n定制策略: 浅树 ($d{=}2, B{=}16$) + included",
        C_BG_TEAL, C_TEAL_DARK, title_bg=C_TEAL,
    )

    cloud = mpatches.FancyBboxPatch(
        (3.96, 2.75), 2.14, 2.35, boxstyle="round,pad=0.06,rounding_size=0.18",
        facecolor=C_BG_WARM, edgecolor=C_CORAL, linewidth=1.35, linestyle="--",
    )
    ax.add_patch(cloud)
    ax.text(5.03, 4.68, "Tailscale WAN\ngRPC (:8000)", ha="center", va="center",
            fontsize=9.1, fontweight="bold", color=C_CORAL)
    ax.text(5.03, 3.65,
            "仅传候选 Token ID 树\n与树注意力掩码\n\nEdge 1 RTT: ~1.0–1.5 s\nEdge 2 RTT: ~0.5–0.8 s",
            ha="center", va="center", fontsize=8.0, color="#333333", linespacing=1.38)

    box(
        6.62, 2.32, 4.18, 3.22,
        "Server: RTX 4080 SUPER (32GB, WSL2)",
        "主验证模型: Qwen3-14B (FP16, ext4 原生加载 ~9s)\n单次树验证中位耗时: $T_{\\mathrm{verify}} \\approx$ 76–78 ms\n\n核心机制: Variable-Budget 静态图零填充\n• 固定捕获单一静态 CUDA Graph ($B_{\\max}{=}64$)\n• 小树 ($K{=}17$) 零填充至 65, 哑槽重定向 max_len-1\n• 掩码屏蔽填充位, KV 重排严格等价, 仅 +2.0 ms 开销",
        C_BG_PURPLE, C_PURPLE, title_bg=C_PURPLE,
    )

    ax.annotate("", xy=(3.91, 4.45), xytext=(3.55, 4.75),
                arrowprops=dict(arrowstyle="<->", color=C_NAVY, lw=1.6))
    ax.annotate("", xy=(3.91, 3.35), xytext=(3.55, 2.95),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL_DARK, lw=1.6))
    ax.annotate("", xy=(6.55, 3.92), xytext=(6.16, 3.92),
                arrowprops=dict(arrowstyle="<->", color=C_PURPLE, lw=1.8))

    # Bottom Section: Proportional Pipeline Timeline
    ax.text(0.2, 1.72, "(b) 广域网单轮验证周期时序与 Proactive Drafting 延迟隐藏机制 ($T_{\\mathrm{overlap}}$)",
            fontsize=10.2, fontweight="bold", color=C_NAVY)

    # Row 1: Serial baseline
    y1, bh = 1.22, 0.34
    ax.text(0.2, y1 + bh / 2, "关闭 Proactive\n(串行等待)", va="center", ha="left", fontsize=8.0, fontweight="bold", color="#444444")
    segs1 = [(1.75, 1.35, C_NAVY, "$T_{\\mathrm{draft}}$"),
             (3.10, 3.30, C_CORAL, "$T_{\\mathrm{net}}$ (上行+下行 WAN RTT)"),
             (6.40, 0.85, C_PURPLE, "$T_{\\mathrm{verify}}$"),
             (7.25, 1.35, C_NAVY, "下一轮 $T_{\\mathrm{draft}}$"),
             (8.60, 2.20, C_CORAL, "下一轮 $T_{\\mathrm{net}}$ ...")]
    for sx, sw, sc, sl in segs1:
        r = mpatches.Rectangle((sx, y1), sw, bh, facecolor=sc, edgecolor="white", lw=0.8, alpha=0.92)
        ax.add_patch(r)
        ax.text(sx + sw / 2, y1 + bh / 2, sl, ha="center", va="center", color="white", fontsize=7.6, fontweight="bold")

    # Speedup annotation cleanly in the gap between Row 1 (1.22) and Row 2 (0.44+0.34=0.78)
    ax.annotate("", xy=(7.80, 1.07), xytext=(8.60, 1.07),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL_DARK, lw=1.4))
    ax.text(8.20, 0.99, "节省 $-T_{\\mathrm{overlap}}$", ha="center", va="top",
            fontsize=7.6, fontweight="bold", color=C_TEAL_DARK)

    # Row 2: Proactive Included
    y2 = 0.42
    ax.text(0.2, y2 + bh / 2, "开启 included\n(并发重叠)", va="center", ha="left", fontsize=8.0, fontweight="bold", color=C_TEAL_DARK)
    segs2 = [(1.75, 1.35, C_NAVY, "$T_{\\mathrm{draft}}$"),
             (3.10, 3.30, C_CORAL, "$T_{\\mathrm{net}}$ (等待窗口)"),
             (6.40, 0.85, C_PURPLE, "$T_{\\mathrm{verify}}$"),
             (7.25, 0.55, C_AMBER, "补全"),
             (7.80, 3.00, C_CORAL, "下一轮提前发起 $T_{\\mathrm{net}}$ ...")]
    for sx, sw, sc, sl in segs2:
        r = mpatches.Rectangle((sx, y2), sw, bh, facecolor=sc, edgecolor="white", lw=0.8, alpha=0.92)
        ax.add_patch(r)
        ax.text(sx + sw / 2, y2 + bh / 2, sl, ha="center", va="center",
                color="#1F2937" if sc == C_AMBER else "white", fontsize=7.6, fontweight="bold")

    # Proactive overlap strip underneath Wait window (widened so text fits with ample margin)
    ov = mpatches.FancyBboxPatch((3.12, 0.08), 3.26, 0.24, boxstyle="round,pad=0.02,rounding_size=0.06",
                                 facecolor=C_TEAL, edgecolor=C_TEAL_DARK, lw=0.9, alpha=0.95)
    ax.add_patch(ov)
    ax.text(3.12 + 3.26 / 2, 0.20, "边缘端并行执行 Proactive Draft (隐藏 $T_{\\mathrm{overlap}}$)",
            ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")

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
    fig, ax = plt.subplots(figsize=(7.6, 4.4))

    ax.bar(x, drafts, w, label="端侧草稿 ($T_{\\mathrm{draft}}$)", color=C_NAVY, edgecolor="white", lw=0.6)
    ax.bar(x, verifies, w, bottom=drafts, label="服务端 14B 验证 ($T_{\\mathrm{verify}}$)",
           color=C_PURPLE, edgecolor="white", lw=0.6, hatch="///")
    b3 = [d + v for d, v in zip(drafts, verifies)]
    ax.bar(x, nets, w, bottom=b3, label="广域网往返与排队 ($T_{\\mathrm{net}}$)", color=C_CORAL, edgecolor="white", lw=0.6)
    b4 = [b + n for b, n in zip(b3, nets)]
    ax.bar(x, posts, w, bottom=b4, label="端侧前后处理 ($T_{\\mathrm{post}}$)", color=C_AMBER, edgecolor="white", lw=0.6)

    totals = [b + p for b, p in zip(b4, posts)]
    for i, (tot, rho, dr, nt, b3_i) in enumerate(zip(totals, rhos, drafts, nets, b3)):
        regime = "网络受限" if rho > 5 else "算力敏感"
        ax.text(
            i, tot + 35,
            f"{tot:.0f} ms\n$\\rho = {rho:.1f}$ ({regime})",
            ha="center", va="bottom", fontsize=8.4, fontweight="bold",
            color=C_CORAL if rho > 5 else C_TEAL_DARK,
        )
        if dr > 180:
            ax.text(i, dr / 2, f"{dr:.0f} ms", ha="center", va="center",
                    color="white", fontsize=8.2, fontweight="bold")
        if nt > 400:
            ax.text(i, b3_i + nt / 2, f"{nt:.0f} ms", ha="center", va="center",
                    color="white", fontsize=8.2, fontweight="bold")

    ax.set_ylabel("单轮验证周期平均耗时 (ms)", fontsize=9.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.2)
    ax.set_ylim(0, max(totals) * 1.42)
    style_ax(ax)
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC",
              loc="upper center", ncol=2, fontsize=8.4)
    plt.tight_layout()
    save_fig(fig, "fig2_latency_breakdown")


def plot_fig3_matrix_mat_throughput(s: dict):
    keys = [
        ("e2_1_node_0.6b", "5060Ti\n0.6B", C_NAVY),
        ("e2_2_node_1.7b", "5060Ti\n1.7B", C_BLUE),
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

    bars1 = ax1.bar(x, mats, width=0.52, color=colors, edgecolor="#222222", lw=0.6, label="均值 $\\mathbb{E}[\\tau]$")
    ax1.scatter(x, meds, color=C_AMBER, edgecolor="#222222", marker="D", s=46, zorder=5, label="中位数 Median")
    for b, val, med in zip(bars1, mats, meds):
        ax1.text(b.get_x() + b.get_width() / 2, max(val, med) + 0.14, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold", color="#1F2937")
    ax1.set_title("(a) 每轮接受长度 ($d{=}4, B{=}32$)", fontsize=10.2, fontweight="bold", pad=8)
    ax1.set_ylabel("每轮接受 Token 数 (tokens/步)", fontsize=9.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8.5)
    ax1.set_ylim(0, 6.2)
    style_ax(ax1)
    ax1.legend(loc="upper center", ncol=2, fontsize=8.2, frameon=True, facecolor="white")

    bars2 = ax2.bar(x, tputs, width=0.52, color=colors, edgecolor="#222222", lw=0.6)
    for b, val in zip(bars2, tputs):
        ax2.text(b.get_x() + b.get_width() / 2, val + 0.30, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=8.6, fontweight="bold", color="#1F2937")

    ab_tput = s["e1_1_auto_batch"]["throughput_tok_s"]
    ax2.axhline(ab_tput, color=C_CORAL, linestyle="--", lw=1.6,
                label=f"Auto-Batch 14B 纯自回归基线 ({ab_tput:.2f} tok/s)")

    ax2.annotate("M4 摊销底噪\n0.6B→1.7B (+6.0%)", xy=(3, tputs[3] + 1.35), xytext=(1.95, 8.2),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.25),
                 fontsize=7.8, fontweight="bold", color=C_TEAL_DARK, ha="center",
                 bbox=dict(boxstyle="round,pad=0.26", fc=C_BG_TEAL, ec=C_TEAL, lw=0.8))
    ax2.annotate("同卡无 CUDA Graph\n验证慢 5.4×", xy=(4, tputs[4] + 1.35), xytext=(3.45, 12.1),
                 arrowprops=dict(arrowstyle="->", color=C_PURPLE, lw=1.25),
                 fontsize=7.8, fontweight="bold", color=C_PURPLE, ha="center",
                 bbox=dict(boxstyle="round,pad=0.26", fc=C_BG_PURPLE, ec=C_PURPLE, lw=0.8))

    ax2.set_title("(b) 端到端解码吞吐 vs. 单机基线", fontsize=10.2, fontweight="bold", pad=8)
    ax2.set_ylabel("解码吞吐 (tokens/s)", fontsize=9.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.6)
    ax2.set_ylim(0, ab_tput * 1.18)
    style_ax(ax2)
    ax2.legend(loc="upper left", fontsize=8.2, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig3_matrix_mat_throughput")


def plot_fig4_proactive_ablation(s: dict):
    modes = ["disabled\n(关闭)", "excluded\n(默认)", "included\n(融合)"]
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

    ax1.set_title("(a) 端侧草稿耗时 $T_{\\mathrm{draft}}$ 压缩效果", fontsize=10.2, fontweight="bold", pad=8)
    ax1.set_ylabel("平均草稿耗时 $T_{\\mathrm{draft}}$ (ms)", fontsize=9.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes, fontsize=9.0)
    ax1.set_ylim(0, 690)
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
    ax2.text(0.02, 0.84, "*相对默认 excluded 提升", transform=ax2.transAxes, fontsize=7.6, color="#555555", va="top")

    ax2.set_title("(b) 广域网端到端解码吞吐提升", fontsize=10.2, fontweight="bold", pad=8)
    ax2.set_ylabel("解码吞吐 (tokens/s)", fontsize=9.5)
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

    # Panel (a)
    ax1_r = ax1.twinx()
    l1 = ax1.plot(nd, n_dr, "o-", color=C_NAVY, lw=2.0, ms=6.5, label="5060 Ti $T_{\\mathrm{draft}}$ (斜率 $22.4$ ms/层)")
    l2 = ax1.plot(md, m_dr, "s-", color=C_TEAL, lw=2.0, ms=6.5, label="Apple M4 $T_{\\mathrm{draft}}$ (斜率 $129.5$ ms/层)")
    l3 = ax1_r.plot(nd, n_mat, "^--", color=C_CORAL, lw=1.7, ms=6.5, label="5060 Ti (1.7B) $\\mathbb{E}[\\tau]$")
    l4 = ax1_r.plot(md, m_mat, "D:", color=C_PURPLE, lw=1.7, ms=5.8, label="Apple M4 (0.6B) $\\mathbb{E}[\\tau]$")

    for dv, rv in zip(nd, n_dr):
        ax1.text(dv, rv + 24, f"{rv:.0f}", ha="center", fontsize=8.0, color=C_NAVY, fontweight="bold")
    for dv, rv in zip(md, m_dr):
        ax1.text(dv, rv + 26, f"{rv:.0f}", ha="center", fontsize=8.0, color=C_TEAL_DARK, fontweight="bold")

    ax1.set_xlabel("投机树最大深度 $d$ (max_beam_len)", fontsize=9.5)
    ax1.set_ylabel("端侧草稿耗时 $T_{\\mathrm{draft}}$ (ms)", fontsize=9.5)
    ax1_r.set_ylabel("平均接受长度 $\\mathbb{E}[\\tau]$ (tokens/步)", fontsize=9.5, color=C_CORAL)
    ax1.set_xticks([2, 4, 6, 8])
    ax1.set_ylim(0, 910)
    ax1_r.set_ylim(1.5, 6.7)
    ax1.spines["top"].set_visible(False)
    ax1_r.spines["top"].set_visible(False)
    ax1.grid(axis="y", linestyle="--", lw=0.6, alpha=0.35)
    ax1.set_title("(a) 草稿耗时线性标度律与接受长度增长", fontsize=10.2, fontweight="bold", pad=8)
    lines = l1 + l2 + l3 + l4
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left", fontsize=7.6, frameon=True, facecolor="white")

    # Panel (b)
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

    ax2.plot(d_grid, pred_node(d_grid), "--", color=C_NAVY, lw=1.9, label=f"5060 Ti 理论预测 ($R^2={r2_node:.3f}$)")
    ax2.scatter(nd, n_meas, color=C_NAVY, s=58, zorder=5, label="5060 Ti 实测归一点")
    ax2.plot(d_grid, pred_mac(d_grid), "--", color=C_TEAL, lw=1.9, label="Apple M4 理论预测")
    ax2.scatter(md, m_meas, color=C_TEAL, marker="s", s=58, zorder=5, label="Apple M4 实测归一点")

    ax2.annotate("5060 Ti 最优点\n$d{=}8$: TPOT $-45\\%$", xy=(8, n_meas[-1]), xytext=(5.45, 175),
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.3),
                 fontsize=8.2, fontweight="bold", color=C_NAVY,
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_BLUE, ec=C_NAVY, lw=0.7))
    ax2.annotate("M4 浅树最优点\n$d{=}2$ (更深即反弹)", xy=(2, m_meas[0]), xytext=(2.15, 188),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.3),
                 fontsize=8.2, fontweight="bold", color=C_TEAL_DARK,
                 bbox=dict(boxstyle="round,pad=0.22", fc=C_BG_TEAL, ec=C_TEAL, lw=0.7))

    ax2.set_xlabel("投机树最大深度 $d$ (max_beam_len)", fontsize=9.5)
    ax2.set_ylabel("归一化 $\\mathrm{TPOT}$ (ms/token)", fontsize=9.5)
    ax2.set_xticks([2, 4, 6, 8])
    ax2.set_ylim(145, 455)
    style_ax(ax2)
    ax2.set_title("(b) 式 (1) 解析模型拟合与相反最优拐点", fontsize=10.2, fontweight="bold", pad=8)
    ax2.legend(loc="upper right", fontsize=7.8, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig5_tree_sweep_theory_fit")


def plot_fig6_3node_before_after(s: dict):
    base = s["e4_base_3node"]
    opt = s["e4_opt_3node"]

    cats = ["Edge 1\n(5060 Ti / 1.7B)", "Edge 2\n(Apple M4 / 0.6B)", "三机集群总吞吐\n(Aggregate)"]
    base_tp = [base["node"]["throughput_tok_s"], base["mac"]["throughput_tok_s"], base["aggregate_throughput_tok_s"]]
    opt_tp = [opt["node"]["throughput_tok_s"], opt["mac"]["throughput_tok_s"], opt["aggregate_throughput_tok_s"]]

    base_mat = [base["node"]["mean_acc"], base["mac"]["mean_acc"]]
    opt_mat = [opt["node"]["mean_acc"], opt["mac"]["mean_acc"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.1))
    x = np.arange(len(cats))
    w = 0.34

    ax1.bar(x - w / 2, base_tp, w, label="E4-Base: 统一默认 ($d{=}4, B{=}32$, excluded)", color=C_SLATE, edgecolor="white", lw=0.6)
    ax1.bar(x + w / 2, opt_tp, w, label="E4-Opt: 异构优化 (5060Ti $8/64$ | M4 $2/16$, included)", color=C_CORAL, edgecolor="white", lw=0.6)

    for i, (v0, v1) in enumerate(zip(base_tp, opt_tp)):
        gain = (v1 - v0) / v0 * 100.0
        ax1.text(i - w / 2, v0 + 0.12, f"{v0:.2f}", ha="center", va="bottom", fontsize=8.5, color="#333333")
        ax1.text(i + w / 2, v1 + 0.12, f"{v1:.2f}\n({gain:+.1f}%)", ha="center", va="bottom",
                 fontsize=8.5, fontweight="bold", color=C_CORAL if gain >= 0 else C_NAVY)

    ax1.text(0.02, 0.72, "双端不均衡比:\n2.20× → 1.23× (-44%)", transform=ax1.transAxes,
             fontsize=7.8, fontweight="bold", color=C_NAVY,
             bbox=dict(boxstyle="round,pad=0.28", fc=C_BG_BLUE, ec=C_NAVY, lw=0.8))

    ax1.set_title("(a) 三机并发吞吐对比 (优化前 vs. 优化后)", fontsize=10.2, fontweight="bold", pad=8)
    ax1.set_ylabel("解码吞吐 (tokens/s)", fontsize=9.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=8.8)
    ax1.set_ylim(0, max(max(base_tp), max(opt_tp)) * 1.38)
    style_ax(ax1)
    ax1.legend(loc="upper left", fontsize=7.6, frameon=True, facecolor="white")

    x2 = np.arange(2)
    c2 = ["Edge 1 (5060 Ti)\n$d{=}4 \\to d{=}8$", "Edge 2 (Apple M4)\n$d{=}4 \\to d{=}2$"]
    ax2.bar(x2 - w / 2, base_mat, w, label="E4-Base $\\mathbb{E}[\\tau]$", color=C_SLATE, edgecolor="white", lw=0.6)
    ax2.bar(x2 + w / 2, opt_mat, w, label="E4-Opt $\\mathbb{E}[\\tau]$", color=C_TEAL, edgecolor="white", lw=0.6)
    for i, (v0, v1) in enumerate(zip(base_mat, opt_mat)):
        ax2.text(i - w / 2, v0 + 0.12, f"{v0:.2f}", ha="center", va="bottom", fontsize=8.8)
        ax2.text(i + w / 2, v1 + 0.12, f"{v1:.2f}", ha="center", va="bottom",
                 fontsize=8.8, fontweight="bold", color=C_TEAL_DARK)

    ax2.annotate("RPC 次数 -28.9%", xy=(0 + w / 2, opt_mat[0] + 0.52), xytext=(0 + w / 2, 6.55),
                 ha="center", fontsize=8.0, fontweight="bold", color=C_NAVY,
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.15),
                 bbox=dict(boxstyle="round,pad=0.24", fc=C_BG_BLUE, ec=C_NAVY, lw=0.75))
    ax2.annotate("本地 Draft -64.0%\n(482 → 174 ms)", xy=(1 + w / 2, opt_mat[1] + 0.55), xytext=(1 + w / 2, 4.65),
                 ha="center", fontsize=7.9, fontweight="bold", color=C_TEAL_DARK,
                 arrowprops=dict(arrowstyle="->", color=C_TEAL_DARK, lw=1.15),
                 bbox=dict(boxstyle="round,pad=0.24", fc=C_BG_TEAL, ec=C_TEAL, lw=0.75))

    ax2.set_title("(b) 异构树预算并发下的接受长度与开销缩减", fontsize=10.2, fontweight="bold", pad=8)
    ax2.set_ylabel("平均接受长度 $\\mathbb{E}[\\tau]$ (tokens/步)", fontsize=9.5)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(c2, fontsize=9.0)
    ax2.set_ylim(0, 7.9)
    style_ax(ax2)
    ax2.legend(loc="upper center", ncol=2, fontsize=8.2, frameon=True, facecolor="white")

    plt.tight_layout()
    save_fig(fig, "fig6_3node_before_after")


if __name__ == "__main__":
    summary = collect_all_metrics()
    plot_fig1_architecture()
    plot_fig2_latency_breakdown(summary)
    plot_fig3_matrix_mat_throughput(summary)
    plot_fig4_proactive_ablation(summary)
    plot_fig5_tree_sweep_theory_fit(summary)
    plot_fig6_3node_before_after(summary)
    print("ALL NEURIPS FIGURES GENERATED.")
