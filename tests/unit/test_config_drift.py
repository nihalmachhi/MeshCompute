from pathlib import Path

from meshcompute.core.settings import Settings


def test_every_example_environment_key_maps_to_a_setting():
    example = Path(__file__).parents[2] / ".env.example"
    keys = [
        line.split("=", 1)[0].strip()
        for line in example.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    fields = {"MESH_COMPUTE_" + name.upper() for name in Settings.model_fields}
    assert set(keys) <= fields
    parsed = Settings(_env_file=example)
    assert parsed.worker_stale_seconds == 45
    assert parsed.api_host == "0.0.0.0"
    assert parsed.api_port == 8000
