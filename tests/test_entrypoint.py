"""Coverage for the launcher when imported without executing it."""

import runpy


def test_launcher_can_be_loaded_as_a_module(project_root):
    namespace = runpy.run_path(
        str(project_root / "scripts" / "screening_acciones.py"),
        run_name="screening_acciones_importado",
    )

    assert callable(namespace["main"])
