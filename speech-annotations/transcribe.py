#!/usr/bin/env python3

# auto-transcribe an audio file into teleplot annotations 

import pandas
from teleplot import Teleplot
import sys
import whisper_timestamped as whisper

if len(sys.argv) != 4:
    print("usage: transcribe.py Microphone.csv Microphone.mp4 <teleplot session>.json")
    sys.exit(1)

mic = sys.argv[1]
mp4 = sys.argv[2]
tpsess = sys.argv[3]


tp = Teleplot()
df = pandas.read_csv(mic, delimiter=",")
df["time"] = df["time"].div(10**9)
t0 = df["time"][0]
for _, row in df.iterrows():
    tp.addSample("dBFS", row["dBFS"], row["time"])

audio = whisper.load_audio(mp4)
model = whisper.load_model("tiny", device="cpu")
result = whisper.transcribe(model, audio, vad=True, language="en")
words = []
for s in result["segments"]:
    words.extend(s["words"])

for w in words:
    tp.annotate(w["text"], t0 + w["start"], t0 + w["end"])

with open(tpsess, "w") as f:
    f.write(tp.toJson())
