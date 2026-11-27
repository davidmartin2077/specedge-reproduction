# SpecEdge 三机异构复现实验报告

> 实验日期：2026-11-27  
> 代码基线：`kaist-ina/specedge`（NeurIPS 2025）+ Apple Silicon MPS 兼容补丁

---

## 1. 实验拓扑与硬件配置

本次复现采用 **1 台 Server + 2 台异构 Edge** 的真实跨设备部署，三台设备通过 Tailscale 组网并以 gRPC（端口 `8000`）通信：

| 节点角色 | 硬件与系统 | 运行模型（FP16） | 推理后端 | Python / PyTorch / Transformers / gRPC |
| :--- | :--- | :--- | :--- | :--- |
| **Server（主验证节点）** | RTX 4080 SUPER（32 GB VRAM, `sm_89`）<br>Windows + WSL2 Ubuntu | `Qwen/Qwen3-14B` | CUDA + CUDA Graph | `3.14.4` / `2.9.0+cu128` / `4.57.1` / `1.75.1` |
| **Edge 1（草稿节点 1）** | RTX 5060 Ti（8 GB VRAM, `sm_120`）<br>Windows | `Qwen/Qwen3-1.7B` | CUDA + CUDA Graph | `3.14.6` / `2.9.1+cu128` / `4.57.6` / `1.75.1` |
| **Edge 2（草稿节点 2）** | Apple M4（16 GB 统一内存）<br>macOS 27.2.1 (`arm64`) | `Qwen/Qwen3-0.6B` | PyTorch MPS（Eager） | `3.14.7` / `2.9.0` / `4.57.1` / `1.75.1` |

---

## 2. 代码改造（MPS 跨端兼容补丁）

官方原版代码假设 Server 与所有 Edge 均使用 NVIDIA CUDA，在 macOS MPS 上运行会触发两类报错。我们在**不改变任何 CUDA 行为**的前提下完成了最小化补丁：

1. **`src/specedge/engine/graph.py`**：
   - 在 `GraphEngine` 和 `BatchGraphEngine` 中检测 `self._device.type == "cuda"`；非 CUDA 设备（如 `mps`）自动跳过 `torch.cuda.CUDAGraph` 捕获并走非图执行路径；
   - 修复了原版代码在非图执行分支中未对 `self._past_key_values.seq_indices` 按 `[:num_beams]` 切片导致的 `KVCache.update` 形状不匹配错误。
2. **`src/util.py`**：
   - 在 `Timing` 计时器中增加设备类型判断：`mps` 设备使用 `torch.mps.synchronize()` 替代 `torch.cuda.synchronize()`，并在 `mode="event"` 时自动回退为 `sync` 模式。

---

## 3. 实验配置与实测结果

- **数据集**：仓库内置 `specbench`（`sample_req_cnt=48`，每端并发执行 10 条请求，共 20 条请求）
- **核心参数**：`max_len=2048`、`max_new_tokens=64`、`max_batch_size=1`、`num_clients=2`、`cache_prefill=true`
- **树状投机参数**：`max_n_beams=32`、`max_beam_len=4`、`max_branch_width=16`、`max_budget=32`；开启 Proactive Drafting（`type=excluded`，`max_beam_len=3`）

### 实测指标汇总

| 指标 | Edge 1（RTX 5060 Ti / `Qwen3-1.7B` / CUDA Graph） | Edge 2（Apple M4 / `Qwen3-0.6B` / MPS Eager） |
| :--- | :--- | :--- |
| **完成请求数 / 解码步数** | 10 条 / 156 步（含 22 步 Proactive） | 10 条 / 152 步（含 23 步 Proactive） |
| **总接受 Token 数** | 643（解码阶段 601） | 616（解码阶段 576） |
| **平均每步接受 Token 数（MAT）** | **3.85**（中位数 **5.0**，最高 **8**） | **3.79**（中位数 **4.0**，最高 **8**） |
| **端侧 Draft 耗时（均值 / 中位数）** | **86.5 ms** / 76.5 ms | **512.5 ms** / 476.4 ms |
| **Server 验证 + 网络往返耗时（均值 / 中位数）** | 1296.6 ms / 819.6 ms | 552.4 ms / 455.0 ms |
| **端到端解码吞吐（Tailscale 广域网）** | 2.78 tok/s | 3.31 tok/s |

---

## 4. 结果解读与结论

1. **投机解码效率得到验证**：
   - 两个小模型（`1.7B` 与 `0.6B`）平均每轮都能让 `14B` 主模型一次性接受接近 **4 个 token**（中位数 4~5 个，配合 Proactive Drafting 单轮最高接受 **8 个 token**），相当于把 `14B` 主模型的逐词推理调用次数减少了约 **3.8 倍**。
   - `1.7B` 相比 `0.6B` 猜得更准（中位数 5.0 vs 4.0），符合“草稿模型越接近主模型、接受率越高”的规律。
2. **CUDA Graph 对树状草稿至关重要**：
   - 尽管 `1.7B` 的参数量接近 `0.6B` 的 3 倍，但 RTX 5060 Ti 借助原生 CUDA Graph，单轮 Draft 仅需 **76.5 ms**，比 Apple M4 上 PyTorch MPS Eager 模式（476.4 ms）快了 **6 倍以上**。
3. **当前端到端速度瓶颈在网络往返（Tailscale 公网/中继 RTT）**：
   - 服务端日志显示，RTX 4080 SUPER 验证一次 `14B` 32-token 树本身仅需 **~70–85 ms**；但本次实验设备通过 Tailscale 跨公网/中继通信（单次往返数百毫秒），导致 `client_wait` 占了总时间的大头。
   - 如果将三台设备放在同一局域网（RTT < 1 ms），RTX 5060 Ti 端（`76 ms` 草稿 + `~80 ms` 验证 ≈ `156 ms` 产出 `3.85` tokens）的理论解码吞吐可达 **~25 tok/s**。
4. **工程踩坑与经验**：
   - WSL2 直接挂载 Windows `/mnt/d`（9p）加载 28 GB 权重慢且容易触发内存异常，将模型拷贝至 WSL2 原生 ext4 后，`Qwen3-14B` 8 个分片加载仅需 **~9 秒**（约 1.1 s/片）。
   - `RTX 4080 SUPER 32GB` 运行 `Qwen3-14B` FP16 需约 30 GB 显存，运行时需关闭其他占显存应用，并使用 `max_batch_size=1` 保留安全显存余量并避免异构 Edge 互相阻塞。

---

## 5. 相关文件清单

- 兼容补丁：`src/specedge/engine/graph.py`、`src/util.py`
- 三机配置示例：`config/specedge_3node.example.yaml`
- 启动脚本：`script/run_client_node.ps1`、`script/run_client_mac.sh`、`script/run_3node_exp.ps1`
