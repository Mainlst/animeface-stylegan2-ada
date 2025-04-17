# multi_generate.py
import os
import argparse
import numpy as np
import torch
import imageio
import sys

# stylegan2-ada-pytorch に含まれる dnnlib/legacy を読み込む
sys.path.append("/workspace/stylegan2-ada-pytorch")
from dnnlib import legacy

def parse_args():
    p = argparse.ArgumentParser(
        description="Multi-Seed アニメ顔画像一括生成ツール"
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--seeds",
        help="カンマ区切りのシード番号リスト。例: 0,50,100"
    )
    group.add_argument(
        "--range", nargs=3, metavar=("START","END","STEP"), type=int,
        help="シード範囲指定: START END STEP (例: 0 200 50)"
    )
    p.add_argument(
        "--network", required=True,
        help="学習済みモデル(.pkl)のパス"
    )
    p.add_argument(
        "--outdir", required=True,
        help="出力画像保存先ディレクトリ"
    )
    p.add_argument(
        "--trunc", type=float, default=1.0,
        help="truncation psi (デフォルト: 1.0)"
    )
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # モデル読み込み
    print(f"Loading network from {args.network}...")
    with open(args.network, "rb") as f:
        G = legacy.load_network_pkl(f)["G_ema"].to(device)

    # シードリスト生成
    if args.seeds:
        seeds = [int(s) for s in args.seeds.split(",")]
    else:
        start, end, step = args.range
        if step > 0:
            seeds = list(range(start, end + 1, step))
        else:
            seeds = list(range(start, end - 1, step))
    print(f"Generating images for seeds: {seeds}")

    # 各シードで画像生成
    for seed in seeds:
        z = torch.from_numpy(np.random.RandomState(seed).randn(1, G.z_dim)).to(device)
        with torch.no_grad():
            img_tensor = G(z, None, truncation_psi=args.trunc, noise_mode='const')[0]
        img = (img_tensor.permute(1,2,0) * 127.5 + 128).clamp(0,255).to(torch.uint8).cpu().numpy()
        out_path = os.path.join(args.outdir, f"seed{seed:04d}.png")
        imageio.imwrite(out_path, img)
        print(f"Saved image: {out_path}")

    print("All images generated!")

if __name__ == "__main__":
    main()
