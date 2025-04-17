# interpolate.py
import os, argparse
import numpy as np
import torch
import imageio
import sys
sys.path.append("/workspace/stylegan2-ada-pytorch") 

from dnnlib import legacy

def parse_args():
    p = argparse.ArgumentParser(description="StyleGAN2-ADA 潜在空間補間 & 動画生成")
    p.add_argument("--network",    required=True, help="学習済みモデル(.pkl)のパス")
    p.add_argument("--seed1",      type=int, default=0,    help="開始シード")
    p.add_argument("--seed2",      type=int, default=100,  help="終了シード")
    p.add_argument("--steps",      type=int, default=60,   help="補間フレーム数")
    p.add_argument("--outdir",     required=True, help="出力先フォルダ")
    p.add_argument("--fps",        type=int, default=30,   help="動画のfps")
    p.add_argument("--trunc",      type=float, default=1.0, help="truncation psi")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # モデル読み込み
    print("Loading network...")
    with open(args.network, "rb") as f:
        G = legacy.load_network_pkl(f)["G_ema"].to(device)

    # 2つの潜在ベクトルを生成
    z1 = np.random.RandomState(args.seed1).randn(1, G.z_dim)
    z2 = np.random.RandomState(args.seed2).randn(1, G.z_dim)
    z1 = torch.from_numpy(z1).to(device)
    z2 = torch.from_numpy(z2).to(device)

    # フレームごとに補間 & 生成
    imgs = []
    for idx, alpha in enumerate(np.linspace(0, 1, args.steps)):
        z = (1 - alpha) * z1 + alpha * z2
        with torch.no_grad():
            img = G(z, None, truncation_psi=args.trunc, noise_mode='const')[0]
        # [C,H,W] -> [H,W,C], uint8
        img = (img.permute(1,2,0) * 127.5 + 128).clamp(0,255).to(torch.uint8).cpu().numpy()
        imgs.append(img)
        # フレームPNGも欲しい場合は以下を有効化
        # imageio.imwrite(f"{args.outdir}/frame_{idx:03d}.png", img)
        print(f"Frame {idx+1}/{args.steps} generated")

    # 動画ファイル書き出し
    video_path = os.path.join(args.outdir, "animation.mp4")
    print(f"Writing video to {video_path} ({args.fps} fps)")
    writer = imageio.get_writer(video_path, fps=args.fps, codec='libx264', ffmpeg_log_level="error")
    for img in imgs:
        writer.append_data(img)
    writer.close()
    print("Done!")

if __name__ == "__main__":
    main()
