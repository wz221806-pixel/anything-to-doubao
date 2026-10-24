# -*- coding: utf-8 -*-
"""
anything-to-doubao / extract_audio.py
从视频文件中提取音频流（纯 PyAV，无需 ffmpeg）。

用法:
  python extract_audio.py <视频路径> [输出音频路径]
    输出默认: 视频同名 .wav
依赖: av (PyAV)
"""
import sys, os

def main():
    if len(sys.argv) < 2:
        print("用法: python extract_audio.py <视频路径> [输出音频路径]")
        sys.exit(1)
    video = sys.argv[1]
    if not os.path.exists(video):
        print(f"ERROR: 视频不存在: {video}")
        sys.exit(1)
    if len(sys.argv) > 2:
        audio = sys.argv[2]
    else:
        base = os.path.splitext(video)[0]
        audio = base + ".wav"

    try:
        import av
    except ImportError:
        print("ERROR: 缺少 av 库，请先安装: pip install av")
        sys.exit(1)

    try:
        container = av.open(video)
        out = av.open(audio, "w")
        out_stream = None
        for frame in container.decode(audio=0):
            if out_stream is None:
                out_stream = out.add_stream("pcm_s16le", rate=frame.sample_rate)
                out_stream.layout = frame.layout.name
            for packet in out_stream.encode(frame):
                out.mux(packet)
        for packet in out_stream.encode(None):
            out.mux(packet)
        out.close()
        container.close()
        size = os.path.getsize(audio)
        print(f"✅ 音频已提取: {audio} ({size/1024/1024:.1f} MB)")
    except Exception as e:
        print(f"ERROR: 音频提取失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
