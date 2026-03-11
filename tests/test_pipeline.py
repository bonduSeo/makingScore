from pathlib import Path

from app.services.pipeline import PipelineRunner


def test_pipeline_fallback_creates_placeholder_files(tmp_path: Path):
    input_audio = tmp_path / "song.mp3"
    input_audio.write_bytes(b"ID3")

    runner = PipelineRunner(output_root=tmp_path / "out")
    result = runner.run(input_audio=input_audio, approach="B", include_score=True)

    assert result.output_dir.exists()
    assert any(p.suffix == ".mid" for p in result.artifacts)
    assert any(p.suffix == ".musicxml" for p in result.artifacts)
