# Omniverse CAD Converter to OpenUSD Data Mapping

## Introduction

### Overview

This document describes how the Omniverse CAD Converter maps CAD, AEC, and
interchange data to OpenUSD. It focuses on current Omniverse CAD Converter
behavior.

The Omniverse CAD Converter imports source files through Tech Soft's HOOPS
Exchange SDK. HOOPS Exchange reads supported formats into an in-memory model
made of model files, product occurrences, part definitions, representation
items, tessellation, graphics attributes, metadata, units, and
format-specific data. Product Representation Compact (PRC) is HOOPS
Exchange's native model format and a useful way to understand the SDK object
model, but the Omniverse CAD Converter does not require users to author,
inspect, or manage a PRC file as a separate interchange step.

The Omniverse CAD Converter consumes the model tree and SDK data surfaces
exposed by HOOPS Exchange and authors one or more OpenUSD layers. The output
is intended for visualization, review, analysis, and downstream scene
workflows. It is not a lossless CAD authoring format exporter.

The primary audience is:

- Users who need to understand what CAD data appears in converted USD.
- Developers integrating the converter into pipelines.
- Downstream tools that need reliable guidance about converter options and
  output structure.
- AI agents that need reliable source material for choosing converter options
  and explaining output USD structure.

### Reference Versions

Omniverse CAD Converter behavior depends on the HOOPS Exchange SDK, OpenUSD,
OpenUSD Exchange, and Omniverse CAD Converter versions included with a release.
Check package metadata and release notes for exact dependency versions.

This document separates implemented output from future or proposed mappings.
Behavioral claims describe the converter release documented by the
corresponding package metadata and release notes.

### General Assumptions and Constraints

This mapping describes one-way conversion from a CAD, AEC, or interchange input
file into OpenUSD. The converter does not preserve enough information for
general USD-to-CAD round trip.

The output layer must remain internally consistent: stage metrics, transforms,
mesh points, material bindings, metadata attributes, visibility, and
composition arcs must describe the same scene scale and hierarchy. Unit
handling is described in [Units and Stage Metrics](#units-and-stage-metrics).

The converter can serialize only data that HOOPS Exchange exposes through the
loaded model tree, loaded entity attributes, tessellation APIs, BIM APIs,
graphics attributes, or other SDK surfaces that the converter actually reads.
Source concepts that the SDK reader does not expose cannot be reconstructed
reliably in this converter.

Some HOOPS Exchange SDK concepts are useful conceptual matches for OpenUSD
schemas but are not emitted by the current converter. Those concepts are listed
in [Future or Proposed Mappings](#future-or-proposed-mappings), not mixed into
current behavior.

### What Is Not Preserved

The current Omniverse CAD Converter does not preserve:

- Enough source data for general CAD round trip.
- Native CAD B-rep topology as an OpenUSD B-rep schema. B-rep and poly B-rep
  geometry are emitted as tessellated `UsdGeomMesh`.
- Point sets, direction items, coordinate systems, or plane representation
  items as dedicated OpenUSD geometry prims.
- CAD assembly constraints other than supported fixed-joint and Contact mappings.
- Visible PMI geometry or editable semantic PMI as dedicated USD annotation
  prims.
- Revit Rooms or Spaces as standalone spatial prims.
- Construction and reference geometry when not loaded by Omniverse CAD Converter
  import options.
- Format-native unit fields that HOOPS Exchange does not expose through the
  loaded model tree.
- Suppressed product occurrences. Suppressed branches are skipped.
- Source data hidden by the HOOPS reader, source-file permissions, missing
  external components, or converter import options.

### Definitions, Acronyms, and Abbreviations

| Term | Description |
| --- | --- |
| Omniverse CAD Converter | NVIDIA converter that imports CAD, AEC, and interchange files and authors OpenUSD output. |
| HOOPS Exchange SDK | Tech Soft's HOOPS Exchange SDK, used by the Omniverse CAD Converter to import supported source formats. |
| CAD | Computer-aided design data read by HOOPS Exchange. |
| AEC | Architecture, engineering, and construction data. |
| BIM | Building Information Modeling data such as sites, buildings, levels, spaces, elements, and relationships. |
| FBX | Autodesk interchange format. The Omniverse CAD Converter relies on hierarchy and unit data exposed by HOOPS Exchange after import. |
| IFC | Industry Foundation Classes BIM exchange format. |
| JT | ISO-standardized product visualization format. The Omniverse CAD Converter has special handling for active layer-filter metadata when filtering hidden geometry. |
| Model file | HOOPS Exchange root object for an imported source. |
| Product occurrence | HOOPS Exchange assembly node. It may carry transform, unit, external file, prototype, visibility, and metadata. |
| Part definition | HOOPS Exchange reusable geometry container referenced by product occurrences. |
| PRC | Product Representation Compact, HOOPS Exchange's native compressed CAD representation. |
| Representation item | HOOPS Exchange geometric item below a part definition, such as B-rep, poly B-rep, set, curve, poly wire, point set, direction, coordinate system, or plane. |
| Tessellation | Triangulated or polyline data used to author `UsdGeomMesh` or `UsdGeomBasisCurves`. |
| PMI | Product manufacturing information such as annotations, dimensions, views, and semantic markup. |
| MPU | USD `metersPerUnit` stage metric. |
| RI | Representation item. |

## Concept Mapping Summary

This table gives the high-level HOOPS Exchange SDK to OpenUSD mapping performed
by the Omniverse CAD Converter. Later sections describe behavior, option gates,
and important limits.

| HOOPS Exchange SDK Concept | Current OpenUSD Result | Controls | Consumer Impact |
| --- | --- | --- | --- |
| Input CAD, AEC, or interchange file | Root `SdfLayer` and `UsdStage` | Output path, `compositionStyle` | One imported source becomes one root USD stage, with optional composed sub-stage files. |
| Model file | Stage metrics, default prim, creator metadata, traversal root | Release dependencies, source data exposed by HOOPS | Supplies model tree, unit context, and root traversal data. |
| Root product occurrence | Root hierarchy under the stage default prim | Source hierarchy, output file stem | Main assembly root becomes addressable USD hierarchy. |
| Product occurrence | `UsdGeomXform` with local transform, visibility, kind, display name, metadata when enabled | `filterStyle`, `omitHiddenOnLoad`, `convertMetadata`, `globalXforms` | Assembly structure, placement, names, hidden state, and metadata are preserved where exposed. |
| Suppressed product occurrence | Not emitted | HOOPS product flags | Suppressed branches do not appear in USD. |
| External product occurrence or file boundary | USD reference or payload to a sub-stage | `compositionStyle` | Large assemblies can remain split into composed USD asset files. |
| Part definition | Prototype `UsdGeomXform`, direct child hierarchy, or sub-stage definition | `instancingStyle`, `compositionStyle` | Reusable CAD parts can be shared through references and instanceable prims. |
| Representation item set | Traversed grouping of child representation items | Source RI hierarchy | May contribute grouping when named or transform-bearing; otherwise children may author geometry below surrounding hierarchy. |
| B-rep representation item | Tessellated `UsdGeomMesh`; optional RI metadata and physics attributes | `tessLOD`, `accurateTessellation`, `dedup`, `convertPhysicsData` | Native topology is not emitted; consumers receive triangulated meshes. |
| Poly B-rep representation item | `UsdGeomMesh` from existing tessellation | `dedup`, `convertPhysicsData` | Existing polygonal B-rep becomes mesh topology and points. |
| Curve representation item | `UsdGeomBasisCurves` when visible and enabled | `convertCurves` | Wire/curve data can be emitted as linear basis curves. |
| Poly wire representation item | `UsdGeomBasisCurves` when visible and enabled | `convertCurves` | Polyline wire data can be emitted as curve prims. |
| Point set, direction, coordinate system, plane RI | Not emitted as dedicated geometry | None currently | These SDK concepts are skipped by current RI traversal. |
| Tessellated faces and style groups | Mesh faces, `UsdGeomSubset`, material bindings, display primvars | `useMaterials`, `materialType` | Per-source-face style or material assignment can remain addressable without splitting every face into separate meshes. |
| HOOPS material and color data | `UsdShadeMaterial`, display primvars, and `omni:hoops:material:*` custom attributes | `useMaterials`, `materialType` | Visual appearance and raw material data remain queryable. |
| HOOPS attributes and properties | `omni:hoops:metadata:*` custom attributes | `convertMetadata` | Source metadata remains queryable as USD attributes. |
| IFC BIM relationships | `omni:hoops:metadata:bim:*` USD relationships | `convertMetadata` and HOOPS IFC relationship data | IFC connectivity can be traversed with USD relationship APIs when matching GlobalIds are exported. |
| Physical properties | `omni:hoops:physics:*` custom attributes on authored RI prims | `convertPhysicsData`, `physicsAccuracyLevel`, `physicsUseGeometryOnRiBRep` | Mass-property-like values can be queried without implying USD physics behavior. |
| Hidden state | Invisible, inactive, omitted, or emitted based on filter mode | `filterStyle`, `omitHiddenOnLoad` | Consumers can choose whether hidden source branches are present, hidden, inactive, or absent. |
| CATIA V5, NX, and SolidWorks `Fix`; CATIA V5 `Fix Together`; NX `Bond`; SolidWorks `Lock` mate | `UsdPhysicsFixedJoint` prims | `readConstraints` | `Fix` is world-anchored; the other listed constraints connect components and retain their relative pose. |

## Current Converter Behavior

### Stage, Model File, and Root Prim

The converter creates or opens a USD stage for the output layer and configures a
default prim. The default prim is an `Xform` and is assigned `kind=assembly`.
The default prim name is derived from the output file stem when converting to a
file, or from the input file stem when converting directly to a layer.

The HOOPS model file supplies the root product occurrence list. The converter
uses the first root product occurrence to configure `metersPerUnit`:

```text
metersPerUnit = A3DAsmProductOccurrenceData::m_dUnit * 0.001
```

HOOPS `m_dUnit` is millimeters per model unit. Multiplying by `0.001` converts
that value to USD meters per unit. Collada, glTF, and GLB instead use `1.0` because
their imported geometry and transforms are in meters.

The converter sets `creator` metadata through the USD layer export path when a
creator string is supplied or left at its build-derived default.

### Product Occurrence Hierarchy

HOOPS product occurrences become `UsdGeomXform` prims when the current mapping
needs an authored hierarchy prim. The converter preserves source names as
display names when the encoded USD identifier differs from the original source
name. Authored prim names are encoded to valid and unique USD identifiers.

Product occurrence transforms are authored as local xform data unless
`instancingStyle=eNone` and `globalXforms=true`. In that global-transform mode,
mesh prims receive global transforms and intermediate hierarchy xforms may not
carry the local transform opinions a reader would see in the default mode.

USD model kinds are assigned after traversal:

- Default prim: `assembly`.
- Parents of authored geometry: `component`.
- Intermediate ancestors: `group`.

Suppressed product occurrences are skipped before traversal. Hidden or removed
product occurrences are handled by `filterStyle`, described in
[Visibility, Suppression, and Filtering](#visibility-suppression-and-filtering).

### Composition and External File Boundaries

`compositionStyle` controls whether detected external CAD file boundaries become
separate USD files:

- `eNone` authors a monolithic output layer.
- `eReference` authors sub-stage files and composes them back by references.
- `ePayload` authors sub-stage files and composes them back by payloads.

File boundaries are detected from product occurrence file paths exposed by
HOOPS Exchange. Sub-stage files are named from the external CAD file stem, with
suffixes added when needed to avoid output-path collisions.

Sub-stages inherit the parent stage up-axis and `metersPerUnit` values. A
sub-stage default prim is created from the external CAD file stem. The
composition arc targets that sub-stage default prim.

Composition arcs are deferred until traversal finishes. This avoids resolving
partially-authored sub-stages during the tree walk.

### Instancing and Prototypes

Prototypes default to repeated parts only (`prototypeAllParts=false`); unique parts are authored
directly. Use `--prototype-all-parts` to restore all-parts prototypes. `--instancing-style none`
disables prototypes regardless of this flag.

`instancingStyle` controls how reusable parts are authored:

- `eNone` emits direct hierarchy without prototype references.
- `eReference` emits prototype references but does not mark occurrence prims
  instanceable.
- `eInstanceableReference` emits prototype references and marks eligible
  occurrence prims instanceable.

With monolithic output and instancing enabled, the converter creates a
`Prototypes` class prim below the default prim. The first authored occurrence of
a reusable part creates a prototype under that class prim. Later occurrences
author internal references to the prototype.

With multi-file composition, sub-stages do not create an internal `Prototypes`
class prim. Geometry is authored directly in each sub-stage, and the external
USD file serves as the shared definition. When multiple parent prims reference
the same sub-stage and `instancingStyle=eInstanceableReference`, those parent
prims can be marked instanceable if doing so would not discard local child
opinions.

The converter checks for local child specs before setting `instanceable=true`.
If local child opinions would be discarded by instanceability, the reference is
kept non-instanceable.

### Representation Item Traversal

Part definitions contain representation items. Current RI traversal handles the
following item types:

| HOOPS RI Type | Current Handling |
| --- | --- |
| `kA3DTypeRiBrepModel` | Computes or retrieves tessellation and emits `UsdGeomMesh`. Optional physical properties can be authored on the RI prim when one exists. |
| `kA3DTypeRiPolyBrepModel` | Reads tessellation and emits `UsdGeomMesh`. Optional physical properties can be authored on the RI prim when one exists. |
| `kA3DTypeRiSet` | Traverses child representation items. |
| `kA3DTypeRiCurve` | Emits `UsdGeomBasisCurves` when `convertCurves=true` and the item is visible and not removed. |
| `kA3DTypeRiPolyWire` | Emits `UsdGeomBasisCurves` when `convertCurves=true` and the item is visible and not removed. |
| `kA3DTypeRiPointSet` | No dedicated geometry is emitted. |
| `kA3DTypeRiDirection` | No dedicated geometry is emitted. |
| `kA3DTypeRiCoordinateSystem` | No dedicated geometry is emitted. |
| `kA3DTypeRiPlane` | No dedicated geometry is emitted. |

Representation item names can create an intermediate USD prim path. If an RI
has no name and no non-identity local transform, geometry may be authored
directly below the surrounding product or part path instead of under a named RI
prim.

### B-rep, Poly B-rep, and Meshes

The converter emits tessellated geometry. B-rep and poly B-rep representation
items are converted to triangulated `UsdGeomMesh` prims rather than native
OpenUSD B-rep schema data.

For each tessellated triangle, the converter authors:

- `faceVertexCounts` with value `3`.
- `faceVertexIndices` indexing authored points.
- `points` as `point3f[]`.
- Normals as indexed vertex primvar data when normal data exists in the mesh
  converter path.

The mesh converter removes degenerate triangles. If source normals are invalid,
the converter computes replacement triangle normals.

Mesh points are authored as float values. To reduce precision loss for large
coordinate magnitudes, the converter subtracts the representation item's
bounding-box centroid from authored points and sets a translate xform on the
mesh prim. This keeps local point values closer to the origin while preserving
the final placement through transforms.

`dedup=true` welds repeated `(position, normal)` pairs and reindexes mesh faces.
`dedup=false` leaves the generated point and normal arrays unwelded.


### Curves and Poly Wires

When `convertCurves=true`, visible HOOPS curve and poly wire tessellation can
be emitted as `UsdGeomBasisCurves`. The converter authors linear, nonperiodic
curves with:

- `points`.
- `curveVertexCounts`.
- Constant `primvars:displayColor`.
- Constant `primvars:displayOpacity`.
- Constant `primvars:widths` when HOOPS line width is greater than zero.

Hidden or removed curve items are not emitted by selecting `filterStyle=eNone`.
The current curve path requires the source item to be shown and not removed.

### Materials, Display Color, and Raw Material Attributes

Material generation is controlled by `useMaterials` and `materialType`.

`useMaterials=false` forces converter material type to `eNone`. `materialType`
then has no generated material-network effect.

| Effective Material Type | Output |
| --- | --- |
| `eNone` | No source-material network. A root-bound `DefaultDisplayColorMaterial` reads display-color and display-opacity primvars. Raw `omni:hoops:material:*` attributes are still authored when material assignments exist. |
| `ePreviewSurface` | USD Preview Surface materials are generated and bound. Raw `omni:hoops:material:*` attributes are also authored on the mesh or subset binding target. |
| `ePreviewSurface_OmniPBR` | OmniPBR materials are generated with Preview Surface support and bound. Raw `omni:hoops:material:*` attributes are also authored on the mesh or subset binding target. |
| `ePreviewSurface_MaterialX` | OpenPBR MaterialX materials are generated for the `mtlx` render context. USD Preview Surface fallback networks are also generated and bound. |

The converter deduplicates generated material prims by material parameters in a
global materials scope under the default prim. For prototype or composed
contexts that need local material bindings, local material prims can specialize
the global material.

When a mesh has multiple source material assignments, the converter creates
`UsdGeomSubset` children with:

- `elementType = "face"`.
- `familyName = "materialBind"`.
- `indices` containing the mesh face indices assigned to that material.

The subset becomes the material binding target. Raw material custom attributes
are authored on that target.

When a mesh has one material assignment, raw material custom attributes are
authored on the mesh itself.

Current raw material attributes are:

| Attribute | Type | Meaning |
| --- | --- | --- |
| `omni:hoops:material:name` | `string` | Source material name when available. |
| `omni:hoops:material:diffuseColor` | `color3f` | Diffuse or display color selected from HOOPS cascaded attributes. |
| `omni:hoops:material:opacity` | `float` | Normalized opacity. |

Display colors and opacity are authored as primvars alongside generated
materials. They are also authored when generated materials are disabled:

- Constant interpolation when one value applies to the mesh.
- Uniform indexed interpolation when values vary per source style assignment.

When generated materials are disabled, the converter binds one
`DefaultDisplayColorMaterial` at the default prim. Its Preview Surface shader
reads `displayColor` and `displayOpacity` through primvar readers.

### Source UVs and Material Textures

Source UVs are preserved by default as indexed face-varying `st`, `st1`, `st2`, etc., retaining
seams across welded vertices. Missing coordinates use an unauthored index; entirely untextured
meshes gain no UVs. Invalid offsets warn and are treated as missing; a renderer may sample the
placeholder. `--no-texture-coordinates` disables source UVs and texture-image export. This does not
generate projection UVs.

Supported material inputs include base color, normal, emissive, roughness, metalness, packed ORM,
and alpha-mask cutouts. Embedded PNG, JPEG, and BMP images are copied into `Textures/` beside the
output USD with relative paths and collision-safe names. Keep that directory with the USD when
moving or sharing it. USDZ packages referenced images into the archive.

Textures require enabled materials and source UVs. Materials with different
texture assignments remain distinct even when their scalar values match.
See [texture limitations](../LIMITATIONS.md#source-uvs-and-material-textures)
for supported mappings, channels, and alpha behavior.

### Metadata Attributes

When `convertMetadata=true`, HOOPS attributes and properties are authored as
custom USD attributes under `omni:hoops:metadata:*`.

Attribute names are built from the HOOPS attribute title and single-attribute
title. If both exist, the converter joins them with `:`. If neither title
exists, it uses `UNKNOWN_TITLE`. Names are then encoded to valid USD property
names.

Current value-type mapping:

| HOOPS Attribute Type | USD Attribute Type |
| --- | --- |
| `kA3DModellerAttributeTypeInt` | `Int` |
| `kA3DModellerAttributeTypeReal` | `Double` |
| `kA3DModellerAttributeTypeString` | `String` |
| `kA3DModellerAttributeTypeTime` | `String` |
| `kA3DModellerAttributeTypeNull` | Not authored |

Metadata attributes are authored with uniform variability. Display names are set
to the unsanitized metadata name when the attribute is created.

For JT files, attributes may be read even when `convertMetadata=false` if hidden
geometry filtering needs active layer-filter metadata. That read path supports
filtering only. It does not author metadata to USD unless `convertMetadata=true`.

### IFC BIM Relationships

IFC BIM relationship export depends on three conditions:

1. HOOPS Exchange exposes BIM relationship data on the model file.
2. Metadata reading is enabled by `convertMetadata=true`.
3. Related IFC elements can be matched to authored USD prims by exported
   `GlobalId` metadata attributes.

The converter reads BIM relationships from HOOPS BIM data and creates USD
relationships on the relating prim. Relationship targets are the USD prim paths
for related elements with matching GlobalIds.

Current relationship names:

| HOOPS BIM Relationship | USD Relationship |
| --- | --- |
| Contained in spatial structure | `omni:hoops:metadata:bim:containedInSpatialStructure` |
| Aggregates | `omni:hoops:metadata:bim:aggregates` |
| Fills element | `omni:hoops:metadata:bim:fillsElement` |
| Voids element | `omni:hoops:metadata:bim:voidsElement` |
| Space boundary | `omni:hoops:metadata:bim:spaceBoundary` |
| Connects path elements | `omni:hoops:metadata:bim:connectsPathElements` |
| Assigns to group | `omni:hoops:metadata:bim:assignsToGroup` |

The converter does not infer BIM relationships from geometry, names, spatial
overlap, or Revit room solids. Missing or unmatched GlobalIds are skipped.

### Physical Properties

When `convertPhysicsData=true`, the converter computes physical properties for
B-rep and poly B-rep representation items using HOOPS Exchange physical
property APIs.

Physical properties are authored as metadata-style custom USD attributes under
`omni:hoops:physics:*`. They are not USD physics simulation data and do not
apply `UsdPhysics` APIs.

Current physics attributes:

| Attribute | Type | Notes |
| --- | --- | --- |
| `omni:hoops:physics:surfaceArea` | `Double` | Surface area from HOOPS physical properties. |
| `omni:hoops:physics:gravityCenterSurfacic` | `Point3d` | Surfacic center of gravity. |
| `omni:hoops:physics:areaMatrixOfInertia` | `DoubleArray` | 3x3 area inertia matrix stored as 9 values. |
| `omni:hoops:physics:volume` | `Double` | Authored only when HOOPS reports volume computed. |
| `omni:hoops:physics:gravityCenterVolumetric` | `Point3d` | Authored only when volume is computed. |
| `omni:hoops:physics:volumeMatrixOfInertia` | `DoubleArray` | Authored only when volume is computed. |
| `omni:hoops:physics:density` | `Double` | Authored only when material density is greater than zero. |

These attributes are authored on the representation-item prim when that prim is
actually authored. If an unnamed, identity-transform RI does not create an
intermediate RI prim, physics attributes are not authored on the mesh by
default.

`physicsAccuracyLevel` is clamped between `0.0` and `1.0` and passed to
`A3DPhysicalPropertiesData::m_dAccuracyLevel`.

`physicsUseGeometryOnRiBRep` maps to
`A3DPhysicalPropertiesData::m_bUseGeometryOnRiBRep`. It requests exact B-rep
geometry for B-rep physical-property computation when available. It does not
cause native B-rep geometry to be authored to USD.

### Assembly Constraints and USD Physics Joints

When `readConstraints=true`, the converter loads supported native assembly
constraints and authors USD Physics fixed joints and supported Contact collision
data. The option defaults to `false`, making constraint conversion opt-in.

The source-CAD-to-USD mapping is:

| Source file format | Source constraint | OpenUSD result |
| --- | --- | --- |
| CATIA V5 (`.CATProduct`) | `Fix` | One world-anchored `UsdPhysicsFixedJoint` per constrained component. The first body relationship is omitted to represent the static world, and the second targets the component. |
| CATIA V5 (`.CATProduct`) | `Fix Together` | Component-to-component `UsdPhysicsFixedJoint` prims that preserve the authored relative pose. A group of N resolved components produces N-1 joints. |
| NX (`.prt`) | `Fix` | One world-anchored `UsdPhysicsFixedJoint` per constrained component. |
| NX (`.prt`) | `Bond` | Component-to-component `UsdPhysicsFixedJoint` prims that preserve the authored relative pose. A group of N resolved components produces N-1 joints. |
| SolidWorks (`.SLDASM`) | `Fix` | One world-anchored `UsdPhysicsFixedJoint` per constrained component. |
| SolidWorks (`.SLDASM`) | `Lock` mate | Component-to-component `UsdPhysicsFixedJoint` prims that preserve the authored relative pose. A group of N resolved components produces N-1 joints. |

The converter authors `localPos0`, `localRot0`, `localPos1`, and `localRot1` so
the fixed joint preserves the component's world pose for CATIA V5, NX, and
SolidWorks `Fix`, or the authored relative pose for CATIA V5 `Fix Together`, NX
`Bond`, and SolidWorks `Lock` mate. Named and nested constraint sets become Scope prims, so joint paths can change.
Source constraint status is represented by `physics:jointEnabled`: OK status
uses the enabled fallback, while other statuses author `false`. Joint body
relationships target converted product-occurrence prims.
Source constraint names are used for joint prim names, with display names
preserved when USD identifier encoding changes the source name.

`readConstraints` is independent of `convertPhysicsData`. The former authors
USD Physics joints and supported Contact rigid-body/collision schemas; the
latter computes mass-property-like values and authors them as
`omni:hoops:physics:*` custom attributes.

Supported `Contact` constraints apply `UsdPhysicsRigidBodyAPI` to bodies and
`UsdPhysicsCollisionAPI` / `UsdPhysicsMeshCollisionAPI` to descendant meshes.
Contact export can disable instancing. Collision meshes use `convexHull`,
which can fill openings and concavities and cause artificial overlaps.
The CLI uses file-path output, supporting Contact with all composition styles.
For backend integrations, composed `SdfLayer` output can skip Contact while
other conversion succeeds; see [constraint limitations](../LIMITATIONS.md#constraint-groups-and-contact-collisions).

### Visibility, Suppression, and Filtering

Visibility comes from HOOPS graphics behavior, cascaded attributes, simplified
representation state, JT layer filters, and converter options.

Suppressed product occurrences are skipped regardless of `filterStyle`.

Hidden, removed, or excluded items are handled by `filterStyle`:

| `filterStyle` | Behavior |
| --- | --- |
| `eNone` | Converts most hidden geometry as visible for mesh paths, subject to source data availability. Curves still require shown/not removed state. |
| `eOmit` | Skips hidden or removed elements and their descendants. |
| `eHide` | Converts hidden elements but authors invisible imageable prims. |
| `eDeactivate` | Converts hidden elements and deactivates affected prims after traversal. |

`omitHiddenOnLoad=true` affects only `filterStyle=eOmit`. In that mode, the
converter requests that HOOPS Exchange not load hidden objects.

For JT files with `filterStyle` other than `eNone`, the converter reads active
layer-filter attributes. A representation item with a `LAYER` attribute is
visible only when one of its layer IDs is in the active layer-filter set.

For Creo files, `viewLayerName` selects a simplified representation by matching
a HOOPS view name. The converter gathers linked-item behavior from that view
and treats excluded product occurrences or representation items as hidden under
the selected filter mode.

### Units and Stage Metrics

USD stage metrics define the physical interpretation of authored coordinates.
For most formats, the converter authors `metersPerUnit` from the first root
product occurrence unit reported by HOOPS Exchange:

```text
metersPerUnit = productOccurrence.m_dUnit * 0.001
```

Collada, glTF, and GLB use `metersPerUnit = 1.0`: their imported geometry and
transforms describe a scene in meters.

The converter does not independently parse every source format's native unit
fields. If HOOPS Exchange does not expose a unit through the loaded model tree,
the converter cannot reconstruct it separately.

Sub-stages created for multi-file composition inherit the parent stage
`metersPerUnit`.

The `upAxis` parameter controls authored stage up-axis:

| `upAxis` | Current Behavior |
| --- | --- |
| `eFileDefault` | Chooses Y-up for Creo, SolidWorks, Collada, and glTF; chooses Z-up for other modeller types. |
| `eYup` | Authors Y-up. |
| `eZup` | Authors Z-up. |

The up-axis setting changes stage metadata only; it does not rotate mesh points
or transforms. Consumers must interpret it together with authored transforms
and mesh coordinates.

## Conversion Options That Affect Mapping

Names in this table match Omniverse CAD Converter parameters and file-format
arguments unless noted. Integer enum values are the values passed through
file-format arguments.

| Option | Values and Defaults | Mapping Impact |
| --- | --- | --- |
| `compositionStyle` | `eNone` (0, default), `eReference` (1), `ePayload` (2) | Chooses monolithic output or separate files composed by references or payloads. |
| `instancingStyle` | `eNone` (0), `eReference` (1), `eInstanceableReference` (2, default) | Controls prototype references and whether eligible occurrence prims are marked instanceable. |
| `prototypeAllParts` | `false` default | Creates prototypes only for repeated parts; `true` includes unique parts unless instancing is disabled. |
| `convertTextureCoordinates` | `true` default | Preserves source UV sets; disabling also prevents material image export. |
| `instancing` | Boolean legacy argument | Maps `true` to `eInstanceableReference` and `false` to `eNone` before `instancingStyle` is parsed. |
| `globalXforms` | `false` default | When instancing is disabled, chooses local transforms on hierarchy prims or global transforms on mesh prims. |
| `filterStyle` | `eNone` (0), `eOmit` (1), `eHide` (2, default), `eDeactivate` (3) | Controls hidden or removed source element handling. Invalid file-format values fall back to `eNone` during argument parsing. |
| `omitHiddenOnLoad` | `true` default | With `filterStyle=eOmit`, requests hidden objects be skipped during HOOPS loading. |
| `convertCurves` | `false` default | Enables visible curve and poly wire output as `UsdGeomBasisCurves`. |
| `convertMetadata` | `false` default | Enables source metadata attributes and IFC BIM relationship export support. |
| `readConstraints` | `false` default | Exports CATIA V5, NX, and SolidWorks `Fix`, CATIA V5 `Fix Together`, NX `Bond`, and SolidWorks `Lock` mate as USD Physics fixed joints under constraint-set scopes, and supported Contact constraints as rigid-body/collision APIs. |
| `convertPhysicsData` | `false` default | Enables physical-property custom attributes on authored B-rep or poly B-rep RI prims. |
| `physicsAccuracyLevel` | `0.0` through `1.0`, default `0.99` | Sets HOOPS physical-property computation accuracy. |
| `physicsUseGeometryOnRiBRep` | `false` default | Requests exact B-rep geometry for physical-property computation when available. |
| `useMaterials` | `true` default | Enables generated material networks when `materialType` is not `eNone`; `false` forces effective material type to `eNone`. |
| `materialType` | `eNone` (0), `ePreviewSurface` (1, default), `ePreviewSurface_OmniPBR` (2), `ePreviewSurface_MaterialX` (3) | Chooses the generated material network type. MaterialX output includes a Preview Surface fallback. Invalid values fall back to `ePreviewSurface`. |
| `dedup` | `true` default | Welds repeated position/normal pairs and reindexes mesh topology. |
| `tessLOD` | `0` through `4`, default `2` | Chooses HOOPS tessellation level of detail for import and fallback tessellation. |
| `accurateTessellation` | `false` default | Requests analysis-oriented tessellation rather than visualization-oriented tessellation. |
| `accurateSurfaceCurvatures` | `true` default | Lets surface curvature influence tessellation triangle elongation. |
| `revitLOD` | `0` through `3`, default `0` | Chooses Revit detail level loaded by HOOPS. Invalid runtime values fall back to `0` at import. |
| `upAxis` | `eFileDefault` (0, default), `eYup` (1), `eZup` (2) | Chooses authored USD stage up-axis policy. |
| `creator` | Build-derived string by default | Authors creator metadata through USD layer export/configuration paths. |
| `viewLayerName` | Empty string default | Selects a Creo simplified representation by view name and applies its hidden/excluded behavior. |
| `reportProgress` | `false` default | Enables progress logging. Does not change USD mapping. |
| `reportProgressFreq` | `4.0` default | Controls progress reporting frequency. Does not change USD mapping. |

## Example USD Shapes

Exact prim names depend on source names, default prim names, composition mode,
and USD identifier encoding. These examples show structural shape only.

### Single Mesh Part

```usda
def Xform "Assembly" (
    kind = "assembly"
)
{
    def Xform "Part" (
        kind = "component"
    )
    {
        def Mesh "Mesh"
        {
            int[] faceVertexCounts = [3, 3, ...]
            int[] faceVertexIndices = [...]
            point3f[] points = [...]
        }
    }
}
```

### Monolithic Prototype Reference

```usda
def Xform "Assembly" (
    kind = "assembly"
)
{
    class Scope "Prototypes"
    {
        def Xform "ReusablePart"
        {
            def Mesh "Mesh" { ... }
        }
    }

    over "OccurrenceA" (
        prepend references = </Assembly/Prototypes/ReusablePart>
    )
    {
        matrix4d xformOp:transform = ...
    }
}
```

### Multi-File Composition Arc

```usda
def Xform "Assembly"
{
    def Xform "ExternalBracket" (
        prepend references = @bracket.usd@</bracket>
    )
    {
        matrix4d xformOp:transform = ...
    }
}
```

With `compositionStyle=ePayload`, the arc is a payload instead of a reference.

### IFC Relationship

```usda
def Xform "BuildingStorey"
{
    rel omni:hoops:metadata:bim:containedInSpatialStructure = [
        </Model/Wall_001>,
        </Model/Door_001>
    ]
}
```

### Material Data Without Generated Materials

```usda
def Mesh "Mesh"
{
    color3f[] primvars:displayColor = [(0.8, 0.6, 0.4)]
    float[] primvars:displayOpacity = [1]
    custom color3f omni:hoops:material:diffuseColor = (0.8, 0.6, 0.4)
    custom float omni:hoops:material:opacity = 1
}
```

### Face Subset Material Binding

```usda
def Mesh "Mesh"
{
    int[] faceVertexCounts = [3, 3, 3]

    def GeomSubset "PaintedMaterial"
    {
        uniform token elementType = "face"
        uniform token familyName = "materialBind"
        int[] indices = [0, 2]
        custom string omni:hoops:material:name = "PaintedMaterial"
    }
}
```

## Format-Specific Concepts

### Creo Simplified Representations

`viewLayerName` selects a Creo simplified representation when HOOPS exposes it
as a view. The converter compares view names case-insensitively because HOOPS
may uppercase simplified representation names. Linked-item graphics behavior
from the selected view is used to mark source entities as hidden or removed for
the selected filter mode.

Selecting a simplified representation requires PMI/view data to be read, but it
does not imply PMI geometry or semantic PMI export.

### PMI and Source Markup

PMI can include dimensions, annotations, views, and other manufacturing data.
The converter may read PMI-related data for metadata or source-view features,
but the current mapping does not author visible PMI geometry, dedicated PMI
schemas, or editable CAD PMI semantics.

If a workflow depends on PMI, validate representative source files and converted
USD output directly.

### JT Active Layer Filters

For JT inputs, active layer-filter metadata can affect visibility. When
`filterStyle` is not `eNone`, the converter reads active layer-filter
attributes and tests RI `LAYER` attributes against that active layer set.

This metadata read path does not author metadata unless `convertMetadata=true`.

### IFC BIM Relationships

IFC relationship data is mapped only when HOOPS exposes BIM relationship
entities and the converter can match relating and related BIM elements to USD
prims through exported `GlobalId` metadata. The converter does not synthesize
IFC relationships from names, geometry, containment guesses, or authored USD
hierarchy.

### Revit Metadata, Rooms, and Spaces

The Revit reader can expose visualization data, tessellation, views, materials,
and metadata through HOOPS Exchange. `revitLOD` controls the Revit detail level
requested during loading.

With `convertMetadata=true`, exposed Revit properties become
`omni:hoops:metadata:*` custom attributes.

Revit Rooms and Spaces are not emitted as standalone USD prims. The current BIM
relationship mapping is based on HOOPS BIM relationship entities such as those
available for IFC. The converter does not reconstruct room or space solids from
Revit boundaries or metadata.

## Appendices

### Appendix A: Tessellated Surfaces to `UsdGeomMesh`

HOOPS Exchange can provide triangulated geometry for B-rep and poly B-rep
representation items. Current converter mesh output maps that tessellation to
`UsdGeomMesh`, `UsdGeomPrimvar`, `UsdGeomSubset`, and material binding concepts.

| HOOPS Tessellation Data | Current OpenUSD Mapping | Notes |
| --- | --- | --- |
| Source triangle vertex data | `UsdGeomMesh` topology and points | Source triangles become `faceVertexCounts=3`, `faceVertexIndices`, and `points`. |
| Source normals | Indexed vertex normal primvar data | Authored when normal data exists in the mesh converter path. Invalid normals can be recomputed. |
| Source texture coordinates | Indexed face-varying `st`, `st1`, etc. | Enabled by default; preserves seams across welded vertices. |
| Source style, material, or color groups | `UsdGeomSubset`, material bindings, raw material attributes, or display primvars | Used to preserve assignment at mesh or subset granularity. |
| Source face grouping | Mesh face-index ranges and subset indices | Source face groups influence material grouping but are not always separate USD prims. |

Each source triangle becomes one USD mesh face. The converter may remove
degenerate triangles, compute replacement normals, translate local points around
a bounding-box centroid, and weld duplicate position/normal pairs.

### Appendix B: Mesh Granularity

A single source representation item can contain multiple source face groups,
style assignments, and material colors. Splitting every source face into a
separate mesh maximizes addressability but increases prim count and duplicates
shared data.

The Omniverse CAD Converter keeps one mesh where practical and uses material
subsets, material bindings, display primvars, and raw material attributes for
assignment-level addressability.

When multiple materials apply to one mesh, `UsdGeomSubset` children are created
for material binding. When material networks are disabled, uniform or constant
display primvars can carry color and opacity without generated `UsdShade`
materials.

### Appendix C: Attribute Mapping

HOOPS `A3DMiscSingleAttributeData` values are mapped to custom USD attributes
under `omni:hoops:metadata:*` when `convertMetadata=true`.

Current converter type mapping:

| HOOPS Attribute Type | Current USD Type |
| --- | --- |
| Integer | `SdfValueTypeNames->Int` |
| Real | `SdfValueTypeNames->Double` |
| String | `SdfValueTypeNames->String` |
| Time | `SdfValueTypeNames->String` |

The converter authors USD attributes, not custom USD metadata fields. This is
intentional because attributes are easier to inspect in USD editors and can
carry variability and display metadata.
