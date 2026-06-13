import sys
import bpy

def export_usdz(filepath, out_path):
    print(f"Opening project for USDZ packaging: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif filepath.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=filepath)

    print(f"Exporting USDZ to: {out_path}")
    # Export scene using USD format if supported by blender installation
    try:
        bpy.ops.wm.usd_export(filepath=out_path)
    except AttributeError:
        # Fallback if specific version of usd_export is named differently
        bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        export_usdz(args[0], args[1])
