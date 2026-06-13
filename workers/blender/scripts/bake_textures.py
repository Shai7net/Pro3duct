import sys
import bpy

def bake_textures(filepath, out_path):
    print(f"Loading model for PBR mapping: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)

    # Standard PBR material node linking logic
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if principled:
                print(f"Verified PBR Principled BSDF on material: {mat.name}")
                # Ready to link baked textures here in production worker

    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        bake_textures(args[0], args[1])
