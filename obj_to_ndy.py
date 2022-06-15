# Created by Crt Vavros.
# The idea of this script is to export blender object hierarchy geometry to NDY/JKL file format and
# then paste exported sections to the end of existing NDY/JKL file to be modified. 
# To get correct indices of exported object's georesurces set script's variables: 
#   mat_start_idx, vert_start_idx, uv_start_idx and surface_start_idx accordingly.
# Exported NDY/JKL sections: copyright, header, materials and georesources without adjoin section.

# Script requires Sith Blender addon to be installed
# Copy the script in Blender script editor, select object and run the script.

import bpy
from math import degrees, pow, sqrt
from mathutils import Vector, Matrix

from sith.text.serutils import *
from sith.model import *
from sith.model.model3doWriter import _vector_to_str as vec2str
from sith.model.model3doWriter import _radius_to_str as r2str
from sith.model.model3doExporter import _model3do_add_obj as model3do_add_obj
from sith.types import Vector3f, Vector4f

from enum import Enum
from typing import List, Tuple

class NdyVersion(Enum):
    IJIM  = 0,
    JKDF2 = 1
    MOTS  = 2

###############################################
# Adjust vars below
out_file             = "test.gndy"
out_version          = NdyVersion.IJIM
mat_start_idx        = 0
vert_start_idx       = 0
uv_start_idx         = 0
surface_start_idx    = 0
sector_idx           = 0
ambient_light        = Vector3f(1.0, 1.0, 1.0)
sector_extra_light   = Vector3f(0.0, 0.0, 0.0)
default_surfflags    = 0x04 # collision

# JKDF2 & MOTS specific
colormaps            = ["dflt.cmp"]
default_colormap_idx = 0

separate_sector_surfaces = True
##############################################

def _vec_convert_to_space(mat: Matrix, vec):
    return mat * Vector(vec)

def _color_to_str(color: Tuple[Vector4f, Vector3f, float]) -> str:
    if isinstance(color, (Vector4f, Vector3f)):
        return vec2str(color, True, 0)
    elif isinstance(color, float):
        return f"{color:.2f}"
def _rgba_to_rgb(rgba:Vector4f):
    return Vector3f(rgba.x, rgba.y, rgba.z)

def _rgba_to_intensity(rgba:Vector4f) -> float:
    return (rgba.x + rgba.y + rgba. z) * 0.33333 # divide by 3

def _rgba_to_intensity_str(rgba:Vector4f) -> str:
    return _color_to_str(_rgba_to_intensity(rgba))

def _ndy_write_section_copyright_ijim(file):
    writeSectionTitle(file, "COPYRIGHT")
    writeLine(file,
        "................................\n"
        "................@...@...@...@...\n"
        ".............@...@..@..@...@....\n"
        "................@.@.@.@.@.@.....\n"
        "@@@@@@@@......@...........@.....\n"
        "@@@@@@@@....@@......@@@....@....\n"
        "@@.....@.....@......@@@.....@@..\n"
        "@@.@@@@@......@.....@@@......@@.\n"
        "@@@@@@@@.......@....@@.....@@...\n"
        "@@@@@@@@.........@@@@@@@@@@.....\n"
        "@@@@@@@@..........@@@@@@........\n"
        "@@.....@..........@@@@@.........\n"
        "@@.@@@@@.........@@@@@@.........\n"
        "@@.....@.........@@@@@@.........\n"
        "@@@@@@@@.........@@@@@@.........\n"
        "@@@@@@@@.........@@@@@@@........\n"
        "@@@...@@.........@@@@@@@........\n"
        "@@.@@@.@.........@.....@........\n"
        "@@..@..@........@.......@.......\n"
        "@@@@@@@@........@.......@.......\n"
        "@@@@@@@@.......@........@.......\n"
        "@@..@@@@.......@........@.......\n"
        "@@@@..@@......@.........@.......\n"
        "@@@@.@.@......@.........@.......\n"
        "@@....@@........................\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "@@@@@@@@@@@@@.@@@@@@@@@@@@@@@@@@\n"
        "@@.@@..@@@@@..@@@@@@@@@@.@@@@@@@\n"
        "@@.@.@.@@@@.@.@@@.@..@@...@@@..@\n"
        "@@..@@@@@@....@@@..@@@@@.@@@@.@@\n"
        "@@@@@@@@...@@.@@@.@@@@@..@@...@@\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "@.(c).lucasarts.entertainment..@\n"
        "@.........company.llc..........@\n"
        "@....(c).lucasfilm.ltd.&.tm....@\n"
        "@.....all.rights.reserved......@\n"
        "@...used.under.authorization...@\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    )
    writeLine(file, "################################")

def _ndy_write_section_copyright_jkdf2(file):
    writeSectionTitle(file, "COPYRIGHT")
    writeLine(file,
        "................................\n"
        "................@...@...@...@...\n"
        ".............@...@..@..@...@....\n"
        "................@.@.@.@.@.@.....\n"
        "@@@@@@@@......@...........@.....\n"
        "@@@@@@@@....@@......@@@....@....\n"
        "@@.....@.....@......@@@.....@@..\n"
        "@@.@@@@@......@.....@@@......@@.\n"
        "@@@@@@@@.......@....@@.....@@...\n"
        "@@@@@@@@.........@@@@@@@@@@.....\n"
        "@@@@@@@@..........@@@@@@........\n"
        "@@.....@..........@@@@@.........\n"
        "@@.@@@@@.........@@@@@@.........\n"
        "@@.....@.........@@@@@@.........\n"
        "@@@@@@@@.........@@@@@@.........\n"
        "@@@@@@@@.........@@@@@@@........\n"
        "@@@...@@.........@@@@@@@........\n"
        "@@.@@@.@.........@.....@........\n"
        "@@..@..@........@.......@.......\n"
        "@@@@@@@@........@.......@.......\n"
        "@@@@@@@@.......@........@.......\n"
        "@@..@@@@.......@........@.......\n"
        "@@@@..@@......@.........@.......\n"
        "@@@@.@.@......@.........@.......\n"
        "@@....@@........................\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "@@@@@@@@@@@@@.@@@@@@@@@@@@@@@@@@\n"
        "@@.@@..@@@@@..@@@@@@@@@@.@@@@@@@\n"
        "@@.@.@.@@@@.@.@@@.@..@@...@@@..@\n"
        "@@..@@@@@@....@@@..@@@@@.@@@@.@@\n"
        "@@@@@@@@...@@.@@@.@@@@@..@@...@@\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "@.copyright.(c).1997.lucasarts.@\n"
        "@@@@@@..entertainment.co..@@@@@@"
    )
    writeLine(file, "################################")

def _ndy_write_section_header_ijim(file):
    writeSectionTitle(file, "HEADER")
    writeLine(file, "# version and global constant settings")
    writeLine(file, "Version                  3")
    writeLine(file, "World Gravity            2.000000")
    writeLine(file, "Ceiling Sky Z            12.000000")
    writeLine(file, "Horizon Distance         200.000000")
    writeLine(file, "Horizon Pixels per Rev   768.000000")
    writeLine(file, "Horizon Sky Offset       0.00000000 0.00000000")
    writeLine(file, "Ceiling Sky Offset       0.00000000 0.00000000")
    writeLine(file, "LOD Distances            0.30000001 0.60000002 0.89999998 1.20000005")
    writeLine(file, "Fog                      0   0.50000000 0.50000000 0.55000001 1.00000000   0.00000000   350.00000000")
    writeLine(file, "################################")

def _ndy_write_section_header_jkdf2(file):
    writeSectionTitle(file, "HEADER")
    writeLine(file, "# version and global constant settings")
    writeLine(file, "Version          1")
    writeLine(file, "World Gravity    4.00")
    writeLine(file, "Ceiling Sky Z    20.000000")
    writeLine(file, "Horizon Distance 200.000000")
    writeLine(file, "Horizon Pixels per Rev 768.000000")
    writeLine(file, "Horizon Sky Offset   0.000000 0.000000")
    writeLine(file, "Ceiling Sky Offset   0.000000 0.000000")
    writeLine(file, "MipMap Distances	1.000000	2.000000	3.000000	4.000000")
    writeLine(file, "LOD Distances		0.300000	0.600000	0.900000	1.200000")
    writeLine(file, "Perspective distance 2.00")
    writeLine(file, "Gouraud distance 2.00")
    writeLine(file, "################################")

def _ndy_write_section_lec_and_header(file, version: NdyVersion):
    if version == NdyVersion.IJIM:
        _ndy_write_section_copyright_ijim(file)
        writeNewLine(file)
        _ndy_write_section_header_ijim(file)
    else:
        _ndy_write_section_copyright_jkdf2(file)
        writeNewLine(file)
        _ndy_write_section_header_jkdf2(file)
    writeNewLine(file)

def _ndy_write_section_materials(file, version: NdyVersion, materials, start_idx):
    num_mats = len(materials)
    if num_mats < 1:
        return

    writeSectionTitle(file, "MATERIALS")
    writeKeyValue(file, "World materials", start_idx+ num_mats + 64)
    writeNewLine(file)

    for idx, mat in enumerate(materials):
        row = '{:}: {:>15}'.format(start_idx + idx, mat)
        if version != NdyVersion.IJIM:
           row += "\t1.000000\t1.000000" 
        writeLine(file, row)

    writeLine(file, "end")
    writeLine(file, "################################")
    writeNewLine(file)
    writeNewLine(file)

def _ndy_write_colormaps(file):
    writeKeyValue(file, "World Colormaps", len(colormaps))
    for idx, cm in enumerate(colormaps):
        writeLine(file, '{:}:\t{}'.format(idx, cm))

def _ndy_write_write_vertices(file, model: Model3do, start_idx) -> List[Mesh3do]:
    vertices = []
    meshes = []
    for n in model.meshHierarchy:
        if n.meshIdx < 0: continue
        m = model.geosets[0].meshes[n.meshIdx]
        meshes.append(m) 
        for v in m.vertices:
            vert = _vec_convert_to_space(n.obj.matrix_world, v) # convert vertex coordinates to global
            vertices.append(vert)
    
    writeKeyValue(file, "World vertices", start_idx + len(vertices))
    writeNewLine(file)

    writeCommentLine(file, "num:     x:         y:         z:")
    for idx, v in enumerate(vertices):
        row = '{:}:'.format(start_idx + idx)
        row += vec2str(v, True, 9)
        writeLine(file, row)
    writeNewLine(file)
    writeNewLine(file)

    return meshes

def _ndy_write_uv_vertices(file, meshs: List[Mesh3do], start_idx):
    uvs = []
    for m in meshs:
        for uv in m.uvs:
            uvs.append(uv)
            
    writeKeyValue(file, "World texture vertices", start_idx + len(uvs))
    writeNewLine(file)

    writeCommentLine(file, " num:	u:	v:")
    for idx, vert in enumerate(uvs):
        row = '{:}:'.format(start_idx + idx)
        row += vec2str(vert, True, 9)
        writeLine(file, row)
    writeNewLine(file)
    writeNewLine(file)

def _surface_vertices_to_str(vert_idxs: List[int], vert_start_idx, uv_vert_idxs: List[int], uv_start_idx):
    out = '{:>8}  '.format(len(vert_idxs))
    for i in range(0, len(vert_idxs)):
        out += "{:>3},{:>2}\t".format(vert_start_idx + vert_idxs[i], uv_start_idx + uv_vert_idxs[i])
    return out

def _surface_vertex_colors_to_str(version: NdyVersion, vert_idxs: List[int], vertices_color):
    out =""
    for vidx in vert_idxs:
        color = vertices_color[vidx]
        if version == NdyVersion.IJIM:
            color = _rgba_to_rgb(vertices_color[vidx])
            color = _color_to_str(color)
        elif version == NdyVersion.MOTS:
            color = Vector4f(color.w, color.x, color.y, color.z)
            color = _color_to_str(color)
        else: # JKDF2
            color = _rgba_to_intensity_str(color)
        out += '{}\t'.format(color)
    return out

def _is_floor(face: Mesh3doFace):
    # if face is banked for less than 46 degrees it's a ground floor
    return round(degrees(Vector(face.normal).angle((0.0, 0.0, 1.0)))) <= 45

def _ndy_write_surfaces(file, version: NdyVersion, meshes: List[Mesh3do], mat_start_idx, vert_start_idx, uv_start_idx, surface_start_idx):
    num_faces = sum(len(m.faces) for m in meshes)
    
    writeKeyValue(file, "World surfaces", surface_start_idx + num_faces)
    writeNewLine(file)

    writeCommentLine(file, " num:	mat:	surfflags:	faceflags:	geo:	light:	tex:	adjoin:	extralight:	nverts:	vertices:	intensities:")
    face_normals = []
    for sec_idx, m in enumerate(meshes):
        if separate_sector_surfaces:
            writeLine(file, f"# Surfaces of Sector {sec_idx}")
        for idx, face in enumerate(m.faces):
            surfflags = default_surfflags
            if _is_floor(face):
                surfflags |= 0x05 # 0x1 - floor | 0x4 - Collision

            row = '{}:\t'.format(surface_start_idx + idx)          # row idx
            row += '{}\t'.format(mat_start_idx + face.materialIdx) # mat idx
            row += '0x{:01x}\t'.format(surfflags)                  # surfflags
            row += '0x{:01x}\t'.format(face.type)                  # faceflags
            row += '{}\t'.format(face.geometryMode)                # geo
            row += '{}\t'.format(face.lightMode)                   # light
            row += '{}\t'.format(face.textureMode)                 # tex
            row += '{}\t'.format(-1)                               # adjoin
            row += '{}\t'.format(_color_to_str(face.color) if version == NdyVersion.IJIM else _rgba_to_intensity_str(face.color))     # extralight
            row += _surface_vertices_to_str(face.vertexIdxs, vert_start_idx, face.uvIdxs, uv_start_idx)
            row += _surface_vertex_colors_to_str(version, face.vertexIdxs, m.vertexColors)
            writeLine(file, row)

            # Local space face normal coordinates
            face_normals.append(face.normal)
            
        # increment start indices
        surface_start_idx += len(m.faces)
        vert_start_idx    += len(m.vertices)
        uv_start_idx      += len(m.uvs)
        if separate_sector_surfaces:
                writeLine(file, f"#######################################")
                writeNewLine(file)

    if not separate_sector_surfaces:
        writeNewLine(file)
    writeNewLine(file)

    # write face normals
    writeCommentLine(file, " --- Surface normals ---")
    surface_start_idx -= len(face_normals)
    for idx, n in enumerate(face_normals):
        row = '{}:\t'.format(surface_start_idx + idx)
        row += vec2str(n, True, 0)
        writeLine(file, row)

    writeNewLine(file)
    writeNewLine(file)

def _ndy_write_section_georesource(file, version: NdyVersion, model: Model3do, mat_start_idx, vert_start_idx, uv_start_idx, surface_start_idx):
    writeSectionTitle(f, "GEORESOURCE")

    if version != NdyVersion.IJIM:
        writeCommentLine(f, " ------ Palette Subsection -----")
        _ndy_write_colormaps(f)

    writeCommentLine(f, " ----- Vertices Subsection -----")
    meshes = _ndy_write_write_vertices(f, model, vert_start_idx)

    writeCommentLine(f, " -- Texture Verts Subsection ---")
    _ndy_write_uv_vertices(f, meshes, uv_start_idx)

    writeCommentLine(f, " ----- Surfaces Subsection -----")
    writeLine(f, "World adjoins 0")
    writeNewLine(f)
    writeCommentLine(f, " num:	flags:	mirror:	dist:")
    writeNewLine(f)

    writeCommentLine(f, " ----- Surfaces Subsection -----")
    _ndy_write_surfaces(f, version, meshes, mat_start_idx, vert_start_idx, uv_start_idx, surface_start_idx)

def _get_sector_dimensions(mesh: Mesh3do, world_matrix):
    bb_min = Vector((999999999999.0, 999999999999.0, 999999999999.0))
    bb_max = Vector((-999999999999.0, -999999999999.0, -999999999999.0))
    center = Vector((0.0, 0.0, 0.0))

    for vert in mesh.vertices:
        vert = _vec_convert_to_space(world_matrix, vert) # convert vertex coordinates to global
        if vert.x < bb_min.x:
            bb_min.x = vert.x
        if vert.x > bb_max.x:
            bb_max.x = vert.x
        if vert.y < bb_min.y:
            bb_min.y = vert.y
        if vert.y > bb_max.y:
            bb_max.y = vert.y
        if vert.z < bb_min.z:
            bb_min.z = vert.z
        if vert.z > bb_max.z:
            bb_max.z = vert.z

        center.x += vert.x
        center.y += vert.y
        center.z += vert.z

    center.x /= len(mesh.vertices)
    center.y /= len(mesh.vertices)
    center.z /= len(mesh.vertices)

    r = 0.0
    for vert in mesh.vertices:
        vert = _vec_convert_to_space(world_matrix, vert) # convert vertex coordinates to global
        dist = sqrt(pow(vert.x - center.x, 2) + pow(vert.y - center.y, 2) + pow(vert.y - center.y, 2))
        if dist > r:
            r = dist
    return (bb_min, bb_max, center, r)

def _ndy_write_section_sectors(file, version: NdyVersion, model: Model3do, sector_idx, vert_start_idx, surface_start_idx):
    meshes = model.geosets[0].meshes
    
    writeCommentLine(f, "###### Sector information ######")
    writeSectionTitle(f, "SECTORS")

    writeKeyValue(file, "World sectors", sector_idx + len(meshes))
    writeNewLine(f)
    writeNewLine(f)

    def _sec_color_2_str(color: Vector4f, version) -> str:
        if version == NdyVersion.IJIM:
            color = _rgba_to_rgb(color)
        else:
            color = _rgba_to_intensity(color)
        return _color_to_str(color)

    for idx, n in enumerate(model.meshHierarchy):
        if n.meshIdx < 0: 
            idx -= 1
            continue
        m = meshes[n.meshIdx]

        writeKeyValue(file, "SECTOR", sector_idx + idx)
        writeKeyValue(file, "FLAGS", '0x{:01x}'.format(0))
        writeKeyValue(file, "AMBIENT LIGHT", _sec_color_2_str(ambient_light, version))
        writeKeyValue(file, "EXTRA LIGHT", _sec_color_2_str(sector_extra_light, version))
        if version  == NdyVersion.IJIM:
            writeKeyValue(file, "AVERAGE LIGHT INTENSITY", '0.0 0.0 0.0')
            writeKeyValue(file, "AVERAGE LIGHT POSITION", '0.0 0.0 0.0')
            writeKeyValue(file, "AVERAGE LIGHT FALLOFF", '0.0 0.0')
        else: # JKDF2 & MOTS
            writeKeyValue(file, "COLORMAP", default_colormap_idx)
            writeKeyValue(file, "TINT", '0.0 0.0 0.0')

        bb_min, bb_max, center, radius = _get_sector_dimensions(m, n.obj.matrix_world)
        writeKeyValue(file, "BOUNDBOX", vec2str(bb_min) + vec2str(bb_max))
        writeKeyValue(file, "CENTER", vec2str(center))
        writeKeyValue(file, "RADIUS", r2str(radius))

        writeKeyValue(file, 'VERTICES', len(m.vertices))
        for i in range(len(m.vertices)):
            writeKeyValue(file, '', '{}: {}'.format(i, vert_start_idx + i))
        vert_start_idx += len(m.vertices)

        writeKeyValue(file, 'SURFACES', '{} {}'.format(surface_start_idx, len(m.faces)))
        surface_start_idx += len(m.faces)
        writeNewLine(f)

def _make_model3do_from_obj(obj: bpy.types.Object, version: NdyVersion):
    model = Model3do(obj.name)
    model.geosets.append(Model3doGeoSet())
    uvAbsolute = False if version == NdyVersion.IJIM else True
    model3do_add_obj(model, obj, parent=obj, uvAbsolute=uvAbsolute, exportVertexColors=True)
    return model

# Get one selected object
if len(bpy.context.selected_objects) == 0:
    print("Error: could not determine which objects to export. Put into '{}' group or select (1) top object in hierarchy!".format(kGModel3do))
    raise Exception('No object selected to export')

if len(bpy.context.selected_objects) > 1:
    print("Error: could not determine which objects to export, more then 1 object selected!")
    raise Exception('Too many objects selected to export')

obj = bpy.context.selected_objects[0]
model = _make_model3do_from_obj(obj, out_version)

assert len(model.geosets) == 1, "Converted OBJ to 3DO model must have exact 1 geoset"

# Write to ndy file
f = open(out_file, 'w', encoding='utf-8')

# write copyright and header sections
_ndy_write_section_lec_and_header(f, out_version)

# Write materials
_ndy_write_section_materials(f, out_version, model.materials, mat_start_idx)

# Write Georesources
_ndy_write_section_georesource(f, out_version, model, mat_start_idx, vert_start_idx, uv_start_idx, surface_start_idx)

# Write sector
_ndy_write_section_sectors(f, out_version, model, sector_idx, vert_start_idx, surface_start_idx)

f.flush()
f.close()