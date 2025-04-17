# AnimeFace StyleGAN2-ADA 🐱🎨

このリポジトリは [NVIDIA の stylegan2-ada-pytorch](https://github.com/NVlabs/stylegan2-ada-pytorch) をサブモジュールとして組み込み、アニメ顔の**静止画生成**・**補間動画生成**・**多点補間動画生成**をワンストップで扱えるツールセットです！

![animation](https://github.com/user-attachments/assets/2c4673ff-3d7a-4eac-b1d3-b0c1f24677f9)

https://github.com/justinpinkney/awesome-pretrained-stylegan2?tab=readme-ov-file#anime-portraits

## ✨ 主な機能

- ✅ `generate.py` : 学習済みモデルによる**単発静止画生成**
- ✅ `multi_generate.py` : 複数シードを指定して**一括静止画生成**
- ✅ `interpolate.py` : 2点間の線形補間で**動画生成**
- ✅ `multi_interpolate.py` : 複数シードを連結して**連続変化動画生成**
- ✅ Docker イメージで**全依存関係をコンテナ化**（GPU 推論＆トレーニング対応）

## 🐳 クイックスタート（Docker）

```bash
# リポジトリをクローン
git clone https://github.com/<your-username>/animeface-stylegan2-ada.git
cd animeface-stylegan2-ada

# Docker イメージをビルド
docker build -t stylegan2-animate .
```

### 必要なデータ配置例

```
data/
├── pretrained/
│   └── your_model.pkl       ← 学習済みモデル (.pkl)
├── samples/                 ← 静止画生成の出力先
└── anim_output/             ← 動画生成の出力先
```
※ `data/anime_finetune.zip` を置いて**追加学習**も可能です

---

## 📸 静止画生成 (generate.py)

```bash
docker run --rm --gpus all -v %cd%:/workspace stylegan2-animate \
  python /workspace/generate.py \
    --network=/workspace/data/pretrained/your_model.pkl \
    --outdir=/workspace/data/samples \
    --trunc=1.0 \
    --seed=0
```

複数枚一括生成したい場合は `multi_generate.py` を使用：

```bash
docker run --rm --gpus all -v %cd%:/workspace stylegan2-animate \
  python /workspace/multi_generate.py \
    --network=/workspace/data/pretrained/your_model.pkl \
    --seeds=0,10,20,30 \
    --outdir=/workspace/data/samples \
    --trunc=1.0
```

## 🎞️ 単点補間動画生成 (interpolate.py)

```bash
docker run --rm --gpus all -v %cd%:/workspace stylegan2-animate \
  python /workspace/interpolate.py \
    --network=/workspace/data/pretrained/your_model.pkl \
    --seed1=0 --seed2=100 \
    --steps=300 \
    --outdir=/workspace/data/anim_output \
    --fps=30 \
    --trunc=1.0
```

## 🔄 多点補間動画生成 (multi_interpolate.py)

#### 範囲指定でシード自動生成
```bash
docker run --rm --gpus all -v %cd%:/workspace stylegan2-animate \
  python /workspace/multi_interpolate.py \
    --network=/workspace/data/pretrained/your_model.pkl \
    --range 0 200 50 \
    --steps-per-seg=300 \
    --outdir=/workspace/data/anim_output \
    --fps=30 \
    --trunc=1.0
```

#### リスト指定でシード手動設定
```bash
docker run --rm --gpus all -v %cd%:/workspace stylegan2-animate \
  python /workspace/multi_interpolate.py \
    --network=/workspace/data/pretrained/your_model.pkl \
    --seeds=0,50,100,150 \
    --steps-per-seg=180 \
    --outdir=/workspace/data/anim_output \
    --fps=30 \
    --trunc=1.0
```

---

## 📂 ディレクトリ構成

```
animeface-stylegan2-ada/
├── Dockerfile
├── README.md
├── LICENSE               ← 自作スクリプト (MIT)
├── LICENSE.stylegan2     ← NVIDIA LICENSE
├── generate.py
├── multi_generate.py
├── interpolate.py
├── multi_interpolate.py
├── stylegan2-ada-pytorch/ ← サブモジュール or フォルダ
│   ├── train.py
│   ├── generate.py (公式)
│   ├── dnnlib/
│   │   ├── legacy.py
│   │   └── __init__.py
│   └── LICENSE
└── data/
    ├── pretrained/
    ├── samples/
    └── anim_output/
```

---

## 📄 ライセンス

1. **stylegan2-ada-pytorch** (サブモジュール)
   - © NVIDIA CORPORATION
   - 詳細は `stylegan2-ada-pytorch/LICENSE` または `LICENSE.stylegan2` をご確認ください

2. **当リポジトリで追加したスクリプト**
   - MIT License (`LICENSE`)  

---

## 🐾 クレジット

> このリポジトリは、猫耳メイドAIアシスタント「ミル」のサポートにより作成されましたにゃん！🐱💕
> もしこのプロジェクトがお役に立ったら、ぜひスターをくださいませっ！
