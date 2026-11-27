import json
import math
import statistics
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

matplotlib.use("Agg")

# Configure clean publication-ready styling with Chinese font support
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "Arial Unicode MS",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8

REPO_ROOT = Path(__file__).resolve().parent.parent
EXP_ROOT = REPO_ROOT / "result" / "exp_suite"
FIG_DIR = REPO_ROOT / "docs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Harmonious academic palette
C_NAVY = "#1B365D"
C_TEAL = "#2A9D8F"
C_CORAL = "#E07A5F"
C_AMBER = "#E9C46A"
C_PURPLE = "#6A4C93"
C_SLATE = "#6C757D"
C_BLUE = "#3A86FF"
C_LIGHT = "#F4F6F9"


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def parse_server_verify_ms(log_path: Path) -> float:
    """Estimate actual 14B server verify duration from server.log Request->Response pairs."""
    if not log_path.exists():
        return 78.0
    from datetime import datetime

    t_req = None
    diffs = []
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "Received request:" in line:
            try:
                ts = line.split()[0]
                t_req = datetime.fromisoformat(ts)
            except Exception:
                t_req = None
        elif "Received response for client" in line and t_req is not None:
            try:
                ts = line.split()[0]
                t_resp = datetime.fromisoformat(ts)
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
    med_draft = statistics.median(draft)
    med_wait = statistics.median(wait)
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
        "median_draft_ms": round(med_draft, 2),
        "mean_wait_ms": round(mean_wait, 2),
        "median_wait_ms": round(med_wait, 2),
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

    # E1-1 Auto-Batch
    ab_rows = load_jsonl(EXP_ROOT / "e1_1_auto_batch" / "auto.jsonl")
    ab_dec = [r["forward_t"] for r in ab_rows if r.get("prefill_cnt", 0) == 0]
    summary["e1_1_auto_batch"] = {
        "steps": len(ab_rows),
        "decode_steps": len(ab_dec),
        "tpot_ms": round(statistics.mean(ab_dec), 2),
        "median_tpot_ms": round(statistics.median(ab_dec), 2),
        "throughput_tok_s": round(1000.0 / statistics.mean(ab_dec), 3),
    }

    # E1-2 Server-Only
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

    # Single-client runs
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

    # 3-node concurrent runs
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

    out_json = EXP_ROOT / "summary.json"
    out_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Saved summary to {out_json}")
    return summary


def save_fig(fig, name: str):
    fig.savefig(FIG_DIR / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG_DIR / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Generated {name}.png and {name}.svg")


def plot_fig1_architecture():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    # Title
    ax.text(
        5.5, 5.15,
        "异构跨平台 SpecEdge 三机协同架构与 Variable-Budget 流水线示意图",
        ha="center", va="center", fontsize=13, fontweight="bold", color=C_NAVY,
    )

    def draw_box(x, y, w, h, title, body, fc, ec):
        box = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.14",
            facecolor=fc, edgecolor=ec, linewidth=1.6,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center",
                fontsize=10, fontweight="bold", color=ec)
        ax.text(x + w / 2, y + h / 2 - 0.16, body, ha="center", va="center",
                fontsize=8.5, color="#222222", linespacing=1.45)

    # Edge 1 (5060 Ti)
    draw_box(
        0.3, 3.05, 3.1, 1.65,
        "Edge 1: RTX 5060 Ti (8GB CUDA)",
        "Qwen3-1.7B | CUDA Graph\n高算力 (T_draft 极低) / 高 WAN RTT\n瓶颈比 ρ >> 1 (网络受限型)\n最优策略: 深树 (d=8, b=64) + included",
        "#EEF6FF", C_NAVY,
    )
    # Edge 2 (M4)
    draw_box(
        0.3, 0.75, 3.1, 1.65,
        "Edge 2: Apple M4 (16GB Unified)",
        "Qwen3-0.6B/1.7B | MPS Eager 补丁\n大统一内存 / 调度开销高 / 较低 RTT\n瓶颈比 ρ ≈ 1 (算力敏感型)\n最优策略: 浅树 (d=2, b=16) + included",
        "#EDF7F6", C_TEAL,
    )
    # Tailscale WAN cloud
    cloud = mpatches.FancyBboxPatch(
        (4.05, 1.7), 2.15, 2.0, boxstyle="round,pad=0.08,rounding_size=0.25",
        facecolor="#FFF8EE", edgecolor=C_CORAL, linewidth=1.4, linestyle="--",
    )
    ax.add_patch(cloud)
    ax.text(5.125, 3.2, "Tailscale WAN\n+ gRPC (:8000)", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color=C_CORAL)
    ax.text(5.125, 2.35, "异构网络 RTT:\nEdge 1: ~1.0–1.5s\nEdge 2: ~0.5–0.8s\n仅传候选 token ID 树",
            ha="center", va="center", fontsize=8.2, color="#444444", linespacing=1.4)

    # Server (4080S)
    draw_box(
        6.9, 1.25, 3.8, 2.95,
        "Server: RTX 4080 SUPER (32GB, WSL2)",
        "主模型: Qwen3-14B (FP16, ext4 快速加载)\n单次验证耗时: T_verify ≈ 75–85 ms\n\n核心改进: Variable-Budget 零填充\n• 固定静态 CUDA Graph (max_budget=64)\n• 小树 (b=16) 自动零填充+掩码屏蔽\n• 单卡无重编译并发服务异构树预算",
        "#F6F2FA", C_PURPLE,
    )

    # Arrows
    ax.annotate("", xy=(4.0, 3.45), xytext=(3.48, 3.75),
                arrowprops=dict(arrowstyle="<->", color=C_NAVY, lw=1.6))
    ax.annotate("", xy=(4.0, 2.1), xytext=(3.48, 1.65),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL, lw=1.6))
    ax.annotate("", xy=(6.82, 2.7), xytext=(6.28, 2.7),
                arrowprops=dict(arrowstyle="<->", color=C_PURPLE, lw=1.8))

    # Bottom mini-legend bar showing Proactive Overlap
    ax.text(0.3, 0.25,
            "单轮时序重叠机制:  [ Edge Draft ] ---> [ 发送候选树 (T_net) + Server 14B 验证 (T_verify) ]  (期间 Edge 同步执行 Proactive Drafting 隐藏延迟 T_overlap)",
            fontsize=8.3, color="#333333",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8F9FA", edgecolor="#CCCCCC"))

    save_fig(fig, "fig1_architecture_timeline")


def plot_fig2_latency_breakdown(s: dict):
    keys = [
        ("e2_1_node_0.6b", "5060 Ti\n0.6B"),
        ("e2_2_node_1.7b", "5060 Ti\n1.7B"),
        ("e2_3_mac_0.6b", "Apple M4\n0.6B"),
        ("e2_4_mac_1.7b", "Apple M4\n1.7B"),
    ]
    labels = [lbl for _, lbl in keys]
    drafts = [s[k]["mean_draft_ms"] for k, _ in keys]
    verifies = [s[k]["server_verify_ms"] for k, _ in keys]
    nets = [s[k]["net_rtt_ms"] for k, _ in keys]
    posts = [s[k]["mean_post_ms"] for k, _ in keys]
    rhos = [s[k]["rho"] for k, _ in keys]

    x = np.arange(len(labels))
    w = 0.52
    fig, ax = plt.subplots(figsize=(8.6, 5.0))

    p1 = ax.bar(x, drafts, w, label="端侧草稿 (Draft)", color=C_NAVY)
    p2 = ax.bar(x, verifies, w, bottom=drafts, label="服务端 14B 验证 (Verify)", color=C_PURPLE)
    b3 = [d + v for d, v in zip(drafts, verifies)]
    p3 = ax.bar(x, nets, w, bottom=b3, label="Tailscale 网络往返与排队 (Net RTT)", color=C_CORAL)
    b4 = [b + n for b, n in zip(b3, nets)]
    p4 = ax.bar(x, posts, w, bottom=b4, label="端侧前后处理 (Pre/Post)", color=C_AMBER)

    totals = [b + p for b, p in zip(b4, posts)]
    for i, (tot, rho, dr) in enumerate(zip(totals, rhos, drafts)):
        regime = "网络受限" if rho > 5 else "算力敏感"
        ax.text(
            i, tot + 35,
            f"总计 {tot:.0f} ms\nρ = {rho:.1f} ({regime})",
            ha="center", va="bottom", fontsize=8.8, fontweight="bold",
            color=C_CORAL if rho > 5 else C_TEAL,
        )
        if dr > 120:
            ax.text(i, dr / 2, f"{dr:.0f}ms", ha="center", va="center",
                    color="white", fontsize=8.5, fontweight="bold")

    ax.set_ylabel("单轮验证周期平均耗时 (ms)", fontsize=10.5)
    ax.set_title("实验 2：2×2 控制变量矩阵的单轮延迟拆解与瓶颈比 ρ 对比", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, max(totals) * 1.42)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        frameon=True, facecolor="white", loc="upper center",
        ncol=2, fontsize=8.8,
    )

    save_fig(fig, "fig2_latency_breakdown")


def plot_fig3_matrix_mat_throughput(s: dict):
    keys = [
        ("e2_1_node_0.6b", "5060Ti\n0.6B", C_NAVY),
        ("e2_2_node_1.7b", "5060Ti\n1.7B", C_BLUE),
        ("e2_3_mac_0.6b", "M4\n0.6B", C_TEAL),
        ("e2_4_mac_1.7b", "M4\n1.7B", "#1D6F63"),
        ("e1_2_server_only", "Server-Only\n14B+0.6B", C_PURPLE),
    ]
    labels = [lbl for _, lbl, _ in keys]
    mats = [s[k]["mean_acc"] for k, _, _ in keys]
    tputs = [s[k]["throughput_tok_s"] for k, _, _ in keys]
    colors = [c for _, _, c in keys]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))
    x = np.arange(len(labels))

    # Left: Mean Accepted Tokens
    bars1 = ax1.bar(x, mats, width=0.55, color=colors, edgecolor="#222222", linewidth=0.6)
    for b, val in zip(bars1, mats):
        ax1.text(b.get_x() + b.get_width() / 2, val + 0.08, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=9.5, fontweight="bold")
    ax1.set_title("(a) 每轮平均接受 Token 数 (MAT, d=4, b=32)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("平均接受长度 E[τ] (tokens/步)", fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylim(0, 5.0)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Right: Throughput vs Baselines
    bars2 = ax2.bar(x, tputs, width=0.55, color=colors, edgecolor="#222222", linewidth=0.6)
    for b, val in zip(bars2, tputs):
        ax2.text(b.get_x() + b.get_width() / 2, val + 0.3, f"{val:.2f}",
                 ha="center", va="bottom", fontsize=9.5, fontweight="bold")

    ab_tput = s["e1_1_auto_batch"]["throughput_tok_s"]
    ax2.axhline(ab_tput, color=C_CORAL, linestyle="--", linewidth=1.6,
                label=f"Auto-Batch 14B 纯自回归基线 ({ab_tput:.2f} tok/s)")
    ax2.set_title("(b) 端到端解码吞吐对比（含纯自回归基线）", fontsize=11, fontweight="bold")
    ax2.set_ylabel("解码吞吐 (tokens/s)", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9)
    ax2.set_ylim(0, ab_tput * 1.18)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper left", fontsize=8.8)

    fig.suptitle("实验 1 & 2：模型规模与异构硬件对接受率与吞吐的交叉影响", fontsize=12.5, fontweight="bold", y=1.02)
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))

    # Left: Draft latency reduction
    b1 = ax1.bar(x - w / 2, n_draft, w, label="RTX 5060 Ti (1.7B)", color=C_NAVY)
    b2 = ax1.bar(x + w / 2, m_draft, w, label="Apple M4 (0.6B)", color=C_TEAL)
    for b in list(b1) + list(b2):
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 10, f"{h:.1f}",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold")
    ax1.set_title("(a) Proactive 模式对端侧草稿耗时 (Draft) 的压缩", fontsize=11, fontweight="bold")
    ax1.set_ylabel("端侧 Draft 平均耗时 (ms)", fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(modes, fontsize=9.5)
    ax1.set_ylim(0, max(m_draft) * 1.22)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(fontsize=9)

    # Right: End-to-end throughput
    b3 = ax2.bar(x - w / 2, n_tput, w, label="RTX 5060 Ti (1.7B)", color=C_NAVY)
    b4 = ax2.bar(x + w / 2, m_tput, w, label="Apple M4 (0.6B)", color=C_TEAL)
    for b in list(b3) + list(b4):
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 0.08, f"{h:.2f}",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold")
    ax2.set_title("(b) Proactive 模式对端到端解码吞吐的提升", fontsize=11, fontweight="bold")
    ax2.set_ylabel("端到端吞吐 (tokens/s)", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(modes, fontsize=9.5)
    ax2.set_ylim(0, max(max(n_tput), max(m_tput)) * 1.24)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(fontsize=9)

    fig.suptitle("实验 3：Proactive Drafting 消融实验（disabled vs excluded vs included）",
                 fontsize=12.5, fontweight="bold", y=1.02)
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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.7))

    # Panel (a): Draft latency scaling vs MAT scaling
    ax1_r = ax1.twinx()
    l1 = ax1.plot(nd, n_dr, "o-", color=C_NAVY, lw=2.2, ms=7, label="5060 Ti Draft 耗时 (斜率 ~22 ms/层)")
    l2 = ax1.plot(md, m_dr, "s-", color=C_TEAL, lw=2.2, ms=7, label="Apple M4 Draft 耗时 (斜率 ~129 ms/层)")
    l3 = ax1_r.plot(nd, n_mat, "^--", color=C_CORAL, lw=1.8, ms=7, label="5060 Ti (1.7B) 平均接受长度 E[τ]")
    l4 = ax1_r.plot(md, m_mat, "D:", color=C_PURPLE, lw=1.8, ms=6, label="Apple M4 (0.6B) 平均接受长度 E[τ]")

    for d_val, dr_val in zip(nd, n_dr):
        ax1.text(d_val, dr_val + 22, f"{dr_val:.0f}ms", ha="center", fontsize=8.2, color=C_NAVY)
    for d_val, dr_val in zip(md, m_dr):
        ax1.text(d_val, dr_val + 25, f"{dr_val:.0f}ms", ha="center", fontsize=8.2, color=C_TEAL)

    ax1.set_xlabel("投机树最大深度 d (max_beam_len)", fontsize=10)
    ax1.set_ylabel("端侧草稿耗时 T_draft (ms)", fontsize=10)
    ax1_r.set_ylabel("平均接受长度 E[τ] (tokens/步)", fontsize=10, color=C_CORAL)
    ax1.set_xticks([2, 4, 6, 8])
    ax1.set_ylim(0, 920)
    ax1_r.set_ylim(1.5, 6.8)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.set_title("(a) 树深度对 Draft 耗时与接受长度的截然不同标度律", fontsize=10.8, fontweight="bold")
    lines = l1 + l2 + l3 + l4
    ax1.legend(lines, [l.get_label() for l in lines], loc="upper left", fontsize=7.8, frameon=True)

    # Panel (b): Normalized TPOT at fixed typical RTT + analytical formula fit
    # Fit linear T_draft(d) = a*d + c and power-law MAT(d) = k * d^alpha
    na, nc = np.polyfit(nd, n_dr, 1)
    ma, mc = np.polyfit(md, m_dr, 1)
    n_mat_coef = np.polyfit(np.log(nd), np.log(n_mat), 1)
    m_mat_coef = np.polyfit(np.log(md), np.log(m_mat), 1)

    d_grid = np.linspace(1.8, 8.2, 100)
    # Fixed representative network+verify latency per link (eliminating WAN jitter to show pure tree effect)
    T_wait_node_ref = 1150.0  # ms (typical node WAN wait + 14B verify)
    T_wait_mac_ref = 520.0    # ms (typical mac WAN wait + 14B verify)

    # Measured normalized TPOT using actual measured draft & MAT at fixed link RTT
    n_tpot_meas = (n_dr + T_wait_node_ref) / n_mat
    m_tpot_meas = (m_dr + T_wait_mac_ref) / m_mat

    n_tpot_pred = (na * d_grid + nc + T_wait_node_ref) / (np.exp(n_mat_coef[1]) * d_grid ** n_mat_coef[0])
    m_tpot_pred = (ma * d_grid + mc + T_wait_mac_ref) / (np.exp(m_mat_coef[1]) * d_grid ** m_mat_coef[0])

    ax2.plot(d_grid, n_tpot_pred, "--", color=C_NAVY, lw=2.0, label="5060 Ti 理论公式预测曲线 (T_wait=1150ms)")
    ax2.scatter(nd, n_tpot_meas, color=C_NAVY, s=65, zorder=5, label="5060 Ti 实测归一点 (越深越快)")
    ax2.plot(d_grid, m_tpot_pred, "--", color=C_TEAL, lw=2.0, label="Apple M4 理论公式预测曲线 (T_wait=520ms)")
    ax2.scatter(md, m_tpot_meas, color=C_TEAL, marker="s", s=65, zorder=5, label="Apple M4 实测归一点 (浅树 d=2 最优)")

    # Highlight optimal points
    ax2.annotate("5060 Ti 最优点\nd=8, TPOT 降 46%", xy=(8, n_tpot_meas[-1]), xytext=(5.7, 175),
                 arrowprops=dict(arrowstyle="->", color=C_NAVY, lw=1.4),
                 fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax2.annotate("M4 最优点\nd=2 (更深则反弹)", xy=(2, m_tpot_meas[0]), xytext=(2.15, 200),
                 arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.4),
                 fontsize=8.5, fontweight="bold", color=C_TEAL)

    ax2.set_xlabel("投机树最大深度 d (max_beam_len)", fontsize=10)
    ax2.set_ylabel("归一化单 Token 延迟 TPOT (ms/token)", fontsize=10)
    ax2.set_xticks([2, 4, 6, 8])
    ax2.set_ylim(140, 460)
    ax2.grid(axis="y", linestyle="--", alpha=0.35)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.set_title("(b) 理论公式拟合与两类设备的相反最优拐点", fontsize=10.8, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=7.8, frameon=True)

    fig.suptitle("实验 4a：投机树深度扫描与异构 TPOT 解析模型拟合验证", fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    save_fig(fig, "fig5_tree_sweep_theory_fit")


def plot_fig6_3node_before_after(s: dict):
    if "e4_base_3node" not in s or "e4_opt_3node" not in s:
        print("Skipping fig6: 3-node runs not yet complete")
        return

    base = s["e4_base_3node"]
    opt = s["e4_opt_3node"]

    cats = ["Edge 1\n(5060 Ti / 1.7B)", "Edge 2\n(Apple M4 / 0.6B)", "三机集群总吞吐\n(Aggregate)"]
    base_tp = [base["node"]["throughput_tok_s"], base["mac"]["throughput_tok_s"], base["aggregate_throughput_tok_s"]]
    opt_tp = [opt["node"]["throughput_tok_s"], opt["mac"]["throughput_tok_s"], opt["aggregate_throughput_tok_s"]]

    base_mat = [base["node"]["mean_acc"], base["mac"]["mean_acc"]]
    opt_mat = [opt["node"]["mean_acc"], opt["mac"]["mean_acc"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.7))
    x = np.arange(len(cats))
    w = 0.34

    b1 = ax1.bar(x - w / 2, base_tp, w, label="默认统一配置 (均 d=4, b=32, excluded)", color=C_SLATE)
    b2 = ax1.bar(x + w / 2, opt_tp, w, label="异构感知优化 (5060Ti d=8,b=64 | M4 d=2,b=16 | included)", color=C_CORAL)

    for i, (v0, v1) in enumerate(zip(base_tp, opt_tp)):
        gain = (v1 - v0) / v0 * 100.0
        ax1.text(i - w / 2, v0 + 0.12, f"{v0:.2f}", ha="center", va="bottom", fontsize=9)
        ax1.text(i + w / 2, v1 + 0.12, f"{v1:.2f}\n({gain:+.1f}%)", ha="center", va="bottom",
                 fontsize=9, fontweight="bold", color=C_CORAL if gain >= 0 else C_NAVY)

    ax1.set_title("(a) 三机并发端到端吞吐对比 (优化前 vs 优化后)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("解码吞吐 (tokens/s)", fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats, fontsize=9.2)
    ax1.set_ylim(0, max(max(base_tp), max(opt_tp)) * 1.28)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="upper left", fontsize=8.0)

    # Right panel: Per-edge MAT & Draft comparison
    x2 = np.arange(2)
    c2 = ["Edge 1 (5060 Ti)\nd=4→d=8", "Edge 2 (Apple M4)\nd=4→d=2"]
    b3 = ax2.bar(x2 - w / 2, base_mat, w, label="默认统一配置 MAT", color=C_SLATE)
    b4 = ax2.bar(x2 + w / 2, opt_mat, w, label="异构感知优化 MAT", color=C_TEAL)
    for i, (v0, v1) in enumerate(zip(base_mat, opt_mat)):
        ax2.text(i - w / 2, v0 + 0.1, f"{v0:.2f}", ha="center", va="bottom", fontsize=9.5)
        ax2.text(i + w / 2, v1 + 0.1, f"{v1:.2f}", ha="center", va="bottom",
                 fontsize=9.5, fontweight="bold", color=C_TEAL)

    ax2.set_title("(b) 异构树预算并发下的平均接受长度 (MAT)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("平均接受长度 E[τ] (tokens/步)", fontsize=10)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(c2, fontsize=9.5)
    ax2.set_ylim(0, max(max(base_mat), max(opt_mat)) * 1.25)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper right", fontsize=8.8)

    fig.suptitle("实验 4b：Variable-Budget 异构并发服务终极对照（默认统一 vs 异构感知优化）",
                 fontsize=12.5, fontweight="bold", y=1.02)
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
    print("ALL FIGURES GENERATED SUCCESSFULLY.")
