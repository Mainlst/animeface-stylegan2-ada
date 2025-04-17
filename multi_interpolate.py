# multi_interpolate.py
import os, argparse
import numpy as np
import torch, imageio
import sys
sys.path.append("/workspace/stylegan2-ada-pytorch") 

from dnnlib import legacy

def parse_args():
    p = argparse.ArgumentParser(
        description="Multi-Seed 潜在補間アニメ動画生成 (範囲指定やリスト指定でシード生成)"
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--seeds",
        help="カンマ区切りシードリスト。例: 0,50,100"
    )
    group.add_argument(
        "--range", nargs=3, metavar=("START","END","STEP"), type=int,
        help="シード範囲指定: START END STEP (例: 0 200 50)"
    )
    p.add_argument(
        "--steps-per-seg", type=int, default=60,
        help="１区間あたりのフレーム数 (デフォルト: 60)"
    )
    p.add_argument(
        "--network", required=True,
        help="学習済みモデル(.pkl)のパス"
    )
    p.add_argument(
        "--outdir", required=True,
        help="出力フォルダ"
    )
    p.add_argument(
        "--fps", type=int, default=30,
        help="動画のFPS (デフォルト: 30)"
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

    # モデルロード
    print(f"Loading network from {args.network}...")
    with open(args.network, "rb") as f:
        G = legacy.load_network_pkl(f)["G_ema"].to(device)

    # シードリスト生成
    if args.seeds:
        seeds = [int(s) for s in args.seeds.split(",")]
    else:
        start, end, step = args.range
        # 終端を含むリスト作成
        if step > 0:
            seeds = list(range(start, end + 1, step))
        else:
            seeds = list(range(start, end - 1, step))
    print(f"Using seeds: {seeds}")

    # 潜在ベクトル生成
    zs = [torch.from_numpy(
            np.random.RandomState(s).randn(1, G.z_dim)
         ).to(device) for s in seeds]

    imgs = []
    total_segs = len(zs) - 1
    for seg in range(total_segs):
        z_start, z_end = zs[seg], zs[seg+1]
        for alpha in np.linspace(0, 1, args.steps_per_seg, endpoint=False):
            z = (1 - alpha) * z_start + alpha * z_end
            with torch.no_grad():
                img = G(z, None, truncation_psi=args.trunc, noise_mode='const')[0]
            img = (img.permute(1,2,0) * 127.5 + 128).clamp(0,255).to(torch.uint8).cpu().numpy()
            imgs.append(img)
        print(f"Segment {seg+1}/{total_segs} done")

    # 最後のフレーム追加
    with torch.no_grad():
        img = G(zs[-1], None, truncation_psi=args.trunc, noise_mode='const')[0]
    img = (img.permute(1,2,0) * 127.5 + 128).clamp(0,255).to(torch.uint8).cpu().numpy()
    imgs.append(img)

    # 動画書き出し
    video_path = os.path.join(args.outdir, "multi_animation.mp4")
    print(f"Writing video to {video_path} ({len(imgs)} frames at {args.fps} fps)")
    writer = imageio.get_writer(video_path, fps=args.fps, codec='libx264', ffmpeg_log_level="error")
    for img in imgs:
        writer.append_data(img)
    writer.close()
    print("All done!")

if __name__ == "__main__":
    main()
