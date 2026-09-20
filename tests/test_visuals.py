from pathlib import Path

from src.main import generate_visual_outputs


def test_generate_visual_outputs(tmp_path):
    output_dir = tmp_path / "plots"

    generate_visual_outputs(output_dir)

    assert (output_dir / "fuzzy_system.png").exists()
    assert (output_dir / "reinforcement_learning.png").exists()
    assert (output_dir / "data_pipeline.png").exists()
