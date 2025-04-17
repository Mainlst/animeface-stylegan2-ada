FROM nvcr.io/nvidia/pytorch:20.12-py3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip && \
    pip install \
        torch==1.7.1+cu110 torchvision==0.8.2+cu110 -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install \
        numpy \
        imageio \
        imageio-ffmpeg==0.4.3 \
        pyspng==0.1.0 \
        onnxruntime \
        tqdm \
        ninja \
        legacy

WORKDIR /workspace

RUN (printf '#!/bin/bash\nunset TORCH_CUDA_ARCH_LIST\nexec \"$@\"\n' >> /entry.sh) && chmod a+x /entry.sh
ENTRYPOINT ["/entry.sh"]
