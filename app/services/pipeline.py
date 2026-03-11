from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelineResult:
    output_dir: Path
    artifacts: list[Path]
    logs: list[str]


class PipelineRunner:
    def __init__(self, output_root: Path):
        self.output_root = output_root
        self.output_root.mkdir(parents=True, exist_ok=True)

    def run(self, input_audio: Path, approach: str, include_score: bool) -> PipelineResult:
        if approach == "A":
            return self._run_end_to_end(input_audio, include_score)
        return self._run_two_step(input_audio, include_score)

    def _run_end_to_end(self, input_audio: Path, include_score: bool) -> PipelineResult:
        job_dir = self.output_root / f"job_{input_audio.stem}_A"
        job_dir.mkdir(parents=True, exist_ok=True)

        out_midi = job_dir / f"{input_audio.stem}.mid"
        logs: list[str] = ["Approach A selected: end-to-end (MT3/MR-MT3-style)."]

        if shutil.which("mt3"):
            cmd = ["mt3", "--audio", str(input_audio), "--output", str(out_midi)]
            logs.append(self._run_command(cmd, cwd=job_dir))
        else:
            out_midi.write_bytes(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0")
            logs.append("mt3 CLI not found; wrote placeholder MIDI header.")

        artifacts = [out_midi]
        if include_score:
            artifacts.extend(self._maybe_make_score(out_midi, job_dir, logs))

        return PipelineResult(output_dir=job_dir, artifacts=artifacts, logs=logs)

    def _run_two_step(self, input_audio: Path, include_score: bool) -> PipelineResult:
        job_dir = self.output_root / f"job_{input_audio.stem}_B"
        stems_dir = job_dir / "stems"
        transcribed_dir = job_dir / "midi"
        stems_dir.mkdir(parents=True, exist_ok=True)
        transcribed_dir.mkdir(parents=True, exist_ok=True)

        logs: list[str] = ["Approach B selected: source separation -> per-stem transcription."]

        if shutil.which("demucs"):
            cmd = ["demucs", "--out", str(stems_dir), str(input_audio)]
            logs.append(self._run_command(cmd, cwd=job_dir))
        else:
            for name in ["drums", "bass", "piano"]:
                (stems_dir / f"{name}.wav").write_bytes(b"RIFF")
            logs.append("demucs not found; created placeholder stems.")

        artifacts: list[Path] = []
        stem_to_tool = {
            "piano.wav": "basic-pitch",
            "bass.wav": "basic-pitch",
            "drums.wav": "omnizart",
        }

        for stem_name, tool in stem_to_tool.items():
            stem = stems_dir / stem_name
            if not stem.exists():
                continue
            midi_out = transcribed_dir / f"{stem.stem}.mid"
            if tool == "basic-pitch" and shutil.which("basic-pitch"):
                cmd = ["basic-pitch", str(transcribed_dir), str(stem)]
                logs.append(self._run_command(cmd, cwd=job_dir))
            elif tool == "omnizart" and shutil.which("omnizart"):
                cmd = ["omnizart", "drum", "transcribe", str(stem), "-o", str(transcribed_dir)]
                logs.append(self._run_command(cmd, cwd=job_dir))
            else:
                midi_out.write_bytes(b"MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0")
                logs.append(f"{tool} not found for {stem_name}; wrote placeholder MIDI.")
            artifacts.append(midi_out)

        if include_score:
            for midi in list(artifacts):
                artifacts.extend(self._maybe_make_score(midi, job_dir, logs))

        return PipelineResult(output_dir=job_dir, artifacts=artifacts, logs=logs)

    @staticmethod
    def _run_command(cmd: list[str], cwd: Path) -> str:
        try:
            completed = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
            return f"$ {' '.join(cmd)}\n{completed.stdout.strip()}"
        except subprocess.CalledProcessError as exc:
            return f"$ {' '.join(cmd)}\nfailed: {exc.stderr.strip()}"

    @staticmethod
    def _maybe_make_score(midi_path: Path, job_dir: Path, logs: list[str]) -> list[Path]:
        artifacts: list[Path] = []
        score_path = job_dir / f"{midi_path.stem}.musicxml"
        if shutil.which("musescore"):
            cmd = ["musescore", str(midi_path), "-o", str(score_path)]
            logs.append(PipelineRunner._run_command(cmd, cwd=job_dir))
        else:
            score_path.write_text("<!-- placeholder score export; install musescore CLI for real conversion -->\n")
            logs.append("musescore not found; created placeholder MusicXML file.")
        artifacts.append(score_path)
        return artifacts
