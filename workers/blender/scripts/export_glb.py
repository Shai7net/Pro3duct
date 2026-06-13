import sys
import bpy

def export_glb(filepath, out_path):
    print(f"Opening project for GLB packaging: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif filepath.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=filepath)

    print(f"Exporting compressed GLB to: {out_path}")
    # Enable Draco compression and export texture mappings
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_materials='EXPORT',
        export_colors=True
    )

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        export_glb(args[0], args[1])
