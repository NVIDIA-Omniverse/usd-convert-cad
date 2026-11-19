# usd-convert-cad Limitations

This file records known limitations for the `usd-convert-cad` package and the `omniverse-cad-to-usd` agent skill that drives it.

## Platform Support

- AutoCAD (`.dwg`, `.dxf`) and Revit (`.rvt`, `.rfa`) conversion is **not supported on `linux-aarch64`**. The HOOPS Exchange DWG/Revit readers are not available for that architecture, so these conversions fail with `A3D_LOAD_INVALID_FILE_FORMAT` (error code `-10005`) and produce no output.
- These formats are supported on `windows-x86_64` and `linux-x86_64`. All other listed formats are supported on all three platforms.
- Do not attempt DWG/DXF or RVT/RFA conversion on `linux-aarch64`; treat those inputs as unsupported on that platform.

## File Size

- Loading Revit source CAD files that are 2 GB or larger can fail due to a HOOPS Exchange SDK limitation.

## Revit Families

- Nested Revit families can be flattened during conversion and merge into one component in the resulting USD hierarchy.

## Material Preservation

- The HOOPS converter preserves physically based rendering (PBR) material
  properties only for glTF (`.gltf` and `.glb`) input. For other CAD and
  interchange formats, conversion may preserve basic colors and material
  assignments but does not preserve the complete source PBR material model.

## Revit Rooms and Spaces

- Revit Rooms and Spaces (spatial elements) are not converted to USD prims. They are defined by bounding elements such as walls and floors instead of being stored as solid geometry, and the HOOPS Exchange Revit reader does not expose them. Related metadata, such as "Room Bounding" on walls, floors, and doors, can still be converted with `--convert-metadata`.
- If you need Rooms and Spaces in USD, use [usd-exporter-revit](https://github.com/NVIDIA-Omniverse/usd-exporter-revit). It runs inside Revit and uses the Revit API to export them.

## Revit Pipe Catalog Elements

### Insufficient Tessellation Quality on Native Revit Pipe Catalog Elements

- When converting Revit models containing pipe catalog elements (pipes, elbows, couplings, tees, etc.), curved surfaces may appear faceted rather than smooth.
- This can result in visible shading artifacts on cylindrical and curved pipe components in the converted USD output.
- Post-conversion mesh cleanup plus normal generation can improve the visual quality of affected pipe elements.

The example below shows a faceted raw conversion and the smoother result after post-conversion mesh cleanup and normal generation.

![Revit pipe elbow before and after post-conversion optimization](docs/images/known-issues/revit_pipe_scene_opt_post_conversion.png)

Recommended workaround:

1. Convert the Revit file to USD with normals disabled, for example by using `--no-normals`.
2. Disable instancing or instanceability on the meshes that need the workaround.
3. Run the `usd-optimize` `meshCleanup` operation with vertex welding enabled.
4. Run the `usd-optimize` `generateNormals` operation with default settings.
5. Inspect curved pipe and elbow surfaces in the final USD asset.

Example `usd-optimize` operation stack:

```json
[
    {
        "operation": "meshCleanup",
        "mergeVertices": true
    },
    {
        "operation": "generateNormals"
    }
]
```

Install `usd-optimize` separately in the same Python 3.12 environment used for `usd-convert-cad`, then run the optimizer script after conversion finishes. The standalone `usd-convert-cad` CLI does not include a built-in post-processing runner.

```powershell
python -m pip install usd-optimize
usd-convert-cad -i model.rvt -o converted.usdc --no-normals --instancing-style none
python post_process_pipe_normals.py
```

Example Python post-process:

```python
from pxr import Usd
from usd_optimize.core import ExecutionContext, UsdOptimizeCore

input_path = "converted.usdc"
output_path = "converted_pipe_normals.usd"

stage = Usd.Stage.Open(input_path)
context = ExecutionContext()
context.set_stage(stage)

results = UsdOptimizeCore.getInstance().executeConfig(
    context,
    [
        {
            "operation": "meshCleanup",
            "mergeVertices": True,
        },
        {
            "operation": "generateNormals",
        },
    ],
)

for success, error, _output in results:
    if not success:
        raise RuntimeError(error)

stage.Export(output_path)
```

Mesh cleanup is important because normal generation works best when neighboring triangles share vertices. Use the workaround selectively on affected curved pipe geometry; aggressive smoothing across an entire model may soften hard-edged objects that should remain crisp.

## 2D Geometry Conversion

- Pass `--convert-curves` to convert visual 2D model-space linework from DWG/DXF files into USD `BasisCurves`. Filled regions may convert as meshes independently of this option.
- Paper-space layouts (title sheets / print layouts) are not supported; only model-space content is converted.
- Text, dimensions, and other annotations are not preserved as text.
- DWG and Revit file reading is not supported on `linux-aarch64`; see [Platform Support](#platform-support).

## Assembly Constraints

- Assembly-constraint export is disabled by default. Pass `--read-constraints` to enable it.
- Supported mappings include CATIA V5, NX, and SolidWorks `Fix`, CATIA V5 `Fix Together`, NX `Bond`, and SolidWorks `Lock` mate constraints.
- The listed fixed constraints become USD Physics fixed joints. Supported Contact constraints additionally apply rigid-body and collision APIs; see [Contact collisions](#constraint-groups-and-contact-collisions).
- Unsupported constraint types and unresolved constraint targets are not exported.
- The `--read-constraints` option is independent of `--convert-physics-data`.

## Source UVs and Material Textures

Source UVs are preserved by default as indexed face-varying `st`, `st1`, `st2`, etc., retaining
seams across welded vertices. Missing coordinates use an unauthored index; entirely untextured
meshes gain no UVs. Invalid offsets warn and are treated as missing; a renderer may sample the
placeholder. `--no-texture-coordinates` disables source UVs and texture-image export. This does not
generate projection UVs.

Supported material inputs include base color, normal, emissive, roughness, metalness, packed ORM,
and alpha-mask cutouts. Embedded PNG, JPEG, and BMP images are copied into `Textures/` beside the
output USD with relative paths and collision-safe names. Keep that directory with the USD when
moving or sharing it. USDZ packages referenced images into the archive.

Textures require enabled materials and source UVs, and a file-backed output destination. Textures
use `st`, repeat wrapping, and no texture transform. Other UV selections, component overrides,
non-unit factors, unsupported raw pixels, and image-write failures produce warnings. Repeated
texture inputs require unsupported layering; conflicting maps are skipped. Color/emissive modulation
requires white material color. Standalone opacity/occlusion, height bump, specular/glossiness,
clearcoat, and environment maps are unsupported. Packed ORM support does not translate
occlusion-strength factors. `BLEND` image alpha and `MASK` with non-unit scalar opacity warn and
skip image alpha; scalar opacity and other supported maps remain available. Texture support does not
guarantee complete source PBR fidelity for every format.

## Constraint Groups and Contact Collisions

`--read-constraints` remains opt-in and independent of `--convert-physics-data`. Supported fixed
joints are now nested under named and nested `ConstraintSet` USD Scope prims, so joint paths can
change. Supported `Contact` constraints apply `UsdPhysicsRigidBodyAPI` to bodies and
`UsdPhysicsCollisionAPI` / `UsdPhysicsMeshCollisionAPI` to descendant meshes. Contact export can
disable instancing on affected hierarchies.

Fixed joints can create rigid bodies without colliders. They preserve attachment relationships
but do not generate collision geometry or mass properties. Conversion warns when an enabled
rigid body has neither enabled collision shapes nor explicit positive mass and inertia.
Before simulation, add appropriate collision geometry or author mass and inertia explicitly.

Collision meshes use `convexHull`, which can close openings, fill concave regions, and create
artificial overlaps for hollow or concave parts. Inspect collision geometry before simulation.
Unsupported constraint types and unresolved targets are skipped.

The CLI uses file-path output, supporting Contact export with all composition styles. Backend
integrations using the `SdfLayer` output overload with references or payloads skip Contact
constraints and log an error; geometry and other physics may still succeed because this overload
does not export required child layers. This restriction does not apply to the CLI file-path call.

## Format Interpretation

- `.prt` and `.asm` file interpretation depends on source content because multiple CAD systems use those extensions.

## Runtime Requirements

- This wheel supports one converter core and does not expose converter selection.
- Installation requires network access to the Python package index hosting the wheel.

## References

- [HOOPS Core converter known issues](https://docs.omniverse.nvidia.com/kit/docs/omni.kit.converter.hoops_core/latest/Known_Issues.html#known-issues)
